#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from datetime import date, timedelta
from typing import Any, Union
from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic_core import PydanticUndefined
from mindbridgeapi.analysis_period import AnalysisPeriod
from mindbridgeapi.analysis_result_item import AnalysisResultItem
from mindbridgeapi.analysis_source_item import AnalysisSourceItem
from mindbridgeapi.analysis_type_item import AnalysisTypeItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAnalysisCreate,
    ApiAnalysisRead,
    ApiAnalysisUpdate,
    ApiDataTableRead,
)
from mindbridgeapi.task_item import TaskItem


def _empty_analysis_results() -> Generator[AnalysisResultItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure analysis_results is
    not None for the AnalysisItem class

    Yields:
        AnalysisResultItem: Will never yield anything
    """
    yield from ()


def _empty_analysis_sources() -> Generator[AnalysisSourceItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure analysis_sources is
    not None for the AnalysisItem class

    Yields:
        AnalysisSourceItem: Will never yield anything
    """
    yield from ()


def _empty_data_tables() -> Generator[ApiDataTableRead, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure data_tables is not
    None for the AnalysisItem class

    Yields:
        ApiDataTableRead: Will never yield anything
    """
    yield from ()


def _empty_tasks() -> Generator[TaskItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure tasks is not None
    for the AnalysisItem class

    Yields:
        TaskItem: Will never yield anything
    """
    yield from ()


class AnalysisItem(ApiAnalysisRead):
    analysis_periods: list[AnalysisPeriod] = Field().merge_field_infos(
        ApiAnalysisRead.model_fields["analysis_periods"],
        default=PydanticUndefined,
        default_factory=lambda: [AnalysisPeriod()],
    )  # type: ignore[assignment]
    analysis_type_id: str = Field().merge_field_infos(
        ApiAnalysisRead.model_fields["analysis_type_id"],
        default=AnalysisTypeItem.GENERAL_LEDGER,
    )
    archived: bool = Field().merge_field_infos(
        ApiAnalysisRead.model_fields["archived"], default=False
    )
    converted: bool = Field().merge_field_infos(
        ApiAnalysisRead.model_fields["converted"], default=False
    )
    interim: bool = Field().merge_field_infos(
        ApiAnalysisRead.model_fields["interim"], default=False
    )
    periodic: bool = Field().merge_field_infos(
        ApiAnalysisRead.model_fields["periodic"], default=False
    )
    analysis_results: Generator[AnalysisResultItem, None, None] = Field(
        default_factory=_empty_analysis_results, exclude=True
    )
    analysis_sources: Generator[AnalysisSourceItem, None, None] = Field(
        default_factory=_empty_analysis_sources, exclude=True
    )
    data_tables: Generator[ApiDataTableRead, None, None] = Field(
        default_factory=_empty_data_tables, exclude=True
    )
    tasks: Generator[TaskItem, None, None] = Field(
        default_factory=_empty_tasks, exclude=True
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    @field_validator("analysis_periods", mode="after")
    @classmethod
    def _sort_analysis_periods(cls, v: list[AnalysisPeriod]) -> list[AnalysisPeriod]:
        return sorted(v)

    @model_validator(mode="after")
    def _set_default_name(self) -> "AnalysisItem":
        if self.name is None:
            if self.analysis_type_id == AnalysisTypeItem.GENERAL_LEDGER:
                self.name = "General ledger analysis"
            elif (
                self.analysis_type_id == AnalysisTypeItem.NOT_FOR_PROFIT_GENERAL_LEDGER
            ):
                self.name = "Not for profit general ledger analysis"
            elif (
                self.analysis_type_id
                == AnalysisTypeItem.NOT_FOR_PROFIT_GENERAL_LEDGER_FUND
            ):
                self.name = "Not for profit general ledger with funds analysis"

        return self

    def _get_post_json(
        self, out_class: type[Union[ApiAnalysisCreate, ApiAnalysisUpdate]]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiAnalysisCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiAnalysisUpdate)

    def add_prior_periods(self, num_to_add: int = 1) -> None:
        """Adds prior periods (assumes 1 year period)."""
        earliest_period = self.analysis_periods[-1]
        for _ in range(num_to_add):
            end_date = earliest_period.start_date - timedelta(days=1)
            leap_year_day_2024 = date(2024, 2, 29)
            if end_date.replace(year=2024) == leap_year_day_2024:
                start_date = end_date.replace(
                    year=(end_date.year - 1), day=28
                ) + timedelta(days=1)
            else:
                start_date = end_date.replace(year=(end_date.year - 1)) + timedelta(
                    days=1
                )

            earliest_period = AnalysisPeriod(start_date=start_date, end_date=end_date)
            self.analysis_periods.append(earliest_period)
