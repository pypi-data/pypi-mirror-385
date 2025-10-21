from netutils.mac import is_valid_mac, mac_to_format

from netbox_network_importer.helper import (
    canonical_interface_name_edited,
    canonical_interface_name_list_edited,
    get_netbox_interface_type,
    vlanconfig_to_list_edited,
)


def convert_interfaces(napalm_interfaces):
    """Convert Genie parsed interfaces to Netbox friendly fields.

    :param genie_interfaces: dictionary of genie parsed interfaces by `show interfaces` command
    :param platform: OS of host device (different OS return returns different genie parsed json)
    """

    converted_result = {}
    """Example of Netbox friendly format
    
    {
        "canonical_interface_name": {
            'enabled': True / False,
            'type': virtual / lag / other,
            'mtu': 1500 / None,
            'description': "Some description" / "",
            'mac_address': "MacAddress" if any
        }
    }
    """

    for name, properties in napalm_interfaces.items():
        canonical_name = canonical_interface_name_edited(name)
        converted_result[canonical_name] = {
            "enabled": properties["is_enabled"],
            "type": get_netbox_interface_type(canonical_name),
            "mtu": properties.get("mtu", None),
            "description": properties.get("description", ""),
        }

        if converted_result[canonical_name]["mtu"] < 1:
            converted_result[canonical_name]["mtu"] = None

        if is_valid_mac(properties.get("mac_address") or ""):
            converted_result[canonical_name]["mac_address"] = mac_to_format(
                properties.get("mac_address"), "MAC_COLON_TWO"
            ).upper()
        else:
            converted_result[canonical_name]["mac_address"] = None

    return converted_result


def convert_lag_interfaces(genie_lag_interfaces, platform="iosxr"):
    """Convert Genie parsed interfaces (lags only) to Netbox friendly fields.

    :param genie_lag_interfaces: dictionary of genie parsed interfaces (lags only) by `show interfaces` command
    :param platform: OS of host device (different OS return returns different genie parsed json)
    """

    converted_result = {}
    """Example of Netbox friendly format
    
    {
        'canonical_interface_lag_name':  ['Etherner1/1', 'Ethernet1/2'], #childrens in canonical names
        'canonical_interface_lag_name' ['Ethernet2/1'] #childrens in canonical names
    }
    """

    if platform == "iosxr":
        for parent_lag, properties in genie_lag_interfaces.items():
            if properties.get("port_channel"):
                if properties.get("port_channel").get("member_count"):
                    if properties.get("port_channel").get("member_count") > 0:
                        converted_result[
                            canonical_interface_name_edited(parent_lag)
                        ] = canonical_interface_name_list_edited(
                            properties.get("port_channel").get("members").keys()
                        )

    elif platform == "iosxe" or platform == "ios":
        for parent_lag, properties in genie_lag_interfaces.items():
            if properties.get("port_channel"):
                if properties.get("port_channel").get("port_channel_member_intfs"):
                    converted_result[canonical_interface_name_edited(parent_lag)] = (
                        canonical_interface_name_list_edited(
                            properties.get("port_channel").get(
                                "port_channel_member_intfs"
                            )
                        )
                    )

    elif platform == "nxos" or platform == "nxos_ssh":
        for parent_lag, properties in genie_lag_interfaces.items():
            if properties.get("port_channel"):
                if properties.get("port_channel").get("port_channel_member_intfs"):
                    converted_result[canonical_interface_name_edited(parent_lag)] = (
                        canonical_interface_name_list_edited(
                            properties.get("port_channel").get(
                                "port_channel_member_intfs"
                            )
                        )
                    )
    else:
        # Platform not yet supported for LAG interface conversion
        raise NotImplementedError(
            f"LAG interface conversion not implemented for platform: {platform}"
        )

    return converted_result


def convert_interfaces_ips(napalm_interfaces_ip, platform="iosxr"):
    """
    Returns all configured IP addresses on all interfaces as a dictionary of dictionaries.
    Keys of the main dictionary represent the name of the interface.
    Values of the main dictionary represent are dictionaries that may consist of two keys
    'ipv4' and 'ipv6' (one, both or none) which are themselves dictionaries with the IP
    addresses as keys.
    Each IP Address dictionary has the following keys:
        * prefix_length (int)
    Example::
        {
            u'FastEthernet8': {
                u'ipv4': {
                    u'10.66.43.169': {
                        'prefix_length': 22
                    }
                }
            },
            u'Loopback555': {
                u'ipv4': {
                    u'192.168.1.1': {
                        'prefix_length': 24
                    }
                },
                u'ipv6': {
                    u'1::1': {
                        'prefix_length': 64
                    },
                    u'2001:DB8:1::1': {
                        'prefix_length': 64
                    },
                    u'2::': {
                        'prefix_length': 64
                    },
                    u'FE80::3': {
                        'prefix_length': u'N/A'
                    }
                }
            },
            u'Tunnel0': {
                u'ipv4': {
                    u'10.63.100.9': {
                        'prefix_length': 24
                    }
                }
            }
        }

    # Extra! Convert all addresses to lower case
    """
    parsed_result = {}

    for ifc, params in napalm_interfaces_ip.items():
        ipv4 = params.get("ipv4", None)
        ipv6 = params.get("ipv6", None)

        # WARNING! - convert all adresses (ipv6) to lower case!!!
        if ipv4:
            lower_ipv4 = dict((k.lower(), v) for k, v in ipv4.items())
        if ipv6:
            lower_ipv6 = dict((k.lower(), v) for k, v in ipv6.items())

        canonical_ifc = canonical_interface_name_edited(ifc)

        if ipv4 or ipv6:
            parsed_result[canonical_ifc] = {}
            ipv4 and parsed_result[canonical_ifc].update({"ipv4": lower_ipv4})
            ipv6 and parsed_result[canonical_ifc].update({"ipv6": lower_ipv6})

    return parsed_result


def convert_interfaces_vlans_iosxr(genie_show_interfaces):
    # Converts subinterfaces to vlans
    # DEPRECATED - will be removed
    """return FORMAT
    {'vlans': {'1': {'interfaces': ['GigabitEthernet0/2/5',
                                    'GigabitEthernet0/2/23'],
                    'shutdown': False,
                    'state': 'active',
                    'vlan_id': '1'},
            '10': {'interfaces': ['GigabitEthernet0/2/0',
                                    'GigabitEthernet0/2/4'],
                    'shutdown': False,
                    'state': 'active',
                    'vlan_id': '10'},
            '2': {'interfaces': [],
                    'shutdown': False,
                    'state': 'unsupport',
                    'vlan_id': '2'}},
    'vlans_interfaces': {'GigabitEthernet0/2/0': {'vlan': '10'},
                        'GigabitEthernet0/2/9': {'vlan': '1'}},
    'vlans_trunks': {}
    }
    """

    RESULT = {"vlans": None, "vlans_interfaces": None, "vlans_trunks": None}
    xr_vlans = {}
    xr_vlans_interfaces = {}
    vlans_trunks = {}

    for interface, properties in genie_show_interfaces.items():
        interface = canonical_interface_name_edited(interface)
        encap1 = properties.get("encapsulations")
        if encap1:
            encap2 = encap1.get("encapsulation")
            if encap2 == "dot1q":
                vid = interface.split(".")[1]
                xr_vlans[vid] = {
                    "interfaces": [interface],
                    "mtu": properties.get("mtu"),
                    "name": f"vlan-{vid}",
                    "shutdown": not properties.get("enabled"),
                    "state": "active",
                    "vlan_id": vid,
                }

                xr_vlans_interfaces[interface] = {"vlan": vid}

    RESULT.update(
        {
            "vlans": xr_vlans,
            "vlans_interfaces": xr_vlans_interfaces,
            "vlans_trunks": vlans_trunks,
        }
    )

    return RESULT


def convert_interfaces_vlans_nxos(show_interface_switchport, show_vlan):
    RESULT = {"vlans": None, "vlans_interfaces": None, "vlans_trunks": None}

    converted_vlans = {}
    if show_vlan.get("vlans"):
        for vid, vlan_params in show_vlan.get("vlans").items():
            converted_vlans[vid] = {
                "vlan_id": vlan_params.get("vlan_id"),
                "name": vlan_params.get("name"),
                "shutdown": vlan_params.get("shutdown"),
                "state": vlan_params.get("state"),
                "interfaces": canonical_interface_name_list_edited(
                    vlan_params.get("interfaces", "")
                ),
            }

    RESULT["vlans"] = converted_vlans

    interfaces = {}
    for ifc_name, values in show_interface_switchport.items():
        can_ifc_name = canonical_interface_name_edited(ifc_name)
        if values["switchport_mode"] == "access" and str(values["access_vlan"]) != 1:
            interfaces[can_ifc_name] = {}
            interfaces[can_ifc_name]["status"] = values["switchport_status"]
            interfaces[can_ifc_name]["name"] = values["access_vlan_mode"]
            interfaces[can_ifc_name]["vlan"] = values["access_vlan"]
        elif values["switchport_mode"] == "trunk":
            interfaces[can_ifc_name] = {}
            interfaces[can_ifc_name]["status"] = values["switchport_status"]
            interfaces[can_ifc_name]["name"] = values["access_vlan_mode"]
            interfaces[can_ifc_name]["vlan"] = "trunk"

    RESULT["vlans_interfaces"] = interfaces

    trunks = {}
    for ifc_name, values in show_interface_switchport.items():
        can_ifc_name = canonical_interface_name_edited(ifc_name)
        if values["switchport_mode"] == "trunk" and values.get("trunk_vlans"):
            trunks[can_ifc_name] = {}
            trunks[can_ifc_name]["encapsulation"] = values[
                "admin_priv_vlan_trunk_encapsulation"
            ]
            trunks[can_ifc_name]["native_vlan"] = values["native_vlan"]
            trunks[can_ifc_name]["status"] = values["switchport_status"]
            trunks[can_ifc_name]["name"] = can_ifc_name
            trunks[can_ifc_name]["vlan_list"] = vlanconfig_to_list_edited(
                values.get("trunk_vlans")
            )

    RESULT["vlans_trunks"] = trunks
    return RESULT


def convert_interfaces_vlans_iosxe(vlans, vlans_interfaces, trunks):
    """return FORMAT
    {'vlans': {'1': {'interfaces': ['GigabitEthernet0/2/5',
                                    'GigabitEthernet0/2/23'],
                    'shutdown': False,
                    'state': 'active',
                    'vlan_id': '1'},
            '10': {'interfaces': ['GigabitEthernet0/2/0',
                                    'GigabitEthernet0/2/4'],
                    'shutdown': False,
                    'state': 'active',
                    'vlan_id': '10'},
            '2': {'interfaces': [],
                    'shutdown': False,
                    'state': 'unsupport',
                    'vlan_id': '2'}},
    'vlans_interfaces': {'GigabitEthernet0/2/0': {'status': 'connected','vlan': '10'},
                        'GigabitEthernet0/2/16': {'status': 'connected','vlan': 'trunk'},
                        'GigabitEthernet0/2/17': {'status': 'notconnect','vlan': '1'},
                        'GigabitEthernet0/2/9': {'status': 'notconnect','vlan': '1'}},
    'vlans_trunks': {'GigabitEthernet0/2/16': {'encapsulation': '802.1q',
                                                'mode': 'on',
                                                'name': 'GigabitEthernet0/2/16',
                                                'status': 'trunking',
                                                'vlan_list': [1, 2, 10, 11, 12]}}}
    """

    converted_vlans = {}
    if vlans.get("vlans"):
        for vid, vlan_params in vlans.get("vlans").items():
            converted_vlans[vid] = {
                "vlan_id": vlan_params.get("vlan_id"),
                "name": vlan_params.get("name"),
                "shutdown": vlan_params.get("shutdown"),
                "state": vlan_params.get("state"),
                "interfaces": canonical_interface_name_list_edited(
                    vlan_params.get("interfaces", "")
                ),
            }

    converted_vlans_interfaces = {}
    if vlans_interfaces.get("interfaces"):
        for ifc, params in vlans_interfaces.get("interfaces").items():
            ifc_name = canonical_interface_name_edited(ifc)
            converted_vlans_interfaces[ifc_name] = {
                "status": params.get("status"),
                "vlan": params.get("vlan"),
            }

    converted_trunks = {}
    if trunks.get("interface"):
        for ifc, params in trunks.get("interface").items():
            ifc_name = canonical_interface_name_edited(ifc)
            converted_trunks[ifc_name] = {
                "name": params.get("name"),
                "mode": params.get("mode"),
                "encapsulation": params.get("encapsulation"),
                "status": params.get("status"),
                "vlan_list": vlanconfig_to_list_edited(
                    params.get("vlans_allowed_active_in_mgmt_domain")
                ),
            }

    return {
        "vlans": converted_vlans,
        "vlans_interfaces": converted_vlans_interfaces,
        "vlans_trunks": converted_trunks,
    }


def convert_bandwidth_interfaces(genie_interfaces, platform="iosxr"):
    converted_result = {}
    """Example of Netbox friendly format
    
    {
        'canonical_interface_name':  10000 #bandwidth
        'canonical_interface_name' 110000000000 #bandwidth
    }
    """

    for ifc_name, properties in genie_interfaces.items():
        canonical_ifc_name = canonical_interface_name_edited(ifc_name)
        if platform in ["nxos", "nxos_ssh"]:
            pass
        elif platform in ["iosxr"]:
            bandwidth = properties.get("bandwidth", None)
            converted_result[canonical_ifc_name] = bandwidth
        elif platform in ["iosxe", "ios"]:
            bandwidth = properties.get("bandwidth", None)
            converted_result[canonical_ifc_name] = bandwidth
        else:
            raise NotImplementedError
        # TODO Other platforms

    return converted_result
