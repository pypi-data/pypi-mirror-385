"""
Loader settings for different snapshot storage backends.

Each loader type has its own settings class that inherits from BaseLoaderSettings.
"""

from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field


class BaseLoaderSettings(BaseModel):
    """Base settings that all loaders must implement"""
    agent_id: Optional[str] = Field(None, description="Agent identifier for isolation")
    enable_logging: bool = Field(True, description="Enable detailed logging")


class LocalLoaderSettings(BaseLoaderSettings):
    """Settings for LocalSnapshotLoader - file-based storage"""

    base_dir: Path = Field(..., description="Base directory for snapshot storage")
    format: Literal["json", "pickle", "msgpack"] = Field("json", description="Serialization format")
    compress: bool = Field(False, description="Enable compression")
    compression_level: int = Field(6, description="Compression level (1-9 for gzip)")
    include_full_tree: bool = Field(True, description="Include full PACT tree vs delta")
    include_metadata: bool = Field(True, description="Include snapshot metadata")

    model_config = {"arbitrary_types_allowed": True}


class SQLiteLoaderSettings(BaseLoaderSettings):
    """Settings for SQLiteSnapshotLoader - database storage (future)"""

    db_path: Path = Field(..., description="Path to SQLite database file")
    table_name: str = Field("snapshots", description="Table name for snapshots")
    connection_pool_size: int = Field(5, description="Connection pool size")

    model_config = {"arbitrary_types_allowed": True}


class RedisLoaderSettings(BaseLoaderSettings):
    """Settings for RedisSnapshotLoader - in-memory storage (future)"""

    host: str = Field("localhost", description="Redis server host")
    port: int = Field(6379, description="Redis server port")
    db: int = Field(0, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")
    ttl_seconds: Optional[int] = Field(None, description="TTL for snapshots in Redis")


class S3LoaderSettings(BaseLoaderSettings):
    """Settings for S3SnapshotLoader - cloud storage (future)"""

    bucket_name: str = Field(..., description="S3 bucket name")
    region: str = Field("us-east-1", description="AWS region")
    prefix: str = Field("snapshots/", description="Key prefix for snapshots")
    access_key: Optional[str] = Field(None, description="AWS access key")
    secret_key: Optional[str] = Field(None, description="AWS secret key")


__all__ = [
    "BaseLoaderSettings",
    "LocalLoaderSettings",
    "SQLiteLoaderSettings",
    "RedisLoaderSettings",
    "S3LoaderSettings",
]
