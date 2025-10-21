import os
from typing import Optional

import oss2

from .base_storage import BaseStorage


class OSSStorage(BaseStorage):
    def __init__(
            self,
            endpoint: Optional[str] = None,
            bucket_name: Optional[str] = None,
            access_key_id: Optional[str] = None,
            access_key_secret: Optional[str] = None,
            prefix: Optional[str] = None,
    ) -> None:
        """OSS storage interface

        Args:
            endpoint: The OSS endpoint
            bucket_name: The OSS bucket name
            access_key_id: The OSS access key
            access_key_secret: The OSS secret key
            prefix: Artifact storage prefix in the OSS bucket
        """
        if endpoint is None:
            endpoint = os.environ.get("OSS_ENDPOINT")
        if bucket_name is None:
            bucket_name = os.environ.get("OSS_BUCKET_NAME")
        if access_key_id is None:
            access_key_id = os.environ.get("OSS_ACCESS_KEY_ID")
        if access_key_secret is None:
            access_key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
        if prefix is None:
            prefix = os.environ.get("OSS_PREFIX", "")
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.prefix = prefix
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        self.bucket = bucket

    def prefixing(self, key):
        if not key.startswith(self.prefix):
            return self.prefix + key
        return key

    def _upload(self, key, path):
        key = self.prefixing(key)
        self.bucket.put_object_from_file(key, path)
        return key

    def _download(self, key, path):
        key = self.prefixing(key)
        if os.path.dirname(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        self.bucket.get_object_to_file(key, path)
        return path

    def list(self, prefix, recursive=False):
        prefix = self.prefixing(prefix)
        keys = []
        if recursive:
            marker = ""
            while True:
                r = self.bucket.list_objects(prefix, marker=marker)
                for obj in r.object_list:
                    if not obj.key.endswith("/"):
                        keys.append(obj.key)
                if not r.is_truncated:
                    break
                marker = r.next_marker
        else:
            marker = ""
            while True:
                r = self.bucket.list_objects(prefix, delimiter="/",
                                             marker=marker)
                for obj in r.object_list:
                    if obj.key == prefix and obj.key.endswith("/"):
                        continue
                    keys.append(obj.key)
                for key in r.prefix_list:
                    keys.append(key)
                if not r.is_truncated:
                    break
                marker = r.next_marker
        return keys

    def copy(self, src, dst):
        src = self.prefixing(src)
        dst = self.prefixing(dst)
        self.bucket.copy_object(self.bucket_name, src, dst)

    def get_md5(self, key):
        key = self.prefixing(key)
        return self.bucket.get_object_meta(key).etag
