"""Tests for select data points of aiohomematic."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, call

import pytest

from aiohomematic.central import CentralUnit
from aiohomematic.client import Client
from aiohomematic.const import DataPointUsage, ParamsetKey
from aiohomematic.model.generic import DpSelect
from aiohomematic.model.hub import SysvarDpSelect

from tests import const, helper

TEST_DEVICES: dict[str, str] = {
    "VCU6354483": "HmIP-STHD.json",
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
async def test_hmselect(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test HmSelect."""
    central, mock_client, _ = central_client_factory
    select: DpSelect = cast(
        DpSelect,
        central.get_generic_data_point(channel_address="VCU6354483:1", parameter="WINDOW_STATE"),
    )
    assert select.usage == DataPointUsage.NO_CREATE
    assert select.unit is None
    assert select.min == "CLOSED"
    assert select.max == "OPEN"
    assert select.values == ("CLOSED", "OPEN")
    assert select.value == "CLOSED"
    await select.send_value(value="OPEN")
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6354483:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="WINDOW_STATE",
        value=1,
    )
    assert select.value == "OPEN"
    await central.data_point_event(
        interface_id=const.INTERFACE_ID, channel_address="VCU6354483:1", parameter="WINDOW_STATE", value=0
    )
    assert select.value == "CLOSED"

    await select.send_value(value=3)
    # do not write. value above max
    assert select.value == "CLOSED"

    await select.send_value(value=1)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6354483:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="WINDOW_STATE",
        value=1,
    )
    # do not write. value above max
    assert select.value == "OPEN"

    call_count = len(mock_client.method_calls)
    await select.send_value(value=1)
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
        (const.CCU_MINI_PORT, TEST_DEVICES, True, True, False, None, None),
    ],
)
async def test_hmsysvarselect(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test HmSysvarSelect."""
    central, mock_client, _ = central_client_factory
    select: SysvarDpSelect = cast(SysvarDpSelect, central.get_sysvar_data_point(legacy_name="list_ext"))
    assert select.usage == DataPointUsage.DATA_POINT
    assert select.unit is None
    assert select.min is None
    assert select.max is None
    assert select.values == ("v1", "v2", "v3")
    assert select.value == "v1"
    await select.send_variable(value="v2")
    assert mock_client.method_calls[-1] == call.set_system_variable(legacy_name="list_ext", value=1)
    assert select.value == "v2"
    await select.send_variable(value=3)
    # do not write. value above max
    assert select.value == "v2"
