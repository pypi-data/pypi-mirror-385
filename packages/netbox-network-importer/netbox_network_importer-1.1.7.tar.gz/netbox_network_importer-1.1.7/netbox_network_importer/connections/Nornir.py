from nornir import InitNornir

from netbox_network_importer.config import get_config


class Nornir:
    def init_nornir_w_netbox(
        filter_parameters={}, logging_enabled=False, logging_level="DEBUG"
    ):
        """Init nornir with Netbox.

        :param filter_parameters: params to filter certain devices
        """
        from loguru import logger

        # Get and validate NORNIR_WORKERS configuration
        nornir_workers = get_config()["config"].get("NORNIR_WORKERS", 20)

        # Validate worker count
        if not isinstance(nornir_workers, int) or nornir_workers < 1:
            logger.warning(
                f"Invalid NORNIR_WORKERS value: {nornir_workers}. Using default of 20."
            )
            nornir_workers = 20
        elif nornir_workers > 100:
            logger.warning(
                f"NORNIR_WORKERS value {nornir_workers} is very high. Consider using a lower value for better performance."
            )

        nr = InitNornir(
            logging={"enabled": logging_enabled, "level": logging_level},
            inventory={
                "plugin": "NetBoxInventory2",
                "options": {
                    "nb_url": get_config()["netbox"]["NETBOX_INSTANCE_URL"],
                    "nb_token": get_config()["netbox"]["NETBOX_API_TOKEN"],
                    "flatten_custom_fields": False,
                    "filter_parameters": filter_parameters,
                    "use_platform_slug": False,
                    "use_platform_napalm_driver": False,
                    # group_file,
                    # defaults_file - could be used for username and password for devices - connection options
                },
            },
            runner={
                "plugin": "threaded",
                "options": {
                    "num_workers": nornir_workers  # configurable workers with validation
                },
            },
        )

        return nr
