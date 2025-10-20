#!/usr/bin/env python3
"""Tests for strict identity handling in BuildContext and format_hex_id."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.templating.tcl_builder import BuildContext  # noqa: E402
from src.templating.tcl_builder import format_hex_id


def _mk_base_ctx(**over):
    return BuildContext(
        board_name="test_board",
        fpga_part="xc7a35tcsg324-2",
        fpga_family="Artix-7",
        pcie_ip_type="7x",
        max_lanes=4,
        supports_msi=True,
        supports_msix=False,
        **over,
    )


def test_permissive_defaults_still_apply():
    ctx = _mk_base_ctx()
    tc = ctx.to_template_context(strict=False)
    # Legacy defaults appear when not strict
    assert tc["vendor_id"] == 0x10EC
    assert tc["device_id"] == 0x8168
    # Check that metadata tracks defaults
    assert "vendor_id" in tc["context_metadata"]["defaults_used"]
    assert "device_id" in tc["context_metadata"]["defaults_used"]
    assert tc["context_metadata"]["strict_mode"] is False


def test_strict_mode_missing_ids_raises():
    ctx = _mk_base_ctx()
    with pytest.raises(ValueError, match=r"Strict mode enabled.*vendor_id"):
        ctx.to_template_context(strict=True)


def test_explicit_values_tracked():
    ctx = _mk_base_ctx(vendor_id=0x1234, device_id=0x5678)
    tc = ctx.to_template_context(strict=False)
    # Check that explicit values are tracked
    assert tc["context_metadata"]["explicit_values"]["vendor_id"] == 0x1234
    assert tc["context_metadata"]["explicit_values"]["device_id"] == 0x5678
    # No defaults should be used
    assert "vendor_id" not in tc["context_metadata"]["defaults_used"]
    assert "device_id" not in tc["context_metadata"]["defaults_used"]


def test_strict_mode_with_explicit_values():
    ctx = _mk_base_ctx(
        vendor_id=0x1234,
        device_id=0x5678,
        revision_id=0x10,
        class_code=0x030000,
        subsys_vendor_id=0x1234,
        subsys_device_id=0x5678,
        pcie_max_link_speed_code=2,  # Gen2 - 5.0 GT/s
        pcie_max_link_width=4,  # x4 lanes
    )
    tc = ctx.to_template_context(strict=True)
    # Should work fine with all explicit values
    assert tc["vendor_id"] == 0x1234
    assert tc["device_id"] == 0x5678
    assert tc["context_metadata"]["strict_mode"] is True
    # No defaults should be used
    assert len(tc["context_metadata"]["defaults_used"]) == 0


def test_format_hex_id_defaults():
    # Permissive mode returns defaults
    assert format_hex_id(None, 4, permissive=True) == "10EC"
    assert format_hex_id(None, 2, permissive=True) == "15"
    assert format_hex_id(None, 6, permissive=True) == "020000"

    # Strict mode raises on None
    with pytest.raises(ValueError, match=r"Cannot format None value"):
        format_hex_id(None, 4, permissive=False)
