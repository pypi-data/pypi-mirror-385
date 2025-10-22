# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "GPUBaremetalClusterCreateParams",
    "ServersSettings",
    "ServersSettingsInterface",
    "ServersSettingsInterfaceExternalInterfaceInputSerializer",
    "ServersSettingsInterfaceSubnetInterfaceInputSerializer",
    "ServersSettingsInterfaceSubnetInterfaceInputSerializerFloatingIP",
    "ServersSettingsInterfaceAnySubnetInterfaceInputSerializer",
    "ServersSettingsInterfaceAnySubnetInterfaceInputSerializerFloatingIP",
    "ServersSettingsCredentials",
    "ServersSettingsSecurityGroup",
]


class GPUBaremetalClusterCreateParams(TypedDict, total=False):
    project_id: int
    """Project ID"""

    region_id: int
    """Region ID"""

    flavor: Required[str]
    """Cluster flavor ID"""

    image_id: Required[str]
    """System image ID"""

    name: Required[str]
    """Cluster name"""

    servers_count: Required[int]
    """Number of servers in the cluster"""

    servers_settings: Required[ServersSettings]
    """Configuration settings for the servers in the cluster"""

    tags: Dict[str, str]
    """Key-value tags to associate with the resource.

    A tag is a key-value pair that can be associated with a resource, enabling
    efficient filtering and grouping for better organization and management. Some
    tags are read-only and cannot be modified by the user. Tags are also integrated
    with cost reports, allowing cost data to be filtered based on tag keys or
    values.
    """


class ServersSettingsInterfaceExternalInterfaceInputSerializer(TypedDict, total=False):
    type: Required[Literal["external"]]

    ip_family: Literal["dual", "ipv4", "ipv6"]
    """Which subnets should be selected: IPv4, IPv6, or use dual stack."""

    name: str
    """Interface name"""


class ServersSettingsInterfaceSubnetInterfaceInputSerializerFloatingIP(TypedDict, total=False):
    source: Required[Literal["new"]]


class ServersSettingsInterfaceSubnetInterfaceInputSerializer(TypedDict, total=False):
    network_id: Required[str]
    """Network ID the subnet belongs to. Port will be plugged in this network"""

    subnet_id: Required[str]
    """Port is assigned an IP address from this subnet"""

    type: Required[Literal["subnet"]]

    floating_ip: ServersSettingsInterfaceSubnetInterfaceInputSerializerFloatingIP
    """Floating IP config for this subnet attachment"""

    name: str
    """Interface name"""


class ServersSettingsInterfaceAnySubnetInterfaceInputSerializerFloatingIP(TypedDict, total=False):
    source: Required[Literal["new"]]


class ServersSettingsInterfaceAnySubnetInterfaceInputSerializer(TypedDict, total=False):
    network_id: Required[str]
    """Network ID the subnet belongs to. Port will be plugged in this network"""

    type: Required[Literal["any_subnet"]]

    floating_ip: ServersSettingsInterfaceAnySubnetInterfaceInputSerializerFloatingIP
    """Floating IP config for this subnet attachment"""

    ip_family: Literal["dual", "ipv4", "ipv6"]
    """Which subnets should be selected: IPv4, IPv6, or use dual stack"""

    name: str
    """Interface name"""


ServersSettingsInterface: TypeAlias = Union[
    ServersSettingsInterfaceExternalInterfaceInputSerializer,
    ServersSettingsInterfaceSubnetInterfaceInputSerializer,
    ServersSettingsInterfaceAnySubnetInterfaceInputSerializer,
]


class ServersSettingsCredentials(TypedDict, total=False):
    password: str
    """Used to set the password for the specified 'username' on Linux instances.

    If 'username' is not provided, the password is applied to the default user of
    the image. Mutually exclusive with '`user_data`' - only one can be specified.
    """

    ssh_key_name: str
    """
    Specifies the name of the SSH keypair, created via the
    [/v1/`ssh_keys` endpoint](/docs/api-reference/cloud/ssh-keys/add-or-generate-ssh-key).
    """

    username: str
    """The 'username' and 'password' fields create a new user on the system"""


class ServersSettingsSecurityGroup(TypedDict, total=False):
    id: Required[str]
    """Resource ID"""


class ServersSettings(TypedDict, total=False):
    interfaces: Required[Iterable[ServersSettingsInterface]]
    """Subnet IPs and floating IPs"""

    credentials: ServersSettingsCredentials
    """Optional server access credentials"""

    security_groups: Iterable[ServersSettingsSecurityGroup]
    """List of security groups UUIDs"""

    user_data: str
    """Optional custom user data (Base64-encoded)"""
