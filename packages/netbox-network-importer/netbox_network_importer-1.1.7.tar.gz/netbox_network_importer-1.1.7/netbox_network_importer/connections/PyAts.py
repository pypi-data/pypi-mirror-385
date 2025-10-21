from genie.testbed import load
from pyats.contrib.creators.netbox import Netbox

from netbox_network_importer.config import get_config


class PyAtsNetbox:
    def __init__(
        self,
        testbed_dict=None,
        topology=False,
        url_filter="platform_id__n=null&has_primary_ip=True",
    ):
        """Create PyATS testbed structure through Netbox

        The value of the temp parameter is stored as a value in
        the class variable temperature. The given value is converted
        into a float value if not yet done.

        :param testbed_dict: pass custom testbed configuration, default: Connection to netbox
        :param topology: Loads tons of information from Netbox, takes a lot of time. default: False
        """

        if not testbed_dict:
            testbed_dict = Netbox(
                netbox_url=get_config()["netbox"]["NETBOX_INSTANCE_URL"],
                user_token=get_config()["netbox"]["NETBOX_API_TOKEN"],
                def_user=get_config()["tacacs"]["TACACS_USERNAME"],
                def_pass=get_config()["tacacs"]["TACACS_PASSWORD"],
                encode_password=True,
                topology=topology,  # Dont load IP addresses etc
                url_filter=url_filter,
                custom_data_source=[],
            )

        self.testbed = load(testbed_dict._generate())

    def get_device(self, hostname):
        return self.testbed.devices[hostname]

    def get_testbed(self):
        return self.testbed

    def connect_device(
        self,
        hostname,
        init_exec_commands=[
            "terminal length 0 ",
        ],
        init_config_commands=[],
        log_stdout=False,
        learn_hostname=True,
        learn_os=True,
    ):
        device = self.get_device(hostname)
        device.connect(
            init_exec_commands=init_exec_commands,
            init_config_commands=init_config_commands,
            log_stdout=log_stdout,
            learn_hostname=learn_hostname,
            learn_os=learn_os,
        )

        return device

    def get_devices(self):
        return self.testbed.devices

    def connection_test(self, hostname):
        try:
            self.connect_device(hostname)
            return (True, f"{hostname} connected successfuly")
        except Exception as e:
            return (False, e)
