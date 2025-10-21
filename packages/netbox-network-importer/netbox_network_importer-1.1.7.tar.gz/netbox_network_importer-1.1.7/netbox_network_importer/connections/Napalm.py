"""
Enhanced NAPALM connection class with structured logging using loguru.
Provides better error handling, logging, and context management.
"""

import napalm
from napalm.pyIOSXR.exceptions import XMLCLIError

from netbox_network_importer.config import get_config, get_napalm_logger
from netbox_network_importer.logging_config import get_component_logger

# Get component-specific logger
napalm_logger = get_component_logger("napalm")

driver_iosxr = napalm.get_network_driver('iosxr')
driver_ios = napalm.get_network_driver('ios')
driver_iosxr_netconf = napalm.get_network_driver('iosxr_netconf')
driver_nxos = napalm.get_network_driver('nxos_ssh')
driver_junos = napalm.get_network_driver('junos')


class Napalm:
    """Enhanced NAPALM connection class with structured logging"""
    
    def __init__(self, address: str, driver: str):
        self.address = address
        self.driver = driver
        self.connection = None
        
        # Get specialized logger for this instance
        self.logger = get_napalm_logger(address)
        
        napalm_logger.bind(address=address, driver=driver).info("Initialized NAPALM connection")

    def __set_napalm_driver(self, hostname: str, driver: str, port: int = 22):
        """Set up NAPALM driver with connection parameters"""
        
        napalm_logger.bind(hostname=hostname, driver=driver, port=port).debug("Setting up NAPALM driver")
        
        conn_param = {
            "hostname": hostname,
            "username": get_config()['tacacs']['TACACS_USERNAME'],
            "password": get_config()['tacacs']['TACACS_PASSWORD'],
            "timeout": 60,
            "optional_args": {
                "fast_cli": False,
                "allow_agent": False,
                "look_for_keys": False,
                "conn_timeout": 30,
                "secret": get_config()['tacacs']['TACACS_PASSWORD']
            }
        }

        try:
            if driver == "ios" or driver == "iosxe":
                napalm_logger.bind(hostname=hostname).debug("Using IOS driver")
                return driver_ios(**conn_param)
            elif driver == "iosxr":
                napalm_logger.bind(hostname=hostname).debug("Using IOSXR driver")
                return driver_iosxr(**conn_param)
            elif driver == "iosxr_netconf":
                napalm_logger.bind(hostname=hostname, port=port).debug("Using IOSXR NETCONF driver")
                conn_param['optional_args'] = {}
                conn_param['optional_args']['port'] = port
                return driver_iosxr_netconf(**conn_param)
            elif driver == 'nxos' or driver == 'nxos_ssh':
                napalm_logger.bind(hostname=hostname).debug("Using NXOS driver")
                conn_param['optional_args'] = {'read_timeout_override': 300}
                return driver_nxos(**conn_param)
            elif driver == 'junos':
                napalm_logger.bind(hostname=hostname).debug("Using Junos driver")
                return driver_junos(**conn_param)
            else:
                napalm_logger.bind(hostname=hostname, driver=driver).error("Unsupported device driver")
                return False
                
        except Exception as e:
            napalm_logger.bind(hostname=hostname, driver=driver, error=str(e)).error("Failed to initialize driver")
            raise

    def open(self):
        """Open connection to device"""
        self.logger.start_operation()
        
        try:
            napalm_logger.bind(address=self.address, driver=self.driver).debug("Opening connection")
            self.connection = self.__set_napalm_driver(self.address, self.driver)
            self.connection.open()
            
            napalm_logger.bind(address=self.address, driver=self.driver).info("Connection opened successfully")
            
        except Exception as e:
            napalm_logger.bind(address=self.address, driver=self.driver, error=str(e)).error("Failed to open connection")
            self.logger.error(e, "Connection failed")
            raise

    def close(self):
        """Close connection to device"""
        if self.connection:
            try:
                self.connection.close()
                napalm_logger.bind(address=self.address).debug("Connection closed")
            except Exception as e:
                napalm_logger.bind(address=self.address, error=str(e)).warning("Error closing connection")
            finally:
                self.connection = None

    def get_interfaces_ip(self):
        """Get interface IP addresses with error handling and logging"""
        operation = "get_interfaces_ip"
        napalm_logger.bind(address=self.address).info(f"Starting {operation}")
        
        try:
            self.open()
            result = self.connection.get_interfaces_ip()
            self.close()
            
            interface_count = len(result) if result else 0
            napalm_logger.bind(address=self.address, interface_count=interface_count).success(f"{operation} completed")
            return result
            
        except XMLCLIError as e:
            if self.driver == 'iosxr':
                napalm_logger.bind(address=self.address, original_driver=self.driver).info("Retrying with NETCONF driver")
                self.driver = 'iosxr_netconf'
                return self.get_interfaces_ip()
            else:
                napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed with XMLCLIError")
                raise
        except Exception as e:
            napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed")
            raise
        finally:
            self.close()

    def get_interfaces(self):
        """Get interfaces with error handling and logging"""
        operation = "get_interfaces"
        napalm_logger.bind(address=self.address).info(f"Starting {operation}")
        
        try:
            self.open()
            result = self.connection.get_interfaces()
            self.close()
            
            interface_count = len(result) if result else 0
            napalm_logger.bind(address=self.address, interface_count=interface_count).success(f"{operation} completed")
            return result
            
        except XMLCLIError as e:
            if self.driver == 'iosxr':
                napalm_logger.bind(address=self.address, original_driver=self.driver).info("Retrying with NETCONF driver")
                self.driver = 'iosxr_netconf'
                return self.get_interfaces()
            else:
                napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed with XMLCLIError")
                raise
        except Exception as e:
            napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed")
            raise
        finally:
            self.close()

    def get_facts(self):
        """Get device facts with error handling and logging"""
        operation = "get_facts"
        napalm_logger.bind(address=self.address).info(f"Starting {operation}")
        
        try:
            self.open()
            result = self.connection.get_facts()
            self.close()
            
            napalm_logger.bind(
                address=self.address,
                hostname=result.get('hostname', 'unknown'),
                vendor=result.get('vendor', 'unknown'),
                model=result.get('model', 'unknown')
            ).success(f"{operation} completed")
            return result
            
        except XMLCLIError as e:
            if self.driver == 'iosxr':
                napalm_logger.bind(address=self.address, original_driver=self.driver).info("Retrying with NETCONF driver")
                self.driver = 'iosxr_netconf'
                return self.get_facts()
            else:
                napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed with XMLCLIError")
                raise
        except Exception as e:
            napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed")
            raise
        finally:
            self.close()

    def connection_test(self):
        """Test connection to device"""
        operation = "connection_test"
        napalm_logger.bind(address=self.address).info(f"Starting {operation}")
        
        try:
            self.open()
            # Use get_interfaces instead of get_facts for problematic IOSXR devices
            self.connection.get_interfaces()
            self.close()
            
            success_msg = f"{self.address} connected successfully"
            napalm_logger.bind(address=self.address).success(f"{operation} passed")
            self.logger.success("Connection test passed")
            
            return (True, success_msg)
            
        except XMLCLIError as e:
            if self.driver == 'iosxr':
                napalm_logger.bind(address=self.address, original_driver=self.driver).info("Retrying connection test with NETCONF driver")
                self.driver = 'iosxr_netconf'
                return self.connection_test()
            else:
                error_msg = f"Connection test failed: {str(e)}"
                napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed with XMLCLIError")
                self.logger.error(e, "Connection test failed")
                return (False, error_msg)
                
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            napalm_logger.bind(address=self.address, error=str(e)).error(f"{operation} failed")
            self.logger.error(e, "Connection test failed")
            return (False, error_msg)
        finally:
            self.close()

    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        if exc_type:
            napalm_logger.bind(
                address=self.address, 
                exception_type=exc_type.__name__,
                error=str(exc_val)
            ).error("Exception in context manager")
