"""
Test for event ordering in DFG with identical timestamps.

This test verifies that the stable sorting approach correctly orders events
throughout the entire case execution, including:
- Start of case execution
- Middle of case execution (the main concern from PR #3)
- End of case execution

The test creates cases with identical timestamps to verify stable sorting behavior.
"""

import pandas as pd

import mpvis


def test_event_ordering_with_identical_timestamps():
    """
    Test that events with identical timestamps are correctly ordered
    throughout the entire case execution, not just at the start.
    """
    # Create a synthetic event log with identical timestamps at different positions
    event_log = pd.DataFrame(
        [
            # Case 1: Identical timestamps in the MIDDLE of execution
            {
                "case_id": "C1",
                "activity": "A",
                "start_time": "2024-01-01 10:00:00",
                "end_time": "2024-01-01 10:00:05",
            },
            {
                "case_id": "C1",
                "activity": "B",
                "start_time": "2024-01-01 10:00:05",
                "end_time": "2024-01-01 10:00:10",
            },
            {
                "case_id": "C1",
                "activity": "C",
                "start_time": "2024-01-01 10:00:10",
                "end_time": "2024-01-01 10:00:10",
            },  # Same timestamp
            {
                "case_id": "C1",
                "activity": "D",
                "start_time": "2024-01-01 10:00:10",
                "end_time": "2024-01-01 10:00:10",
            },  # Same timestamp
            {
                "case_id": "C1",
                "activity": "E",
                "start_time": "2024-01-01 10:00:10",
                "end_time": "2024-01-01 10:00:15",
            },
            # Case 2: Similar pattern to verify consistency
            {
                "case_id": "C2",
                "activity": "A",
                "start_time": "2024-01-01 11:00:00",
                "end_time": "2024-01-01 11:00:05",
            },
            {
                "case_id": "C2",
                "activity": "B",
                "start_time": "2024-01-01 11:00:05",
                "end_time": "2024-01-01 11:00:10",
            },
            {
                "case_id": "C2",
                "activity": "C",
                "start_time": "2024-01-01 11:00:10",
                "end_time": "2024-01-01 11:00:10",
            },  # Same timestamp
            {
                "case_id": "C2",
                "activity": "D",
                "start_time": "2024-01-01 11:00:10",
                "end_time": "2024-01-01 11:00:10",
            },  # Same timestamp
            {
                "case_id": "C2",
                "activity": "E",
                "start_time": "2024-01-01 11:00:10",
                "end_time": "2024-01-01 11:00:15",
            },
            # Case 3: Identical timestamps at START
            {
                "case_id": "C3",
                "activity": "A",
                "start_time": "2024-01-01 12:00:00",
                "end_time": "2024-01-01 12:00:00",
            },  # Same timestamp
            {
                "case_id": "C3",
                "activity": "B",
                "start_time": "2024-01-01 12:00:00",
                "end_time": "2024-01-01 12:00:05",
            },
            {
                "case_id": "C3",
                "activity": "C",
                "start_time": "2024-01-01 12:00:05",
                "end_time": "2024-01-01 12:00:10",
            },
            # Case 4: Identical timestamps at END
            {
                "case_id": "C4",
                "activity": "A",
                "start_time": "2024-01-01 13:00:00",
                "end_time": "2024-01-01 13:00:05",
            },
            {
                "case_id": "C4",
                "activity": "B",
                "start_time": "2024-01-01 13:00:05",
                "end_time": "2024-01-01 13:00:10",
            },
            {
                "case_id": "C4",
                "activity": "C",
                "start_time": "2024-01-01 13:00:10",
                "end_time": "2024-01-01 13:00:15",
            },
            {
                "case_id": "C4",
                "activity": "D",
                "start_time": "2024-01-01 13:00:15",
                "end_time": "2024-01-01 13:00:15",
            },  # Same timestamp
        ]
    )

    # Format the event log
    event_log_format = {
        "case:concept:name": "case_id",
        "concept:name": "activity",
        "time:timestamp": "end_time",
        "start_timestamp": "start_time",
        "org:resource": "",
        "cost:total": "",
    }

    formatted_log = mpvis.log_formatter(event_log, event_log_format)

    # Discover the DFG
    dfg, start_activities, end_activities = mpvis.mpdfg.discover_multi_perspective_dfg(
        log=formatted_log,
        calculate_time=True,
        calculate_cost=False,
    )

    # Verify expected connections exist with correct frequencies
    connections = dfg["connections"]

    # Case 1 & 2 & 4: Check middle connections (C -> D -> E)
    # These are the critical connections that test middle-of-case ordering
    assert ("C", "D") in connections, "Connection C -> D should exist (middle of case)"
    assert connections[("C", "D")]["frequency"] == 3, "C -> D should occur 3 times (Cases 1, 2, 4)"

    assert ("D", "E") in connections, "Connection D -> E should exist (middle of case)"
    assert connections[("D", "E")]["frequency"] == 2, "D -> E should occur twice (Cases 1, 2)"

    # All cases: Check start connections (A -> B)
    assert ("A", "B") in connections, "Connection A -> B should exist (start of case)"
    assert connections[("A", "B")]["frequency"] == 4, "A -> B should occur 4 times (all cases)"

    # Check B -> C connection exists
    assert ("B", "C") in connections, "Connection B -> C should exist"
    assert connections[("B", "C")]["frequency"] == 4, "B -> C should occur 4 times (all cases)"

    # Verify that we don't have unexpected connections (which would indicate wrong ordering)
    # For example, D -> C should NOT exist if ordering is correct
    assert (
        "D",
        "C",
    ) not in connections, "Connection D -> C should NOT exist (would indicate wrong ordering)"

    # Verify start and end activities are correct
    assert "A" in start_activities, "A should be a start activity"
    assert start_activities["A"] == 4, "A should start 4 cases"

    assert "E" in end_activities or "D" in end_activities, "E or D should be end activities"


def test_stable_sort_preserves_original_order():
    """
    Test that stable sorting preserves the original order of rows
    when timestamps are identical.
    """
    # Create a log where the original row order matters
    event_log = pd.DataFrame(
        [
            # Case with events in specific order (row 0, 1, 2, 3)
            {
                "case_id": "C1",
                "activity": "X",
                "start_time": "2024-01-01 10:00:00",
                "end_time": "2024-01-01 10:00:00",
            },
            {
                "case_id": "C1",
                "activity": "Y",
                "start_time": "2024-01-01 10:00:00",
                "end_time": "2024-01-01 10:00:00",
            },
            {
                "case_id": "C1",
                "activity": "Z",
                "start_time": "2024-01-01 10:00:00",
                "end_time": "2024-01-01 10:00:00",
            },
            {
                "case_id": "C1",
                "activity": "W",
                "start_time": "2024-01-01 10:00:00",
                "end_time": "2024-01-01 10:00:05",
            },
        ]
    )

    event_log_format = {
        "case:concept:name": "case_id",
        "concept:name": "activity",
        "time:timestamp": "end_time",
        "start_timestamp": "start_time",
        "org:resource": "",
        "cost:total": "",
    }

    formatted_log = mpvis.log_formatter(event_log, event_log_format)

    dfg, start_activities, end_activities = mpvis.mpdfg.discover_multi_perspective_dfg(
        log=formatted_log,
        calculate_time=True,
        calculate_cost=False,
    )

    connections = dfg["connections"]

    # If stable sort works, we should see X -> Y -> Z -> W in that order
    assert ("X", "Y") in connections, "X -> Y connection should exist (stable sort test)"
    assert ("Y", "Z") in connections, "Y -> Z connection should exist (stable sort test)"
    assert ("Z", "W") in connections, "Z -> W connection should exist (stable sort test)"

    # These should NOT exist if order is preserved
    assert ("Y", "X") not in connections, "Y -> X should NOT exist (would indicate order violation)"
    assert ("Z", "Y") not in connections, "Z -> Y should NOT exist (would indicate order violation)"
