from datetime import datetime

from freezegun import freeze_time

from army_days.core import compute_results, generate_default_configuration


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_standard(standard_test_config):
    results = compute_results(standard_test_config)
    assert results is not None
    assert results[0].title == "Item 2"  # verify sorting works
    assert len(results) == 4  # verify past events are excluded
    assert results[2].days == 129.0  # verify that we're *not* using army butt days
    # switch settings...
    standard_test_config.config.use_army_butt_days = True
    standard_test_config.config.show_completed = True
    results = compute_results(standard_test_config)
    assert results is not None
    assert results[0].title == "Item 4"  # verify sorting and showcompleted
    assert len(results) == 6  # verify past events are included
    assert results[0].days == -840.0
    assert results[4].days == 128.5  # army butt days now in use


@freeze_time("2024-08-05T13:00:00")
def test_generate_default_configuration():
    config = generate_default_configuration()
    assert config is not None
    assert config.config.use_army_butt_days is False
    assert config.config.show_completed is False
    assert len(config.entries) == 2
    assert config.entries[0].date == datetime(2025, 8, 5)
    assert config.entries[1].date == datetime(2023, 8, 5)


@freeze_time("2024-02-29T13:00:00")  # LEAP DAY
def test_generate_default_configuration_leap_day():
    config = generate_default_configuration()
    assert config is not None
    assert config.config.use_army_butt_days is False
    assert config.config.show_completed is False
    assert len(config.entries) == 2
    assert config.entries[0].date == datetime(2025, 3, 1)


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_show_past_all(standard_test_config):
    """Test that show_past_days=0 shows all past events"""
    results = compute_results(standard_test_config, show_past_days=0)
    assert len(results) == 6  # all events including past ones
    assert results[0].title == "Item 4"  # oldest past event first
    assert results[0].days == -840.0


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_show_past_limited(standard_test_config):
    """Test that show_past_days with a value limits past events"""
    # Only show past events within 1 day
    results = compute_results(standard_test_config, show_past_days=1)
    assert len(results) == 5  # should exclude Item 4 (840 days ago)
    # Should include Item 6 (1 day ago) and all future events
    assert results[0].title == "Item 6"
    assert results[0].days == -1.0


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_show_past_with_limit_365(standard_test_config):
    """Test show_past_days with 365 day limit"""
    results = compute_results(standard_test_config, show_past_days=365)
    assert len(results) == 5  # Item 4 is 840 days ago, should be excluded
    assert all(event.days >= -365 or event.days >= 0 for event in results)


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_always_show(standard_test_config):
    """Test that events with always_show=True are always displayed"""
    # Add a past event with always_show=True
    from army_days.models import EntryModel

    standard_test_config.entries.append(
        EntryModel(title="Always Shown Past Event", date=datetime(2023, 1, 1), always_show=True)
    )
    results = compute_results(standard_test_config)
    # Should show the always_show event even though show_completed is False
    assert any(event.title == "Always Shown Past Event" for event in results)
    assert len(results) == 5  # 4 future events + 1 always_show past event


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_always_show_with_past_limit(standard_test_config):
    """Test that show_past_limit works with always_show"""
    from army_days.models import EntryModel

    # Add an event that's outside the show_past_limit
    standard_test_config.entries.append(
        EntryModel(
            title="Old Always Show Event",
            date=datetime(2020, 1, 1),
            always_show=True,
            show_past_limit=365,  # Only show if within 365 days
        )
    )
    results = compute_results(standard_test_config)
    # Should NOT show the event because it's more than 365 days ago
    assert not any(event.title == "Old Always Show Event" for event in results)
    assert len(results) == 4  # Only future events

    # Now add one within the limit
    standard_test_config.entries.append(
        EntryModel(
            title="Recent Always Show Event",
            date=datetime(2024, 6, 1),
            always_show=True,
            show_past_limit=365,
        )
    )
    results = compute_results(standard_test_config)
    # Should show the recent event
    assert any(event.title == "Recent Always Show Event" for event in results)
    assert len(results) == 5  # 4 future events + 1 recent always_show event


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_always_show_no_limit(standard_test_config):
    """Test that always_show with no show_past_limit shows event regardless of age"""
    from army_days.models import EntryModel

    # Add a very old event with always_show but no limit
    standard_test_config.entries.append(
        EntryModel(title="Ancient Event", date=datetime(2000, 1, 1), always_show=True, show_past_limit=None)
    )
    results = compute_results(standard_test_config)
    # Should show the ancient event
    assert any(event.title == "Ancient Event" for event in results)


@freeze_time("2024-08-05T13:00:00")
def test_compute_results_combined_show_past_and_always_show(standard_test_config):
    """Test that show_past_days and always_show work together correctly"""
    from army_days.models import EntryModel

    # Add an always_show event with a limit
    standard_test_config.entries.append(
        EntryModel(
            title="Limited Always Show",
            date=datetime(2023, 8, 1),
            always_show=True,
            show_past_limit=400,
        )
    )
    # Add a regular past event
    standard_test_config.entries.append(EntryModel(title="Regular Past Event", date=datetime(2024, 7, 1)))

    # With show_past_days=30, should show:
    # - All future events
    # - "Regular Past Event" (35 days ago, within 30... wait no, it's July 1 to Aug 5 = 35 days, so outside 30)
    # - "Limited Always Show" (369 days ago, within 400 day limit)
    results = compute_results(standard_test_config, show_past_days=30)
    assert any(event.title == "Limited Always Show" for event in results)
    # Regular Past Event is 35 days ago, so should not show with 30 day limit
    assert not any(event.title == "Regular Past Event" for event in results)


@freeze_time("2024-08-05T13:00:00")
def test_generate_default_configuration_includes_past_event():
    """Test that generate_default_configuration includes a past event with always_show"""
    config = generate_default_configuration()
    assert len(config.entries) == 2
    # Check that the second entry has always_show and show_past_limit
    past_event = config.entries[1]
    assert past_event.always_show is True
    assert past_event.show_past_limit == 400
    assert past_event.date == datetime(2023, 8, 5)
