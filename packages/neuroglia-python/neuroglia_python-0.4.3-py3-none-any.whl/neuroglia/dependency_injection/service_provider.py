from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, List, Optional, Type, get_args, get_origin

from neuroglia.core.type_extensions import TypeExtensions


class ServiceLifetime(Enum):
    """
    Defines the abstraction for service instance lifecycle management in the dependency injection container.

    This enumeration controls how and when service instances are created, cached, and disposed of
    throughout the application lifecycle, enabling proper resource management and performance optimization.

    Lifetime Patterns:
        - TRANSIENT: New instance every time (stateless services)
        - SCOPED: One instance per scope/request (request-specific state)
        - SINGLETON: One instance for entire application (shared state)

    Examples:
        ```python
        # Transient: New instance each time (e.g., calculators, validators)
        services.add_transient(EmailValidator)
        services.add_transient(PriceCalculator)

        # Scoped: One per HTTP request (e.g., repositories, unit of work)
        services.add_scoped(UserRepository)
        services.add_scoped(OrderRepository)

        # Singleton: One for entire app (e.g., configuration, cache)
        services.add_singleton(AppConfiguration)
        services.add_singleton(MemoryCache)
        ```

    See Also:
        - Dependency Injection Guide: https://bvandewe.github.io/pyneuro/patterns/dependency-injection/
        - Service Registration: https://bvandewe.github.io/pyneuro/features/
    """

    TRANSIENT = "transient"
    """Transient services are created each time they are requested - ideal for lightweight, stateless services."""

    SCOPED = "scoped"
    """Scoped services are created once per scope (e.g., HTTP request) - perfect for request-specific state."""

    SINGLETON = "singleton"
    """Singleton services are created once and reused for the entire application lifetime - best for shared state."""


# Forward references - these will be defined later in this file


class ServiceProviderBase(ABC):
    """
    Represents the abstraction for dependency injection containers that manage and provide service instances.

    This abstraction defines the core contract for dependency injection systems, enabling loose coupling,
    testability, and modular architecture by managing object creation and dependency resolution throughout
    the application lifecycle.

    Key Responsibilities:
        - Service instance creation and management
        - Dependency graph resolution and injection
        - Lifetime management (singleton, scoped, transient)
        - Service scope creation and disposal
        - Circular dependency detection and handling

    Examples:
        ```python
        # Service resolution
        provider = services.build_provider()

        # Get optional service
        email_service = provider.get_service(EmailService)
        if email_service:
            await email_service.send_email("test@example.com", "Hello")

        # Get required service (throws if not found)
        user_repository = provider.get_required_service(UserRepository)
        users = await user_repository.get_all_async()

        # Get all implementations of an interface
        validators = provider.get_services(IValidator)
        for validator in validators:
            validator.validate(data)

        # Create scoped context
        with provider.create_scope() as scope:
            scoped_service = scope.get_service(RequestScopedService)
            # Scoped services disposed automatically
        ```

    Architecture:
        ```
        Application -> ServiceProvider -> ServiceDescriptor -> Service Instance
                   ^                  ^                     ^
                   |                  |                     |
              Resolution           Configuration        Implementation
        ```

    See Also:
        - Dependency Injection Guide: https://bvandewe.github.io/pyneuro/patterns/dependency-injection/
        - Service Registration: https://bvandewe.github.io/pyneuro/features/configurable-type-discovery/
        - Getting Started: https://bvandewe.github.io/pyneuro/getting-started/
    """

    def get_service(self, type: type) -> Optional[any]:
        """Gets the service with the specified type, if any has been registered"""
        raise NotImplementedError()

    def get_required_service(self, type: type) -> any:
        """Gets the required service with the specified type"""
        raise NotImplementedError()

    def get_services(self, type: type) -> list:
        """Gets all services of the specified type"""
        raise NotImplementedError()

    def create_scope(self) -> "ServiceScopeBase":
        """Creates a new service scope"""
        raise NotImplementedError()


class ServiceScopeBase(ABC):
    """
    Represents the abstraction for service scopes that provide controlled dependency lifetimes and isolation.

    Service scopes create isolated contexts where scoped services are instantiated once per scope
    and automatically disposed when the scope ends. This is crucial for managing per-request state,
    database connections, and other resources that need controlled lifecycles.

    Key Features:
        - Isolated service instances per scope
        - Automatic resource cleanup on disposal
        - Prevents service leakage between requests
        - Enables proper unit of work patterns
        - Supports nested scopes for complex scenarios

    Examples:
        ```python
        # HTTP request scope pattern
        @app.middleware("http")
        async def scoped_middleware(request: Request, call_next):
            with service_provider.create_scope() as scope:
                # Scoped services are unique to this request
                request.state.scope = scope

                # All scoped services share the same instances within this request
                user_repository = scope.get_service(UserRepository)
                order_repository = scope.get_service(OrderRepository)

                response = await call_next(request)
                # Automatic cleanup happens here
                return response

        # Unit of work pattern
        async def process_order(order_data: dict):
            with service_provider.create_scope() as scope:
                unit_of_work = scope.get_service(UnitOfWork)
                order_service = scope.get_service(OrderService)

                try:
                    order = await order_service.create_order(order_data)
                    await unit_of_work.commit_async()
                    return order
                except Exception:
                    await unit_of_work.rollback_async()
                    raise
                # Automatic resource disposal

        # Testing with isolated scopes
        def test_user_service():
            with test_provider.create_scope() as scope:
                user_service = scope.get_service(UserService)
                # Each test gets fresh scoped services
                assert user_service.user_count == 0
        ```

    See Also:
        - Service Scopes Guide: https://bvandewe.github.io/pyneuro/patterns/dependency-injection
        - Request Lifecycle Management: https://bvandewe.github.io/pyneuro/features/
    """

    @abstractmethod
    def get_service_provider(self) -> ServiceProviderBase:
        """Gets the scoped service provider"""
        raise NotImplementedError()

    @abstractmethod
    def dispose(self):
        """Disposes of the service scope"""
        raise NotImplementedError()


class ServiceScope(ServiceScopeBase, ServiceProviderBase):
    """Represents the default implementation of the IServiceScope class"""

    def __init__(
        self,
        root_service_provider: ServiceProviderBase,
        scoped_service_descriptors: list[ServiceDescriptor],
        all_service_descriptors: list[ServiceDescriptor],
    ):
        self._root_service_provider = root_service_provider
        self._scoped_service_descriptors = scoped_service_descriptors
        self._all_service_descriptors = all_service_descriptors
        self._realized_scoped_services = dict[Type, List]()  # Instance-level cache

    _root_service_provider: ServiceProviderBase
    """ Gets the IServiceProvider that has created the service scope """

    _scoped_service_descriptors: list[ServiceDescriptor]
    """ Gets a list containing the configurations of all scoped dependencies """

    def get_service_provider(self) -> ServiceProviderBase:
        return self

    def get_service(self, type: type) -> Optional[any]:
        if type == ServiceProviderBase:
            return self

        # First check if we have a scoped service descriptor
        scoped_descriptor = next(
            (descriptor for descriptor in self._scoped_service_descriptors if descriptor.service_type == type),
            None,
        )
        if scoped_descriptor is not None:
            # Check if we already have a cached scoped instance
            realized_services = self._realized_scoped_services.get(type)
            if realized_services is not None and len(realized_services) > 0:
                return realized_services[0]
            else:
                # Build new scoped service
                return self._build_service(scoped_descriptor)

        # For non-scoped services, we need to check if it's a transient that might have scoped dependencies
        # Try to find the descriptor in the root provider and handle it accordingly
        root_descriptor = next(
            (descriptor for descriptor in self._all_service_descriptors if descriptor.service_type == type),
            None,
        )
        if root_descriptor is not None:
            # If it's a transient service, build it in the scope context so dependencies resolve correctly
            if root_descriptor.lifetime == ServiceLifetime.TRANSIENT:
                return self._build_service(root_descriptor)
            # For singleton services, delegate to root provider
            elif root_descriptor.lifetime == ServiceLifetime.SINGLETON:
                return self._root_service_provider.get_service(type)
            # Scoped services should have been handled above, but just in case
            elif root_descriptor.lifetime == ServiceLifetime.SCOPED:
                return self._build_service(root_descriptor)

        # Fall back to root service provider for anything else
        return self._root_service_provider.get_service(type)

    def get_required_service(self, type: type) -> any:
        service = self.get_service(type)
        if service is None:
            raise Exception(f"Failed to resolve service of type '{type.__name__}'")
        return service

    def get_services(self, type: type) -> list:
        if type == ServiceProviderBase:
            return [self]
        service_descriptors = [descriptor for descriptor in self._scoped_service_descriptors if descriptor.service_type == type]
        realized_services = self._realized_scoped_services.get(type)
        if realized_services is None:
            realized_services = list()
        for descriptor in service_descriptors:
            if any(type(service) == descriptor.service_type for service in realized_services):
                continue
            realized_services.append(self._build_service(descriptor))

        # Only get singleton and transient services from root provider
        # Scoped services should only come from the current scope
        root_services = []
        try:
            # Call a special method that only returns singleton/transient services
            root_services = self._root_service_provider._get_non_scoped_services(type)
        except Exception:
            # If there's an error getting root services, just use what we have from scope
            pass

        return realized_services + root_services

    def _build_service(self, service_descriptor: ServiceDescriptor) -> any:
        """Builds a new scoped service"""
        if service_descriptor.singleton is not None:
            service = service_descriptor.singleton
        elif service_descriptor.implementation_factory is not None:
            service = service_descriptor.implementation_factory(self)
        else:
            is_service_generic = not inspect.isclass(service_descriptor.implementation_type)
            service_generic_type = service_descriptor.implementation_type.__origin__ if is_service_generic else None
            service_type = service_descriptor.implementation_type if service_generic_type is None else service_generic_type
            service_init_args = [param for param in inspect.signature(service_type.__init__).parameters.values() if param.name not in ["self", "args", "kwargs"]]
            service_generic_args = TypeExtensions.get_generic_arguments(service_descriptor.implementation_type)
            service_args = dict[Type, any]()
            for init_arg in service_init_args:
                # Use typing.get_origin() and get_args() for robust generic type handling
                origin = get_origin(init_arg.annotation)
                args = get_args(init_arg.annotation)

                # Determine the dependency type to resolve
                if origin is not None and args:
                    # It's a parameterized generic type (e.g., Repository[User, int])
                    # Check if it contains type variables that need substitution
                    # (e.g., CacheRepositoryOptions[TEntity, TKey] -> CacheRepositoryOptions[MozartSession, str])
                    dependency_type = TypeExtensions._substitute_generic_arguments(init_arg.annotation, service_generic_args)
                else:
                    # Simple non-generic type
                    dependency_type = init_arg.annotation

                dependency = self.get_service(dependency_type)
                if dependency is None and init_arg.default == init_arg.empty and init_arg.name != "self":
                    raise Exception(f"Failed to build service of type '{service_descriptor.service_type.__name__}' because the service provider failed to resolve service '{dependency_type.__name__}'")
                service_args[init_arg.name] = dependency
            service = service_descriptor.implementation_type(**service_args)

        # Cache the scoped service
        realized_services = self._realized_scoped_services.get(service_descriptor.service_type)
        if realized_services is None:
            self._realized_scoped_services[service_descriptor.service_type] = [service]
        else:
            realized_services.append(service)
        return service

    def dispose(self):
        for services in self._realized_scoped_services.values():
            for service in services:
                try:
                    if hasattr(service, "__exit__"):
                        service.__exit__(None, None, None)
                except:
                    pass
        self._realized_scoped_services = dict[Type, List]()

    def create_scope(self) -> ServiceScopeBase:
        return self

    def dispose(self):
        for services in self._realized_scoped_services.values():
            for service in services:
                try:
                    if hasattr(service, "__exit__"):
                        service.__exit__(None, None, None)
                except:
                    pass
        self._realized_scoped_services = dict[Type, List]()


class ServiceProvider(ServiceProviderBase):
    """Represents the default implementation of the IServiceProvider class"""

    def __init__(self, service_descriptors: list[ServiceDescriptor]):
        """Initializes a new service provider using the specified service dependency configuration"""
        self._service_descriptors = service_descriptors
        self._realized_services = dict[Type, List]()  # Instance-level cache

    _service_descriptors: list[ServiceDescriptor]
    """ Gets a list containing the configuration of all registered dependencies """

    def get_service(self, type: type) -> Optional[any]:
        if type == ServiceProviderBase:
            return self

        descriptor = next(
            (descriptor for descriptor in self._service_descriptors if descriptor.service_type == type),
            None,
        )
        if descriptor is None:
            return None

        # For transient services, always create new instances
        if descriptor.lifetime == ServiceLifetime.TRANSIENT:
            return self._build_service(descriptor)

        # For non-transient services, check cache first
        realized_services = self._realized_services.get(type)
        if realized_services is not None:
            return realized_services[0]

        return self._build_service(descriptor)

    def get_required_service(self, type: type) -> any:
        service = self.get_service(type)
        if service is None:
            raise Exception(f"Failed to resolve service of type '{type.__name__}'")
        return service

    def get_services(self, type: type) -> list:
        if type == ServiceProviderBase:
            return [self]
        service_descriptors = [descriptor for descriptor in self._service_descriptors if descriptor.service_type == type]
        realized_services = self._realized_services.get(type)
        if realized_services is None:
            realized_services = list()
        for descriptor in service_descriptors:
            implementation_type = descriptor.get_implementation_type()
            realized_service = next(
                (service for service in realized_services if self._is_service_instance_of(service, implementation_type)),
                None,
            )
            if realized_service is None:
                realized_services.append(self._build_service(descriptor))
        return realized_services

    def _get_non_scoped_services(self, type: type) -> list:
        """
        Gets all singleton and transient services of the specified type,
        excluding scoped services (which should only be resolved from a ServiceScope).

        This is used by ServiceScope.get_services() to avoid trying to resolve
        scoped services from the root provider.
        """
        if type == ServiceProviderBase:
            return [self]

        # Only include singleton and transient descriptors (skip scoped)
        service_descriptors = [descriptor for descriptor in self._service_descriptors if descriptor.service_type == type and descriptor.lifetime != ServiceLifetime.SCOPED]

        realized_services = self._realized_services.get(type)
        if realized_services is None:
            realized_services = list()

        # Build services for non-scoped descriptors
        result_services = []
        for descriptor in service_descriptors:
            implementation_type = descriptor.get_implementation_type()
            realized_service = next(
                (service for service in realized_services if self._is_service_instance_of(service, implementation_type)),
                None,
            )
            if realized_service is None:
                service = self._build_service(descriptor)
                result_services.append(service)
            else:
                result_services.append(realized_service)

        return result_services

    def _is_service_instance_of(self, service: Any, type_: type) -> bool:
        if hasattr(type_, "__origin__"):
            service_type = service.__orig_class__ if hasattr(service, "__orig_class__") else type(service)
            service_generic_arguments = TypeExtensions.get_generic_arguments(service_type)
            implementation_generic_arguments = TypeExtensions.get_generic_arguments(type_)
            for i in range(len(implementation_generic_arguments)):
                generic_argument_name = list(implementation_generic_arguments.keys())[i]
                service_generic_argument = service_generic_arguments.get(generic_argument_name, None)
                if service_generic_argument is None or service_generic_argument != implementation_generic_arguments[generic_argument_name]:
                    return False
            return isinstance(service, type_.__origin__)
        else:
            return isinstance(service, type_)

    def _build_service(self, service_descriptor: ServiceDescriptor) -> any:
        """Builds a new service provider based on the configured dependencies"""
        if service_descriptor.lifetime == ServiceLifetime.SCOPED:
            raise Exception(f"Failed to resolve scoped service of type '{service_descriptor.implementation_type}' from root service provider")
        if service_descriptor.singleton is not None:
            service = service_descriptor.singleton
        elif service_descriptor.implementation_factory is not None:
            service = service_descriptor.implementation_factory(self)
        else:
            is_service_generic = not inspect.isclass(service_descriptor.implementation_type)  # if implementation_type is not a class, then it must be a generic type
            service_generic_type = service_descriptor.implementation_type.__origin__ if is_service_generic else None  # retrieve the generic type, used to determine the __init__ args
            service_type = service_descriptor.implementation_type if service_generic_type is None else service_generic_type  # get the type used to determine the __init__ args: the implementation type as is or its generic type definition
            service_init_args = [param for param in inspect.signature(service_type.__init__).parameters.values() if param.name not in ["self", "args", "kwargs"]]  # gets the __init__ args and leave out self, args and kwargs
            service_generic_args = TypeExtensions.get_generic_arguments(service_descriptor.implementation_type)  # gets the generic args: we will need them to substitute the type args of potential generic dependencies
            service_args = dict[Type, any]()
            for init_arg in service_init_args:
                # Use typing.get_origin() and get_args() for robust generic type handling
                origin = get_origin(init_arg.annotation)
                args = get_args(init_arg.annotation)

                # Determine the dependency type to resolve
                if origin is not None and args:
                    # It's a parameterized generic type (e.g., Repository[User, int])
                    # Check if it contains type variables that need substitution
                    # (e.g., CacheRepositoryOptions[TEntity, TKey] -> CacheRepositoryOptions[MozartSession, str])
                    dependency_type = TypeExtensions._substitute_generic_arguments(init_arg.annotation, service_generic_args)
                else:
                    # Simple non-generic type
                    dependency_type = init_arg.annotation

                dependency = self.get_service(dependency_type)
                if dependency is None and init_arg.default == init_arg.empty and init_arg.name != "self":
                    raise Exception(f"Failed to build service of type '{service_descriptor.service_type.__name__}' because the service provider failed to resolve service '{dependency_type.__name__}'")
                service_args[init_arg.name] = dependency
            service = service_descriptor.implementation_type(**service_args)
        if service_descriptor.lifetime != ServiceLifetime.TRANSIENT:
            realized_services = self._realized_services.get(service_descriptor.service_type)
            if realized_services is None:
                self._realized_services[service_descriptor.service_type] = [service]
            else:
                realized_services.append(service)
        return service

    def create_scope(self) -> ServiceScopeBase:
        return ServiceScope(
            self,
            [descriptor for descriptor in self._service_descriptors if descriptor.lifetime == ServiceLifetime.SCOPED],
            self._service_descriptors,
        )

    def dispose(self):
        for service in self._realized_services:
            try:
                service.__exit__()
            except:
                pass
        self._realized_services = dict[Type, List]()


class ServiceDescriptor:
    """
    Represents the configuration metadata for service registration in the dependency injection container.

    Service descriptors encapsulate all information needed to create and manage service instances,
    including the service type, implementation strategy, lifetime management, and creation logic.

    Configuration Options:
        - Service Type: The interface or abstract class being registered
        - Implementation Type: The concrete class to instantiate
        - Singleton: Pre-created instance to reuse
        - Implementation Factory: Custom creation logic
        - Lifetime: How instances are managed (singleton, scoped, transient)

    Examples:
        ```python
        # Interface to implementation mapping
        descriptor = ServiceDescriptor(
            service_type=IUserRepository,
            implementation_type=SqlUserRepository,
            lifetime=ServiceLifetime.SCOPED
        )

        # Singleton instance
        config = AppConfiguration()
        descriptor = ServiceDescriptor(
            service_type=AppConfiguration,
            singleton=config,
            lifetime=ServiceLifetime.SINGLETON
        )

        # Factory-based creation
        def create_email_service(provider: ServiceProvider) -> EmailService:
            config = provider.get_service(EmailConfiguration)
            return SmtpEmailService(config.smtp_server, config.port)

        descriptor = ServiceDescriptor(
            service_type=EmailService,
            implementation_factory=create_email_service,
            lifetime=ServiceLifetime.TRANSIENT
        )
        ```

    See Also:
        - Service Registration: https://bvandewe.github.io/pyneuro/features/
        - Dependency Injection Guide: https://bvandewe.github.io/pyneuro/patterns/
    """

    def __init__(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        singleton: any = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ):
        """Initializes a new service descriptor"""
        if singleton is not None and lifetime != ServiceLifetime.SINGLETON:
            raise Exception("A singleton service dependency must have lifetime set to 'SINGLETON'")
        self.service_type = service_type
        self.implementation_type = implementation_type
        self.singleton = singleton
        self.implementation_factory = implementation_factory
        self.lifetime = lifetime
        if self.singleton is None and self.implementation_factory is None and self.implementation_type is None:
            self.implementation_type = self.service_type

    service_type: type
    """ Gets the type of the service dependency """

    implementation_type: Optional[type]
    """ Gets the service dependency's implementation/concretion type, if any, to be instanciated on demand by a service provider. If set, 'singleton' and 'implementation-factory' are ignored. """

    singleton: any
    """ Gets the service instance singleton, if any. If set, 'implementation_type' and 'implementation-factory' are ignored. """

    implementation_factory: Callable[[ServiceProvider], any]
    """ Gets a function, if any, use to create a new instance of the service dependency. If set, 'implementation_type' and 'singleton' are ignored. """

    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON
    """ Gets the service's lifetime. Defaults to 'SINGLETON' """

    def get_implementation_type(self) -> type:
        """Gets the service's implementation type"""
        if self.implementation_type is not None:
            return self.implementation_type
        return_type = inspect.signature(self.implementation_factory).return_annotation if self.implementation_factory != None else None
        if return_type is None and self.implementation_factory != None:
            if self.implementation_type is None:
                raise Exception(f"Failed to determine the return type of the implementation factory configured for service of type '{self.service_type.__name__}'. Either specify the implementation type, or use a function instead of a lambda as factory callable.")
            else:
                return_type = self.implementation_type
        return type(self.singleton) if self.singleton is not None else inspect.signature(self.implementation_factory).return_annotation


# ServiceCollection will be defined at the end of this file


class ServiceCollection(List[ServiceDescriptor]):
    """
    Represents a fluent configuration builder for dependency injection container services.

    The ServiceCollection provides a chainable API for registering services with different
    lifetimes and configuration options, making it easy to set up complex dependency graphs
    with minimal boilerplate code.

    Key Features:
        - Fluent registration API with method chaining
        - Support for all service lifetimes (singleton, scoped, transient)
        - Interface-to-implementation mappings
        - Factory-based service creation
        - Conditional registration with try_add methods
        - Automatic service provider building

    Examples:
        ```python
        # Basic service registration
        services = ServiceCollection()

        # Singleton services (shared across application)
        services.add_singleton(AppConfiguration) \\
                .add_singleton(ICache, MemoryCache) \\
                .add_singleton(ILogger, FileLogger)

        # Scoped services (one per request/scope)
        services.add_scoped(IUserRepository, SqlUserRepository) \\
                .add_scoped(IOrderRepository, SqlOrderRepository) \\
                .add_scoped(UnitOfWork)

        # Transient services (new instance each time)
        services.add_transient(IValidator, EmailValidator) \\
                .add_transient(IValidator, PasswordValidator) \\
                .add_transient(OrderService)

        # Factory-based registration
        services.add_singleton(
            IEmailService,
            implementation_factory=lambda p: SmtpEmailService(
                p.get_service(EmailConfiguration)
            )
        )

        # Conditional registration (only if not already registered)
        services.try_add_scoped(IUserRepository, InMemoryUserRepository)

        # Build the container
        provider = services.build_provider()
        ```

    Registration Patterns:
        ```python
        # Self-registration (concrete class as interface)
        services.add_scoped(UserService)

        # Interface mapping
        services.add_scoped(IUserService, UserService)

        # Multiple implementations
        services.add_transient(INotificationSender, EmailSender) \\
                .add_transient(INotificationSender, SmsSender)

        # Configuration-based factories
        services.add_singleton(
            DatabaseContext,
            implementation_factory=lambda p: DatabaseContext(
                p.get_service(DatabaseConfiguration).connection_string
            )
        )
        ```

    See Also:
        - Dependency Injection Guide: https://bvandewe.github.io/pyneuro/patterns/
        - Service Registration: https://bvandewe.github.io/pyneuro/features/
        - Getting Started: https://bvandewe.github.io/pyneuro/getting-started/
    """

    def add_singleton(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        singleton: any = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
    ) -> ServiceCollection:
        """Registers a new singleton service dependency"""
        self.append(
            ServiceDescriptor(
                service_type,
                implementation_type,
                singleton,
                implementation_factory,
                ServiceLifetime.SINGLETON,
            )
        )
        return self

    def try_add_singleton(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        singleton: any = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
    ) -> ServiceCollection:
        """Attempts to register a new singleton service dependency, if one has not already been registered"""
        if any(descriptor.service_type == service_type for descriptor in self):
            return self
        return self.add_singleton(service_type, implementation_type, singleton, implementation_factory)

    def add_transient(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
    ) -> ServiceCollection:
        """Registers a new transient service dependency"""
        self.append(
            ServiceDescriptor(
                service_type,
                implementation_type,
                None,
                implementation_factory,
                ServiceLifetime.TRANSIENT,
            )
        )
        return self

    def try_add_transient(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
    ) -> ServiceCollection:
        """Attempts to register a new transient service dependency, if one has not already been registered"""
        if any(descriptor.service_type == service_type for descriptor in self):
            return self
        return self.add_transient(service_type, implementation_type, implementation_factory)

    def add_scoped(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        singleton: any = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
    ) -> ServiceCollection:
        """Registers a new scoped service dependency"""
        self.append(
            ServiceDescriptor(
                service_type,
                implementation_type,
                singleton,
                implementation_factory,
                ServiceLifetime.SCOPED,
            )
        )
        return self

    def try_add_scoped(
        self,
        service_type: type,
        implementation_type: Optional[type] = None,
        singleton: any = None,
        implementation_factory: Callable[[ServiceProvider], any] = None,
    ) -> ServiceCollection:
        """Attempts to register a new scoped service dependency, if one has not already been registered"""
        if any(descriptor.service_type == service_type for descriptor in self):
            return self
        return self.add_scoped(service_type, implementation_type, singleton, implementation_factory)

    def build(self) -> ServiceProviderBase:
        return ServiceProvider(self)
