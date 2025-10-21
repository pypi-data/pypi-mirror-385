from datetime import datetime

import pytest

from army_days.models import ConfigModel, DaysModel, EntryModel


@pytest.fixture
def standard_test_config() -> DaysModel:
    return DaysModel(
        config=ConfigModel(
            use_army_butt_days=False,
            show_completed=False,
        ),
        entries=[
            EntryModel(
                title="Item 1",
                date=datetime(2024, 12, 12),
            ),
            EntryModel(
                title="Item 2",
                date=datetime(2024, 8, 5),
            ),
            EntryModel(
                title="Item 3",
                date=datetime(2024, 8, 6),
            ),
            EntryModel(
                title="Item 4",
                date=datetime(2022, 4, 18),
            ),
            EntryModel(
                title="Item 5",
                date=datetime(2030, 1, 1),
            ),
            EntryModel(
                title="Item 6",
                date=datetime(2024, 8, 4),
            ),
        ],
    )
