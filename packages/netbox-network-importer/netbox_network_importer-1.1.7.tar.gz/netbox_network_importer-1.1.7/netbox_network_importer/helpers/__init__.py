"""
Helper utilities for the NetBox Network Importer.

This package provides common utilities to reduce code duplication:
- error_handling: Standardized error handling decorators and utilities
- batch_query: Efficient batch querying utilities for NetBox API
- result_factory: Factory functions for creating NetboxResult objects
"""

# Make common utilities easily accessible
from .batch_query import NetboxBatchQuery
from .error_handling import (
    create_batch_interface_lookup,
    create_not_found_result,
    create_skipped_result,
    handle_netbox_operation,
    should_skip_interface,
)
from .result_factory import (
    NetboxResultFactory,
    create_cable_check_result,
    create_dependency_error_result,
    create_ignored_interface_result,
)

__all__ = [
    # Error handling
    "handle_netbox_operation",
    "create_skipped_result",
    "create_not_found_result",
    "should_skip_interface",
    "create_batch_interface_lookup",
    # Batch querying
    "NetboxBatchQuery",
    # Result factory
    "NetboxResultFactory",
    "create_ignored_interface_result",
    "create_cable_check_result",
    "create_dependency_error_result",
]
