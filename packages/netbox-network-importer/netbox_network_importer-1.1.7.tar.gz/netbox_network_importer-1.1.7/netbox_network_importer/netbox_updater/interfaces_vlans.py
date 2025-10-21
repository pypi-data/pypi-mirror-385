from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.helpers import (
    NetboxBatchQuery,
    NetboxResultFactory,
    create_ignored_interface_result,
    handle_netbox_operation,
    should_skip_interface,
)
from netbox_network_importer.results.results import Action


def process_interfaces_vlans(host, parsed_data) -> list:
    RESULTS = []  # list of NetboxResult

    # Init connection to Netbox via PyNetbox
    netbox = Netbox.connect()

    # find the device instance in netbox
    netbox_device = netbox.dcim.devices.get(host.data["id"])

    # Use batch query for better performance
    batch_query = NetboxBatchQuery(netbox)
    netbox_interfaces_dict = batch_query.get_device_interfaces(netbox_device.id)

    # INIT Dictionary of stored vlans in NETBOX
    # if configured vlan is found, it will be removed from dict
    # vlans left in dictionary will be removed at the end
    netbox_interfaces_with_vlan = get_interfaces_with_vlan(
        netbox_conn=netbox, device_id=netbox_device.id
    )

    vlans_interfaces = parsed_data["vlans_interfaces"]
    vlans_trunks = parsed_data["vlans_trunks"]
    vlans = parsed_data["vlans"]

    for interface_name, ifc_vlan_data in vlans_interfaces.items():
        netbox_ifc = netbox_interfaces_dict.get(interface_name, None)

        # skip if interface is not found in netbox
        if not netbox_ifc:
            RESULTS.append(
                NetboxResultFactory.create_not_found(
                    name=f"Interface {interface_name}",
                    context="check interface configuration on device",
                    action=Action.LOOKUP,
                    diff=ifc_vlan_data,
                )
            )
            continue

        # Skip IGNORED interfaces
        if should_skip_interface(netbox_ifc):
            RESULTS.append(
                create_ignored_interface_result(netbox_ifc.name, Action.LOOKUP)
            )
            continue

        # Assign multiple tagged vlan to interface
        if ifc_vlan_data["vlan"] == "trunk":
            netbox_vlans = []

            # if interface is not found in configured TRUNKS
            if not vlans_trunks.get(interface_name):
                if netbox_ifc.lag is not None:
                    RESULTS.append(
                        NetboxResultFactory.create_no_change(
                            name=f"Device: {host.name} Interface: {interface_name}",
                            action=Action.LOOKUP,
                            message=f"Device: {host.name} Interface: {interface_name} mode: trunk. Part of port channel",
                        )
                    )
                    continue
                elif (
                    ifc_vlan_data.get("status", None) == "disabled"
                    or ifc_vlan_data.get("status", None) == "notconnect"
                ):
                    continue
                else:
                    # RESULTS.append(
                    #    NetboxResult(
                    #        result=f"Device: {host.name} Interface: {interface_name} mode: trunk. Unable to parse trunks from device",
                    #        status=Status.CHECK_MANUALLY,
                    #        action=Action.LOOKUP,
                    #        diff={"vlan_data": ifc_vlan_data,
                    #              "trunks": vlans_trunks}
                    #    )
                    # )
                    continue

            vlans_vids_allowed_on_trunk = vlans_trunks[interface_name]["vlan_list"]

            # Go through each vlan vid in trunk mode and assing it
            for vid_integer in vlans_vids_allowed_on_trunk:
                # convert vlan_vid int to string
                vid = str(vid_integer)

                # TODO: what if name does not exists
                vname = vlans.get(vid, {}).get("name")
                if not vname:
                    # TODO: Ignore vid;s which does not have crated VLANs
                    # RESULTS.append(
                    #    NetboxResult(
                    #        result=f"Device: {host.name} Interface: {interface_name} has configured VLAN ID: {vid}. But VLAN does not exists on Device.",
                    #        status=Status.CHECK_MANUALLY,
                    #        action=Action.LOOKUP,
                    #        diff={"host": host.name, "ifc": interface_name,
                    #              "vid": vid, "vlan_vid_data": vlans.get(vid, None)}
                    #    )
                    # )
                    continue

                # Skip VID == 1, skip 999?
                if vid == "1":
                    continue

                try:
                    RESULTS.append(
                        create_vlan(
                            vname=vname,
                            vid=vid,
                            netbox_conn=netbox,
                            batch_query=batch_query,
                        )
                    )
                    # Use batch query to get VLAN instead of direct API call
                    netbox_vlan, was_created = batch_query.get_or_create_vlan(
                        vid, vname
                    )

                    if netbox_vlan:
                        netbox_vlans.append(netbox_vlan)
                    else:
                        # VLAN creation/lookup failed
                        RESULTS.append(
                            NetboxResultFactory.create_failed(
                                name=f"VLAN {vname} {vid}",
                                error="Failed to get or create VLAN",
                                action=Action.LOOKUP,
                            )
                        )
                        continue
                except Exception as e:
                    RESULTS.append(
                        NetboxResultFactory.create_exception(
                            name=f"VLAN {vname} {vid}",
                            exception=e,
                            action=Action.LOOKUP,
                            context="Unable to get/create VLAN - Processing VLANs is aborted",
                        )
                    )
                    # end processing
                    return RESULTS

                # remove vlan from already configured vlans on interface (if exists)
                # vlans left in alredy configured vlans will be removed
                netbox_interfaces_with_vlan = remove_configured_vlan(
                    configured_vlan=netbox_interfaces_with_vlan,
                    ifc_name=netbox_ifc.name,
                    vid=netbox_vlan.vid,
                    vname=vname,
                    vlan_type="tagged_vlans",
                )

            # assign VLAN to interface
            RESULTS.append(
                add_tagged_vlans_to_interface(
                    netbox_ifc=netbox_ifc, netbox_vlans=netbox_vlans
                )
            )

        elif ifc_vlan_data["vlan"] == "routed":
            if (
                ifc_vlan_data.get("status", None) == "disabled"
                or ifc_vlan_data.get("status", None) == "notconnect"
            ):
                continue
            else:
                RESULTS.append(
                    NetboxResultFactory.create_no_change(
                        name=f"{netbox_ifc.name} - Routed interface",
                        action=Action.LOOKUP,
                        context="SKIPPING",
                    )
                )
                continue

        elif ifc_vlan_data["vlan"] in ["unassigned", "unassigne"]:
            continue

        # Assign untagged vlan to interface
        else:
            vid = str(ifc_vlan_data["vlan"])
            vname = vlans.get(vid, {}).get("name")
            if not vname:
                RESULTS.append(
                    NetboxResultFactory.create_check_manually(
                        name=f"Interface {interface_name}",
                        reason=f"VLAN ID: {vid} does not exist on device",
                        action=Action.LOOKUP,
                        diff={
                            "host": host.name,
                            "ifc": interface_name,
                            "vid": vid,
                            "vlan_vid_data": vlans.get(vid, None),
                        },
                    )
                )
                continue

            if vid == "1":
                continue

            try:
                RESULTS.append(
                    create_vlan(
                        vname=vname,
                        vid=vid,
                        netbox_conn=netbox,
                        batch_query=batch_query,
                    )
                )
                # Use batch query to get VLAN instead of direct API call
                netbox_vlan, was_created = batch_query.get_or_create_vlan(vid, vname)

                if not netbox_vlan:
                    RESULTS.append(
                        NetboxResultFactory.create_failed(
                            name=f"VLAN {vname} {vid}",
                            error="Failed to get or create VLAN",
                            action=Action.LOOKUP,
                        )
                    )
                    return RESULTS
            except Exception as e:
                RESULTS.append(
                    NetboxResultFactory.create_exception(
                        name=f"VLAN {vname} {vid}",
                        exception=e,
                        action=Action.LOOKUP,
                        context="Unable to get/create VLAN - Processing VLANs is aborted",
                    )
                )
                # end processing
                return RESULTS

            # add vlan to interface
            RESULTS.append(
                add_untagged_vlan_to_interface(
                    netbox_ifc=netbox_ifc, netbox_vlan=netbox_vlan
                )
            )

            # remove vlan from dictionary of already exisitng vlans in netbox (if exists)
            netbox_interfaces_with_vlan = remove_configured_vlan(
                configured_vlan=netbox_interfaces_with_vlan,
                ifc_name=netbox_ifc.name,
                vid=netbox_vlan.vid,
                vname=vname,
                vlan_type="untagged_vlan",
            )

    # REMOVE vlan from interfaces which are not configured anymore
    # all vlans left in netbox_interfaces_with_vlan
    RESULTS.extend(
        delete_netbox_obsolete_vlans(
            vlans_to_remove=netbox_interfaces_with_vlan,
            netbox_device=netbox_device,
            netbox=netbox,
            netbox_interfaces_dict=netbox_interfaces_dict,
        )
    )
    return RESULTS


def add_tagged_vlans_to_interface(netbox_ifc, netbox_vlans):
    @handle_netbox_operation("Tagged VLANs assignment", Action.CREATE)
    def _add_tagged_vlans(interface, vlans):
        before = get_changes_tagged_vlans(interface)

        for netbox_vlan in vlans:
            if netbox_vlan not in interface.tagged_vlans:
                interface.mode = "tagged"
                interface.tagged_vlans.append(netbox_vlan)

        after = get_changes_tagged_vlans(interface)
        if interface.save():
            return NetboxResultFactory.create_update_result(
                name=f"{interface.name} - Tagged VLANs",
                before=before,
                after=after,
            )
        else:
            return NetboxResultFactory.create_no_change(
                name=f"{interface.name} - Tagged VLANs",
                action=Action.CREATE,
            )

    return _add_tagged_vlans(netbox_ifc, netbox_vlans)


def remove_tagged_vlans_from_interface(netbox_vlans, netbox_ifc):
    @handle_netbox_operation("Tagged VLANs removal", Action.DELETE)
    def _remove_tagged_vlans(vlans_dict, interface):
        for identifier, nb_vlan in vlans_dict.items():
            if nb_vlan in interface.tagged_vlans:
                interface.tagged_vlans.remove(nb_vlan)

        if not interface.untagged_vlan and not interface.tagged_vlans:
            interface.mode = ""

        if interface.save():
            # Reload interface to get updated state
            interface = interface.api.dcim.interfaces.get(interface.id)
            return NetboxResultFactory.create_success(
                name=f"{interface.name} - Tagged VLANs removed",
                action=Action.DELETE,
                diff={
                    "remove": [
                        {"vid": vlan[0], "name": vlan[1]}
                        for vlan in vlans_dict.values()
                    ]
                },
            )
        else:
            return NetboxResultFactory.create_failed(
                name=f"{interface.name} - Tagged VLANs",
                error="Unable to remove tagged VLANs",
                action=Action.DELETE,
            )

    return _remove_tagged_vlans(netbox_vlans, netbox_ifc)


def add_untagged_vlan_to_interface(netbox_ifc, netbox_vlan):
    if not netbox_vlan:
        return NetboxResultFactory.create_failed(
            name=f"{netbox_ifc.name} - Untagged VLAN",
            error="VLAN not found in netbox",
            action=Action.LOOKUP,
        )

    @handle_netbox_operation("Untagged VLAN assignment", Action.CREATE)
    def _add_untagged_vlan(interface, vlan):
        before = get_changes_untagged_vlan(interface)
        interface.mode = "access"
        interface.untagged_vlan = vlan

        after = get_changes_untagged_vlan(interface)
        if interface.save():
            return NetboxResultFactory.create_update_result(
                name=f"{interface.name} - Untagged VLAN",
                before=before,
                after=after,
            )
        else:
            return NetboxResultFactory.create_no_change(
                name=f"{interface.name} - Untagged VLAN",
                action=Action.CREATE,
            )

    return _add_untagged_vlan(netbox_ifc, netbox_vlan)


def remove_untagged_vlan_from_interface(netbox_vlan, netbox_ifc):
    @handle_netbox_operation("Untagged VLAN removal", Action.DELETE)
    def _remove_untagged_vlan(vlan, interface):
        before = get_changes_untagged_vlan(interface)

        if interface.untagged_vlan == vlan:
            interface.untagged_vlan = None
            if not interface.untagged_vlan and not interface.tagged_vlans:
                interface.mode = None

            if interface.save():
                reload_ifc = interface.api.dcim.interfaces.get(interface.id)
                after = get_changes_untagged_vlan(reload_ifc)

                return NetboxResultFactory.create_update_result(
                    name=f"{interface.name} - Untagged VLAN removed",
                    before=before,
                    after=after,
                )
            else:
                return NetboxResultFactory.create_failed(
                    name=f"{interface.name} - Untagged VLAN",
                    error="could not be removed",
                    action=Action.DELETE,
                )
        else:
            return NetboxResultFactory.create_no_change(
                name=f"{interface.name} - Untagged VLAN",
                action=Action.UPDATE,
            )

    return _remove_untagged_vlan(netbox_vlan, netbox_ifc)


def create_vlan(vname, vid, netbox_conn, batch_query=None):
    """
    Create or get VLAN using batch query cache to avoid repeated API calls.

    Args:
        vname: VLAN name
        vid: VLAN ID
        netbox_conn: NetBox connection
        batch_query: NetboxBatchQuery instance for caching (optional)

    Returns:
        NetboxResult indicating success, failure, or no change
    """

    @handle_netbox_operation("VLAN creation", Action.CREATE)
    def _create_vlan(vlan_name, vlan_id, nb_conn, batch_q=None):
        # Use batch query cache if available
        if batch_q:
            vlan, was_created = batch_q.get_or_create_vlan(vlan_id, vlan_name)
            if vlan:
                if was_created:
                    return NetboxResultFactory.create_success(
                        name=f"VLAN ID: {vlan_id} Name: {vlan_name}",
                        action=Action.CREATE,
                        diff={"vid": vlan_id, "name": vlan_name},
                    )
                else:
                    return NetboxResultFactory.create_no_change(
                        name=f"VLAN ID: {vlan_id} Name: {vlan_name}",
                        action=Action.CREATE,
                        message="VLAN already exists",
                    )
            else:
                return NetboxResultFactory.create_failed(
                    name=f"VLAN ID: {vlan_id} Name: {vlan_name}",
                    error="Unable to create or find VLAN",
                    action=Action.CREATE,
                )

        # Fallback to original logic if no batch query
        # First try to find existing VLAN
        try:
            nb_vlan = nb_conn.ipam.vlans.get(
                vid=vlan_id, name=vlan_name, site_id="null"
            )
            if nb_vlan:
                return NetboxResultFactory.create_no_change(
                    name=f"VLAN ID: {vlan_id} Name: {vlan_name}",
                    action=Action.CREATE,
                    message="VLAN already exists",
                )
        except (LookupError, AttributeError, ValueError):
            # If lookup fails due to not found or invalid parameters, continue with creation attempt
            pass

        # Try to create the VLAN
        created_vlan = nb_conn.ipam.vlans.create({"vid": vlan_id, "name": vlan_name})
        if created_vlan:
            return NetboxResultFactory.create_success(
                name=f"VLAN ID: {vlan_id} Name: {vlan_name}",
                action=Action.CREATE,
                diff={"vid": vlan_id, "name": vlan_name},
            )
        else:
            return NetboxResultFactory.create_failed(
                name=f"VLAN ID: {vlan_id} Name: {vlan_name}",
                error="Unable to create",
                action=Action.CREATE,
            )

    return _create_vlan(vname, vid, netbox_conn, batch_query)


def delete_netbox_obsolete_vlans(
    vlans_to_remove, netbox_device, netbox, netbox_interfaces_dict
):
    RESULTS = []
    for ifc, type_vlans in vlans_to_remove.items():
        nb_ifc = netbox_interfaces_dict.get(ifc, None)

        # Skip if interface not found
        if not nb_ifc:
            continue

        # Skip IGNORED interfaces
        if should_skip_interface(nb_ifc):
            RESULTS.append(create_ignored_interface_result(nb_ifc.name, Action.DELETE))
            continue

        if type_vlans.get("untagged_vlan"):
            nb_vlan = type_vlans.get("untagged_vlan")
            RESULTS.append(remove_untagged_vlan_from_interface(nb_vlan, nb_ifc))

        if type_vlans.get("tagged_vlans"):
            tagged_vlans = type_vlans.get("tagged_vlans")
            # Remove all tagged_vlans at once
            RESULTS.append(remove_tagged_vlans_from_interface(tagged_vlans, nb_ifc))

    return RESULTS


def remove_configured_vlan(configured_vlan, ifc_name, vid, vname, vlan_type):
    if vlan_type == "untagged_vlan":
        if configured_vlan.get(ifc_name):
            if configured_vlan[ifc_name].get(vlan_type):
                if configured_vlan[ifc_name][vlan_type].vid == vid:
                    configured_vlan[ifc_name].pop(vlan_type)

    if vlan_type == "tagged_vlans":
        if configured_vlan.get(ifc_name):
            if configured_vlan[ifc_name].get(vlan_type):
                configured_vlan[ifc_name][vlan_type].pop((vid, vname), None)

    return configured_vlan


def get_interfaces_with_vlan(netbox_conn, device_id):
    tagged = get_tagged_vlans_interfaces(netbox_conn, device_id)
    untagged = get_untagged_vlan_interfaces(netbox_conn, device_id)

    merged_dict = {}

    for ifc, vlans in tagged.items():
        if merged_dict.get(ifc, None):
            merged_dict[ifc].update(vlans)
        else:
            merged_dict[ifc] = vlans

    for ifc, vlan in untagged.items():
        if merged_dict.get(ifc, None):
            merged_dict[ifc].update(vlan)
        else:
            merged_dict[ifc] = vlan

    return merged_dict


def get_tagged_vlans_interfaces(netbox_conn, device_id):
    """return FORMAT
    {'GigabitEthernet0/2/16': {'tagged_vlans': {(1, 'default'): PYNETBOX_OBJECT,
                                        (12, 'dwdm-T6'): PYNETBOX_OBJECT}}
    """
    res = {
        ifc.name: {
            "tagged_vlans": {
                (vlan.vid, vlan.name): vlan
                for vlan in [vlan for vlan in ifc.tagged_vlans]
            }
        }
        for ifc in netbox_conn.dcim.interfaces.filter(device_id=device_id)
        if ifc.tagged_vlans
    }

    return res


def get_untagged_vlan_interfaces(netbox_conn, device_id):
    res = {
        ifc.name: {"untagged_vlan": ifc.untagged_vlan}
        for ifc in netbox_conn.dcim.interfaces.filter(device_id=device_id)
        if ifc.untagged_vlan
    }

    return res


def get_changes_tagged_vlans(netbox_ifc):
    # return {vlan.vid: vlan.name for vlan in netbox_ifc.tagged_vlans}
    return [{"name": vlan.name, "vid": vlan.vid} for vlan in netbox_ifc.tagged_vlans]


def get_changes_untagged_vlan(netbox_ifc):
    if netbox_ifc.untagged_vlan:
        return {
            "vid": netbox_ifc.untagged_vlan.vid,
            "name": netbox_ifc.untagged_vlan.name,
        }
    else:
        return {}
