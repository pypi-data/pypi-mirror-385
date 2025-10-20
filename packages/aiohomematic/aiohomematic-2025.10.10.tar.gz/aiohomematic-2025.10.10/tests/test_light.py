"""Tests for light data points of aiohomematic."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, call

import pytest

from aiohomematic.central import CentralUnit
from aiohomematic.client import Client
from aiohomematic.const import WAIT_FOR_CALLBACK, DataPointUsage, ParamsetKey
from aiohomematic.model.custom import (
    CustomDpColorDimmer,
    CustomDpColorDimmerEffect,
    CustomDpColorTempDimmer,
    CustomDpDimmer,
    CustomDpIpFixedColorLight,
    CustomDpIpRGBWLight,
)
from aiohomematic.model.custom.light import _NOT_USED, _ColorBehaviour, _FixedColor, _TimeUnit

from tests import const, helper

TEST_DEVICES: dict[str, str] = {
    "VCU0000098": "HM-DW-WM.json",
    "VCU0000115": "HM-LC-DW-WM.json",
    "VCU0000122": "HM-LC-Dim1L-CV.json",
    "VCU1399816": "HmIP-BDT.json",
    "VCU6985973": "HmIP-BSL.json",
    "VCU3747418": "HM-LC-RGBW-WM.json",
    "VCU4704397": "HmIPW-WRC6.json",
    "VCU5629873": "HmIP-RGBW.json",
    "VCU9973336": "HBW-LC-RGBWW-IN6-DR.json",
}

# pylint: disable=protected-access


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cedimmer(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpDimmer."""
    central, mock_client, _ = central_client_factory
    light: CustomDpDimmer = cast(CustomDpDimmer, helper.get_prepared_custom_data_point(central, "VCU1399816", 4))
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.service_method_names == ("turn_off", "turn_on")
    assert light.color_temp_kelvin is None
    assert light.hs_color is None
    assert light.supports_brightness is True
    assert light.supports_color_temperature is False
    assert light.supports_effects is False
    assert light.supports_hs_color is False
    assert light.supports_transition is True
    assert light.effect is None
    assert light.effects is None

    assert light.brightness == 0
    assert light.brightness_pct == 0
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1399816:4",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.brightness_pct == 100
    await light.turn_on(brightness=28)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1399816:4",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.10980392156862745,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 28
    assert light.brightness_pct == 10
    assert light.is_on

    assert light.group_brightness is None
    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU1399816:3", parameter="LEVEL", value=0.4
    )
    assert light.group_brightness == 102

    await light.turn_on(on_time=5.0, ramp_time=6.0)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU1399816:4",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"LEVEL": 0.10980392156862745, "RAMP_TIME": 6.0, "ON_TIME": 5.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await light.turn_on(on_time=5.0)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU1399816:4",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"ON_TIME": 5.0, "LEVEL": 0.10980392156862745},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off(ramp_time=6.0)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU1399816:4",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"RAMP_TIME": 6.0, "LEVEL": 0.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0
    await light.turn_on()
    assert light.brightness == 255
    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1399816:4",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off()
    light.set_timer_on_time(on_time=0.5)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU1399816:4",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"ON_TIME": 0.5, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    light.set_timer_on_time(on_time=1.6)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU1399816:4",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"ON_TIME": 1.6, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cecolordimmereffect(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpColorDimmerEffect."""
    central, mock_client, _ = central_client_factory
    light: CustomDpColorDimmerEffect = cast(
        CustomDpColorDimmerEffect, helper.get_prepared_custom_data_point(central, "VCU3747418", 1)
    )
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.color_temp_kelvin is None
    assert light.hs_color == (0.0, 0.0)
    assert light.supports_brightness is True
    assert light.supports_color_temperature is False
    assert light.supports_effects is True
    assert light.supports_hs_color is True
    assert light.supports_transition is True
    assert light.effect is None
    assert light.effects == (
        "Off",
        "Slow color change",
        "Medium color change",
        "Fast color change",
        "Campfire",
        "Waterfall",
        "TV simulation",
    )

    assert light.brightness == 0
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    await light.turn_on(brightness=28)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.10980392156862745,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 28
    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0

    assert light.hs_color == (0.0, 0.0)
    await light.turn_on(hs_color=(44.4, 69.3))
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU3747418:2",
        paramset_key=ParamsetKey.VALUES,
        parameter="COLOR",
        value=25,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (45.0, 100)

    await light.turn_on(hs_color=(0, 50))
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU3747418:2",
        paramset_key=ParamsetKey.VALUES,
        parameter="COLOR",
        value=0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (0.0, 100.0)

    await light.turn_on(effect="Slow color change")

    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:3",
        paramset_key=ParamsetKey.VALUES,
        parameter="PROGRAM",
        value=1,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    assert light.effect == "Slow color change"

    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU3747418:2", parameter="COLOR", value=201
    )
    assert light.hs_color == (0.0, 0.0)
    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU3747418:2", parameter="COLOR", value=None
    )
    assert light.hs_color == (0.0, 0.0)

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)

    await light.turn_on(brightness=28, effect="Slow color change")
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU3747418:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.10980392156862745,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3747418:3",
        paramset_key=ParamsetKey.VALUES,
        parameter="PROGRAM",
        value=1,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cecolortempdimmer(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpColorTempDimmer."""
    central, mock_client, _ = central_client_factory
    light: CustomDpColorTempDimmer = cast(
        CustomDpColorTempDimmer, helper.get_prepared_custom_data_point(central, "VCU0000115", 1)
    )
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.color_temp_kelvin == 2000
    assert light.hs_color is None
    assert light.supports_brightness is True
    assert light.supports_color_temperature is True
    assert light.supports_effects is False
    assert light.supports_hs_color is False
    assert light.supports_transition is True
    assert light.effect is None
    assert light.effects is None
    assert light.brightness == 0
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000115:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    await light.turn_on(brightness=28)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000115:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.10980392156862745,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 28
    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000115:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0

    assert light.color_temp_kelvin == 2000
    await light.turn_on(color_temp_kelvin=2309)
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU0000115:2",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.1930835734870317,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000115:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_temp_kelvin == 2309

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceipfixedcolorlight(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpIpFixedColorLight."""
    central, mock_client, _ = central_client_factory
    light: CustomDpIpFixedColorLight = cast(
        CustomDpIpFixedColorLight, helper.get_prepared_custom_data_point(central, "VCU6985973", 8)
    )
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.color_temp_kelvin is None
    assert light.hs_color == (0.0, 0.0)
    assert light.supports_brightness is True
    assert light.supports_color_temperature is False
    assert light.supports_effects is True
    assert light.supports_hs_color is True
    assert light.supports_transition is True
    assert light.effect is None
    assert light.effects == (
        "ON",
        "BLINKING_SLOW",
        "BLINKING_MIDDLE",
        "BLINKING_FAST",
        "FLASH_SLOW",
        "FLASH_MIDDLE",
        "FLASH_FAST",
        "BILLOW_SLOW",
        "BILLOW_MIDDLE",
        "BILLOW_FAST",
    )
    assert light.brightness == 0
    assert light.is_on is False
    assert light.color_name == _FixedColor.BLACK
    assert light.channel_color_name is None
    assert light.group_brightness is None
    assert light.channel_hs_color is None
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 7, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    await light.turn_on(brightness=28)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "LEVEL": 0.10980392156862745},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 28
    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6985973:8",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0
    assert light.color_name == _FixedColor.WHITE

    await light.turn_on(hs_color=(350, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 4, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.RED

    await light.turn_on(hs_color=(0.0, 0.0))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 7, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.WHITE

    await light.turn_on(hs_color=(60.0, 50.0))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 6, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.YELLOW

    await light.turn_on(hs_color=(120, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 2, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.GREEN

    await light.turn_on(hs_color=(180, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 3, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.TURQUOISE

    await light.turn_on(hs_color=(240, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 1, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.BLUE

    await light.turn_on(hs_color=(300, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR": 5, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_name == _FixedColor.PURPLE

    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU6985973:7", parameter="LEVEL", value=0.5
    )
    assert light.group_brightness == 127

    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU6985973:7", parameter="COLOR", value=1
    )
    assert light.channel_hs_color == (240.0, 100.0)
    assert light.channel_color_name == _FixedColor.BLUE

    await light.turn_off()
    light.set_timer_on_time(on_time=18)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"DURATION_VALUE": 18, "COLOR_BEHAVIOUR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off()
    light.set_timer_on_time(on_time=17000)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "DURATION_UNIT": 1, "DURATION_VALUE": 283, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off()
    light.set_timer_on_time(on_time=1000000)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "DURATION_UNIT": 2, "DURATION_VALUE": 277, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await light.turn_on(ramp_time=18)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "RAMP_TIME_VALUE": 18, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(ramp_time=17000)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "RAMP_TIME_UNIT": 1, "RAMP_TIME_VALUE": 283, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(ramp_time=1000000)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU6985973:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "RAMP_TIME_UNIT": 2, "RAMP_TIME_VALUE": 277, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceipfixedcolorlightwired(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpIpFixedColorLight."""
    central, mock_client, _ = central_client_factory
    light: CustomDpIpFixedColorLight = cast(
        CustomDpIpFixedColorLight, helper.get_prepared_custom_data_point(central, "VCU4704397", 8)
    )
    assert light.channel.device.has_sub_devices is False
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.color_temp_kelvin is None
    assert light.hs_color == (0.0, 0.0)
    assert light.supports_brightness is True
    assert light.supports_color_temperature is False
    assert light.supports_effects is True
    assert light.supports_hs_color is True
    assert light.supports_transition is True
    assert light.effect is None
    assert light.effects == (
        _ColorBehaviour.ON,
        "BLINKING_SLOW",
        "BLINKING_MIDDLE",
        "BLINKING_FAST",
        "FLASH_SLOW",
        "FLASH_MIDDLE",
        "FLASH_FAST",
        "BILLOW_SLOW",
        "BILLOW_MIDDLE",
        "BILLOW_FAST",
    )
    assert light.brightness == 0
    assert light.is_on is False
    assert light.color_name == _FixedColor.BLACK
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 7, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.WHITE

    await light.turn_on(brightness=100)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "LEVEL": 0.39215686274509803},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 100
    assert light.color_name == _FixedColor.WHITE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU4704397:8",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0
    assert light.color_name == _FixedColor.WHITE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(350, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 4, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.RED
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(0.0, 0.0))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 7, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.WHITE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(60.0, 50.0))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 6, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.YELLOW
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(120, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 2, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.GREEN
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(180, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 3, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.TURQUOISE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(240, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.BLUE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(hs_color=(300, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "COLOR": 5, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    assert light.color_name == _FixedColor.PURPLE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_off()
    assert light.brightness == 0
    assert light.color_name == _FixedColor.PURPLE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(brightness=100)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "LEVEL": 0.39215686274509803},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 100
    assert light.color_name == _FixedColor.PURPLE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(brightness=33)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 1, "LEVEL": 0.12941176470588237},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 33
    assert light.color_name == _FixedColor.PURPLE
    assert light.effect == _ColorBehaviour.ON

    await light.turn_on(effect="FLASH_MIDDLE")
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "LEVEL": 0.12941176470588237},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 33
    assert light.color_name == _FixedColor.PURPLE
    assert light.effect == "FLASH_MIDDLE"

    await light.turn_on(brightness=66)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "LEVEL": 0.25882352941176473},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 66
    assert light.color_name == _FixedColor.PURPLE
    assert light.effect == "FLASH_MIDDLE"

    await light.turn_off()

    light.set_timer_on_time(on_time=18)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "DURATION_VALUE": 18, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off()
    light.set_timer_on_time(on_time=17000)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "DURATION_UNIT": 1, "DURATION_VALUE": 283, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off()
    light.set_timer_on_time(on_time=1000000)
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "DURATION_UNIT": 2, "DURATION_VALUE": 277, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await light.turn_on(ramp_time=18)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "RAMP_TIME_VALUE": 18, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(ramp_time=17000)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "RAMP_TIME_UNIT": 1, "RAMP_TIME_VALUE": 283, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(ramp_time=1000000)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "RAMP_TIME_UNIT": 2, "RAMP_TIME_VALUE": 277, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    await light.turn_on(effect="BLINKING_SLOW")
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 2, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(brightness=28)
    await light.turn_on(effect="FLASH_MIDDLE")
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU4704397:8",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_BEHAVIOUR": 6, "LEVEL": 0.10980392156862745},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceiprgbwlight(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpIpRGBWLight."""
    central, mock_client, _ = central_client_factory
    light: CustomDpIpRGBWLight = cast(
        CustomDpIpRGBWLight, helper.get_prepared_custom_data_point(central, "VCU5629873", 1)
    )
    assert light.channel.device.has_sub_devices is False
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.color_temp_kelvin is None
    assert light.hs_color is None
    assert light.supports_brightness is True
    assert light.supports_color_temperature is False
    assert light.supports_effects is True
    assert light.supports_hs_color is True
    assert light.supports_transition is True
    assert light.effect is None
    assert light.effects == (
        "NO_EFFECT",
        "EFFECT_01_END_CURRENT_PROFILE",
        "EFFECT_01_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_02_END_CURRENT_PROFILE",
        "EFFECT_02_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_03_END_CURRENT_PROFILE",
        "EFFECT_03_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_04_END_CURRENT_PROFILE",
        "EFFECT_04_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_05_END_CURRENT_PROFILE",
        "EFFECT_05_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_06_END_CURRENT_PROFILE",
        "EFFECT_06_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_07_END_CURRENT_PROFILE",
        "EFFECT_07_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_08_END_CURRENT_PROFILE",
        "EFFECT_08_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_09_END_CURRENT_PROFILE",
        "EFFECT_09_INTERRUPT_CURRENT_PROFILE",
        "EFFECT_10_END_CURRENT_PROFILE",
        "EFFECT_10_INTERRUPT_CURRENT_PROFILE",
    )

    assert light.brightness == 0

    await light.turn_on()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU5629873:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    await light.turn_on(brightness=28)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU5629873:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.10980392156862745,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 28
    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU5629873:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0

    assert light.color_temp_kelvin is None
    await light.turn_on(color_temp_kelvin=3000)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"COLOR_TEMPERATURE": 3000, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.color_temp_kelvin == 3000

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)

    assert light.hs_color is None
    await light.turn_on(hs_color=(44.4, 69.3))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"HUE": 44, "SATURATION": 0.693, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (44, 69.3)

    await light.turn_on(hs_color=(0, 50))
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"HUE": 0, "SATURATION": 0.5, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (0.0, 50.0)

    await light.turn_on(effect="EFFECT_01_END_CURRENT_PROFILE")
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={"EFFECT": 1, "LEVEL": 1.0},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(hs_color=(44, 66), ramp_time=5)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={
            "HUE": 44,
            "SATURATION": 0.66,
            "DURATION_VALUE": _NOT_USED,
            "RAMP_TIME_UNIT": _TimeUnit.SECONDS,
            "RAMP_TIME_VALUE": 5,
            "LEVEL": 1.0,
        },
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_off(ramp_time=5)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={
            "DURATION_VALUE": _NOT_USED,
            "RAMP_TIME_UNIT": _TimeUnit.SECONDS,
            "RAMP_TIME_VALUE": 5,
            "LEVEL": 0.0,
        },
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await light.turn_on(hs_color=(44, 66), ramp_time=5, on_time=8760)
    assert mock_client.method_calls[-1] == call.put_paramset(
        channel_address="VCU5629873:1",
        paramset_key_or_link_address=ParamsetKey.VALUES,
        values={
            "HUE": 44,
            "SATURATION": 0.66,
            "RAMP_TIME_UNIT": _TimeUnit.SECONDS,
            "RAMP_TIME_VALUE": 5,
            "DURATION_UNIT": _TimeUnit.SECONDS,
            "DURATION_VALUE": 8760,
            "LEVEL": 1.0,
        },
        wait_for_callback=WAIT_FOR_CALLBACK,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "port",
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (const.CCU_MINI_PORT, TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cecolordimmer(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CustomDpColorDimmer."""
    central, mock_client, _ = central_client_factory
    light: CustomDpColorDimmer = cast(
        CustomDpColorDimmer, helper.get_prepared_custom_data_point(central, "VCU9973336", 13)
    )
    assert light.usage == DataPointUsage.CDP_PRIMARY
    assert light.color_temp_kelvin is None
    assert light.hs_color == (0.0, 0.0)
    assert light.supports_brightness is True
    assert light.supports_color_temperature is False
    assert light.supports_effects is False
    assert light.supports_hs_color is True
    assert light.supports_transition is True
    assert light.effect is None

    assert light.brightness == 0
    assert light.brightness_pct == 0
    await light.turn_on()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9973336:13",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 255
    await light.turn_on(brightness=28)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9973336:13",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.10980392156862745,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 28
    await light.turn_off()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9973336:13",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=0.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.brightness == 0

    assert light.hs_color == (0.0, 0.0)
    await light.turn_on(hs_color=(44.4, 69.3))
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU9973336:15",
        paramset_key=ParamsetKey.VALUES,
        parameter="COLOR",
        value=25,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9973336:13",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (45.0, 100)

    await light.turn_on(hs_color=(0, 50))
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU9973336:15",
        paramset_key=ParamsetKey.VALUES,
        parameter="COLOR",
        value=0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9973336:13",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (0.0, 100.0)
    await light.turn_on(hs_color=(0, 1))
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU9973336:15",
        paramset_key=ParamsetKey.VALUES,
        parameter="COLOR",
        value=200,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9973336:13",
        paramset_key=ParamsetKey.VALUES,
        parameter="LEVEL",
        value=1.0,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert light.hs_color == (0.0, 0.0)
    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU9973336:15", parameter="COLOR", value=201
    )
    assert light.hs_color == (0.0, 0.0)
    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU9973336:15", parameter="COLOR", value=None
    )
    assert light.hs_color == (0.0, 0.0)

    await light.turn_on()
    call_count = len(mock_client.method_calls)
    await light.turn_on()
    assert call_count == len(mock_client.method_calls)

    await light.turn_off()
    call_count = len(mock_client.method_calls)
    await light.turn_off()
    assert call_count == len(mock_client.method_calls)
