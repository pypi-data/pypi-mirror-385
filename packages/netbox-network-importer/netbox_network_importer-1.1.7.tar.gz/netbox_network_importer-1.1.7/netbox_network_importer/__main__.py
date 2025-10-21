import os
import sys

import click
import requests
from loguru import logger
from nornir_utils.plugins.functions import print_title

from netbox_network_importer.config import clear_config_cache, get_config, setup_logger
from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.connections.Nornir import Nornir
from netbox_network_importer.connections.PyAts import PyAtsNetbox
from netbox_network_importer.helper import remove_key_from_results
from netbox_network_importer.outputers.output import html_output, json_output
from netbox_network_importer.processors.progress_indicator import ProgressIndicator
from netbox_network_importer.processors.save_netbox_results import SaveNetboxResults
from netbox_network_importer.tasks.connection_test import connection_test
from netbox_network_importer.tasks.synchronizer import (
    synchronize_interfaces,
    synchronize_interfaces_bandwidths,
    synchronize_interfaces_ips,
    synchronize_interfaces_lags,
    synchronize_interfaces_vlans,
    synchronize_serials,
)


def get_print_result_function():
    """Get the appropriate print_result function based on configuration

    Returns:
        function: Either nornir_rich.functions.print_result or nornir_utils.plugins.functions.print_result
    """
    try:
        config = get_config()
        use_nornir_rich = config.get("config", {}).get("USE_NORNIR_RICH_PRINT", True)

        if use_nornir_rich:
            from nornir_rich.functions import print_result

            logger.info(
                "Using nornir_rich.functions.print_result for output formatting"
            )
        else:
            from nornir_utils.plugins.functions import print_result

            logger.info(
                "Using nornir_utils.plugins.functions.print_result for output formatting"
            )

        return print_result
    except Exception as e:
        # Fallback to nornir_rich if config fails
        logger.warning(
            f"Failed to get print_result configuration, falling back to nornir_rich: {e}"
        )
        from nornir_rich.functions import print_result

        return print_result


@click.group()
@click.option(
    "--configs",
    "-c",
    type=click.Path(),
    multiple=False,
    help="path to folder with configurations",
)
def cli(configs):
    # set custom configs folder path
    if configs:
        os.environ["CONFIG_FOLDER_PATH"] = os.path.abspath(configs)

    setup_logger()


@cli.command()
@click.option(
    "--device",
    "-d",
    type=str,
    multiple=False,
    required=True,
    help="Run on specificied device",
)
@click.option(
    "--command",
    "-c",
    type=str,
    multiple=False,
    required=True,
    help="Run command e.g. show version",
)
def pyats(device, command):
    """
    Connect to device using pyats and pynetbox and print parsed command
    """

    pyats = PyAtsNetbox()
    nb = Netbox.connect()

    nb_dev = nb.dcim.devices.get(name=device)
    hostname = nb_dev.name

    dev = pyats.connect_device(hostname)

    from pprint import pprint

    pprint(dev.parse(command))


@cli.command()
@click.option(
    "--devices", "-d", type=str, multiple=True, help="Run on specificied devices"
)
@click.option(
    "--platforms", "-p", type=str, multiple=True, help="Run on specificied platforms"
)
@logger.catch
# CLI callable command
def synchronize(devices, platforms):
    """Run set of Nornir task to update data in Netbox from network devices

    Args:
        devices (str): device name filter, can be used multiple times
        platforms (str): platform name filter, can be used multiple times
    Returns:
        dict: Dictionary of hosts, it's actions and results
    """

    result_data = run_synchronizer(devices, platforms)
    return result_data


@cli.command()
@click.option(
    "--devices",
    "-d",
    type=str,
    multiple=True,
    help="Run on specificied devices",
    required=True,
)
@logger.catch
# CLI callable command
def synchronize_device(devices):
    """Synchronize specific device data in Netbox from network

    Args:
        devices (str): device name filter, can be used multiple times
    Returns:
        dict: Dictionary of hosts, it's actions and results
    """

    result_data = run_synchronizer(devices, [])
    return result_data


def run_synchronizer(devices, platforms):
    """Run set of Nornir task to update data in Netbox from network devices

    Args:
        devices (str): device name filter, can be used multiple times
        platforms (str): platform name filter, can be used multiple times
    Returns:
        dict: Dictionary of hosts, it's actions and results
    """
    # store netbox process results into a dict
    save_netbox_results_data = {}

    # init devices (nornir) with Netbox
    # filter out devices without IP or Platform
    try:
        nr = Nornir.init_nornir_w_netbox(
            filter_parameters={
                "name": devices,
                "platform": platforms,
                "has_primary_ip": True,
                "platform_id__n": "null",
                "status": "active",
            }
        )
    except ValueError as e:
        logger.error(f"Error connecting to Netbox: {e}")
        logger.error("Exiting...")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Netbox: {e}")
        logger.error("Exiting...")
        sys.exit(1)

    # init device connector with pyAts via Netbox
    # filter out devices without IP or Platform
    try:
        nb_pyats_devices = PyAtsNetbox(
            url_filter="platform_id__n=null&has_primary_ip=True"
        )
    except KeyError as e:
        logger.error(f"Unable to create PyATS testbed structure through Netbox: {e}")
        logger.error("Exiting...")
        sys.exit(1)

    print_result_keys = ["name", "result", "diff", "exception"]

    # Get the configured print_result function
    print_result = get_print_result_function()

    # Connection Test - Skip failed hosts from this action
    print_title("Connection Test")
    nr = nr.with_processors(get_processors(save_netbox_results_data, nr))

    connection_tests = nr.run(task=connection_test, pyats=nb_pyats_devices)
    print_result(connection_tests, vars=print_result_keys)

    skipped_hosts = []
    if connection_tests.failed_hosts:
        # Skip failed hosts in other processing
        for host, result in connection_tests.failed_hosts.items():
            skipped_hosts.append(host)
            # remove host from other processing
            nr.inventory.hosts.pop(host)
        print_title(f"SKIPPING HOSTS: {skipped_hosts}")

    # Create/Update Netbox Interaces
    save_netbox_results_data = run_task(
        task_method=synchronize_serials,
        skipped_hosts=skipped_hosts,
        result_dict_data=save_netbox_results_data,
        print_result_keys=print_result_keys,
        nornir=nr,
        pyats=nb_pyats_devices,
    )

    # Create/Update Netbox Interaces
    save_netbox_results_data = run_task(
        task_method=synchronize_interfaces,
        skipped_hosts=skipped_hosts,
        result_dict_data=save_netbox_results_data,
        print_result_keys=print_result_keys,
        nornir=nr,
        pyats=nb_pyats_devices,
    )

    # CRUD Netbox LAGs
    save_netbox_results_data = run_task(
        task_method=synchronize_interfaces_lags,
        skipped_hosts=skipped_hosts,
        result_dict_data=save_netbox_results_data,
        print_result_keys=print_result_keys,
        nornir=nr,
        pyats=nb_pyats_devices,
    )

    # CRUD netbox IPs on interfaces
    save_netbox_results_data = run_task(
        task_method=synchronize_interfaces_ips,
        skipped_hosts=skipped_hosts,
        result_dict_data=save_netbox_results_data,
        print_result_keys=print_result_keys,
        nornir=nr,
        pyats=nb_pyats_devices,
    )

    # Create VLANs
    save_netbox_results_data = run_task(
        task_method=synchronize_interfaces_vlans,
        skipped_hosts=skipped_hosts,
        result_dict_data=save_netbox_results_data,
        print_result_keys=print_result_keys,
        nornir=nr,
        pyats=nb_pyats_devices,
    )

    # Update Netbox Interaces Bandwidths
    save_netbox_results_data = run_task(
        task_method=synchronize_interfaces_bandwidths,
        skipped_hosts=skipped_hosts,
        result_dict_data=save_netbox_results_data,
        print_result_keys=print_result_keys,
        nornir=nr,
        pyats=nb_pyats_devices,
    )

    netbox_result_data_without_not_changed = remove_key_from_results(
        save_netbox_results_data, "NOT_CHANGED"
    )
    json_output(save_netbox_results_data)
    html_output(netbox_result_data_without_not_changed)

    return save_netbox_results_data


def get_processors(netbox_result_data: dict, nornir_instance=None):
    """Returns list of processors

    Args:
        netbox_result_data (dict): Dict, which will be filled with data.
        nornir_instance: Nornir instance to get host count from

    Returns:
        list: list of processors
    """
    # Get total host count if Nornir instance is provided
    total_hosts = len(nornir_instance.inventory.hosts) if nornir_instance else 0

    processors = [
        ProgressIndicator(total_hosts=total_hosts),
        SaveNetboxResults(netbox_result_data),
    ]
    return processors


def post_process_skipped_hosts(complete_task, skipped_hosts, data) -> dict:
    for skipped_host in skipped_hosts:
        data[skipped_host][complete_task.name] = {"skipped": True}
    return data


def run_task(
    task_method,
    skipped_hosts,
    result_dict_data,
    print_result_keys,
    nornir,
    pyats,
):
    # Create/Update Netbox Interaces
    print_title(f"Running {task_method.__name__} - skipping {skipped_hosts}")
    # always call with_processors
    nr = nornir.with_processors(get_processors(result_dict_data, nornir))

    nr_run_result = nr.run(task=task_method, on_failed=True, pyats=pyats)
    # add info to complete result, that task was skipped
    result_dict_data = post_process_skipped_hosts(
        complete_task=nr_run_result, skipped_hosts=skipped_hosts, data=result_dict_data
    )

    # Get the configured print_result function
    print_result = get_print_result_function()
    print_result(nr_run_result, vars=print_result_keys)

    return result_dict_data


if __name__ == "__main__":
    # Display CLI
    cli()
