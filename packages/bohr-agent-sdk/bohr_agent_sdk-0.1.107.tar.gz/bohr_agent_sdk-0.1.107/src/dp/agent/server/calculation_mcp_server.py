import inspect
import os
from collections.abc import Callable
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Literal, Optional, TypedDict

import mcp
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.context_injection import (
    find_context_parameter,
)
from mcp.server.fastmcp.utilities.func_metadata import (
    _get_typed_signature,
    func_metadata,
)
from starlette.responses import JSONResponse
from starlette.routing import Route

from .executor import executor_dict
from .storage import storage_dict
from .utils import get_logger, JobResult, Tool
logger = get_logger(__name__)


def parse_uri(uri):
    scheme = urlparse(uri).scheme
    if scheme == "":
        key = uri
        scheme = "local"
    else:
        key = uri[len(scheme)+3:]
    return scheme, key


def init_storage(storage_config: Optional[dict] = None):
    if not storage_config:
        storage_config = {"type": "local"}
    storage_config = deepcopy(storage_config)
    storage_type = storage_config.pop("type")
    storage = storage_dict[storage_type](**storage_config)
    return storage_type, storage


def init_executor(executor_config: Optional[dict] = None):
    if not executor_config:
        executor_config = {"type": "local"}
    executor_config = deepcopy(executor_config)
    executor_type = executor_config.pop("type")
    return executor_type, executor_dict[executor_type](**executor_config)


@contextmanager
def set_directory(workdir: str):
    cwd = os.getcwd()
    os.makedirs(workdir, exist_ok=True)
    try:
        os.chdir(workdir)
        yield
    finally:
        os.chdir(cwd)


def query_job_status(job_id: str, executor: Optional[dict] = None
                     ) -> Literal["Running", "Succeeded", "Failed"]:
    """
    Query status of a calculation job
    Args:
        job_id (str): The ID of the calculation job
    Returns:
        status (str): One of "Running", "Succeeded" or "Failed"
    """
    trace_id, exec_id = job_id.split("/")
    with set_directory(trace_id):
        _, executor = init_executor(executor)
        status = executor.query_status(exec_id)
        logger.info("Job %s status is %s" % (job_id, status))
    return status


def terminate_job(job_id: str, executor: Optional[dict] = None):
    """
    Terminate a calculation job
    Args:
        job_id (str): The ID of the calculation job
    """
    trace_id, exec_id = job_id.split("/")
    with set_directory(trace_id):
        _, executor = init_executor(executor)
        executor.terminate(exec_id)
        logger.info("Job %s is terminated" % job_id)


def handle_input_artifacts(fn, kwargs, storage):
    storage_type, storage = init_storage(storage)
    sig = inspect.signature(fn)
    input_artifacts = {}
    for name, param in sig.parameters.items():
        if param.annotation is Path or (
            param.annotation is Optional[Path] and
                kwargs.get(name) is not None):
            uri = kwargs[name]
            scheme, key = parse_uri(uri)
            if scheme == storage_type:
                s = storage
            else:
                s = storage_dict[scheme]()
            path = s.download(key, "inputs/%s" % name)
            logger.info("Artifact %s downloaded to %s" % (
                uri, path))
            kwargs[name] = Path(path)
            input_artifacts[name] = {
                "storage_type": scheme,
                "uri": uri,
            }
    return kwargs, input_artifacts


def handle_output_artifacts(results, exec_id, storage):
    storage_type, storage = init_storage(storage)
    output_artifacts = {}
    if isinstance(results, dict):
        for name in results:
            if isinstance(results[name], Path):
                key = storage.upload("%s/outputs/%s" % (exec_id, name),
                                     results[name])
                uri = storage_type + "://" + key
                logger.info("Artifact %s uploaded to %s" % (
                    results[name], uri))
                results[name] = uri
                output_artifacts[name] = {
                    "storage_type": storage_type,
                    "uri": uri,
                }
    return results, output_artifacts


# MCP does not regard Any as serializable in Python 3.12
# use Optional[Any] to work around
def get_job_results(job_id: str, executor: Optional[dict] = None,
                    storage: Optional[dict] = None) -> Optional[Any]:
    """
    Get results of a calculation job
    Args:
        job_id (str): The ID of the calculation job
    Returns:
        results (Any): results of the calculation job
    """
    trace_id, exec_id = job_id.split("/")
    with set_directory(trace_id):
        _, executor = init_executor(executor)
        results = executor.get_results(exec_id)
        results, output_artifacts = handle_output_artifacts(
            results, exec_id, storage)
        logger.info("Job %s result is %s" % (job_id, results))
    return JobResult(result=results, job_info={
        "output_artifacts": output_artifacts,
    })


class CalculationMCPServer:
    def __init__(self, *args, preprocess_func=None, fastmcp_mode=False,
                 **kwargs):
        """
        Args:
            preprocess_func: The preprocess function for all tools
            fastmcp_mode: compatible for fastmcp.FastMCP
        """
        self.preprocess_func = preprocess_func
        self.fastmcp_mode = fastmcp_mode
        self.mcp = FastMCP(*args, **kwargs)

    def add_patched_tool(self, fn, new_fn, name, is_async=False, doc=None,
                         override_return_annotation=False):
        """patch the metadata of the tool"""
        context_kwarg = find_context_parameter(fn)

        def _get_typed_signature_patched(call):
            """patch parameters"""
            typed_signature = _get_typed_signature(call)
            new_typed_signature = _get_typed_signature(new_fn)
            parameters = []
            for param in typed_signature.parameters.values():
                if param.annotation is Path:
                    parameters.append(inspect.Parameter(
                        name=param.name, default=param.default,
                        annotation=str, kind=param.kind))
                elif param.annotation is Optional[Path]:
                    parameters.append(inspect.Parameter(
                        name=param.name, default=param.default,
                        annotation=Optional[str], kind=param.kind))
                else:
                    parameters.append(param)
            for param in new_typed_signature.parameters.values():
                if param.name != "kwargs":
                    parameters.append(param)
            return inspect.Signature(
                parameters,
                return_annotation=(new_typed_signature.return_annotation
                                   if override_return_annotation
                                   else typed_signature.return_annotation))

        # Due to the frequent changes of MCP, we use a patching style here
        mcp.server.fastmcp.utilities.func_metadata._get_typed_signature = \
            _get_typed_signature_patched
        func_arg_metadata = func_metadata(
            fn,
            skip_names=[context_kwarg] if context_kwarg is not None else [],
            structured_output=None,
        )
        mcp.server.fastmcp.utilities.func_metadata._get_typed_signature = \
            _get_typed_signature
        if self.fastmcp_mode and func_arg_metadata.wrap_output:
            # Only simulate behavior of fastmcp for output_schema
            func_arg_metadata.output_schema["x-fastmcp-wrap-result"] = True
        parameters = func_arg_metadata.arg_model.model_json_schema(
            by_alias=True)
        tool = Tool(
            fn=new_fn,
            name=name,
            description=doc or fn.__doc__,
            parameters=parameters,
            fn_metadata=func_arg_metadata,
            is_async=is_async,
            context_kwarg=context_kwarg,
        )
        self.mcp._tool_manager._tools[name] = tool

    def add_tool(self, fn, *args, **kwargs):
        tool = Tool.from_function(fn, *args, **kwargs)
        self.mcp._tool_manager._tools[tool.name] = tool
        return tool

    def tool(self, preprocess_func=None):
        if preprocess_func is None:
            preprocess_func = self.preprocess_func

        def decorator(fn: Callable) -> Callable:
            def submit_job(executor: Optional[dict] = None,
                           storage: Optional[dict] = None,
                           **kwargs) -> TypedDict("results", {
                               "job_id": str, "extra_info": Optional[dict]}):
                trace_id = datetime.today().strftime('%Y-%m-%d-%H:%M:%S.%f')
                logger.info("Job processing (Trace ID: %s)" % trace_id)
                with set_directory(trace_id):
                    if preprocess_func is not None:
                        executor, storage, kwargs = preprocess_func(
                            executor, storage, kwargs)
                    kwargs, input_artifacts = handle_input_artifacts(
                        fn, kwargs, storage)
                    executor_type, executor = init_executor(executor)
                    res = executor.submit(fn, kwargs)
                    exec_id = res["job_id"]
                    job_id = "%s/%s" % (trace_id, exec_id)
                    logger.info("Job submitted (ID: %s)" % job_id)
                result = {
                    "job_id": job_id,
                    "extra_info": res.get("extra_info"),
                }
                return JobResult(result=result, job_info={
                    "trace_id": trace_id,
                    "executor_type": executor_type,
                    "job_id": job_id,
                    "extra_info": res.get("extra_info"),
                    "input_artifacts": input_artifacts,
                })

            async def run_job(executor: Optional[dict] = None,
                              storage: Optional[dict] = None, **kwargs):
                context = self.mcp.get_context()
                trace_id = datetime.today().strftime('%Y-%m-%d-%H:%M:%S.%f')
                logger.info("Job processing (Trace ID: %s)" % trace_id)
                with set_directory(trace_id):
                    if preprocess_func is not None:
                        executor, storage, kwargs = preprocess_func(
                            executor, storage, kwargs)
                    kwargs, input_artifacts = handle_input_artifacts(
                        fn, kwargs, storage)
                    executor_type, executor = init_executor(executor)
                    res = await executor.async_run(
                        fn, kwargs, context, trace_id)
                    exec_id = res["job_id"]
                    job_id = "%s/%s" % (trace_id, exec_id)
                    results = res["result"]
                    results, output_artifacts = handle_output_artifacts(
                        results, exec_id, storage)
                    logger.info("Job %s result is %s" % (job_id, results))
                    await context.log(level="info", message="Job %s result is"
                                      " %s" % (job_id, results))
                return JobResult(result=results, job_info={
                    "trace_id": trace_id,
                    "executor_type": executor_type,
                    "job_id": job_id,
                    "extra_info": res.get("extra_info"),
                    "input_artifacts": input_artifacts,
                    "output_artifacts": output_artifacts,
                })

            self.add_patched_tool(fn, run_job, fn.__name__, is_async=True)
            self.add_patched_tool(
                fn, submit_job, "submit_" + fn.__name__, doc="Submit a job",
                override_return_annotation=True)
            self.add_tool(query_job_status)
            self.add_tool(terminate_job)
            self.add_tool(get_job_results)
            return fn
        return decorator

    def run(self, **kwargs):
        if os.environ.get("DP_AGENT_RUNNING_MODE") in ["1", "true"]:
            return

        async def health_check(request):
            return JSONResponse({"status": "ok"})

        self.mcp._custom_starlette_routes.append(
            Route(
                "/health",
                endpoint=health_check,
                methods=["GET"],
                name="health_check",
                include_in_schema=True,
            )
        )
        self.mcp.run(**kwargs)
