# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from .tag import Tag
from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "GPUBaremetalCluster",
    "ServersSettings",
    "ServersSettingsInterface",
    "ServersSettingsInterfaceExternalInterfaceOutputSerializer",
    "ServersSettingsInterfaceSubnetInterfaceOutputSerializer",
    "ServersSettingsInterfaceSubnetInterfaceOutputSerializerFloatingIP",
    "ServersSettingsInterfaceAnySubnetInterfaceOutputSerializer",
    "ServersSettingsInterfaceAnySubnetInterfaceOutputSerializerFloatingIP",
    "ServersSettingsSecurityGroup",
]


class ServersSettingsInterfaceExternalInterfaceOutputSerializer(BaseModel):
    ip_family: Literal["dual", "ipv4", "ipv6"]
    """Which subnets should be selected: IPv4, IPv6, or use dual stack."""

    name: Optional[str] = None
    """Interface name"""

    type: Literal["external"]


class ServersSettingsInterfaceSubnetInterfaceOutputSerializerFloatingIP(BaseModel):
    source: Literal["new"]


class ServersSettingsInterfaceSubnetInterfaceOutputSerializer(BaseModel):
    floating_ip: Optional[ServersSettingsInterfaceSubnetInterfaceOutputSerializerFloatingIP] = None
    """Floating IP config for this subnet attachment"""

    name: Optional[str] = None
    """Interface name"""

    network_id: str
    """Network ID the subnet belongs to. Port will be plugged in this network"""

    subnet_id: str
    """Port is assigned an IP address from this subnet"""

    type: Literal["subnet"]


class ServersSettingsInterfaceAnySubnetInterfaceOutputSerializerFloatingIP(BaseModel):
    source: Literal["new"]


class ServersSettingsInterfaceAnySubnetInterfaceOutputSerializer(BaseModel):
    floating_ip: Optional[ServersSettingsInterfaceAnySubnetInterfaceOutputSerializerFloatingIP] = None
    """Floating IP config for this subnet attachment"""

    ip_address: Optional[str] = None
    """Fixed IP address"""

    ip_family: Literal["dual", "ipv4", "ipv6"]
    """Which subnets should be selected: IPv4, IPv6, or use dual stack"""

    name: Optional[str] = None
    """Interface name"""

    network_id: str
    """Network ID the subnet belongs to. Port will be plugged in this network"""

    type: Literal["any_subnet"]


ServersSettingsInterface: TypeAlias = Annotated[
    Union[
        ServersSettingsInterfaceExternalInterfaceOutputSerializer,
        ServersSettingsInterfaceSubnetInterfaceOutputSerializer,
        ServersSettingsInterfaceAnySubnetInterfaceOutputSerializer,
    ],
    PropertyInfo(discriminator="type"),
]


class ServersSettingsSecurityGroup(BaseModel):
    name: str
    """Name."""


class ServersSettings(BaseModel):
    interfaces: List[ServersSettingsInterface]

    security_groups: List[ServersSettingsSecurityGroup]
    """Security groups names"""

    ssh_key_name: Optional[str] = None
    """SSH key name"""

    user_data: Optional[str] = None
    """Optional custom user data (Base64-encoded) Mutually exclusive with 'password'."""


class GPUBaremetalCluster(BaseModel):
    id: str
    """Cluster unique identifier"""

    created_at: datetime
    """Cluster creation date time"""

    flavor: str
    """Cluster flavor name"""

    managed_by: Literal["k8s", "user"]
    """User type managing the resource"""

    name: str
    """Cluster name"""

    servers_count: int
    """Cluster servers count"""

    servers_ids: List[str]
    """List of cluster nodes"""

    servers_settings: ServersSettings

    status: Literal["active", "deleting", "error", "new", "resizing"]
    """Cluster status"""

    tags: List[Tag]
    """List of key-value tags associated with the resource.

    A tag is a key-value pair that can be associated with a resource, enabling
    efficient filtering and grouping for better organization and management. Some
    tags are read-only and cannot be modified by the user. Tags are also integrated
    with cost reports, allowing cost data to be filtered based on tag keys or
    values.
    """

    updated_at: Optional[datetime] = None
    """Cluster update date time"""
