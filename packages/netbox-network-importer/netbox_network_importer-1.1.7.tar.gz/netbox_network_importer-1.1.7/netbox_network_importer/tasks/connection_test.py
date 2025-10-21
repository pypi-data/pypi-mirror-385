from nornir.core.task import Task, Result
from netbox_network_importer.results.results import TaskNetboxResult, Status
from netbox_network_importer.connections.Napalm import Napalm
from netbox_network_importer.helper import get_address_from_netbox_task


def connection_test(task: Task, pyats) -> Result:
    if not task.host.platform:
        task_result = TaskNetboxResult(task=task.name,
                                       netbox_results=[],
                                       status="failed",
                                       exception="Platform is not set",
                                       comment="Platform is not set")
        return Result(
            host=task.host,
            exception=f"{task.host.name} - Platform is not set",
            result=f"{task.host.name} - Platform is not set",
            failed=True,
            netbox_results=task_result,
            diff=task_result.to_dict())

    elif task.host.platform not in ['ios', 'iosxr', 'iosxe', 'nxos', 'nxos_ssh', 'junos']:
        task_result = TaskNetboxResult(task=task.name,
                                       netbox_results=[],
                                       status="failed",
                                       exception=f"Unsupported platform {task.host.platform}",
                                       comment=f"Unsupported platform {task.host.platform}")
        return Result(
            host=task.host,
            exception=f"{task.host.name} - Unsupported platform {task.host.platform}",
            result=f"{task.host.name} - Unsupported platform {task.host.platform}",
            failed=True,
            netbox_results=task_result,
            diff=task_result.to_dict())

    # NAPALM connection test
    host_ip = get_address_from_netbox_task(task)

    if not host_ip:
        task_result = TaskNetboxResult(task=task.name,
                                       netbox_results=[],
                                       status="failed",
                                       exception=f"Primary IP not set",
                                       comment=f"Primary IP not set")
        return Result(
            host=task.host,
            exception=f"{task.host.name} - Primary IP not set",
            result=f"{task.host.name} - Primary IP not set",
            failed=True,
            netbox_results=task_result,
            diff=task_result.to_dict())

    dev = Napalm(host_ip, task.host.platform)
    connected, message = dev.connection_test()
    if not connected:
        task_result = TaskNetboxResult(task=task.name,
                                       netbox_results=[],
                                       status="failed",
                                       exception=message,
                                       comment="Failed to connect to device via Napalm")

        return Result(
            host=task.host,
            exception=message,
            result=f"{task.host.name} - Failed to connect to napalm",
            failed=True,
            netbox_results=task_result,
            diff=task_result.to_dict(except_status_codes=[Status.NOT_CHANGED]))

    # Pyats Connection Test
    connected, message = pyats.connection_test(hostname=task.host.name)
    if not connected:
        task_result = TaskNetboxResult(task=task.name,
                                       netbox_results=[],
                                       status="failed",
                                       exception=message,
                                       comment="Unable to connect to device via PyATS")
        return Result(
            host=task.host,
            exception=message,
            result=f"{task.host.name} - Unable to connect to device",
            netbox_results=task_result,
            diff=task_result.to_dict(except_status_codes=[Status.NOT_CHANGED]),
            failed=True)

    # Return OK

    task_result = TaskNetboxResult(task=task.name,
                                   netbox_results=[],
                                   status="completed")
    return Result(host=task.host,
                  result="Connection test - OK",
                  netbox_results=task_result,
                  diff=task_result.to_dict(except_status_codes=[Status.NOT_CHANGED]))
