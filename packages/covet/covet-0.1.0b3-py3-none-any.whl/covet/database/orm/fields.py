"""
ORM Field Types

Comprehensive field type definitions for the CovetPy ORM.
Supports 17+ field types with validation, serialization, and database mapping.
"""

import json
import re
import uuid
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, List, Optional, Type


class Field:
    """
    Base class for all ORM fields.

    Provides common functionality for field definition, validation, and serialization.
    """

    def __init__(
        self,
        primary_key: bool = False,
        unique: bool = False,
        nullable: bool = True,
        null: bool = None,  # Alias for nullable
        default: Any = None,
        default_factory: Optional[Callable] = None,
        db_column: Optional[str] = None,
        db_index: bool = False,
        validators: Optional[List[Callable]] = None,
        verbose_name: Optional[str] = None,
        help_text: Optional[str] = None,
        editable: bool = True,
        choices: Optional[List] = None,
    ):
        """
        Initialize field.

        Args:
            primary_key: Whether this is a primary key
            unique: Whether values must be unique
            nullable: Whether NULL values are allowed (alias: null)
            null: Alias for nullable
            default: Default value
            default_factory: Callable that returns default value
            db_column: Database column name (defaults to field name)
            db_index: Whether to create an index
            validators: List of validation functions
            verbose_name: Human-readable field name
            help_text: Help text for documentation
            editable: Whether field can be edited
            choices: List of valid choices
        """
        self.primary_key = primary_key
        self.unique = unique
        # Support both 'nullable' and 'null' parameters (null takes precedence)
        if null is not None:
            nullable = null
        self.nullable = nullable if not primary_key else False
        self.default = default
        self.default_factory = default_factory
        self.db_column = db_column
        self.db_index = db_index or unique or primary_key
        self.validators = validators or []
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.editable = editable
        self.choices = choices

        self.name: Optional[str] = None  # Set by metaclass
        self.model: Optional[Type] = None  # Set by metaclass

    def get_default(self) -> Any:
        """Get default value for this field."""
        if self.default_factory:
            return self.default_factory()
        return self.default

    def validate(self, value: Any) -> Any:
        """
        Validate field value.

        Args:
            value: Value to validate

        Returns:
            Validated value

        Raises:
            ValueError: If validation fails
        """
        # Check nullable
        if value is None:
            if not self.nullable:
                raise ValueError(f"{self.name}: NULL values not allowed")
            return None

        # Check choices
        if self.choices and value not in [
            choice[0] if isinstance(choice, tuple) else choice for choice in self.choices
        ]:
            raise ValueError(f"{self.name}: Value must be one of {self.choices}")

        # Run custom validators
        for validator in self.validators:
            validator(value)

        # Type-specific validation
        return self.to_python(value)

    def to_python(self, value: Any) -> Any:
        """
        Convert database value to Python value.

        Args:
            value: Database value

        Returns:
            Python value
        """
        return value

    def to_db(self, value: Any) -> Any:
        """
        Convert Python value to database value.

        Args:
            value: Python value

        Returns:
            Database value
        """
        if value is None:
            return None
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """
        Get database column type for this field.

        Args:
            dialect: Database dialect (postgresql, mysql, sqlite)

        Returns:
            SQL column type
        """
        raise NotImplementedError("Subclasses must implement get_db_type()")

    def __get__(self, instance, owner):
        """
        Descriptor protocol: Get field value from instance.

        When accessing Model.field_name, returns the Field object (for class access).
        When accessing instance.field_name, returns the value from instance.__dict__.

        Args:
            instance: Model instance (None for class access)
            owner: Model class

        Returns:
            Field object (class access) or field value (instance access)
        """
        if instance is None:
            # Class access: Model.username -> Field object
            return self

        # Instance access: user.username -> actual value
        # Check instance __dict__ first (where values are stored)
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]

        # Not set yet, return default
        return self.get_default()

    def __set__(self, instance, value):
        """
        Descriptor protocol: Set field value on instance.

        Stores the value in instance.__dict__[field_name].

        Args:
            instance: Model instance
            value: Value to set
        """
        instance.__dict__[self.name] = value


class CharField(Field):
    """Character field for short strings."""

    def __init__(self, max_length: int = 255, min_length: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        if len(value) > self.max_length:
            raise ValueError(
                f"{self.name}: String length {len(value)} exceeds maximum {self.max_length}"
            )

        if len(value) < self.min_length:
            raise ValueError(
                f"{self.name}: String length {len(value)} below minimum {self.min_length}"
            )

        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return f"VARCHAR({self.max_length})"


class TextField(Field):
    """Text field for long strings."""

    def to_python(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return "TEXT"


class IntegerField(Field):
    """Integer field."""

    def __init__(
        self,
        auto_increment: bool = False,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.auto_increment = auto_increment
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{self.name}: Value must be an integer")

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name}: Value {value} below minimum {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name}: Value {value} above maximum {self.max_value}")

        return value

    def to_python(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "SERIAL" if self.auto_increment else "INTEGER"
        elif dialect == "mysql":
            return "INT AUTO_INCREMENT" if self.auto_increment else "INT"
        else:  # sqlite
            return "INTEGER"


class BigIntegerField(IntegerField):
    """64-bit integer field."""

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "BIGSERIAL" if self.auto_increment else "BIGINT"
        elif dialect == "mysql":
            return "BIGINT AUTO_INCREMENT" if self.auto_increment else "BIGINT"
        else:  # sqlite
            return "INTEGER"


class SmallIntegerField(IntegerField):
    """16-bit integer field."""

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "SMALLSERIAL" if self.auto_increment else "SMALLINT"
        elif dialect == "mysql":
            return "SMALLINT AUTO_INCREMENT" if self.auto_increment else "SMALLINT"
        else:  # sqlite
            return "INTEGER"


class FloatField(Field):
    """Floating point field."""

    def to_python(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        return float(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "mysql":
            return "FLOAT"
        return "REAL"


class DecimalField(Field):
    """Decimal field for precise numeric values."""

    def __init__(self, max_digits: int = 10, decimal_places: int = 2, **kwargs):
        super().__init__(**kwargs)
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def to_python(self, value: Any) -> Optional[Decimal]:
        if value is None:
            return None
        return Decimal(str(value))

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return f"NUMERIC({self.max_digits}, {self.decimal_places})"


class BooleanField(Field):
    """Boolean field."""

    def __init__(self, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = False
        super().__init__(**kwargs)

    def to_python(self, value: Any) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "mysql":
            return "BOOLEAN"
        elif dialect == "sqlite":
            return "INTEGER"  # SQLite doesn't have native boolean
        return "BOOLEAN"


class DateTimeField(Field):
    """DateTime field."""

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now  # Update on every save
        self.auto_now_add = auto_now_add  # Set on first save only

        if auto_now or auto_now_add:
            self.editable = False

    def to_python(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Try parsing common formats
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
        raise ValueError(f"{self.name}: Invalid datetime value")

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "mysql":
            return "DATETIME"
        elif dialect == "sqlite":
            return "TEXT"  # SQLite stores as text
        return "TIMESTAMP"


class DateField(Field):
    """Date field."""

    def to_python(self, value: Any) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise ValueError(f"{self.name}: Invalid date value")

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "sqlite":
            return "TEXT"
        return "DATE"


class TimeField(Field):
    """Time field."""

    def to_python(self, value: Any) -> Optional[dt_time]:
        if value is None:
            return None
        if isinstance(value, dt_time):
            return value
        if isinstance(value, str):
            return dt_time.fromisoformat(value)
        raise ValueError(f"{self.name}: Invalid time value")

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "sqlite":
            return "TEXT"
        return "TIME"


class JSONField(Field):
    """JSON field for storing structured data."""

    def to_python(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            return json.loads(value)
        return value

    def to_db(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        return json.dumps(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "JSONB"
        elif dialect == "mysql":
            return "JSON"
        return "TEXT"


class UUIDField(Field):
    """UUID field."""

    def __init__(self, auto_generate: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_generate = auto_generate
        if auto_generate and not kwargs.get("default_factory"):
            self.default_factory = uuid.uuid4

    def to_python(self, value: Any) -> Optional[uuid.UUID]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

    def to_db(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "UUID"
        return "VARCHAR(36)"


class EmailField(CharField):
    """Email field with validation."""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", 254)
        super().__init__(**kwargs)

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        # Simple email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            raise ValueError(f"{self.name}: Invalid email address")

        return value


class URLField(CharField):
    """URL field with validation."""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", 2048)
        super().__init__(**kwargs)

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        # Simple URL validation
        url_pattern = r"^https?://[^\s]+"
        if not re.match(url_pattern, value):
            raise ValueError(f"{self.name}: Invalid URL")

        return value


class BinaryField(Field):
    """Binary data field."""

    def to_python(self, value: Any) -> Optional[bytes]:
        if value is None:
            return None
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode("utf-8")
        return bytes(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "BYTEA"
        elif dialect == "mysql":
            return "BLOB"
        return "BLOB"


class ArrayField(Field):
    """Array/List field (PostgreSQL specific)."""

    def __init__(self, base_field: Field, size: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.base_field = base_field
        self.size = size

    def to_python(self, value: Any) -> Optional[List]:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return json.loads(value)
        return list(value)

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        return value  # PostgreSQL handles arrays natively

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            base_type = self.base_field.get_db_type(dialect)
            size_spec = f"[{self.size}]" if self.size else "[]"
            return f"{base_type}{size_spec}"
        # For non-PostgreSQL, store as JSON
        return "TEXT"


class EnumField(Field):
    """Enum field."""

    def __init__(self, enum_class: Type[Enum], **kwargs):
        super().__init__(**kwargs)
        self.enum_class = enum_class
        if "choices" not in kwargs:
            self.choices = [(e.value, e.name) for e in enum_class]

    def to_python(self, value: Any) -> Optional[Enum]:
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value
        return self.enum_class(value)

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, Enum):
            return value.value
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return "VARCHAR(50)"


__all__ = [
    "Field",
    "CharField",
    "TextField",
    "IntegerField",
    "BigIntegerField",
    "SmallIntegerField",
    "FloatField",
    "DecimalField",
    "BooleanField",
    "DateTimeField",
    "DateField",
    "TimeField",
    "JSONField",
    "UUIDField",
    "EmailField",
    "URLField",
    "BinaryField",
    "ArrayField",
    "EnumField",
]
