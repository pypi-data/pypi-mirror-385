"""
V2 Tool Calling System

Core components for tool declaration, registration, execution, and schema generation.
Built on V1's proven Schema system with enhanced pairing integrity.
"""

from .schema import (
    Schema,
    SchemaType,
    Base,
    BuiltinTypeMap,
    is_builtin_type,
    is_annotation_pydantic_model,
    IterableRoot,
    ResultType,
)

__all__ = [
    # Schema system
    "Schema",
    "SchemaType", 
    "Base",
    "BuiltinTypeMap",
    "is_builtin_type",
    "is_annotation_pydantic_model",
    "IterableRoot",
    "ResultType",
]