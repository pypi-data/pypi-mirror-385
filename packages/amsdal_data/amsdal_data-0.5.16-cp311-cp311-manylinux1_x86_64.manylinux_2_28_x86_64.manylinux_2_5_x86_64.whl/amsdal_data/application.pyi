from _typeshed import Incomplete
from amsdal_data.aliases.using import LAKEHOUSE_DB_ALIAS as LAKEHOUSE_DB_ALIAS
from amsdal_data.data_models.connection_status import ConnectionStatus as ConnectionStatus
from amsdal_data.internal_schemas.metadata import metadata_schema as metadata_schema
from amsdal_data.internal_schemas.reference import reference_schema as reference_schema
from amsdal_data.internal_schemas.transaction import transaction_schema as transaction_schema
from amsdal_data.services.operation_manager import AsyncOperationManager as AsyncOperationManager, OperationManager as OperationManager
from amsdal_data.utils import get_schemas_for_connection_name as get_schemas_for_connection_name, resolve_backend_class as resolve_backend_class
from amsdal_glue_core.common.interfaces.connection import AsyncConnectionBase, ConnectionBase
from amsdal_utils.config.data_models.amsdal_config import AmsdalConfig as AmsdalConfig
from amsdal_utils.utils.decorators import async_mode_only, sync_mode_only
from amsdal_utils.utils.singleton import Singleton
from typing import Any, ClassVar

class DataApplication(metaclass=Singleton):
    DEFAULT_CONTAINER_NAME: ClassVar[str]
    LAKEHOUSE_CONTAINER_NAME: ClassVar[str]
    _is_lakehouse_only: bool
    _application: Incomplete
    _operation_manager: Incomplete
    _extra_connections: dict[str, ConnectionBase]
    _external_service_connections: dict[str, Any]
    @sync_mode_only
    def __init__(self) -> None: ...
    @property
    def is_lakehouse_only(self) -> bool: ...
    @property
    def operation_manager(self) -> OperationManager: ...
    @property
    def connections_statuses(self) -> list[ConnectionStatus]: ...
    def setup(self, config: AmsdalConfig) -> None: ...
    def get_extra_connection(self, name: str) -> Any:
        """Get an extra connection (lock, cache, etc.) by name."""
    def get_external_service_connection(self, name: str) -> Any:
        """Get an external service connection (email, storage, etc.) by name."""
    @staticmethod
    def register_internal_tables() -> None: ...
    def teardown(self) -> None: ...
    def wait_for_background_tasks(self) -> None: ...

class AsyncDataApplication(metaclass=Singleton):
    DEFAULT_CONTAINER_NAME: ClassVar[str]
    LAKEHOUSE_CONTAINER_NAME: ClassVar[str]
    _is_lakehouse_only: bool
    _application: Incomplete
    _operation_manager: Incomplete
    _extra_connections: dict[str, AsyncConnectionBase]
    _external_service_connections: dict[str, Any]
    @async_mode_only
    def __init__(self) -> None: ...
    @property
    def is_lakehouse_only(self) -> bool: ...
    @property
    def operation_manager(self) -> AsyncOperationManager: ...
    @property
    async def connections_statuses(self) -> list[ConnectionStatus]: ...
    async def setup(self, config: AmsdalConfig) -> None: ...
    def get_extra_connection(self, name: str) -> Any:
        """Get an extra connection (lock, cache, etc.) by name."""
    def get_external_service_connection(self, name: str) -> Any:
        """Get an external service connection (email, storage, etc.) by name."""
    @staticmethod
    async def register_internal_tables() -> None: ...
    async def teardown(self) -> None: ...
    async def wait_for_background_tasks(self) -> None: ...
