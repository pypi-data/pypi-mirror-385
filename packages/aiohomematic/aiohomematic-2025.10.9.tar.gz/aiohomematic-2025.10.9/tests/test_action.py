"""Tests for action data points of aiohomematic."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, call

import pytest

from aiohomematic.central import CentralUnit
from aiohomematic.client import Client
from aiohomematic.const import DataPointUsage, ParamsetKey
from aiohomematic.model.generic import DpAction

from tests import const, helper

TEST_DEVICES: dict[str, str] = {
    "VCU9724704": "HmIP-DLD.json",
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
async def test_hmaction(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test HmAction."""
    central, mock_client, _ = central_client_factory
    action: DpAction = cast(
        DpAction,
        central.get_generic_data_point(channel_address="VCU9724704:1", parameter="LOCK_TARGET_LEVEL"),
    )
    assert action.usage == DataPointUsage.NO_CREATE
    assert action.is_readable is False
    assert action.value is None
    assert action.values == ("LOCKED", "UNLOCKED", "OPEN")
    assert action.hmtype == "ENUM"
    await action.send_value(value="OPEN")
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9724704:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LOCK_TARGET_LEVEL",
        value=2,
    )
    await action.send_value(value=1)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU9724704:1",
        paramset_key=ParamsetKey.VALUES,
        parameter="LOCK_TARGET_LEVEL",
        value=1,
    )

    call_count = len(mock_client.method_calls)
    await action.send_value(value=1)
    assert (call_count + 1) == len(mock_client.method_calls)
