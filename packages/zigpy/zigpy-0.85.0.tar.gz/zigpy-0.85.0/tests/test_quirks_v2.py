"""Tests for the quirks v2 module."""

import pathlib
from typing import Any, Final
from unittest.mock import AsyncMock

from frozendict import frozendict
import pytest

from zigpy.const import (
    SIG_ENDPOINTS,
    SIG_EP_INPUT,
    SIG_EP_OUTPUT,
    SIG_EP_PROFILE,
    SIG_EP_TYPE,
    SIG_MODELS_INFO,
)
from zigpy.device import Device
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice, signature_matches
from zigpy.quirks.registry import DeviceRegistry
from zigpy.quirks.v2 import (
    BinarySensorMetadata,
    ChangedEntityMetadata,
    CustomDeviceV2,
    DeviceAlertLevel,
    DeviceAlertMetadata,
    EntityMetadata,
    EntityPlatform,
    EntityType,
    FirmwareVersionFilterMetadata,
    NumberMetadata,
    PreventDefaultEntityCreationMetadata,
    QuirkBuilder,
    SwitchMetadata,
    WriteAttributeButtonMetadata,
    ZCLCommandButtonMetadata,
    ZCLSensorMetadata,
    add_to_registry_v2,
    recursive_freeze,
)
from zigpy.quirks.v2.homeassistant import EntityType, UnitOfTime
from zigpy.quirks.v2.homeassistant.sensor import SensorDeviceClass, SensorStateClass
import zigpy.types as t
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.general import (
    Alarms,
    Basic,
    Groups,
    Identify,
    LevelControl,
    OnOff,
    Ota,
    PowerConfiguration,
    Scenes,
)
from zigpy.zcl.clusters.homeautomation import Diagnostic
from zigpy.zcl.clusters.lightlink import LightLink
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef, ZCLCommandDef
from zigpy.zdo.types import LogicalType, NodeDescriptor

from .async_mock import sentinel


@pytest.fixture(name="device_mock")
def real_device(app_mock) -> Device:
    """Device fixture with a single endpoint."""
    ieee = sentinel.ieee
    nwk = 0x2233
    device = Device(app_mock, ieee, nwk)

    device.add_endpoint(1)
    device[1].profile_id = 255
    device[1].device_type = 255
    device.model = "model"
    device.manufacturer = "manufacturer"
    device[1].add_input_cluster(3)
    device[1].add_output_cluster(6)
    return device


async def test_quirks_v2(device_mock):
    """Test adding a v2 quirk to the registry and getting back a quirked device."""
    registry = DeviceRegistry()

    signature = {
        SIG_MODELS_INFO: (("manufacturer", "model"),),
        SIG_ENDPOINTS: {
            1: {
                SIG_EP_PROFILE: 255,
                SIG_EP_TYPE: 255,
                SIG_EP_INPUT: [3],
                SIG_EP_OUTPUT: [6],
            }
        },
    }

    class TestCustomCluster(CustomCluster, Basic):
        """Custom cluster for testing quirks v2."""

        class AttributeDefs(BaseAttributeDefs):  # pylint: disable=too-few-public-methods
            """Attribute definitions for the custom cluster."""

            # pylint: disable=disallowed-name
            foo: Final = ZCLAttributeDef(id=0x0000, type=t.uint8_t)
            # pylint: disable=disallowed-name
            bar: Final = ZCLAttributeDef(id=0x0000, type=t.uint8_t)
            # pylint: disable=disallowed-name, invalid-name
            report: Final = ZCLAttributeDef(id=0x0000, type=t.uint8_t)

    entry = (
        # Quirk builder creation line, this comment is read by this unit test
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .filter(signature_matches(signature))
        .adds(
            TestCustomCluster,
            constant_attributes={TestCustomCluster.AttributeDefs.foo: 3},
        )
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    # coverage for overridden __eq__ method
    assert entry.adds_metadata[0] != entry.adds_metadata[1]
    assert entry.adds_metadata[0] != entry

    quirked = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)
    assert quirked in registry
    # this would need to be updated if the line number of the call to QuirkBuilder
    # changes in this test in the future
    assert str(quirked.quirk_metadata.quirk_file).endswith(
        "zigpy/tests/test_quirks_v2.py"
    )

    # To avoid having to rewrite this test every time quirks change, we read the current
    # file to find the line number
    quirk_builder_line = next(
        index
        for index, line in enumerate(pathlib.Path(__file__).read_text().splitlines())
        if "# Quirk builder creation line" in line
    )
    assert quirked.quirk_metadata.quirk_file_line == quirk_builder_line + 2

    ep = quirked.endpoints[1]

    assert ep.basic is not None
    assert isinstance(ep.basic, Basic)
    assert isinstance(ep.basic, TestCustomCluster)
    # pylint: disable=protected-access
    assert ep.basic._CONSTANT_ATTRIBUTES[TestCustomCluster.AttributeDefs.foo.id] == 3

    assert ep.on_off is not None
    assert isinstance(ep.on_off, OnOff)

    additional_entities = quirked.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ]
    assert len(additional_entities) == 1
    assert additional_entities[0].endpoint_id == 1
    assert additional_entities[0].cluster_id == OnOff.cluster_id
    assert additional_entities[0].cluster_type == ClusterType.Server
    assert (
        additional_entities[0].attribute_name
        == OnOff.AttributeDefs.start_up_on_off.name
    )
    assert additional_entities[0].enum == OnOff.StartUpOnOff
    assert additional_entities[0].entity_type == EntityType.CONFIG

    registry.remove(quirked)
    assert quirked not in registry


async def test_quirks_v2_model_manufacturer(device_mock):
    """Test the potential exceptions when model and manufacturer are set up incorrectly."""
    registry = DeviceRegistry()

    with pytest.raises(
        ValueError,
        match="manufacturer and model must be provided together or completely omitted.",
    ):
        (
            QuirkBuilder(device_mock.manufacturer, model=None, registry=registry)
            .adds(Basic.cluster_id)
            .adds(OnOff.cluster_id)
            .enum(
                OnOff.AttributeDefs.start_up_on_off.name,
                OnOff.StartUpOnOff,
                OnOff.cluster_id,
            )
            .add_to_registry()
        )

    with pytest.raises(
        ValueError,
        match="manufacturer and model must be provided together or completely omitted.",
    ):
        (
            QuirkBuilder(manufacturer=None, model=device_mock.model, registry=registry)
            .adds(Basic.cluster_id)
            .adds(OnOff.cluster_id)
            .enum(
                OnOff.AttributeDefs.start_up_on_off.name,
                OnOff.StartUpOnOff,
                OnOff.cluster_id,
            )
            .add_to_registry()
        )

    with pytest.raises(
        ValueError,
        match="At least one manufacturer and model must be specified for a v2 quirk.",
    ):
        (
            QuirkBuilder(registry=registry)
            .adds(Basic.cluster_id)
            .adds(OnOff.cluster_id)
            .enum(
                OnOff.AttributeDefs.start_up_on_off.name,
                OnOff.StartUpOnOff,
                OnOff.cluster_id,
                translation_key="start_up_on_off",
                fallback_name="Start up on/off",
            )
            .add_to_registry()
        )


async def test_quirks_v2_quirk_builder_cloning(device_mock):
    """Test the quirk builder clone functionality."""
    registry = DeviceRegistry()

    base = (
        QuirkBuilder(registry=registry)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .applies_to("foo", "bar")
    )

    cloned = base.clone()
    base.add_to_registry()

    (
        cloned.adds(PowerConfiguration.cluster_id)
        .applies_to(device_mock.manufacturer, device_mock.model)
        .add_to_registry()
    )

    quirked = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)
    assert (
        quirked.endpoints[1].in_clusters.get(PowerConfiguration.cluster_id) is not None
    )


async def test_quirks_v2_signature_match(device_mock):
    """Test the signature_matches filter."""
    registry = DeviceRegistry()

    signature_no_match = {
        SIG_MODELS_INFO: (("manufacturer", "model"),),
        SIG_ENDPOINTS: {
            1: {
                SIG_EP_PROFILE: 260,
                SIG_EP_TYPE: 255,
                SIG_EP_INPUT: [3],
            }
        },
    }

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .filter(signature_matches(signature_no_match))
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    quirked = registry.get_device(device_mock)
    assert not isinstance(quirked, CustomDeviceV2)


async def test_quirks_v2_multiple_matches_not_raises(device_mock):
    """Test that adding multiple quirks v2 entries for the same device doesn't raise.

    When the quirk is EXACTLY the same the semantics of sets prevents us from
    having multiple quirks in the registry.
    """
    registry = DeviceRegistry()

    entry1 = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    entry2 = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    assert entry1 == entry2
    assert entry1 != registry
    assert isinstance(registry.get_device(device_mock), CustomDeviceV2)


async def test_quirks_v2_with_custom_device_class(device_mock):
    """Test adding a quirk with a custom device class to the registry."""
    registry = DeviceRegistry()

    class CustomTestDevice(CustomDeviceV2):
        """Custom test device for testing quirks v2."""

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .device_class(CustomTestDevice)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    assert isinstance(registry.get_device(device_mock), CustomTestDevice)


async def test_quirks_v2_with_node_descriptor(device_mock):
    """Test adding a quirk with an overridden node descriptor to the registry."""
    registry = DeviceRegistry()

    node_descriptor = NodeDescriptor(
        logical_type=LogicalType.Router,
        complex_descriptor_available=0,
        user_descriptor_available=0,
        reserved=0,
        aps_flags=0,
        frequency_band=NodeDescriptor.FrequencyBand.Freq2400MHz,
        mac_capability_flags=NodeDescriptor.MACCapabilityFlags.AllocateAddress,
        manufacturer_code=4174,
        maximum_buffer_size=82,
        maximum_incoming_transfer_size=82,
        server_mask=0,
        maximum_outgoing_transfer_size=82,
        descriptor_capability_field=NodeDescriptor.DescriptorCapability.NONE,
    )

    assert device_mock.node_desc != node_descriptor

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .node_descriptor(node_descriptor)
        .add_to_registry()
    )

    quirked: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)
    assert quirked.node_desc == node_descriptor


async def test_quirks_v2_replace_occurrences(device_mock):
    """Test adding a quirk that replaces all occurrences of a cluster."""
    registry = DeviceRegistry()

    device_mock[1].add_output_cluster(Identify.cluster_id)

    device_mock.add_endpoint(2)
    device_mock[2].profile_id = 255
    device_mock[2].device_type = 255
    device_mock[2].add_input_cluster(Identify.cluster_id)

    device_mock.add_endpoint(3)
    device_mock[3].profile_id = 255
    device_mock[3].device_type = 255
    device_mock[3].add_output_cluster(Identify.cluster_id)

    class CustomIdentifyCluster(CustomCluster, Identify):
        """Custom identify cluster for testing quirks v2."""

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .replace_cluster_occurrences(CustomIdentifyCluster)
        .add_to_registry()
    )

    quirked: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)

    assert isinstance(
        quirked.endpoints[1].in_clusters[Identify.cluster_id], CustomIdentifyCluster
    )
    assert isinstance(
        quirked.endpoints[1].out_clusters[Identify.cluster_id], CustomIdentifyCluster
    )
    assert isinstance(
        quirked.endpoints[2].in_clusters[Identify.cluster_id], CustomIdentifyCluster
    )
    assert isinstance(
        quirked.endpoints[3].out_clusters[Identify.cluster_id], CustomIdentifyCluster
    )


async def test_quirks_v2_skip_configuration(device_mock):
    """Test adding a quirk that skips configuration to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .skip_configuration()
        .add_to_registry()
    )

    quirked: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)
    assert quirked.skip_configuration is True


async def test_quirks_v2_removes(device_mock):
    """Test adding a quirk that removes a cluster to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .removes(Identify.cluster_id)
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(Identify.cluster_id) is None


async def test_quirks_v2_endpoints(device_mock):
    """Test adding a quirk that modifies endpoints to the registry."""
    registry = DeviceRegistry()

    device_mock[1].add_output_cluster(Identify.cluster_id)

    device_mock.add_endpoint(2)
    device_mock[2].profile_id = 255
    device_mock[2].device_type = 255
    device_mock[2].add_input_cluster(Identify.cluster_id)
    device_mock[2].add_output_cluster(OnOff.cluster_id)

    device_mock.add_endpoint(3)
    device_mock[3].profile_id = 255
    device_mock[3].device_type = 255
    device_mock[3].add_input_cluster(Identify.cluster_id)
    device_mock[3].add_output_cluster(OnOff.cluster_id)

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds_endpoint(1, profile_id=260, device_type=260)  # 1 not modified
        .removes_endpoint(2)
        .replaces_endpoint(3, profile_id=260, device_type=260)
        .adds_endpoint(4)
        .adds(OnOff.cluster_id, endpoint_id=4)
        .replaces_endpoint(5)
        .add_to_registry()
    )

    quirked: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)

    # verify endpoint 1 was not modified, as it already existed before
    assert 1 in quirked.endpoints
    assert quirked.endpoints[1].profile_id == 255
    assert quirked.endpoints[1].device_type == 255

    # verify endpoint 2 was removed
    assert 2 not in quirked.endpoints

    # verify endpoint 3 profile id and device type were replaced
    assert 3 in quirked.endpoints
    assert quirked.endpoints[3].profile_id == 260
    assert quirked.endpoints[3].device_type == 260

    # verify original clusters still exist on endpoint 3 where id and type were replaced
    assert quirked.endpoints[3].in_clusters.get(Identify.cluster_id) is not None
    assert quirked.endpoints[3].out_clusters.get(OnOff.cluster_id) is not None

    # verify endpoint 4 was added with default profile id and device type using adds
    assert 4 in quirked.endpoints
    assert quirked.endpoints[4].profile_id == 260
    assert quirked.endpoints[4].device_type == 255

    # verify cluster was added to endpoint 4
    assert quirked.endpoints[4].in_clusters.get(OnOff.cluster_id) is not None

    # verify endpoint 5 was added with default profile id and device type using replaces
    assert 5 in quirked.endpoints
    assert quirked.endpoints[5].profile_id == 260
    assert quirked.endpoints[5].device_type == 255


async def test_quirks_v2_processing_order(device_mock):
    """Test quirks v2 metadata processing order."""
    registry = DeviceRegistry()

    device_mock.add_endpoint(2)
    device_mock[2].add_input_cluster(Identify.cluster_id)
    device_mock[2].add_output_cluster(OnOff.cluster_id)

    device_mock.add_endpoint(3)
    device_mock[3].add_input_cluster(Identify.cluster_id)
    device_mock[3].add_output_cluster(OnOff.cluster_id)

    class TestCustomIdentifyCluster(CustomCluster, Identify):
        """Custom identify cluster for testing quirks v2."""

    # the order of operations in the quirk builder below barely matters,
    # but is laid out in a way that generally follows the expected execution order
    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .removes_endpoint(2)  # wipes device reported clusters from endpoint 2
        .adds_endpoint(2)  # adds a new "blank" endpoint 2 with no clusters
        .removes(Identify.cluster_id, endpoint_id=3)  # test removing cluster
        .adds(TestCustomIdentifyCluster, endpoint_id=3)  # then "replacing" it by adds
        .adds(LevelControl.cluster_id, endpoint_id=2)  # adds one custom cluster to ep 2
        .add_to_registry()
    )

    quirked: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)

    # verify endpoint 2 was removed and a new one added with device clusters removed
    assert 2 in quirked.endpoints
    assert quirked.endpoints[2].in_clusters.get(Identify.cluster_id) is None
    assert quirked.endpoints[2].out_clusters.get(OnOff.cluster_id) is None

    # verify endpoint 2 cluster added by quirk is present though
    assert quirked.endpoints[2].in_clusters.get(LevelControl.cluster_id) is not None

    # verify endpoint 3 cluster was replaced by alternatively using removes and adds
    # instead of just using replaces directly
    assert 3 in quirked.endpoints
    assert isinstance(
        quirked.endpoints[3].in_clusters[Identify.cluster_id], TestCustomIdentifyCluster
    )


async def test_quirks_v2_apply_custom_configuration(device_mock):
    """Test adding a quirk custom configuration to the registry."""
    registry = DeviceRegistry()

    class CustomOnOffCluster(CustomCluster, OnOff):
        """Custom on off cluster for testing quirks v2."""

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(CustomOnOffCluster)
        .adds(CustomOnOffCluster, cluster_type=ClusterType.Client)
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    # pylint: disable=line-too-long
    quirked_cluster: CustomOnOffCluster = quirked_device.endpoints[1].in_clusters[
        CustomOnOffCluster.cluster_id
    ]
    assert isinstance(quirked_cluster, CustomOnOffCluster)
    # verify server cluster type was set when adding
    assert quirked_cluster.cluster_type == ClusterType.Server

    quirked_cluster.apply_custom_configuration = AsyncMock()

    quirked_client_cluster: CustomOnOffCluster = quirked_device.endpoints[
        1
    ].out_clusters[CustomOnOffCluster.cluster_id]
    assert isinstance(quirked_client_cluster, CustomOnOffCluster)
    # verify client cluster type was set when adding
    assert quirked_client_cluster.cluster_type == ClusterType.Client

    quirked_client_cluster.apply_custom_configuration = AsyncMock()

    await quirked_device.apply_custom_configuration()

    assert quirked_cluster.apply_custom_configuration.await_count == 1
    assert quirked_client_cluster.apply_custom_configuration.await_count == 1


async def test_quirks_v2_sensor(device_mock):
    """Test adding a quirk that defines a sensor to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .sensor(
            OnOff.AttributeDefs.on_time.name,
            OnOff.cluster_id,
            translation_key="on_time",
            fallback_name="On time",
            suggested_display_precision=0,
        )
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(OnOff.cluster_id) is not None

    # pylint: disable=line-too-long
    sensor_metadata: EntityMetadata = quirked_device.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ][0]
    assert sensor_metadata.entity_type == EntityType.STANDARD
    assert sensor_metadata.entity_platform == EntityPlatform.SENSOR
    assert sensor_metadata.cluster_id == OnOff.cluster_id
    assert sensor_metadata.endpoint_id == 1
    assert sensor_metadata.cluster_type == ClusterType.Server
    assert isinstance(sensor_metadata, ZCLSensorMetadata)
    assert sensor_metadata.attribute_name == OnOff.AttributeDefs.on_time.name
    assert sensor_metadata.divisor == 1
    assert sensor_metadata.multiplier == 1
    assert sensor_metadata.suggested_display_precision == 0


async def test_quirks_v2_sensor_validation_failure_no_translation_key(device_mock):
    """Test translation key and device class both not set causes exception."""
    registry = DeviceRegistry()

    with pytest.raises(ValueError, match="must have a translation_key or device_class"):
        (
            QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
            .adds(OnOff.cluster_id)
            .sensor(
                OnOff.AttributeDefs.on_time.name,
                OnOff.cluster_id,
                fallback_name="On time",
            )
            .add_to_registry()
        )


async def test_quirks_v2_switch(device_mock):
    """Test adding a quirk that defines a switch to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .switch(
            OnOff.AttributeDefs.on_time.name,
            OnOff.cluster_id,
            force_inverted=True,
            invert_attribute_name=OnOff.AttributeDefs.off_wait_time.name,
            translation_key="on_time",
            fallback_name="On time",
        )
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(OnOff.cluster_id) is not None

    switch_metadata: EntityMetadata = quirked_device.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ][0]
    assert switch_metadata.entity_type == EntityType.CONFIG
    assert switch_metadata.entity_platform == EntityPlatform.SWITCH
    assert switch_metadata.cluster_id == OnOff.cluster_id
    assert switch_metadata.endpoint_id == 1
    assert switch_metadata.cluster_type == ClusterType.Server
    assert isinstance(switch_metadata, SwitchMetadata)
    assert switch_metadata.attribute_name == OnOff.AttributeDefs.on_time.name
    assert switch_metadata.force_inverted is True
    assert (
        switch_metadata.invert_attribute_name == OnOff.AttributeDefs.off_wait_time.name
    )


async def test_quirks_v2_number(device_mock):
    """Test adding a quirk that defines a number to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .number(
            OnOff.AttributeDefs.on_time.name,
            OnOff.cluster_id,
            min_value=0,
            max_value=100,
            step=1,
            unit=UnitOfTime.SECONDS,
            translation_key="on_time",
            fallback_name="On time",
        )
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(OnOff.cluster_id) is not None

    # pylint: disable=line-too-long
    number_metadata: EntityMetadata = quirked_device.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ][0]
    assert number_metadata.entity_type == EntityType.CONFIG
    assert number_metadata.entity_platform == EntityPlatform.NUMBER
    assert number_metadata.cluster_id == OnOff.cluster_id
    assert number_metadata.endpoint_id == 1
    assert number_metadata.cluster_type == ClusterType.Server
    assert isinstance(number_metadata, NumberMetadata)
    assert number_metadata.attribute_name == OnOff.AttributeDefs.on_time.name
    assert number_metadata.min == 0
    assert number_metadata.max == 100
    assert number_metadata.step == 1
    assert number_metadata.unit == "s"
    assert number_metadata.mode is None
    assert number_metadata.multiplier is None


async def test_quirks_v2_binary_sensor(device_mock):
    """Test adding a quirk that defines a binary sensor to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .binary_sensor(
            OnOff.AttributeDefs.on_off.name,
            OnOff.cluster_id,
            translation_key="on_off",
            fallback_name="On/off",
        )
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(OnOff.cluster_id) is not None

    # pylint: disable=line-too-long
    binary_sensor_metadata: EntityMetadata = quirked_device.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ][0]
    assert binary_sensor_metadata.entity_type == EntityType.DIAGNOSTIC
    assert binary_sensor_metadata.entity_platform == EntityPlatform.BINARY_SENSOR
    assert binary_sensor_metadata.cluster_id == OnOff.cluster_id
    assert binary_sensor_metadata.endpoint_id == 1
    assert binary_sensor_metadata.cluster_type == ClusterType.Server
    assert isinstance(binary_sensor_metadata, BinarySensorMetadata)
    assert binary_sensor_metadata.attribute_name == OnOff.AttributeDefs.on_off.name


async def test_quirks_v2_write_attribute_button(device_mock):
    """Test adding a quirk that defines a write attr button to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .write_attr_button(
            OnOff.AttributeDefs.on_time.name,
            20,
            OnOff.cluster_id,
            translation_key="on_time",
            fallback_name="On time",
        )
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(OnOff.cluster_id) is not None

    # pylint: disable=line-too-long
    write_attribute_button: EntityMetadata = quirked_device.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ][0]
    assert write_attribute_button.entity_type == EntityType.CONFIG
    assert write_attribute_button.entity_platform == EntityPlatform.BUTTON
    assert write_attribute_button.cluster_id == OnOff.cluster_id
    assert write_attribute_button.endpoint_id == 1
    assert write_attribute_button.cluster_type == ClusterType.Server
    assert isinstance(write_attribute_button, WriteAttributeButtonMetadata)
    assert write_attribute_button.attribute_name == OnOff.AttributeDefs.on_time.name
    assert write_attribute_button.attribute_value == 20


async def test_quirks_v2_command_button(device_mock):
    """Test adding a quirk that defines a command button to the registry."""
    registry = DeviceRegistry()

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .command_button(
            OnOff.ServerCommandDefs.on_with_timed_off.name,
            OnOff.cluster_id,
            command_kwargs={"on_off_control": OnOff.OnOffControl.Accept_Only_When_On},
            translation_key="on_with_timed_off",
            fallback_name="On with timed off",
        )
        .command_button(
            OnOff.ServerCommandDefs.on_with_timed_off.name,
            OnOff.cluster_id,
            command_kwargs={
                "on_off_control_foo": OnOff.OnOffControl.Accept_Only_When_On
            },
            translation_key="on_with_timed_off",
            fallback_name="On with timed off",
        )
        .command_button(
            OnOff.ServerCommandDefs.on_with_timed_off.name,
            OnOff.cluster_id,
            translation_key="on_with_timed_off",
            fallback_name="On with timed off",
        )
        .add_to_registry()
    )

    quirked_device: CustomDeviceV2 = registry.get_device(device_mock)
    assert isinstance(quirked_device, CustomDeviceV2)

    assert quirked_device.endpoints[1].in_clusters.get(OnOff.cluster_id) is not None

    button: EntityMetadata = quirked_device.exposes_metadata[
        (1, OnOff.cluster_id, ClusterType.Server)
    ][0]
    assert button.entity_type == EntityType.CONFIG
    assert button.entity_platform == EntityPlatform.BUTTON
    assert button.cluster_id == OnOff.cluster_id
    assert button.endpoint_id == 1
    assert button.cluster_type == ClusterType.Server
    assert isinstance(button, ZCLCommandButtonMetadata)
    assert button.command_name == OnOff.ServerCommandDefs.on_with_timed_off.name
    assert len(button.kwargs) == 1
    assert button.kwargs["on_off_control"] == OnOff.OnOffControl.Accept_Only_When_On

    # coverage for overridden eq method
    assert (
        button
        != quirked_device.exposes_metadata[(1, OnOff.cluster_id, ClusterType.Server)][1]
    )
    assert button != quirked_device

    button = quirked_device.exposes_metadata[(1, OnOff.cluster_id, ClusterType.Server)][
        2
    ]

    assert button.kwargs == {}
    assert button.args == ()


async def test_quirks_v2_also_applies_to(device_mock):
    """Test adding the same quirk for multiple manufacturers and models."""
    registry = DeviceRegistry()

    class CustomTestDevice(CustomDeviceV2):
        """Custom test device for testing quirks v2."""

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .also_applies_to("manufacturer2", "model2")
        .also_applies_to("manufacturer3", "model3")
        .device_class(CustomTestDevice)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    assert isinstance(registry.get_device(device_mock), CustomTestDevice)

    device_mock.manufacturer = "manufacturer2"
    device_mock.model = "model2"
    assert isinstance(registry.get_device(device_mock), CustomTestDevice)

    device_mock.manufacturer = "manufacturer3"
    device_mock.model = "model3"
    assert isinstance(registry.get_device(device_mock), CustomTestDevice)


async def test_quirks_v2_with_custom_device_class_raises(device_mock):
    """Test adding a quirk with a custom device class to the registry raises

    if the class is not a subclass of CustomDeviceV2.
    """
    registry = DeviceRegistry()

    class CustomTestDevice(CustomDevice):
        """Custom test device for testing quirks v2."""

    with pytest.raises(
        AssertionError,
        match="is not a subclass of CustomDeviceV2",
    ):
        (
            QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
            .device_class(CustomTestDevice)
            .adds(Basic.cluster_id)
            .adds(OnOff.cluster_id)
            .enum(
                OnOff.AttributeDefs.start_up_on_off.name,
                OnOff.StartUpOnOff,
                OnOff.cluster_id,
            )
            .add_to_registry()
        )


async def test_quirks_v2_matches_v1(app_mock):
    """Test that quirks v2 entries are equivalent to quirks v1."""
    registry = DeviceRegistry()

    class PowerConfig1CRCluster(CustomCluster, PowerConfiguration):
        """Updating power attributes: 1 CR2032."""

        _CONSTANT_ATTRIBUTES = {
            PowerConfiguration.AttributeDefs.battery_size.id: 10,
            PowerConfiguration.AttributeDefs.battery_quantity.id: 1,
            PowerConfiguration.AttributeDefs.battery_rated_voltage.id: 30,
        }

    class ScenesCluster(CustomCluster, Scenes):
        """Ikea Scenes cluster."""

        server_commands = Scenes.server_commands.copy()
        server_commands.update(
            {
                0x0007: ZCLCommandDef(
                    "press",
                    {"param1": t.int16s, "param2": t.int8s, "param3": t.int8s},
                    is_manufacturer_specific=True,
                ),
                0x0008: ZCLCommandDef(
                    "hold",
                    {"param1": t.int16s, "param2": t.int8s},
                    is_manufacturer_specific=True,
                ),
                0x0009: ZCLCommandDef(
                    "release",
                    {
                        "param1": t.int16s,
                    },
                    is_manufacturer_specific=True,
                ),
            }
        )

    # pylint: disable=invalid-name
    SHORT_PRESS = "remote_button_short_press"
    TURN_ON = "turn_on"
    COMMAND = "command"
    COMMAND_RELEASE = "release"
    COMMAND_TOGGLE = "toggle"
    CLUSTER_ID = "cluster_id"
    ENDPOINT_ID = "endpoint_id"
    PARAMS = "params"
    LONG_PRESS = "remote_button_long_press"
    triggers = {
        (SHORT_PRESS, TURN_ON): {
            COMMAND: COMMAND_TOGGLE,
            CLUSTER_ID: OnOff.cluster_id,
            ENDPOINT_ID: 1,
        },
        (LONG_PRESS, TURN_ON): {
            COMMAND: COMMAND_RELEASE,
            CLUSTER_ID: Scenes.cluster_id,
            ENDPOINT_ID: 1,
            PARAMS: {"param1": 0},
        },
    }

    class IkeaTradfriRemote3(CustomDevice):
        """Custom device representing variation of IKEA five button remote."""

        signature = {
            # <SimpleDescriptor endpoint=1 profile=260 device_type=2064
            # device_version=2
            # input_clusters=[0, 1, 3, 9, 2821, 4096]
            # output_clusters=[3, 4, 5, 6, 8, 25, 4096]>
            SIG_MODELS_INFO: [("IKEA of Sweden", "TRADFRI remote control")],
            SIG_ENDPOINTS: {
                1: {
                    SIG_EP_PROFILE: zha.PROFILE_ID,
                    SIG_EP_TYPE: zha.DeviceType.COLOR_SCENE_CONTROLLER,
                    SIG_EP_INPUT: [
                        Basic.cluster_id,
                        PowerConfiguration.cluster_id,
                        Identify.cluster_id,
                        Alarms.cluster_id,
                        Diagnostic.cluster_id,
                        LightLink.cluster_id,
                    ],
                    SIG_EP_OUTPUT: [
                        Identify.cluster_id,
                        Groups.cluster_id,
                        Scenes.cluster_id,
                        OnOff.cluster_id,
                        LevelControl.cluster_id,
                        Ota.cluster_id,
                        LightLink.cluster_id,
                    ],
                }
            },
        }

        replacement = {
            SIG_ENDPOINTS: {
                1: {
                    SIG_EP_PROFILE: zha.PROFILE_ID,
                    SIG_EP_TYPE: zha.DeviceType.COLOR_SCENE_CONTROLLER,
                    SIG_EP_INPUT: [
                        Basic.cluster_id,
                        PowerConfig1CRCluster,
                        Identify.cluster_id,
                        Alarms.cluster_id,
                        LightLink.cluster_id,
                    ],
                    SIG_EP_OUTPUT: [
                        Identify.cluster_id,
                        Groups.cluster_id,
                        ScenesCluster,
                        OnOff.cluster_id,
                        LevelControl.cluster_id,
                        Ota.cluster_id,
                        LightLink.cluster_id,
                    ],
                }
            }
        }

        device_automation_triggers = triggers

    ieee = sentinel.ieee
    nwk = 0x2233
    ikea_device = Device(app_mock, ieee, nwk)

    ikea_device.add_endpoint(1)
    ikea_device[1].profile_id = zha.PROFILE_ID
    ikea_device[1].device_type = zha.DeviceType.COLOR_SCENE_CONTROLLER
    ikea_device.model = "TRADFRI remote control"
    ikea_device.manufacturer = "IKEA of Sweden"
    ikea_device[1].add_input_cluster(Basic.cluster_id)
    ikea_device[1].add_input_cluster(PowerConfiguration.cluster_id)
    ikea_device[1].add_input_cluster(Identify.cluster_id)
    ikea_device[1].add_input_cluster(Alarms.cluster_id)
    ikea_device[1].add_input_cluster(Diagnostic.cluster_id)
    ikea_device[1].add_input_cluster(LightLink.cluster_id)

    ikea_device[1].add_output_cluster(Identify.cluster_id)
    ikea_device[1].add_output_cluster(Groups.cluster_id)
    ikea_device[1].add_output_cluster(Scenes.cluster_id)
    ikea_device[1].add_output_cluster(OnOff.cluster_id)
    ikea_device[1].add_output_cluster(LevelControl.cluster_id)
    ikea_device[1].add_output_cluster(Ota.cluster_id)
    ikea_device[1].add_output_cluster(LightLink.cluster_id)

    registry.add_to_registry(IkeaTradfriRemote3)

    quirked = registry.get_device(ikea_device)

    assert isinstance(quirked, IkeaTradfriRemote3)

    registry = DeviceRegistry()

    (
        QuirkBuilder(ikea_device.manufacturer, ikea_device.model, registry=registry)
        .replaces(PowerConfig1CRCluster)
        .replaces(ScenesCluster, cluster_type=ClusterType.Client)
        .device_automation_triggers(triggers)
        .add_to_registry()
    )

    quirked_v2 = registry.get_device(ikea_device)

    assert isinstance(quirked_v2, CustomDeviceV2)

    assert len(quirked_v2.endpoints[1].in_clusters) == 6
    assert len(quirked_v2.endpoints[1].out_clusters) == 7

    assert isinstance(
        quirked_v2.endpoints[1].in_clusters[PowerConfig1CRCluster.cluster_id],
        PowerConfig1CRCluster,
    )

    assert isinstance(
        quirked_v2.endpoints[1].out_clusters[ScenesCluster.cluster_id], ScenesCluster
    )

    for cluster_id, cluster in quirked.endpoints[1].in_clusters.items():
        assert isinstance(
            quirked_v2.endpoints[1].in_clusters[cluster_id], type(cluster)
        )

    for cluster_id, cluster in quirked.endpoints[1].out_clusters.items():
        assert isinstance(
            quirked_v2.endpoints[1].out_clusters[cluster_id], type(cluster)
        )

    assert quirked.device_automation_triggers == quirked_v2.device_automation_triggers
    assert (
        quirked.device_automation_triggers[("remote_button_long_press", "turn_on")][
            "cluster_id"
        ]
        == 0x0005
    )


async def test_quirks_v2_add_to_registry_v2_logs_error(caplog):
    """Test adding a quirk with old API logs."""
    registry = DeviceRegistry()

    (
        add_to_registry_v2("foo", "bar", registry=registry)
        .adds(OnOff.cluster_id)
        .binary_sensor(
            OnOff.AttributeDefs.on_off.name,
            OnOff.cluster_id,
            translation_key="on_off",
            fallback_name="On/off",
        )
        .add_to_registry()
    )

    assert (
        "add_to_registry_v2 is deprecated and will be removed in a future release"
        in caplog.text
    )


async def test_quirks_v2_friendly_name(device_mock: Device) -> None:
    registry = DeviceRegistry()

    entry = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .friendly_name(model="Real Model Name", manufacturer="Real Manufacturer")
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    assert entry.friendly_name is not None
    assert entry.friendly_name.model == "Real Model Name"
    assert entry.friendly_name.manufacturer == "Real Manufacturer"


async def test_quirks_v2_no_friendly_name(device_mock: Device) -> None:
    registry = DeviceRegistry()

    entry = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(Basic.cluster_id)
        .adds(OnOff.cluster_id)
        .enum(
            OnOff.AttributeDefs.start_up_on_off.name,
            OnOff.StartUpOnOff,
            OnOff.cluster_id,
            translation_key="start_up_on_off",
            fallback_name="Start up on/off",
        )
        .add_to_registry()
    )

    assert entry.friendly_name is None


async def test_quirks_v2_device_alerts(device_mock: Device) -> None:
    registry = DeviceRegistry()

    entry = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .device_alert(level="warning", message="This device has routing problems.")
        .device_alert(
            level="error", message="This device irreparably crashes the mesh."
        )
        .add_to_registry()
    )

    assert entry.device_alerts == (
        DeviceAlertMetadata(
            level=DeviceAlertLevel.WARNING,
            message="This device has routing problems.",
        ),
        DeviceAlertMetadata(
            level=DeviceAlertLevel.ERROR,
            message="This device irreparably crashes the mesh.",
        ),
    )


async def test_quirks_v2_disable_entity_creation(device_mock: Device) -> None:
    registry = DeviceRegistry()

    def filter_func(entity) -> bool:
        return True

    entry = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .prevent_default_entity_creation(endpoint_id=1, unique_id_suffix="something")
        .prevent_default_entity_creation(endpoint_id=1, cluster_id=OnOff.cluster_id)
        .prevent_default_entity_creation(
            endpoint_id=1, cluster_id=OnOff.cluster_id, cluster_type=ClusterType.Client
        )
        .prevent_default_entity_creation(function=filter_func)
        .add_to_registry()
    )

    assert entry.disabled_default_entities == (
        PreventDefaultEntityCreationMetadata(
            endpoint_id=1,
            cluster_id=None,
            cluster_type=None,
            unique_id_suffix="something",
            function=None,
        ),
        PreventDefaultEntityCreationMetadata(
            endpoint_id=1,
            cluster_id=OnOff.cluster_id,
            cluster_type=ClusterType.Server,  # by default
            unique_id_suffix=None,
            function=None,
        ),
        PreventDefaultEntityCreationMetadata(
            endpoint_id=1,
            cluster_id=OnOff.cluster_id,
            cluster_type=ClusterType.Client,
            unique_id_suffix=None,
            function=None,
        ),
        PreventDefaultEntityCreationMetadata(
            endpoint_id=None,
            cluster_id=None,
            cluster_type=None,
            unique_id_suffix=None,
            function=filter_func,
        ),
    )


async def test_quirks_v2_primary_entity(device_mock: Device) -> None:
    registry = DeviceRegistry()

    builder = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .adds(OnOff.cluster_id)
        .switch(
            OnOff.AttributeDefs.on_time.name,
            OnOff.cluster_id,
            force_inverted=True,
            invert_attribute_name=OnOff.AttributeDefs.off_wait_time.name,
            translation_key="on_time",
            fallback_name="On time",
            primary=True,
        )
    )

    with pytest.raises(ValueError):
        # Having a second primary entity is not allowed
        builder.sensor(
            OnOff.AttributeDefs.on_time.name,
            OnOff.cluster_id,
            translation_key="on_time",
            fallback_name="On time",
            primary=True,
        )

    entry = builder.add_to_registry()

    assert len(entry.entity_metadata) == 1
    assert entry.entity_metadata[0].primary is True


@pytest.mark.parametrize(
    ("fw_version", "min_version", "max_version", "allow_missing", "expected_match"),
    [
        # Basic version filtering
        (100, 50, 150, True, True),  # Within range
        (25, 50, 150, True, False),  # Below min
        (175, 50, 150, True, False),  # Above/equal max
        (150, 50, 150, True, False),  # Equal to max (exclusive)
        (50, 50, 150, True, True),  # Equal to min (inclusive)
        # Only min version specified
        (100, 50, None, True, True),  # Above min
        (25, 50, None, True, False),  # Below min
        (50, 50, None, True, True),  # Equal to min
        # Only max version specified
        (100, None, 150, True, True),  # Below max
        (175, None, 150, True, False),  # Above/equal max
        (150, None, 150, True, False),  # Equal to max
        # Missing firmware version handling
        (None, 50, 150, True, True),  # Missing allowed
        (None, 50, 150, False, False),  # Missing not allowed
        (None, None, None, True, True),  # No constraints, missing allowed
        (None, None, None, False, False),  # No constraints, missing not allowed
    ],
)
async def test_quirks_v2_firmware_version_filter(
    device_mock, fw_version, min_version, max_version, allow_missing, expected_match
):
    """Test firmware version filtering functionality."""
    registry = DeviceRegistry()

    # Add OTA cluster to device with firmware version
    device_mock[1].add_output_cluster(Ota.cluster_id)
    ota_cluster = device_mock[1].out_clusters[Ota.cluster_id]

    if fw_version is not None:
        ota_cluster._attr_cache[Ota.AttributeDefs.current_file_version.id] = fw_version

    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .firmware_version_filter(
            min_version=min_version,
            max_version=max_version,
            allow_missing=allow_missing,
        )
        .adds(Basic.cluster_id)
        .add_to_registry()
    )

    quirked = registry.get_device(device_mock)
    is_quirked = isinstance(quirked, CustomDeviceV2)

    assert is_quirked == expected_match


async def test_quirks_v2_firmware_version_filter_no_ota_cluster(device_mock):
    """Test firmware version filter when device has no OTA cluster."""
    registry1 = DeviceRegistry()

    # Test with allow_missing=True (should match)
    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry1)
        .firmware_version_filter(min_version=50, max_version=150, allow_missing=True)
        .adds(Basic.cluster_id)
        .add_to_registry()
    )

    quirked = registry1.get_device(device_mock)
    assert isinstance(quirked, CustomDeviceV2)

    registry2 = DeviceRegistry()

    # Test with allow_missing=False (should not match)
    (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry2)
        .firmware_version_filter(min_version=50, max_version=150, allow_missing=False)
        .adds(Basic.cluster_id)
        .add_to_registry()
    )

    quirked = registry2.get_device(device_mock)
    assert not isinstance(quirked, CustomDeviceV2)


async def test_quirks_v2_firmware_version_filter_metadata(device_mock):
    """Test that firmware version filter metadata is properly set."""
    registry = DeviceRegistry()

    entry = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .firmware_version_filter(min_version=10, max_version=50, allow_missing=False)
        .adds(Basic.cluster_id)
        .add_to_registry()
    )

    assert entry.fw_version_filter is not None
    assert isinstance(entry.fw_version_filter, FirmwareVersionFilterMetadata)
    assert entry.fw_version_filter.min_version == 10
    assert entry.fw_version_filter.max_version == 50
    assert entry.fw_version_filter.allow_missing is False


async def test_quirks_v2_change_entity_metadata(device_mock: Device) -> None:
    """Test changing entity metadata functionality."""
    registry = DeviceRegistry()

    def filter_func(entity) -> bool:
        return True

    entry = (
        QuirkBuilder(device_mock.manufacturer, device_mock.model, registry=registry)
        .change_entity_metadata(
            endpoint_id=1,
            unique_id_suffix="something",
            new_primary=True,
        )
        .change_entity_metadata(
            endpoint_id=1,
            cluster_id=OnOff.cluster_id,
            new_translation_key="custom_key",
            new_translation_placeholders={"index": "subkey"},
        )
        .change_entity_metadata(
            endpoint_id=1,
            cluster_id=OnOff.cluster_id,
            cluster_type=ClusterType.Client,
            new_device_class=SensorDeviceClass.POWER,
            new_state_class=SensorStateClass.MEASUREMENT,
            new_entity_category=EntityType.CONFIG,
            new_entity_registry_enabled_default=False,
        )
        .change_entity_metadata(
            function=filter_func,
            new_unique_id="custom_unique_id",
            new_fallback_name="Custom Fallback Name",
        )
        .add_to_registry()
    )

    assert entry.changed_entity_metadata == (
        ChangedEntityMetadata(
            endpoint_id=1,
            cluster_id=None,
            cluster_type=None,
            unique_id_suffix="something",
            function=None,
            new_primary=True,
            new_unique_id=None,
            new_translation_key=None,
            new_translation_placeholders=None,
            new_device_class=None,
            new_state_class=None,
            new_entity_category=None,
            new_entity_registry_enabled_default=None,
            new_fallback_name=None,
        ),
        ChangedEntityMetadata(
            endpoint_id=1,
            cluster_id=OnOff.cluster_id,
            cluster_type=ClusterType.Server,  # by default
            unique_id_suffix=None,
            function=None,
            new_primary=None,
            new_unique_id=None,
            new_translation_key="custom_key",
            new_translation_placeholders={"index": "subkey"},
            new_device_class=None,
            new_state_class=None,
            new_entity_category=None,
            new_entity_registry_enabled_default=None,
            new_fallback_name=None,
        ),
        ChangedEntityMetadata(
            endpoint_id=1,
            cluster_id=OnOff.cluster_id,
            cluster_type=ClusterType.Client,
            unique_id_suffix=None,
            function=None,
            new_primary=None,
            new_unique_id=None,
            new_translation_key=None,
            new_translation_placeholders=None,
            new_device_class=SensorDeviceClass.POWER,
            new_state_class=SensorStateClass.MEASUREMENT,
            new_entity_category=EntityType.CONFIG,
            new_entity_registry_enabled_default=False,
            new_fallback_name=None,
        ),
        ChangedEntityMetadata(
            endpoint_id=None,
            cluster_id=None,
            cluster_type=None,
            unique_id_suffix=None,
            function=filter_func,
            new_primary=None,
            new_unique_id="custom_unique_id",
            new_translation_key=None,
            new_translation_placeholders=None,
            new_device_class=None,
            new_state_class=None,
            new_entity_category=None,
            new_entity_registry_enabled_default=None,
            new_fallback_name="Custom Fallback Name",
        ),
    )


def strict_eq(a: Any, b: Any) -> bool:
    """Recursively check equality and type matching."""
    if type(a) is not type(b):
        return False
    if a != b:
        return False
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return False
        return all(strict_eq(a[k], b[k]) for k in a)
    if isinstance(a, tuple | list):
        if len(a) != len(b):
            return False
        return all(
            strict_eq(a_item, b_item) for a_item, b_item in zip(a, b, strict=False)
        )
    return True


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        ({}, frozendict()),
        ([], ()),
        ({"a": 1, "b": 2}, frozendict({"a": 1, "b": 2})),
        ([1, 2, 3], (1, 2, 3)),
        (
            {"outer": {"inner": "value"}},
            frozendict({"outer": frozendict({"inner": "value"})}),
        ),
        ({"key": [1, 2, 3]}, frozendict({"key": (1, 2, 3)})),
        ([{"a": 1}, {"b": 2}], (frozendict({"a": 1}), frozendict({"b": 2}))),
        ([[1, 2], [3, 4]], ((1, 2), (3, 4))),
        (
            {"a": [1, {"b": 2}], "c": {"d": [3, 4]}},
            frozendict(
                {"a": (1, frozendict({"b": 2})), "c": frozendict({"d": (3, 4)})}
            ),
        ),
        (42, 42),
        ("string", "string"),
        (None, None),
        (True, True),
        (3.14, 3.14),
        (frozendict({"a": 1}), frozendict({"a": 1})),
        ((1, 2, 3), (1, 2, 3)),
        ((1, [2], {3: 4}), (1, (2,), frozendict({3: 4}))),
        (
            {"triggers": {("key1", "key2"): {"param": 0}}},
            frozendict(
                {"triggers": frozendict({("key1", "key2"): frozendict({"param": 0})})}
            ),
        ),
    ],
)
def test_recursive_freeze(obj, expected):
    """Test recursive_freeze converts mutable collections to immutable ones."""
    result = recursive_freeze(obj)
    assert strict_eq(result, expected)
    hash(result)
