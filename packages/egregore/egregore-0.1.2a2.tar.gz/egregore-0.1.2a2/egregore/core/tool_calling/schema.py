"""
V2 Tool Calling Schema System - Adapted from V1

Comprehensive schema system for tool parameter and response definitions.
Supports JSON Schema generation from Python type annotations.
"""

from pydantic import BaseModel, Field, RootModel
from typing import Any, Optional, Type, cast, Generic, TypeVar, Callable, get_args, get_origin, Union, Literal
from enum import Enum
import types
import inspect
from inspect import Parameter, isclass
from types import UnionType, GenericAlias


class SchemaType(Enum):
    """Schema type enumeration for JSON Schema generation."""

    TYPE_UNSPECIFIED = 'type_unspecified'
    STRING = 'string'
    NUMBER = 'number'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    ARRAY = 'array'
    OBJECT = 'object'


BuiltinTypeMap = {
    str: SchemaType.STRING,
    int: SchemaType.INTEGER,
    float: SchemaType.NUMBER,
    bool: SchemaType.BOOLEAN,
    list: SchemaType.ARRAY,
    dict: SchemaType.OBJECT,
}

VersionedUnionType = types.UnionType


def is_builtin_type(annotation: Parameter.annotation) -> bool:
    """Check if annotation is a builtin type supported by schema generation."""
    return annotation in BuiltinTypeMap.keys()


def is_annotation_pydantic_model(annotation: Any) -> bool:
    """Check if annotation is a Pydantic model class."""
    try:
        return isclass(annotation) and issubclass(annotation, BaseModel)
    except TypeError:
        return False


class Base(BaseModel):
    """Base class for schema-related models."""
    
    def to_json_dict(self) -> dict[str, object]:
        return self.model_dump(exclude_none=True, mode='json')


class Schema(Base):
    """
    Schema that defines the format of input and output data.
    
    Comprehensive JSON Schema implementation supporting:
    - Basic types (str, int, float, bool, list, dict)
    - Complex types (Union, Optional, Literal, Generic)
    - Pydantic models with automatic property extraction
    - Parameter validation and default values
    """

    example: Optional[Any] = Field(
        default=None,
        description="Optional. Example of the object. Will only populated when the object is the root.",
    )
    pattern: Optional[str] = Field(
        default=None,
        description="Optional. Pattern of the Type.STRING to restrict a string to a regular expression.",
    )
    default: Optional[Any] = Field(
        default=None, description="Optional. Default value of the data."
    )
    max_length: Optional[int] = Field(
        default=None,
        description="Optional. Maximum length of the Type.STRING",
    )
    min_length: Optional[int] = Field(
        default=None,
        description="Optional. SCHEMA FIELDS FOR TYPE STRING Minimum length of the Type.STRING",
    )
    min_properties: Optional[int] = Field(
        default=None,
        description="Optional. Minimum number of the properties for Type.OBJECT.",
    )
    max_properties: Optional[int] = Field(
        default=None,
        description="Optional. Maximum number of the properties for Type.OBJECT.",
    )
    any_of: Optional[list['Schema']] = Field(
        default=None,
        description="Optional. The value should be validated against any (one or more) of the subschemas in the list.",
    )
    description: Optional[str] = Field(
        default=None, description="Optional. The description of the data."
    )
    enum: Optional[list[str]] = Field(
        default=None,
        description='Optional. Possible values of the element of primitive type with enum format. Examples: 1. We can define direction as : {type:STRING, format:enum, enum:["EAST", NORTH", "SOUTH", "WEST"]} 2. We can define apartment number as : {type:INTEGER, format:enum, enum:["101", "201", "301"]}',
    )
    format: Optional[str] = Field(
        default=None,
        description='Optional. The format of the data. Supported formats: for NUMBER type: "float", "double" for INTEGER type: "int32", "int64" for STRING type: "email", "byte", etc',
    )
    items: Optional['Schema'] = Field(
        default=None,
        description="Optional. SCHEMA FIELDS FOR TYPE ARRAY Schema of the elements of Type.ARRAY.",
    )
    max_items: Optional[int] = Field(
        default=None,
        description="Optional. Maximum number of the elements for Type.ARRAY.",
    )
    maximum: Optional[float] = Field(
        default=None,
        description="Optional. Maximum value of the Type.INTEGER and Type.NUMBER",
    )
    min_items: Optional[int] = Field(
        default=None,
        description="Optional. Minimum number of the elements for Type.ARRAY.",
    )
    minimum: Optional[float] = Field(
        default=None,
        description="Optional. SCHEMA FIELDS FOR TYPE INTEGER and NUMBER Minimum value of the Type.INTEGER and Type.NUMBER",
    )
    nullable: Optional[bool] = Field(
        default=None,
        description="Optional. Indicates if the value may be null.",
    )
    properties: Optional[dict[str, 'Schema']] = Field(
        default=None,
        description="Optional. SCHEMA FIELDS FOR TYPE OBJECT Properties of Type.OBJECT.",
    )
    property_ordering: Optional[list[str]] = Field(
        default=None,
        description="Optional. The order of the properties. Not a standard field in open api spec. Only used to support the order of the properties.",
    )
    required: Optional[list[str]] = Field(
        default=None,
        description="Optional. Required properties of Type.OBJECT.",
    )
    title: Optional[str] = Field(
        default=None, description="Optional. The title of the Schema."
    )
    type: Optional[SchemaType] = Field(
        default=None, description="Optional. The type of the data."
    )

    def to_json_dict(self, lower_formatting: bool = False) -> dict[str, object]:
        """Convert schema to JSON dict with optional lowercase type formatting."""
        json_dict = super().to_json_dict()
        if "type" in json_dict and lower_formatting:
            json_dict["type"] = cast(str, json_dict["type"]).lower()
        return json_dict

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert schema to OpenAI-compatible function parameter schema."""
        json_dict = self.to_json_dict(lower_formatting=True)
        
        # Convert SchemaType enum values to strings
        if "type" in json_dict and hasattr(json_dict["type"], "value"):
            json_dict["type"] = json_dict["type"].value
            
        return json_dict

    @classmethod
    def from_parameter(
        cls: Type['Schema'],
        param: Parameter,
    ) -> "Schema":
        """
        Parse schema from function parameter.
        
        Supports automatic schema generation from type annotations including:
        - Basic types (str, int, float, bool, list, dict)
        - Union types and Optional types  
        - Generic types (List[T], Dict[K,V])
        - Literal types for enums
        - Pydantic models with property extraction
        
        Args:
            param: Function parameter with type annotation
            
        Returns:
            Schema object representing the parameter
            
        Raises:
            ValueError: If parameter type is not supported
        """
        schema: Schema = cls(properties=None)
        
        if is_builtin_type(param.annotation):
            if param.default is not Parameter.empty:
                schema.default = param.default
            schema.type = BuiltinTypeMap[param.annotation]
            return schema
            
        if (
            isinstance(param.annotation, UnionType)
            # only parse simple UnionType, example int | str | float | bool
            # complex UnionType will be invoked in raise branch
            and all(
                (is_builtin_type(arg) or arg is type(None))
                for arg in get_args(param.annotation)
            )
        ):
            schema.type = BuiltinTypeMap[dict]
            schema.any_of = []
            unique_types = set()
            for arg in get_args(param.annotation):
                if arg.__name__ == 'NoneType':  # Optional type
                    schema.nullable = True
                    continue
                schema_in_any_of = cls.from_parameter(
                    Parameter(
                        'item', Parameter.POSITIONAL_OR_KEYWORD, annotation=arg
                    ),
                )
                if (
                    schema_in_any_of.model_dump_json(exclude_none=True)
                    not in unique_types
                ):
                    schema.any_of.append(schema_in_any_of)
                    unique_types.add(
                        schema_in_any_of.model_dump_json(exclude_none=True))
            if len(schema.any_of) == 1:  # param: list | None -> Array
                schema.type = schema.any_of[0].type
                schema.any_of = None
            if (
                param.default is not Parameter.empty
                and param.default is not None
            ):
                schema.default = param.default
            return schema
            
        if isinstance(param.annotation, GenericAlias) or hasattr(param.annotation, '__origin__'):
            origin = get_origin(param.annotation)
            args = get_args(param.annotation)
            if origin is dict:
                schema.type = BuiltinTypeMap[dict]
                if param.default is not Parameter.empty:
                    schema.default = param.default
                return schema
            if origin is Literal:
                if not all(isinstance(arg, str) for arg in args):
                    raise ValueError(
                        f'Literal type {param.annotation} must be a list of strings.'
                    )
                schema.type = BuiltinTypeMap[str]
                schema.enum = list(args)
                if param.default is not Parameter.empty:
                    schema.default = param.default
                return schema
            if origin is list:
                schema.type = BuiltinTypeMap[list]
                schema.items = cls.from_parameter(
                    Parameter(
                        'item',
                        Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=args[0],
                    ),
                )
                if param.default is not Parameter.empty:
                    schema.default = param.default
                return schema
            if origin is Union:
                schema.any_of = []
                schema.type = BuiltinTypeMap[dict]
                unique_types = set()
                for arg in args:
                    # The first check is for NoneType in Python 3.9, since the __name__
                    # attribute is not available in Python 3.9
                    if type(arg) is type(None) or (
                        hasattr(arg, '__name__') and arg.__name__ == 'NoneType'
                    ):  # Optional type
                        schema.nullable = True
                        continue
                    schema_in_any_of = cls.from_parameter(
                        Parameter(
                            'item',
                            Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=arg,
                        ),
                    )
                    if (
                        len(param.annotation.__args__) == 2
                        and type(None) in param.annotation.__args__
                    ):  # Optional type
                        for optional_arg in param.annotation.__args__:
                            if (
                                hasattr(optional_arg, '__origin__')
                                and optional_arg.__origin__ is list
                            ):
                                # Optional type with list, for example Optional[list[str]]
                                schema.items = schema_in_any_of.items
                    if (
                        schema_in_any_of.model_dump_json(exclude_none=True)
                        not in unique_types
                    ):
                        schema.any_of.append(schema_in_any_of)
                        unique_types.add(
                            schema_in_any_of.model_dump_json(exclude_none=True))
                # param: Union[List, None] -> Array
                if len(schema.any_of) == 1:
                    schema.type = schema.any_of[0].type
                    schema.any_of = None
                if (
                    param.default is not None
                    and param.default is not Parameter.empty
                ):
                    schema.default = param.default
                return schema
                # all other generic alias will be invoked in raise branch
                
        if (
            # for user defined class, we only support pydantic model
            is_annotation_pydantic_model(param.annotation)
        ):
            if (
                param.default is not Parameter.empty
                and param.default is not None
            ):
                schema.default = param.default
            schema.type = BuiltinTypeMap[dict]
            schema.properties = {}
            for field_name, field_info in param.annotation.model_fields.items():
                schema.properties[field_name] = cls.from_parameter(
                    Parameter(
                        field_name,
                        Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=field_info.annotation,
                    ),
                )
            schema.required = schema._get_required_fields()
            return schema
            
        raise ValueError(
            f'Failed to parse the parameter {param} '
            ' automatic function calling. Automatic function calling works best with'
            ' simpler function signature schema, consider manually parse your'
        )

    def _get_required_fields(self) -> Optional[list[str]]:
        """Get list of required fields from object properties."""
        if not self.properties:
            return None
        return [
            field_name
            for field_name, field_schema in self.properties.items()
            if not field_schema.nullable and field_schema.default is None
        ]


T = TypeVar('T')


class IterableRoot(RootModel[list[T]]):
    """Root model for iterable collections."""
    root: list[T]

    def __iter__(self):
        return iter(self.root)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.root})"

    def __str__(self):
        return f"{self.__class__.__name__}({self.root})"
    
    def __getitem__(self, index: int | slice) -> T:
        if isinstance(index, slice):
            return self.root[index]
        else:
            return self.root[index]
    
    def __len__(self) -> int:
        return len(self.root)
    
    def __contains__(self, item: T) -> bool:
        return item in self.root


ResultType = TypeVar("ResultType", bound=Type[BaseModel])