from typing import Any

from google.cloud import storage  # type: ignore[import-untyped]

from ._get_storage_client import get_storage_client
from .settings import settings_manager


def get_bucket(
    config_key: str | None = None,
    *,
    auth_config_key: str | None = None,
    **kwargs: Any,
) -> storage.Bucket:
    settings = settings_manager.get_settings(config_key)
    client = get_storage_client(auth_config_key, **kwargs)
    return client.bucket(settings.bucket_name)
