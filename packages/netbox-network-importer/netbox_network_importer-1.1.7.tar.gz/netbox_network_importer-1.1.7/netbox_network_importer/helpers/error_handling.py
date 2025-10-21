"""
Common error handling utilities to reduce code duplication across netbox_updater modules.
"""

from functools import wraps

from loguru import logger
from pynetbox.core.query import RequestError

from netbox_network_importer.results.results import Action, NetboxResult, Status


def handle_netbox_operation(operation_name: str, action: Action):
    """
    Decorator to standardize error handling for NetBox operations.

    Args:
        operation_name: Name of the operation for logging (e.g., "Interface deletion", "MAC address update")
        action: The NetBox action being performed (CREATE, UPDATE, DELETE, etc.)

    Returns:
        Decorator function that wraps NetBox operations with standardized error handling
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract interface/object name for logging - assume first argument is the NetBox object
            obj_name = "unknown"
            obj_id = "unknown"

            if args:
                first_arg = args[0]
                if hasattr(first_arg, "name"):
                    obj_name = first_arg.name
                if hasattr(first_arg, "id"):
                    obj_id = first_arg.id
                elif hasattr(first_arg, "address"):  # For IP addresses
                    obj_name = first_arg.address
                    if hasattr(first_arg, "id"):
                        obj_id = first_arg.id

            try:
                return func(*args, **kwargs)

            except RequestError as e:
                if e.req.status_code == 409:
                    # Handle 409 Conflict - dependent objects exist
                    logger.error(
                        f"{operation_name} failed due to dependencies: {obj_name} (NetBox ID: {obj_id}) - {str(e)}"
                    )
                    return NetboxResult(
                        result=f"{obj_name} - could not be {action.name.lower()}d: {str(e)}",
                        status=Status.FAILED,
                        action=action,
                        diff={},
                        exception=e,
                    )
                else:
                    # Handle other HTTP errors
                    logger.error(
                        f"{operation_name} failed with HTTP error: {obj_name} (NetBox ID: {obj_id}) - {str(e)}"
                    )
                    return NetboxResult(
                        result=f"{obj_name} - could not be {action.name.lower()}d: {str(e)}",
                        status=Status.FAILED,
                        action=action,
                        diff={},
                        exception=e,
                    )

            except Exception as e:
                logger.error(
                    f"{operation_name} exception: {obj_name} (NetBox ID: {obj_id}) - {str(e)}"
                )
                return NetboxResult(
                    result=f"{obj_name} - {operation_name.lower()} exception: {str(e)}",
                    status=Status.EXCEPTION,
                    action=action,
                    diff={},
                    exception=e,
                )

        return wrapper

    return decorator


def create_skipped_result(
    name: str, reason: str, action: Action = Action.LOOKUP
) -> NetboxResult:
    """
    Create a standardized NetboxResult for skipped operations.

    Args:
        name: Name of the object being skipped
        reason: Reason for skipping (e.g., "Ignored by Importer")
        action: The action that was skipped

    Returns:
        NetboxResult with SKIPPED status
    """
    return NetboxResult(
        result=f"{name} - {reason} - Skipping",
        status=Status.SKIPPED,
        action=action,
        diff="",
    )


def create_not_found_result(
    name: str, context: str, action: Action = Action.LOOKUP
) -> NetboxResult:
    """
    Create a standardized NetboxResult for objects not found in NetBox.

    Args:
        name: Name of the object not found
        context: Additional context (e.g., device name)
        action: The action that failed due to missing object

    Returns:
        NetboxResult with ANOMALLY status
    """
    return NetboxResult(
        result=f"{name} not found in NetBox - {context}",
        status=Status.ANOMALLY,
        action=action,
        diff={},
    )


def should_skip_interface(interface, import_field: str = "ignore_importer") -> bool:
    """
    Check if an interface should be skipped based on custom fields.

    Args:
        interface: NetBox interface object
        import_field: Custom field name to check (default: "ignore_importer")

    Returns:
        True if interface should be skipped, False otherwise
    """
    return interface.custom_fields.get(import_field, False)


def create_batch_interface_lookup(nb, device_id):
    """
    Create a batch lookup dictionary for interfaces to avoid repeated API calls.

    Args:
        nb: NetBox connection object
        device_id: Device ID to filter interfaces

    Returns:
        Dictionary mapping canonical interface names to NetBox interface objects
    """
    from netbox_network_importer.helper import canonical_interface_name_edited

    interfaces = nb.dcim.interfaces.filter(device_id=device_id)
    return {canonical_interface_name_edited(ifc.name): ifc for ifc in interfaces}
