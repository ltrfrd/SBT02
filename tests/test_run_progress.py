# =============================================================================
# tests/test_run_progress.py
# -----------------------------------------------------------------------------
# Purpose:
#   Verify that starting a new run copies stops from the latest route run
#   that already has stops.
#
# Endpoint flow tested:
#   - POST /runs/
#   - POST /stops/
#   - POST /runs/end
#   - POST /runs/start
#   - GET /runs/{run_id}/stops
# =============================================================================


# =============================================================================
# Test: starting a new run copies stops from the latest route run with stops
# =============================================================================
def test_start_run_copies_stops_from_latest_route_run(client):

    # -------------------------------------------------------------------------
    # Create driver
    # -------------------------------------------------------------------------
    driver_response = client.post(
        "/drivers/",
        json={
            "name": "John Driver",
            "email": "john.driver@example.com",
            "phone": "111-222-3333",
        },
    )
    assert driver_response.status_code in (200, 201)
    driver_id = driver_response.json()["id"]  # Created driver ID

    # -------------------------------------------------------------------------
    # Create route
    # -------------------------------------------------------------------------
    route_response = client.post(
        "/routes/",
        json={
            "route_number": "12",
            "unit_number": "BUS-12",
            "driver_id": driver_id,
        },
    )
    assert route_response.status_code in (200, 201)
    route_id = route_response.json()["id"]  # Created route ID

    # -------------------------------------------------------------------------
    # Create source run directly
    # This run will hold the original stops that should be copied later
    # -------------------------------------------------------------------------
    source_run_response = client.post(
        "/runs/",
        json={
            "driver_id": driver_id,
            "route_id": route_id,
            "run_type": "AM",
        },
    )
    assert source_run_response.status_code in (200, 201)
    source_run_id = source_run_response.json()["id"]  # Original run ID

    # -------------------------------------------------------------------------
    # Add stops to the source run
    # -------------------------------------------------------------------------
    stop_1_response = client.post(
        "/stops/",
        json={
            "run_id": source_run_id,
            "sequence": 1,
            "type": "pickup",
            "name": "Stop 1",
            "address": "123 First Street",
            "planned_time": "07:10:00",
            "latitude": 53.5461,
            "longitude": -113.4938,
        },
    )
    assert stop_1_response.status_code in (200, 201)

    stop_2_response = client.post(
        "/stops/",
        json={
            "run_id": source_run_id,
            "sequence": 2,
            "type": "pickup",
            "name": "Stop 2",
            "address": "456 Second Avenue",
            "planned_time": "07:20:00",
            "latitude": 53.5561,
            "longitude": -113.5038,
        },
    )
    assert stop_2_response.status_code in (200, 201)

    # -------------------------------------------------------------------------
    # End the source run so the same driver can start a new active run
    # -------------------------------------------------------------------------
    end_response = client.post(f"/runs/end?run_id={source_run_id}")
    assert end_response.status_code == 200

    # -------------------------------------------------------------------------
    # Start a fresh run on the same route
    # Expected behavior: stops are copied from the latest route run with stops
    # -------------------------------------------------------------------------
    new_run_response = client.post(
        "/runs/start",
        json={
            "driver_id": driver_id,
            "route_id": route_id,
            "run_type": "AM",
        },
    )
    assert new_run_response.status_code in (200, 201)
    new_run_id = new_run_response.json()["id"]  # New active run ID

    assert new_run_id != source_run_id  # Ensure this is a different run

    # -------------------------------------------------------------------------
    # Load copied stops from the new run
    # -------------------------------------------------------------------------
    new_stops_response = client.get(f"/runs/{new_run_id}/stops")
    assert new_stops_response.status_code == 200

    new_stops = new_stops_response.json()
    assert len(new_stops) == 2  # Two stops should be copied

    # -------------------------------------------------------------------------
    # Validate copied stop 1
    # -------------------------------------------------------------------------
    assert new_stops[0]["run_id"] == new_run_id
    assert new_stops[0]["sequence"] == 1
    assert new_stops[0]["name"] == "Stop 1"
    assert new_stops[0]["address"] == "123 First Street"
    assert new_stops[0]["planned_time"] == "07:10:00"
    assert new_stops[0]["latitude"] == 53.5461
    assert new_stops[0]["longitude"] == -113.4938

    # -------------------------------------------------------------------------
    # Validate copied stop 2
    # -------------------------------------------------------------------------
    assert new_stops[1]["run_id"] == new_run_id
    assert new_stops[1]["sequence"] == 2
    assert new_stops[1]["name"] == "Stop 2"
    assert new_stops[1]["address"] == "456 Second Avenue"
    assert new_stops[1]["planned_time"] == "07:20:00"
    assert new_stops[1]["latitude"] == 53.5561
    assert new_stops[1]["longitude"] == -113.5038

# =============================================================================
# tests/test_run_progress.py — Run Progress Tests
# -----------------------------------------------------------------------------
# Responsibilities:
#   - Verify run progress endpoints
#   - Verify stop-copy behavior when starting a new run
#   - Verify by-driver progress fallback uses stored run progress
# =============================================================================


def test_get_run_progress_by_driver_uses_stored_current_stop_sequence(client):
    # -------------------------------------------------------------------------
    # Create a driver
    # -------------------------------------------------------------------------
    driver_res = client.post(
        "/drivers/",
        json={
            "name": "Driver Progress Stored",                         # Driver display name
            "email": "driver_progress_stored@example.com",            # Unique driver email
            "phone": "780-555-1101",                                  # Driver phone
        },
    )
    assert driver_res.status_code in (200, 201)                       # Driver should be created
    driver_id = driver_res.json()["id"]                               # Created driver ID

    # -------------------------------------------------------------------------
    # Create a route
    # -------------------------------------------------------------------------
    route_res = client.post(
        "/routes/",
        json={
            "route_number": "R-PROGRESS-STORED",                      # Unique route number
            "unit_number": "BUS-PROGRESS-01",                         # Required unit number
            "driver_id": driver_id,                                   # Required assigned driver
        },
    )
    assert route_res.status_code in (200, 201)                        # Route should be created
    route_id = route_res.json()["id"]                                 # Created route ID

    # -------------------------------------------------------------------------
    # Create a source run that will provide stops for copy-forward logic
    # -------------------------------------------------------------------------
    seed_run_res = client.post(
        "/runs/",
        json={
            "driver_id": driver_id,                                   # Same driver
            "route_id": route_id,                                     # Same route
            "run_type": "AM",                                         # Run type
        },
    )
    assert seed_run_res.status_code in (200, 201)                     # Seed run should be created
    seed_run_id = seed_run_res.json()["id"]                           # Seed run ID

    # -------------------------------------------------------------------------
    # Add ordered stops to the seed run
    # -------------------------------------------------------------------------
    stop_1_res = client.post(
        "/stops/",
        json={
            "run_id": seed_run_id,                                    # Parent run ID
            "sequence": 1,                                            # First stop
            "type": "pickup",                                         # Stop type
            "name": "Stop 1",                                         # Stop name
            "address": "100 First St",                                # Stop address
            "planned_time": "07:10:00",                               # Planned time
            "latitude": 53.5461,                                      # Latitude
            "longitude": -113.4938,                                   # Longitude
        },
    )
    assert stop_1_res.status_code in (200, 201)                       # First stop should be created

    stop_2_res = client.post(
        "/stops/",
        json={
            "run_id": seed_run_id,                                    # Parent run ID
            "sequence": 2,                                            # Second stop
            "type": "pickup",                                         # Stop type
            "name": "Stop 2",                                         # Stop name
            "address": "200 Second St",                               # Stop address
            "planned_time": "07:20:00",                               # Planned time
            "latitude": 53.5561,                                      # Latitude
            "longitude": -113.4838,                                   # Longitude
        },
    )
    assert stop_2_res.status_code in (200, 201)                       # Second stop should be created

    stop_3_res = client.post(
        "/stops/",
        json={
            "run_id": seed_run_id,                                    # Parent run ID
            "sequence": 3,                                            # Third stop
            "type": "pickup",                                         # Stop type
            "name": "Stop 3",                                         # Stop name
            "address": "300 Third St",                                # Stop address
            "planned_time": "07:30:00",                               # Planned time
            "latitude": 53.5661,                                      # Latitude
            "longitude": -113.4738,                                   # Longitude
        },
    )
    assert stop_3_res.status_code in (200, 201)                       # Third stop should be created

    # -------------------------------------------------------------------------
    # End the seed run so the driver can start a new active run
    # -------------------------------------------------------------------------
    end_res = client.post(f"/runs/end?run_id={seed_run_id}")
    assert end_res.status_code == 200                                 # Seed run should end cleanly

    # -------------------------------------------------------------------------
    # Start a new active run for the same driver/route
    # The endpoint should copy stops from the latest same-route run with stops
    # -------------------------------------------------------------------------
    active_run_res = client.post(
        "/runs/start",
        json={
            "driver_id": driver_id,                                   # Same driver
            "route_id": route_id,                                     # Same route
            "run_type": "AM",                                         # Run type
        },
    )
    assert active_run_res.status_code in (200, 201)                   # Active run should start
    active_run_id = active_run_res.json()["id"]                       # New active run ID

    # -------------------------------------------------------------------------
    # Persist driver progress at stop sequence 2
    # -------------------------------------------------------------------------
    arrive_res = client.post(f"/runs/{active_run_id}/arrive_stop?stop_sequence=2")
    assert arrive_res.status_code == 200                              # Stop arrival should succeed

    # -------------------------------------------------------------------------
    # Call by-driver progress without current_stop_sequence
    # It should use stored run.current_stop_sequence instead of defaulting to 1
    # -------------------------------------------------------------------------
    progress_res = client.get(f"/runs/progress/by_driver?driver_id={driver_id}")
    assert progress_res.status_code == 200                            # Progress lookup should succeed

    data = progress_res.json()                                        # Response payload

       # -------------------------------------------------------------------------
    # Verify stored progress was used
    # -------------------------------------------------------------------------
    assert data["current_stop_sequence"] == 2                         # Current stop should be stored stop
    assert data["current_stop_index"] == 2                            # Stop index should reflect sequence 2
    assert data["total_stops"] == 3                                   # Three copied stops should exist
    assert data["remaining_stops"] == 2                               # Remaining includes current stop and later stops
    assert data["next_stop_sequence"] == 3                            # Next stop should be stop 3