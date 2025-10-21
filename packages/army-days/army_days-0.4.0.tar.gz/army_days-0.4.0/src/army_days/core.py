from datetime import datetime

from .models import ComputedEventModel, ConfigModel, DaysModel, EntryModel


def compute_results(days: DaysModel, show_past_days: int | None = None) -> list[ComputedEventModel]:
    results = []
    now = datetime.now()
    current = datetime(now.year, now.month, now.day)
    for entry in days.entries:
        tmp_date = entry.date.astimezone()  # force it to local time
        event_date = datetime(tmp_date.year, tmp_date.month, tmp_date.day)
        time_delta = (event_date - current).days
        new_computed_event = ComputedEventModel(title=entry.title, date=tmp_date, days=time_delta)
        if time_delta > 0 and days.config.use_army_butt_days and now.hour >= 12:
            new_computed_event.days -= 0.5

        # Determine if we should include this event
        should_show = False

        # Always show future events
        if time_delta >= 0:
            should_show = True
        # Past events: check various conditions
        else:
            # Check config-level show_completed
            if days.config.show_completed:
                should_show = True

            # Check CLI parameter --show-past
            if show_past_days is not None:
                # If show_past_days is provided without a value, show all past events
                # If it has a value, only show events within that many days in the past
                if show_past_days == 0 or abs(time_delta) <= show_past_days:
                    should_show = True

            # Check per-event always_show option
            if entry.always_show:
                # If show_past_limit is set, only show if within limit
                if entry.show_past_limit is None or abs(time_delta) <= entry.show_past_limit:
                    should_show = True

        if should_show:
            results.append(new_computed_event)

    results.sort(key=lambda x: x.date)
    return results


def generate_default_configuration() -> DaysModel:
    now = datetime.now()
    if now.month == 2 and now.day == 29:
        new_date = datetime(now.year + 1, 3, 1)
    else:
        new_date = datetime(now.year + 1, now.month, now.day)

    # Create a past date for demonstration
    if now.month == 2 and now.day == 29:
        past_date = datetime(now.year - 1, 3, 1)
    else:
        past_date = datetime(now.year - 1, now.month, now.day)

    return DaysModel(
        config=ConfigModel(),
        entries=[
            EntryModel(title="your one year anniversary of using army-days", date=new_date),
            EntryModel(
                title="example always-shown event (e.g., 'broke my leg')",
                date=past_date,
                always_show=True,
                show_past_limit=400,
            ),
        ],
    )
