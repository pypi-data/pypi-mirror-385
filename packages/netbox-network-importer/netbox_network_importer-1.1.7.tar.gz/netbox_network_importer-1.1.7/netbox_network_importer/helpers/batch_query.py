"""
Utilities for batch querying NetBox to reduce API calls and improve performance.
"""

from typing import Any, Dict

from netbox_network_importer.helper import canonical_interface_name_edited


class NetboxBatchQuery:
    """
    Utility class for performing batch queries to reduce API calls.
    """

    def __init__(self, nb_connection):
        """
        Initialize with NetBox connection.

        Args:
            nb_connection: PyNetbox connection object
        """
        self.nb = nb_connection
        self._interface_cache = {}
        self._ip_cache = {}
        self._device_cache = {}
        self._vlan_cache = {}  # Cache for VLAN lookups

    def get_device_interfaces(self, device_id: int) -> Dict[str, Any]:
        """
        Get all interfaces for a device with caching.

        Args:
            device_id: NetBox device ID

        Returns:
            Dictionary mapping canonical interface names to NetBox interface objects
        """
        if device_id not in self._interface_cache:
            interfaces = self.nb.dcim.interfaces.filter(device_id=device_id)
            self._interface_cache[device_id] = {
                canonical_interface_name_edited(ifc.name): ifc for ifc in interfaces
            }
        return self._interface_cache[device_id]

    def get_device_ip_addresses(self, device_id: int) -> Dict[int, Dict[str, Any]]:
        """
        Get all IP addresses for a device with caching, organized by interface.

        Args:
            device_id: NetBox device ID

        Returns:
            Dictionary mapping interface_id to {ip_address: ip_object}
        """
        if device_id not in self._ip_cache:
            # NetBox 4.4.4 changed how generic relation filters work
            # Use the new app.model string format instead of object_type ID
            all_device_ips = self.nb.ipam.ip_addresses.filter(
                assigned_object_type="dcim.interface", device_id=device_id
            )

            # Create a mapping of interface_id -> {ip_address: ip_object}
            device_ips_by_interface = {}
            for ip_obj in all_device_ips:
                interface_id = ip_obj.assigned_object_id
                if interface_id not in device_ips_by_interface:
                    device_ips_by_interface[interface_id] = {}
                device_ips_by_interface[interface_id][ip_obj.address] = ip_obj

            self._ip_cache[device_id] = device_ips_by_interface

        return self._ip_cache[device_id]

    def get_lag_interfaces(self, device_id: int) -> Dict[str, Any]:
        """
        Get all LAG interfaces for a device.

        Args:
            device_id: NetBox device ID

        Returns:
            Dictionary mapping canonical interface names to NetBox LAG interface objects
        """
        lag_interfaces = self.nb.dcim.interfaces.filter(device_id=device_id, type="lag")
        return {
            canonical_interface_name_edited(ifc.name): ifc for ifc in lag_interfaces
        }

    def get_lag_children(self, device_id: int) -> Dict[str, Any]:
        """
        Get all LAG child interfaces for a device.

        Args:
            device_id: NetBox device ID

        Returns:
            Dictionary mapping canonical interface names to NetBox child interface objects
        """
        lag_children = self.nb.dcim.interfaces.filter(
            device_id=device_id, lag_id__n="null"
        )
        return {canonical_interface_name_edited(ifc.name): ifc for ifc in lag_children}

    def get_interfaces_with_vlans(self, device_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Get all interfaces with VLAN assignments for a device.

        Args:
            device_id: NetBox device ID

        Returns:
            Dictionary with interface names as keys and VLAN assignments as values
        """
        tagged = self._get_tagged_vlans_interfaces(device_id)
        untagged = self._get_untagged_vlan_interfaces(device_id)

        merged_dict = {}

        # Merge tagged VLANs
        for ifc, vlans in tagged.items():
            if ifc not in merged_dict:
                merged_dict[ifc] = {}
            merged_dict[ifc].update(vlans)

        # Merge untagged VLANs
        for ifc, vlan in untagged.items():
            if ifc not in merged_dict:
                merged_dict[ifc] = {}
            merged_dict[ifc].update(vlan)

        return merged_dict

    def _get_tagged_vlans_interfaces(self, device_id: int) -> Dict[str, Dict[str, Any]]:
        """Get interfaces with tagged VLANs."""
        return {
            ifc.name: {
                "tagged_vlans": {
                    (vlan.vid, vlan.name): vlan for vlan in ifc.tagged_vlans
                }
            }
            for ifc in self.nb.dcim.interfaces.filter(device_id=device_id)
            if ifc.tagged_vlans
        }

    def _get_untagged_vlan_interfaces(
        self, device_id: int
    ) -> Dict[str, Dict[str, Any]]:
        """Get interfaces with untagged VLANs."""
        return {
            ifc.name: {"untagged_vlan": ifc.untagged_vlan}
            for ifc in self.nb.dcim.interfaces.filter(device_id=device_id)
            if ifc.untagged_vlan
        }

    def get_or_create_vlan(self, vid: str, vname: str, site_id: str = "null"):
        """
        Get or create a VLAN with caching to avoid repeated API calls.

        Args:
            vid: VLAN ID as string
            vname: VLAN name
            site_id: Site ID (default: "null")

        Returns:
            Tuple of (NetBox VLAN object or None, created_flag: bool)
            created_flag is True if VLAN was newly created, False if it already existed
        """
        cache_key = f"{vid}:{vname}:{site_id}"

        # Check cache first - if in cache, it means it already existed
        if cache_key in self._vlan_cache:
            return self._vlan_cache[cache_key], False

        # Try to find existing VLAN
        try:
            vlan = self.nb.ipam.vlans.get(vid=vid, name=vname, site_id=site_id)
            if vlan:
                self._vlan_cache[cache_key] = vlan
                return vlan, False
        except (LookupError, AttributeError, ValueError):
            # If lookup fails, continue to creation
            pass

        # Create VLAN if not found
        try:
            create_params = {"vid": vid, "name": vname}
            if site_id != "null":
                create_params["site"] = site_id
            created_vlan = self.nb.ipam.vlans.create(create_params)
            if created_vlan:
                self._vlan_cache[cache_key] = created_vlan
                return created_vlan, True
        except Exception:
            # Cache None to avoid repeated failed attempts
            self._vlan_cache[cache_key] = None

        return None, False

    def clear_cache(self, device_id: int = None):
        """
        Clear cached data for a device or all devices.

        Args:
            device_id: Specific device to clear cache for, or None for all devices
        """
        if device_id is None:
            self._interface_cache.clear()
            self._ip_cache.clear()
            self._device_cache.clear()
            self._vlan_cache.clear()  # Clear VLAN cache too
        else:
            self._interface_cache.pop(device_id, None)
            self._ip_cache.pop(device_id, None)
            self._device_cache.pop(device_id, None)
            # Note: VLAN cache is global, not device-specific
