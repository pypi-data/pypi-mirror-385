from datetime import datetime

from pydantic import BaseModel, Field


class ConfigModel(BaseModel):
    model_config = {"populate_by_name": True}

    use_army_butt_days: bool = Field(default=False, alias="useArmyButtDays")
    show_completed: bool = Field(default=False, alias="showCompleted")


class EntryModel(BaseModel):
    model_config = {"populate_by_name": True}

    title: str
    date: datetime
    always_show: bool = Field(default=False, alias="alwaysShow")
    show_past_limit: int | None = Field(default=None, alias="showPastLimit")


class DaysModel(BaseModel):
    config: ConfigModel
    entries: list[EntryModel]


class ComputedEventModel(EntryModel):
    days: float
