"""Defines base SQLAlchemy models and utilities for ORM usage.

This module provides automatic table naming, dictionary conversion, and lifecycle hooks for SQLModel-based ORM models.
It also includes mixins for audit fields and soft deletion support.

Classes:
    IDbModel: Interface for lifecycle hooks and field-level permissions.
    DbModel: Base SQLModel with automatic tablename and dict conversion.
    AuditableDbModel: Mixin for audit fields (created/updated info).
    SoftDeletableDbModel: Mixin for soft delete support.
    BaseModel: Combines audit and soft delete mixins with DbModel.
"""
import re
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, ClassVar

import inflect
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import String, Text, event, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import expression
from sqlmodel import Field, SQLModel

from fastwings.error_code import ServerErrorCode

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.sql.schema import Column
    from typing_extensions import Self


# --- Core Model Interface and Lifecycle Events ---
class IDbModel:
    """Interface for lifecycle hooks and field-level permissions in database models.

    These methods are automatically triggered by SQLAlchemy event listeners to manage model lifecycle events and
    field-level access control.

    Attributes:
        view_only_fields (Iterable[str]): Fields that are view-only and should not be updated.
        not_update_fields (Iterable[str]): Fields that should not be updated.
    """
    # Using ClassVar to indicate these are class-level configurations
    view_only_fields: ClassVar[Iterable[str]] = ()
    not_update_fields: ClassVar[Iterable[str]] = ()

    def before_create(self) -> None:
        """Hook called before a new model instance is inserted into the database.

        This method can be overridden to implement custom logic before creation.
        """
        pass

    def before_update(self) -> None:
        """Hook called before an existing model instance is updated in the database.

        This method can be overridden to implement custom logic before update.
        """
        pass

    def before_save(self) -> None:
        """Hook called before both create and update operations.

        This method can be overridden to implement logic common to both creation and update.
        """
        pass

    def before_delete(self) -> None:
        """Hook called before a model instance is deleted from the database.

        This method can be overridden to implement custom logic before deletion.
        """
        pass


@event.listens_for(IDbModel, 'before_insert', propagate=True)
def receive_before_insert(mapper: Mapper[Any], connection: "Connection", target: IDbModel) -> None:
    """SQLAlchemy event listener for before_insert.

    Args:
        mapper (Mapper): SQLAlchemy mapper.
        connection: Database connection.
        target (IDbModel): The model instance being inserted.
    """
    target.before_create()
    target.before_save()


@event.listens_for(IDbModel, 'before_update', propagate=True)
def receive_before_update(mapper: Mapper[Any], connection: "Connection", target: IDbModel) -> None:
    """SQLAlchemy event listener for before_update.

    Args:
        mapper (Mapper): SQLAlchemy mapper.
        connection: Database connection.
        target (IDbModel): The model instance being updated.
    """
    target.before_update()
    target.before_save()


@event.listens_for(IDbModel, 'before_delete', propagate=True)
def receive_before_delete(mapper: Mapper[Any], connection: "Connection", target: IDbModel) -> None:
    """SQLAlchemy event listener for before_delete.

    Args:
        mapper (Mapper): SQLAlchemy mapper.
        connection: Database connection.
        target (IDbModel): The model instance being deleted.
    """
    target.before_delete()


def generate_unique_uuid() -> uuid.UUID:
    """Generates a unique UUID value.

    Returns:
        uuid.UUID: A new unique UUID.
    """
    return uuid.uuid4()


def _validate_column_data(column: "Column[Any]", value: Any) -> None:
    """Validates data for a specific column based on its type and constraints.

    Args:
        column: The SQLAlchemy column object.
        value (Any): The value to validate for the column.

    Raises:
        ValueError: If a required field is missing or maximum length is exceeded.
        TypeError: If the value type doesn't match the column type.
    """
    if value is None:
        if not column.nullable and not column.primary_key and not column.server_default and not column.default:
            raise ServerErrorCode.DATABASE_ERROR.value(ValueError(f"'{column.name}' is a required field."))
        return

    # Validate string types
    if isinstance(column.type, (String, Text)):
        if not isinstance(value, str):
            raise ServerErrorCode.DATABASE_ERROR.value(
                TypeError(f"'{column.name}' expects a string value, got {type(value).__name__}.")
            )

        # Check max length for String columns
        if (isinstance(column.type, String)
            and hasattr(column.type, 'length')
            and column.type.length
            and len(str(value)) > column.type.length):
            raise ServerErrorCode.DATABASE_ERROR.value(
                ValueError(f"Maximum length reached for '{column.name}'. "
                           f"Must be {column.type.length} characters or less.")
            )


p = inflect.engine()


class DbModel(SQLModel, IDbModel):
    """Base SQLModel with automatic tablename and dictionary conversion.

    Provides automatic plural snake_case table naming and update/from_data utilities.

    Attributes:
        id (uuid.UUID): Primary key UUID for the model.
        view_only_fields (Iterable[str]): Fields that are view-only and should not be updated.
        not_update_fields (Iterable[str]): Fields that should not be updated.
    """
    id: uuid.UUID = Field(default_factory=generate_unique_uuid, primary_key=True, index=True, nullable=False)

    # Define base view-only and non-updatable fields
    view_only_fields: ClassVar[Iterable[str]] = ('id',)
    not_update_fields: ClassVar[Iterable[str]] = ('id',)

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        """Generates table name from class name in plural snake_case.

        Returns:
            str: Table name for the model.
        """
        words = re.findall("[A-Z][^A-Z]*", cls.__name__)
        if len(words) == 1:
            return p.plural(words[0].lower())
        elif len(words) > 1:
            return "_".join(words[:-1]).lower() + "_" + p.plural(words[-1].lower())
        return cls.__name__.lower()

    def __repr__(self) -> str:
        """Returns a string representation of the model instance.

        Returns:
            str: String representation in the format <ClassName(id=...)>.
        """
        return f"<{self.__class__.__name__}(id={self.id})>"

    def update(self, data: dict[str, Any] | PydanticBaseModel) -> "Self":
        """Updates the model instance with data from a dictionary or Pydantic model.

        Respects `view_only_fields` and `not_update_fields` to prevent updates to protected fields.

        Args:
            data (dict[str, Any] | PydanticBaseModel): Data to update the model with.

        Returns:
            Self: The updated model instance.
        """
        if isinstance(data, PydanticBaseModel):
            # Use Pydantic's optimized method to get only set fields
            data = data.model_dump(exclude_unset=True)

        # Combine fields that should never be written to during an update
        protected_fields = set(self.view_only_fields) | set(self.not_update_fields)

        for key, value in data.items():
            # Check if the field is part of the model and not protected
            if hasattr(self, key) and key not in protected_fields:
                table = getattr(self, "__table__", None)
                if table is not None:
                    column = table.columns.get(key)
                    if column is not None:
                        _validate_column_data(column, value)
                setattr(self, key, value)
        return self

    @classmethod
    def from_data(cls: type["Self"], data: dict[str, Any] | PydanticBaseModel) -> "Self":
        """Creates a new model instance from a dictionary or Pydantic model.

        Respects `view_only_fields` to prevent setting protected fields.

        Args:
            data (dict[str, Any] | PydanticBaseModel): Data to create the model from.

        Returns:
            Self: The newly created model instance.

        Raises:
            ValueError: If required fields are missing.
        """
        if isinstance(data, PydanticBaseModel):
            data = data.model_dump()

        # Filter out any data for fields that are view-only
        allowed_data = {
            key: value for key, value in data.items() if key not in cls.view_only_fields
        }

        # Validate data before creating the instance
        table = getattr(cls, "__table__", None)
        if table is not None:
            for key, value in allowed_data.items():
                column = table.columns.get(key)
                if column is not None:
                    _validate_column_data(column, value)

        return cls(**allowed_data)

    def to_dict(
        self, ignore_fields: tuple[str, ...] = ("is_deleted", "password", "updated_at", "_sa_instance_state"),
        _seen: set[int] | None = None,  # for recursion guard
    ) -> dict[str, Any]:
        """Recursively converts DB object instance to python dictionary.

        Args:
            ignore_fields (Tuple[str]): Fields to exclude from the result.
            _seen (set | None, optional): Set of object IDs already visited to prevent infinite recursion.

        Returns:
            dict[str, Any]: Dictionary representation of the model instance.
        """
        if _seen is None:
            _seen = set()

        # Use object ID to prevent infinite recursion
        obj_id = id(self)
        if obj_id in _seen:
            return {}

        _seen = _seen | {obj_id}

        # Start from __dict__ but exclude ignored fields
        result: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if key in ignore_fields or key.startswith("_"):
                continue

            if isinstance(value, (InstrumentedList, list)):
                result[key] = [
                    item.to_dict(ignore_fields, _seen) if isinstance(item, DbModel) else item
                    for item in value
                ]
            elif isinstance(value, DbModel):
                result[key] = value.to_dict(ignore_fields, _seen)
            else:
                result[key] = value

        return result


@event.listens_for(Mapper, 'mapper_configured')
def validate_class_columns(mapper: Mapper[Any], cls: type[Any]) -> None:
    """Validates that any view-only field that isn't nullable has a default value.

    Prevents runtime errors on creation by ensuring view-only fields are properly configured.

    Args:
        mapper (Mapper): SQLAlchemy mapper.
        cls: The model class being configured.

    Raises:
        TypeError: If a view-only field is not nullable and lacks a default value.
    """
    if not issubclass(cls, IDbModel):
        return

    # Get the table object safely. If it doesn't exist, table will be None.
    table = getattr(cls, "__table__", None)

    # Set the iterable to table.columns only if table is valid, otherwise use an empty list.
    columns_to_check = table.columns if table is not None and hasattr(table, "columns") else []

    for c in columns_to_check:
        if c.primary_key:
            continue
        if c.name in cls.view_only_fields and not c.nullable and not c.server_default and not c.default:
            raise TypeError(
                f"Field '{c.name}' in model '{cls.__name__}' is 'view_only' and not nullable, "
                "but has no default or server_default value. This will cause errors on insert."
            )


class AuditableDbModel(IDbModel):
    """Mixin for audit fields tracking creation and update info.

    Adds created_at, created_by, updated_at, and updated_by fields to the model.

    Attributes:
        created_at (datetime): Timestamp when the record was created.
        created_by (int | None): ID of the creator. Defaults to `None`.
        updated_at (datetime | None): Timestamp of last update. Defaults to `None`.
        updated_by (int | None): ID of the last updater. Defaults to `None`.
        view_only_fields (Iterable[str]): Audit fields that are view-only.
        ignore_fields (Iterable[str]): Audit fields to ignore in certain operations.
    """
    created_at: datetime = Field(
        description="Created time",
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    created_by: int | None = Field(default=None, description="The creator id", nullable=True)
    updated_at: datetime | None = Field(default=None, description="Last updated time", nullable=True)
    updated_by: int | None = Field(default=None, description="The latest updator id", nullable=True)

    def before_create(self) -> None:
        """Hook called before a new model instance is inserted to set created_by.

        Sets the created_by field from session info if available.
        """
        super().before_create()

        # Get session from the object
        session = Session.object_session(self)
        if session and "user_id" in session.info:
            user_id = session.info["user_id"]
            # Validate type before assignment
            if not isinstance(user_id, (int, type(None))):
                raise TypeError(f"user_id must be int or None, got {type(user_id).__name__}")
            self.created_by = user_id

    def before_update(self) -> None:
        """Hook called before an existing model instance is updated to set updated_by and updated_at.

        Sets the updated_by and updated_at fields from session info if available.
        """
        super().before_update()

        self.updated_at = datetime.now(timezone.utc)

        # Get session from the object
        session = Session.object_session(self)
        if session and "user_id" in session.info:
            user_id = session.info["user_id"]
            # Validate type before assignment
            if not isinstance(user_id, (int, type(None))):
                raise TypeError(f"user_id must be int or None, got {type(user_id).__name__}")
            self.updated_by = user_id

    view_only_fields: ClassVar[Iterable[str]] = ('created_at', 'created_by', 'updated_at', 'updated_by')
    ignore_fields: ClassVar[Iterable[str]] = ('created_at', 'created_by', 'updated_at', 'updated_by')


class SoftDeletableDbModel(IDbModel):
    """Mixin for soft delete support in database models.

    Adds an is_deleted field and a soft_delete method to mark records as deleted without removing them from the
    database.

    Attributes:
        is_deleted (bool): Indicates if the record is soft deleted. Defaults to `False`.
        view_only_fields (Iterable[str]): Soft delete fields that are view-only.
        ignore_fields (Iterable[str]): Soft delete fields to ignore in certain operations.
    """

    is_deleted: bool = Field(
        default=False, sa_column_kwargs={"server_default": expression.false()}
    )

    view_only_fields: ClassVar[Iterable[str]] = ('is_deleted',)
    ignore_fields: ClassVar[Iterable[str]] = ('is_deleted',)

    def soft_delete(self) -> None:
        """Marks the record as deleted by setting is_deleted to True."""
        self.is_deleted = True


class BaseModel(AuditableDbModel, SoftDeletableDbModel, DbModel):
    """Base database model with audit fields and soft delete support.

    Combines audit and soft delete mixins with the core DbModel for comprehensive ORM functionality.
    This model includes:
    - Automatic UUID primary key generation
    - Automatic table naming (plural snake_case)
    - Audit fields (created_at, created_by, updated_at, updated_by)
    - Soft delete support (is_deleted flag)
    - Dictionary conversion utilities (update, from_data)
    - Lifecycle hooks (before_create, before_update, before_save, before_delete)
    """

    # Properly merge view_only_fields from all parent classes
    view_only_fields: ClassVar[Iterable[str]] = (
        *DbModel.view_only_fields,
        *AuditableDbModel.view_only_fields,
        *SoftDeletableDbModel.view_only_fields,
    )

    # Properly merge not_update_fields from all parent classes
    not_update_fields: ClassVar[Iterable[str]] = (
        *DbModel.not_update_fields,
    )

    # Properly merge ignore_fields from all parent classes
    ignore_fields: ClassVar[Iterable[str]] = (
        *AuditableDbModel.ignore_fields,
        *SoftDeletableDbModel.ignore_fields,
    )
