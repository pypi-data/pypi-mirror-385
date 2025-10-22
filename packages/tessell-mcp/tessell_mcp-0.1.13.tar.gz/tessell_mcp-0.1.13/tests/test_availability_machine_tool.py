import os
import time
import pytest
from mcp_core.tools.service.availability_machine import *

# Import shared configuration from conftest.py
from conftest import TEST_SERVICE_ID, TEST_AVAILABILITY_MACHINE_ID, SNAPSHOT_NAME

def test_get_availability_machine_id_by_service_id():
    """Test retrieving availability machine ID from service ID."""
    result = get_availability_machine_id(TEST_SERVICE_ID)
    assert result["status_code"] == 200
    assert "availability_machine_id" in result
    assert result["availability_machine_id"] is not None

def test_create_snapshot_tool():
    """Test creating a snapshot with description (default empty if not provided)."""
    description = "Test snapshot created by pytest"
    result = create_snapshot(
        availability_machine_id=TEST_AVAILABILITY_MACHINE_ID,
        name=SNAPSHOT_NAME,
        description=description
    )
    assert result["status_code"] == 201
    assert "snapshot" in result
    snapshot = result["snapshot"]
    # Accept either dict with 'name' or a dict with 'details' containing 'snapshot'
    if isinstance(snapshot, dict) and "details" in snapshot and "snapshot" in snapshot["details"]:
        assert snapshot["details"]["snapshot"] == SNAPSHOT_NAME
    elif isinstance(snapshot, dict) and "name" in snapshot:
        assert snapshot["name"] == SNAPSHOT_NAME
        assert snapshot.get("description", "") == description
    else:
        pytest.fail(f"Unexpected snapshot structure: {snapshot}")

def test_list_snapshots_tool():
    """Test listing snapshots."""
    result = list_snapshots(availability_machine_id=TEST_AVAILABILITY_MACHINE_ID)
    assert result["status_code"] == 200
    assert "snapshots" in result
    assert isinstance(result["snapshots"], dict)
    snapshots = result["snapshots"].get("snapshots")
    assert isinstance(snapshots, list)
    assert len(snapshots) > 0, "No snapshots found; at least one snapshot should be available."

def test_create_snapshot_invalid_am_id():
    """Test creating a snapshot with invalid availability machine ID."""
    result = create_snapshot(availability_machine_id="", name="test")
    assert result["status_code"] == 400
    assert "error" in result

def test_create_snapshot_no_name():
    """Test creating a snapshot without name."""
    result = create_snapshot(availability_machine_id=TEST_AVAILABILITY_MACHINE_ID, name="")
    assert result["status_code"] == 400
    assert "error" in result

def test_get_availability_machine_id_invalid_service():
    """Test getting availability machine ID for invalid service."""
    result = get_availability_machine_id("invalid-service-id")
    assert result["status_code"] != 200
    assert "error" in result
