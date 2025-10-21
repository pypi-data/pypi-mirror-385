"""
Factory functions for creating common NetboxResult objects to reduce duplication.
"""

from netbox_network_importer.helper import get_diff
from netbox_network_importer.results.results import Action, NetboxResult, Status


class NetboxResultFactory:
    """Factory class for creating standardized NetboxResult objects."""

    @staticmethod
    def create_success(
        name: str, action: Action, diff=None, message: str = None
    ) -> NetboxResult:
        """
        Create a success result.

        Args:
            name: Object name
            action: Action performed
            diff: Difference data (optional)
            message: Custom success message (optional)

        Returns:
            NetboxResult with CHANGED status
        """
        if message is None:
            action_verb = (
                action.name.lower() + "d" if action != Action.CREATE else "created"
            )
            message = f"{name} - {action_verb} successfully"

        return NetboxResult(
            result=message,
            status=Status.CHANGED,
            action=action,
            diff=diff or {},
        )

    @staticmethod
    def create_no_change(
        name: str, action: Action, message: str = None
    ) -> NetboxResult:
        """
        Create a no-change result.

        Args:
            name: Object name
            action: Action attempted
            message: Custom message (optional)

        Returns:
            NetboxResult with NOT_CHANGED status
        """
        if message is None:
            message = f"{name} - nothing to do"

        return NetboxResult(
            result=message,
            status=Status.NOT_CHANGED,
            action=action,
            diff={},
        )

    @staticmethod
    def create_skipped(
        name: str, reason: str, action: Action = Action.LOOKUP
    ) -> NetboxResult:
        """
        Create a skipped result.

        Args:
            name: Object name
            reason: Reason for skipping
            action: Action that was skipped

        Returns:
            NetboxResult with SKIPPED status
        """
        return NetboxResult(
            result=f"{name} - {reason} - Skipping",
            status=Status.SKIPPED,
            action=action,
            diff={},
        )

    @staticmethod
    def create_not_found(
        name: str, context: str = "", action: Action = Action.LOOKUP
    ) -> NetboxResult:
        """
        Create a not-found result.

        Args:
            name: Object name not found
            context: Additional context
            action: Action that failed due to missing object

        Returns:
            NetboxResult with ANOMALLY status
        """
        message = f"{name} not found in NetBox"
        if context:
            message += f" - {context}"

        return NetboxResult(
            result=message,
            status=Status.ANOMALLY,
            action=action,
            diff={},
        )

    @staticmethod
    def create_check_manually(
        name: str, reason: str, action: Action, diff=None
    ) -> NetboxResult:
        """
        Create a check-manually result.

        Args:
            name: Object name
            reason: Reason requiring manual check
            action: Action that requires manual intervention
            diff: Additional data for manual review

        Returns:
            NetboxResult with CHECK_MANUALLY status
        """
        return NetboxResult(
            result=f"{name} - CHECK MANUALLY - {reason}",
            status=Status.CHECK_MANUALLY,
            action=action,
            diff=diff or {},
        )

    @staticmethod
    def create_failed(
        name: str, error: str, action: Action, exception=None
    ) -> NetboxResult:
        """
        Create a failed result.

        Args:
            name: Object name
            error: Error description
            action: Action that failed
            exception: Exception object (optional)

        Returns:
            NetboxResult with FAILED status
        """
        return NetboxResult(
            result=f"{name} - could not be {action.name.lower()}d: {error}",
            status=Status.FAILED,
            action=action,
            diff={},
            exception=exception,
        )

    @staticmethod
    def create_exception(
        name: str, error: str, action: Action, exception=None
    ) -> NetboxResult:
        """
        Create an exception result.

        Args:
            name: Object name
            error: Error description
            action: Action that caused exception
            exception: Exception object (optional)

        Returns:
            NetboxResult with EXCEPTION status
        """
        return NetboxResult(
            result=f"{name} - {action.name.lower()} exception: {error}",
            status=Status.EXCEPTION,
            action=action,
            diff={},
            exception=exception,
        )

    @staticmethod
    def create_update_result(
        name: str, before: dict, after: dict, nb_object=None
    ) -> NetboxResult:
        """
        Create an update result with before/after comparison.

        Args:
            name: Object name
            before: State before update
            after: State after update
            nb_object: NetBox object (for reload if needed)

        Returns:
            NetboxResult with appropriate status based on changes
        """
        diff = get_diff(before, after)

        if diff:
            return NetboxResultFactory.create_success(
                name=name,
                action=Action.UPDATE,
                diff=diff,
            )
        else:
            return NetboxResultFactory.create_no_change(
                name=name,
                action=Action.UPDATE,
            )


# Convenience functions for common patterns
def create_ignored_interface_result(
    interface_name: str, action: Action = Action.LOOKUP
) -> NetboxResult:
    """Create result for interface ignored by importer."""
    return NetboxResultFactory.create_skipped(
        name=interface_name,
        reason="Ignored by Importer",
        action=action,
    )


def create_cable_check_result(interface_name: str, interface_obj) -> NetboxResult:
    """Create result for interface that has cable connection."""
    return NetboxResultFactory.create_check_manually(
        name=interface_name,
        reason="Cable exists",
        action=Action.DELETE,
        diff={
            "name": interface_obj.name,
            "device_name": interface_obj.device.name,
            "description": interface_obj.description,
            "cable_id": interface_obj.cable.id,
        },
    )


def create_dependency_error_result(
    name: str, action: Action, error_msg: str, exception=None
) -> NetboxResult:
    """Create result for operations that fail due to dependencies (409 Conflict)."""
    return NetboxResultFactory.create_failed(
        name=name,
        error=error_msg,
        action=action,
        exception=exception,
    )
