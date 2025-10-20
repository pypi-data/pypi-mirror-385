"""
Comprehensive JSON serialization with intelligent type handling and automatic conversion.

This module provides enterprise-grade JSON serialization capabilities including automatic type
conversion for complex Python objects, intelligent deserialization with type inference,
enum handling, datetime conversion, and integration with configurable type discovery.

Key Features:
    - JsonEncoder: Custom JSON encoder for complex Python types
    - JsonSerializer: Full-featured serialization service with type inference
    - Automatic type conversion for enums, datetime, decimals, and custom objects
    - Type registry integration for intelligent enum discovery
    - Dataclass and generic type support (List[T], Dict[K,V], Optional[T])
    - Comprehensive error handling and fallback strategies
    - Application builder integration for easy setup

Examples:
    ```python
    # Quick setup
    JsonSerializer.configure(app_builder, type_modules=["domain.models", "shared.enums"])

    # Manual registration
    services.add_singleton(JsonSerializer)
    serializer = provider.get_service(JsonSerializer)

    # Serialize complex objects
    order = Order(items=[...], status=OrderStatus.PENDING, total=Decimal("99.99"))
    json_text = serializer.serialize_to_text(order)

    # Type-safe deserialization
    restored_order = serializer.deserialize_from_text(json_text, Order)
    ```

See Also:
    - JSON Serialization Guide: https://bvandewe.github.io/pyneuro/features/serialization/
    - Type Discovery: https://bvandewe.github.io/pyneuro/features/configurable-type-discovery/
    - Getting Started: https://bvandewe.github.io/pyneuro/getting-started/
"""

import json
import typing
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union, get_args, get_origin

from neuroglia.serialization.abstractions import Serializer, TextSerializer

if TYPE_CHECKING:
    from neuroglia.hosting.abstractions import ApplicationBuilderBase


class JsonEncoder(json.JSONEncoder):
    """
    Enhanced JSON encoder that provides automatic conversion for complex Python types.

    This encoder extends the standard JSON encoder to handle common Python types that
    are not natively JSON serializable, including enums, datetime objects, decimals,
    and custom objects with intelligent fallback mechanisms.

    Supported Types:
        - Enums: Converted to their name value for human readability
        - DateTime: Converted to ISO format strings
        - Custom Objects: Serialized using their __dict__ with private field filtering
        - Unsupported Types: Gracefully converted to string representation

    Examples:
        ```python
        from enum import Enum
        from datetime import datetime
        from decimal import Decimal

        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        class Order:
            def __init__(self, id: str, status: Status, total: Decimal):
                self.id = id
                self.status = status
                self.total = total
                self.created_at = datetime.now()
                self._internal_field = "hidden"

        # Automatic encoding
        order = Order("123", Status.ACTIVE, Decimal('99.99'))
        json_str = json.dumps(order, cls=JsonEncoder)

        # Result:
        # {
        #   "id": "123",
        #   "status": "ACTIVE",
        #   "total": "99.99",
        #   "created_at": "2025-09-27T10:30:00.123456"
        #   // Note: _internal_field is filtered out
        # }
        ```

    See Also:
        - JSON Serialization: https://bvandewe.github.io/pyneuro/features/serialization/
        - Type Handling Guide: https://bvandewe.github.io/pyneuro/patterns/
    """

    def default(self, obj):
        if issubclass(type(obj), Enum):
            return obj.name
        elif issubclass(type(obj), datetime):
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            filtered_dict = {key: value for key, value in obj.__dict__.items() if not key.startswith("_") and value is not None}
            return filtered_dict
        try:
            return super().default(obj)
        except Exception:
            return str(obj)


class JsonSerializer(TextSerializer):
    """
    Comprehensive JSON serialization service with intelligent type handling and conversion.

    This service provides advanced JSON serialization capabilities including automatic type
    conversion, intelligent deserialization with type inference, enum handling, datetime
    conversion, and integration with the framework's type registry for robust object reconstruction.

    Key Features:
        - Automatic type conversion for complex Python objects
        - Intelligent type inference during deserialization
        - Enum handling with multiple matching strategies
        - DateTime conversion with ISO format support
        - Dataclass and custom object support
        - Generic type handling (List[T], Dict[K,V], Optional[T])
        - Type registry integration for enum discovery
        - Comprehensive error handling and fallback strategies

    Examples:
        ```python
        # Service registration
        services.add_singleton(JsonSerializer)
        serializer = provider.get_service(JsonSerializer)

        # Basic serialization
        user = User(name="John", email="john@example.com", created_at=datetime.now())
        json_text = serializer.serialize_to_text(user)

        # Type-safe deserialization
        user_data = '{"name": "Alice", "email": "alice@example.com"}'
        user = serializer.deserialize_from_text(user_data, User)

        # Complex object graphs
        @dataclass
        class Order:
            id: str
            items: List[OrderItem]
            status: OrderStatus
            total: Decimal
            created_at: datetime

        order = Order(
            id="ORD-123",
            items=[OrderItem("prod1", 2), OrderItem("prod2", 1)],
            status=OrderStatus.PENDING,
            total=Decimal("99.99"),
            created_at=datetime.now()
        )

        # Serialize complex object
        json_data = serializer.serialize_to_text(order)

        # Deserialize with full type reconstruction
        restored_order = serializer.deserialize_from_text(json_data, Order)
        assert isinstance(restored_order.status, OrderStatus)
        assert isinstance(restored_order.items[0], OrderItem)

        # API response handling
        class UsersController(ControllerBase):
            @get("/users/{user_id}")
            async def get_user(self, user_id: str) -> str:
                user = await self.user_service.get_by_id(user_id)
                return self.json_serializer.serialize_to_text(user)
        ```

    Type Inference:
        The serializer includes intelligent type inference for fields without explicit
        type annotations, using naming patterns and value analysis:

        ```python
        # Automatic decimal detection for money fields
        data = '{"price": "99.99", "total_amount": "149.50"}'
        obj = serializer.deserialize_from_text(data, Product)
        # price and total_amount automatically converted to Decimal

        # Automatic datetime detection
        data = '{"created_at": "2025-09-27T10:30:00"}'
        obj = serializer.deserialize_from_text(data, Entity)
        # created_at automatically converted to datetime

        # Enum matching by name or value
        data = '{"status": "ACTIVE"}'
        obj = serializer.deserialize_from_text(data, User)
        # status automatically matched to UserStatus.ACTIVE enum
        ```

    See Also:
        - JSON Serialization Guide: https://bvandewe.github.io/pyneuro/features/serialization/
        - Type Registry Integration: https://bvandewe.github.io/pyneuro/features/configurable-type-discovery/
        - API Response Handling: https://bvandewe.github.io/pyneuro/features/mvc-controllers/
    """

    def _is_aggregate_root(self, obj: Any) -> bool:
        """
        Check if an object is an AggregateRoot instance.

        An AggregateRoot has three key characteristics:
        - state property (contains the aggregate's data)
        - register_event method (for domain events)
        - domain_events property (pending events)

        Args:
            obj: The object to check

        Returns:
            True if the object is an AggregateRoot instance
        """
        return hasattr(obj, "state") and hasattr(obj, "register_event") and hasattr(obj, "domain_events")

    def _is_aggregate_root_type(self, cls: type) -> bool:
        """
        Check if a type is an AggregateRoot class.

        Examines the class's generic bases to determine if it inherits from AggregateRoot.

        Args:
            cls: The class to check

        Returns:
            True if the class is an AggregateRoot type
        """
        if not hasattr(cls, "__orig_bases__"):
            return False

        for base in cls.__orig_bases__:
            if hasattr(base, "__origin__"):
                base_name = getattr(base.__origin__, "__name__", "")
                if base_name == "AggregateRoot":
                    return True

        return False

    def _get_state_type(self, aggregate_type: type) -> Optional[type]:
        """
        Extract the state type (TState) from an AggregateRoot[TState, TKey] type.

        For example, if the aggregate is Order(AggregateRoot[OrderState, str]),
        this returns OrderState.

        Args:
            aggregate_type: The AggregateRoot class

        Returns:
            The state class (TState), or None if not found
        """
        if not hasattr(aggregate_type, "__orig_bases__"):
            return None

        for base in aggregate_type.__orig_bases__:
            if hasattr(base, "__args__") and len(get_args(base)) >= 1:
                # Return TState (first generic argument)
                return get_args(base)[0]

        return None

    def serialize(self, value: Any) -> bytearray:
        text = self.serialize_to_text(value)
        if text is None:
            return None
        return text.encode()

    def serialize_to_text(self, value: Any) -> str:
        """
        Serialize a value to JSON text with automatic AggregateRoot state extraction.

        For AggregateRoot instances, automatically extracts and serializes the state
        instead of the aggregate wrapper, resulting in clean state-only storage.

        Args:
            value: The object to serialize (can be Entity, AggregateRoot, or any object)

        Returns:
            JSON string representation

        Examples:
            ```python
            # Entity serialization (unchanged)
            customer = Customer(id="c1", name="John")
            json_text = serializer.serialize_to_text(customer)
            # Result: {"id": "c1", "name": "John"}

            # AggregateRoot serialization (state extracted automatically)
            order = Order(OrderState(id="o1", status=OrderStatus.PENDING))
            json_text = serializer.serialize_to_text(order)
            # Result: {"id": "o1", "status": "PENDING"}  <- Just the state!
            ```
        """
        # If it's an AggregateRoot, serialize the state (not the wrapper)
        if self._is_aggregate_root(value):
            return self.serialize_to_text(value.state)

        # Otherwise serialize directly
        return json.dumps(value, cls=JsonEncoder)

    def deserialize(self, input: bytearray, expected_type: Any | None) -> Any:
        return self.deserialize_from_text(input.decode(), expected_type)

    def deserialize_from_text(self, input: str, expected_type: Optional[type] = None) -> Any:
        """
        Deserialize JSON text with automatic AggregateRoot reconstruction.

        For AggregateRoot types, automatically deserializes the state and reconstructs
        the aggregate wrapper with proper initialization.

        Args:
            input: JSON string to deserialize
            expected_type: Expected type for deserialization

        Returns:
            Deserialized object (Entity, AggregateRoot, or plain object)

        Examples:
            ```python
            # Entity deserialization (unchanged)
            json_text = '{"id": "c1", "name": "John"}'
            customer = serializer.deserialize_from_text(json_text, Customer)

            # AggregateRoot deserialization (automatic reconstruction)
            json_text = '{"id": "o1", "status": "PENDING"}'
            order = serializer.deserialize_from_text(json_text, Order)
            # Result: Order instance with state and empty event list
            assert order.state.id == "o1"
            assert order.domain_events == []
            ```
        """
        value = json.loads(input)

        # If no expected type, return the raw parsed value
        if expected_type is None:
            return value

        # Check for backward compatibility with old AggregateSerializer format
        # Old format: {"aggregate_type": "Order", "state": {...}}
        # New format: {"id": "...", ...}  (direct state)
        if isinstance(value, dict) and "aggregate_type" in value and "state" in value:
            # Handle old format for backward compatibility during transition
            value = value["state"]
            input = json.dumps(value)

        # Check if expected_type is an AggregateRoot class
        if self._is_aggregate_root_type(expected_type):
            return self._deserialize_aggregate(value, expected_type)

        # Handle list deserialization at top level
        if isinstance(value, list) and hasattr(expected_type, "__args__"):
            return self._deserialize_nested(value, expected_type)

        # Handle dict types
        if not isinstance(value, dict):
            return value
        elif expected_type == dict:
            return dict(value)

        return self._deserialize_object(value, expected_type)

    def _deserialize_aggregate(self, data: dict, aggregate_type: type) -> Any:
        """
        Deserialize an aggregate from clean state data.

        This reconstructs an AggregateRoot instance from its state data:
        1. Get the state type from AggregateRoot[TState, TKey]
        2. Deserialize the state data to TState instance
        3. Create the aggregate wrapper with the state
        4. Initialize empty pending events

        Args:
            data: Dictionary of state fields (clean, no metadata wrapper)
            aggregate_type: The AggregateRoot class to instantiate

        Returns:
            Reconstructed aggregate instance with state and empty events
        """
        # Get the state type from AggregateRoot[TState, TKey]
        state_type = self._get_state_type(aggregate_type)

        if state_type is None:
            # Fallback: create aggregate with empty state
            aggregate = object.__new__(aggregate_type)
            aggregate.state = object.__new__(object)
            aggregate._pending_events = []
            return aggregate

        # Deserialize the state data to a state instance
        state_json = json.dumps(data)
        state_instance = self.deserialize_from_text(state_json, state_type)

        # Create the aggregate instance without calling __init__
        aggregate = object.__new__(aggregate_type)
        aggregate.state = state_instance

        # Initialize pending events as empty list
        # (Events are ephemeral and should be dispatched immediately, not persisted)
        aggregate._pending_events = []

        return aggregate

    def _deserialize_object(self, data: dict, expected_type: type) -> Any:
        """Deserialize a dictionary into an object using type annotations."""
        fields = {}

        # Collect all type annotations from the class hierarchy
        type_hints = {}
        for base_type in reversed(expected_type.__mro__):
            if hasattr(base_type, "__annotations__"):
                type_hints.update(base_type.__annotations__)

        # Deserialize each field using its type annotation
        for key, value in data.items():
            if key in type_hints:
                field_type = type_hints[key]
                fields[key] = self._deserialize_nested(value, field_type)
            else:
                # For fields without type annotations, try intelligent type inference
                fields[key] = self._infer_and_deserialize(key, value, expected_type)

        # Create the object instance
        instance = object.__new__(expected_type)
        instance.__dict__ = fields
        return instance

    def _infer_and_deserialize(self, field_name: str, value: Any, target_type: type) -> Any:
        """
        Intelligently infer the correct type for a field and deserialize accordingly.
        This method uses various heuristics to guess the appropriate type.
        """
        # If the value is already a simple type, return as-is
        if isinstance(value, (int, float, bool, type(None))):
            return value

        if isinstance(value, str):
            # Try to detect datetime strings
            if self._is_datetime_string(value):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))

            # Try to detect decimal/money fields by name patterns
            if any(pattern in field_name.lower() for pattern in ["price", "cost", "amount", "total", "fee"]):
                try:
                    from decimal import Decimal

                    return Decimal(value)
                except (ValueError, TypeError):
                    pass

            # Try to find matching enum types in the target class
            enum_value = self._try_deserialize_enum(value, target_type)
            if enum_value is not None:
                return enum_value

        # For lists and dicts, recursively process
        if isinstance(value, list):
            return [self._infer_and_deserialize(f"{field_name}_item", item, target_type) for item in value]

        if isinstance(value, dict):
            return {k: self._infer_and_deserialize(f"{field_name}_{k}", v, target_type) for k, v in value.items()}

        return value

    def _is_datetime_string(self, value: str) -> bool:
        """Check if a string looks like an ISO datetime."""
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False

    def _try_deserialize_enum(self, value: str, target_type: type) -> Any:
        """
        Try to deserialize a string value as an enum using the configurable TypeRegistry.
        """
        if not isinstance(value, str):
            return None

        try:
            from neuroglia.core.type_registry import get_type_registry

            type_registry = get_type_registry()
            return type_registry.find_enum_for_value(value, target_type)

        except ImportError:
            # Fallback to basic enum detection if TypeRegistry not available
            return self._basic_enum_detection(value, target_type)

    def _basic_enum_detection(self, value: str, target_type: type) -> Any:
        """
        Fallback enum detection that only checks the target type's module.
        Used when TypeRegistry is not available.
        """
        try:
            import sys
            from enum import Enum

            target_module = getattr(target_type, "__module__", None)
            if not target_module:
                return None

            module = sys.modules.get(target_module)
            if module:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Enum) and attr != Enum:
                        for enum_member in attr:
                            if enum_member.value == value or enum_member.value == value.lower() or enum_member.name == value or enum_member.name == value.upper():
                                return enum_member
        except Exception:
            pass

        return None

    def _deserialize_nested(self, value: Any, expected_type: type) -> Any:
        """Recursively deserializes a nested object. Support native types (str, int, float, bool) as well as Generic Types that also include subtypes (typing.Dict, typing.List)."""

        # Handle None for Optional types
        if value is None:
            return None

        origin_type = get_origin(expected_type)
        if origin_type is not None:
            # This is a generic type (e.g., Optional[SomeType], List[SomeType])
            type_args = get_args(expected_type)
            if origin_type is Union and type(None) in type_args:
                # This is an Optional type
                non_optional_type = next(t for t in type_args if t is not type(None))
                return self._deserialize_nested(value, non_optional_type)

            elif origin_type in (list, typing.List):
                # Handle List deserialization
                if len(type_args) > 0:
                    # List with type hints (e.g. typing.List[str])
                    item_type = type_args[0]
                else:
                    item_type = type(value[0]) if value else object

                # Deserialize each item in the list
                return [self._deserialize_nested(v, item_type) for v in value]

            elif origin_type is dict:
                # Handle Dict deserialization
                if len(type_args) > 0:
                    # Dictionary with type hints (e.g. typing.Dict[str, int])
                    key_type, val_type = type_args
                    return {self._deserialize_nested(k, key_type): self._deserialize_nested(v, val_type) for k, v in value.items()}
                else:
                    # Dictionary without type hints, use the actual type of each value
                    return {k: self._deserialize_nested(v, type(v)) for k, v in value.items()}

        if isinstance(value, dict):
            # Handle Dataclass deserialization
            if is_dataclass(expected_type):
                field_dict = {}
                for field in fields(expected_type):
                    if field.name in value:
                        field_value = self._deserialize_nested(value[field.name], field.type)
                        field_dict[field.name] = field_value
                # Create instance and set fields (works for frozen and non-frozen dataclasses)
                instance = object.__new__(expected_type)
                for key, val in field_dict.items():
                    object.__setattr__(instance, key, val)
                return instance

            # If the expected type is a plain dict, we need to deserialize each value in the dict.
            if hasattr(expected_type, "__args__") and expected_type.__args__:
                # Dictionary with type hints (e.g. typing.Dict[str, int])
                key_type, val_type = expected_type.__args__
                return {self._deserialize_nested(k, key_type): self._deserialize_nested(v, val_type) for k, v in value.items()}
            else:
                # Dictionary without type hints, use the actual type of each value
                return {k: self._deserialize_nested(v, type(v)) for k, v in value.items()}

        elif isinstance(value, list):
            # List with type hints (e.g. typing.List[str])
            if hasattr(expected_type, "__args__") and expected_type.__args__:
                # Extract the actual type from the generic alias
                item_type = expected_type.__args__[0]
                if hasattr(item_type, "__origin__"):  # Check if it's a generic alias
                    if len(item_type.__args__) == 1:
                        item_type = item_type.__args__[0]  # Get the actual type
                    else:
                        item_type = item_type.__origin__

            else:
                item_type = type(value[0]) if value else object

            # Deserialize each item in the list, handling dataclasses properly
            values = []
            for v in value:
                # Check if the item should be a dataclass instance
                if isinstance(v, dict) and is_dataclass(item_type):
                    # Deserialize dict to dataclass using proper field deserialization
                    field_dict = {}
                    for field in fields(item_type):
                        if field.name in v:
                            field_value = self._deserialize_nested(v[field.name], field.type)
                            field_dict[field.name] = field_value
                    # Create instance and set fields (works for frozen and non-frozen dataclasses)
                    instance = object.__new__(item_type)
                    for key, val in field_dict.items():
                        object.__setattr__(instance, key, val)
                    values.append(instance)
                else:
                    # For non-dataclass types, use regular deserialization
                    deserialized = self._deserialize_nested(v, item_type)
                    values.append(deserialized)
            return values

        elif isinstance(value, str) and expected_type == datetime:
            return datetime.fromisoformat(value)

        elif expected_type.__name__ == "Decimal" or (hasattr(expected_type, "__module__") and expected_type.__module__ == "decimal"):
            # Handle Decimal deserialization
            from decimal import Decimal

            if isinstance(value, (str, int, float)):
                return Decimal(str(value))
            return value

        elif hasattr(expected_type, "__bases__") and expected_type.__bases__ and issubclass(expected_type, Enum):
            # Handle Enum deserialization - check both value and name
            for enum_member in expected_type:
                if enum_member.value == value or enum_member.name == value:
                    return enum_member
            raise ValueError(f"Invalid enum value for {expected_type.__name__}: {value}")

        else:
            # Return the value as is for types that do not require deserialization
            return value

    @staticmethod
    def configure(builder: "ApplicationBuilderBase", type_modules: Optional[list[str]] = None) -> "ApplicationBuilderBase":
        """
        Configures the specified application builder to use the JsonSerializer.

        Args:
            builder: The application builder to configure
            type_modules: Optional list of module names to scan for types (enums, etc.)
                         For example: ["domain.entities", "domain.models", "shared.enums"]
        """
        builder.services.add_singleton(JsonSerializer)
        builder.services.add_singleton(
            Serializer,
            implementation_factory=lambda provider: provider.get_required_service(JsonSerializer),
        )
        builder.services.add_singleton(
            TextSerializer,
            implementation_factory=lambda provider: provider.get_required_service(JsonSerializer),
        )

        # Register type modules for enum discovery if provided
        if type_modules:
            try:
                from neuroglia.core.type_registry import get_type_registry

                type_registry = get_type_registry()
                type_registry.register_modules(type_modules)
            except ImportError:
                # TypeRegistry not available, silently continue
                pass

        return builder

    @staticmethod
    def register_type_modules(module_names: list[str]) -> None:
        """
        Register modules for type discovery (convenience method).

        Args:
            module_names: List of module names to scan for types
        """
        try:
            from neuroglia.core.type_registry import register_types_modules

            register_types_modules(module_names)
        except ImportError:
            # TypeRegistry not available, silently continue
            pass
