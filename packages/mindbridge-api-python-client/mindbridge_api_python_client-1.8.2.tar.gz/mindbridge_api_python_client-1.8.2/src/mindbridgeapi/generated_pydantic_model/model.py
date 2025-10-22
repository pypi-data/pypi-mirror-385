#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Annotated, Any, Optional, Union
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel


class Type(str, Enum):
    """The event type that triggered the webhook."""

    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"


class Type1(str, Enum):
    """The event type that triggered the webhook."""

    INGESTION_COMPLETE = "ingestion.complete"
    INGESTION_FAILED = "ingestion.failed"


class Type2(str, Enum):
    """The type of account group error."""

    ERROR_LOWEST_LEVEL_WITH_NO_MAC = "ERROR_LOWEST_LEVEL_WITH_NO_MAC"
    ERROR_LOWEST_LEVEL_WITHOUT_LEVEL_4_MAC = "ERROR_LOWEST_LEVEL_WITHOUT_LEVEL_4_MAC"
    ERROR_INCONSISTENT_SHEET_HIERARCHY = "ERROR_INCONSISTENT_SHEET_HIERARCHY"


class ApiAccountGroupErrorRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    arguments: Annotated[
        Optional[list[str]],
        Field(
            description="A list of values relevant to the type of account group error."
        ),
    ] = None
    type: Annotated[
        Optional[Type2], Field(description="The type of account group error.")
    ] = None


class ApiAccountGroupRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_grouping_id: Annotated[
        Optional[str],
        Field(
            alias="accountGroupingId",
            description="The unique identifier for the account grouping that the account group belongs to.",
        ),
    ] = None
    account_tags: Annotated[
        Optional[list[str]],
        Field(
            alias="accountTags",
            description="A list of account tags assigned to this account group.",
        ),
    ] = None
    code: Annotated[
        Optional[str], Field(description="The account code for this account group.")
    ] = None
    description: Annotated[
        Optional[dict[str, str]],
        Field(description="A description of the account code for this account group."),
    ] = None
    errors: Annotated[
        Optional[list[ApiAccountGroupErrorRead]],
        Field(description="A list of errors associated with this account group."),
    ] = None
    hierarchy: Annotated[
        Optional[list[str]],
        Field(description="A list of the parent codes for this account group."),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    lowest_level: Annotated[Optional[bool], Field(alias="lowestLevel")] = None
    mac_code: Annotated[
        Optional[str],
        Field(
            alias="macCode", description="The MAC code mapped to this account group."
        ),
    ] = None
    order_index: Annotated[
        Optional[int],
        Field(
            alias="orderIndex",
            description="The order in which this account group is displayed, relative to other account groups with the same parent.",
        ),
    ] = None
    parent_code: Annotated[
        Optional[str],
        Field(
            alias="parentCode", description="The parent code for this account group."
        ),
    ] = None
    published_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="publishedDate",
            description="The date this account group was published. If not set, this account group is not published.\n\nPublished account groups cannot be updated.",
        ),
    ] = None


class ApiAccountGroupUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_tags: Annotated[
        Optional[list[str]],
        Field(
            alias="accountTags",
            description="A list of account tags assigned to this account group.",
        ),
    ] = None
    mac_code: Annotated[
        Optional[str],
        Field(
            alias="macCode", description="The MAC code mapped to this account group."
        ),
    ] = None


class PublishStatus(str, Enum):
    """The current status of the account grouping."""

    DRAFT = "DRAFT"
    UNPUBLISHED_CHANGES = "UNPUBLISHED_CHANGES"
    PUBLISHED = "PUBLISHED"


class ApiAccountGroupingUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    archived: Annotated[
        Optional[bool],
        Field(description="When `true`, the account grouping is archived."),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of the account grouping.")
    ] = None
    publish_status: Annotated[
        Optional[PublishStatus],
        Field(
            alias="publishStatus",
            description="The current status of the account grouping.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class Status(str, Enum):
    """Indicates the current status of the account mapping."""

    MANUAL = "MANUAL"
    MAC_CODE = "MAC_CODE"
    MODIFIED_MAC = "MODIFIED_MAC"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    UNMAPPED = "UNMAPPED"
    USED = "USED"
    UNUSED = "UNUSED"


class ApiAccountMappingUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_tags: Annotated[
        Optional[list[str]],
        Field(
            alias="accountTags",
            description="A list of account tags associated with this account.",
        ),
    ] = None
    code: Annotated[
        Optional[str],
        Field(description="The account grouping code mapped to this account."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class Frequency(str, Enum):
    """The frequency with which your client's financial data is reported."""

    ANNUAL = "ANNUAL"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    QUARTERLY = "QUARTERLY"
    MONTHLY = "MONTHLY"
    THIRTEEN_PERIODS = "THIRTEEN_PERIODS"


class ApiAccountingPeriodCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fiscal_start_day: Annotated[
        Optional[int],
        Field(
            alias="fiscalStartDay",
            description="The date of the month that the fiscal period begins.",
        ),
    ] = None
    fiscal_start_month: Annotated[
        Optional[int],
        Field(
            alias="fiscalStartMonth",
            description="The month that the fiscal period begins.",
        ),
    ] = None
    frequency: Annotated[
        Optional[Frequency],
        Field(
            description="The frequency with which your client's financial data is reported."
        ),
    ] = None


class ApiAccountingPeriodRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fiscal_start_day: Annotated[
        Optional[int],
        Field(
            alias="fiscalStartDay",
            description="The date of the month that the fiscal period begins.",
        ),
    ] = None
    fiscal_start_month: Annotated[
        Optional[int],
        Field(
            alias="fiscalStartMonth",
            description="The month that the fiscal period begins.",
        ),
    ] = None
    frequency: Annotated[
        Optional[Frequency],
        Field(
            description="The frequency with which your client's financial data is reported."
        ),
    ] = None


class ApiAccountingPeriodUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fiscal_start_day: Annotated[
        Optional[int],
        Field(
            alias="fiscalStartDay",
            description="The date of the month that the fiscal period begins.",
        ),
    ] = None
    fiscal_start_month: Annotated[
        Optional[int],
        Field(
            alias="fiscalStartMonth",
            description="The month that the fiscal period begins.",
        ),
    ] = None
    frequency: Annotated[
        Optional[Frequency],
        Field(
            description="The frequency with which your client's financial data is reported."
        ),
    ] = None


class ApiAmbiguousColumnRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ambiguous_formats: Annotated[
        Optional[list[str]],
        Field(
            alias="ambiguousFormats",
            description="A list of ambiguous formats detected.",
        ),
    ] = None
    position: Annotated[
        Optional[int],
        Field(description="The position of the column with the resolution."),
    ] = None
    selected_format: Annotated[
        Optional[str],
        Field(
            alias="selectedFormat",
            description="The data format to be used in case of ambiguity.",
        ),
    ] = None


class ApiAmbiguousColumnUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    position: Annotated[
        Optional[int],
        Field(description="The position of the column with the resolution."),
    ] = None
    selected_format: Annotated[
        Optional[str],
        Field(
            alias="selectedFormat",
            description="The data format to be used in case of ambiguity.",
        ),
    ] = None


class ApiAnalysisImportantColumnRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    column_name: Annotated[
        Optional[str],
        Field(
            alias="columnName",
            description="The name of the column as it appears in the imported file.",
        ),
    ] = None
    field: Annotated[
        Optional[str], Field(description="The name of the additional data column.")
    ] = None


class ApiAnalysisPeriodGapRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_period_id: Annotated[
        Optional[str],
        Field(alias="analysisPeriodId", description="Identifies the analysis period."),
    ] = None
    days: Annotated[
        Optional[int],
        Field(description="The number of days between two analysis periods."),
    ] = None
    previous_analysis_period_id: Annotated[
        Optional[str],
        Field(
            alias="previousAnalysisPeriodId",
            description="Identifies the previous analysis period relevant to the current analysis period.",
        ),
    ] = None


class ApiAnalysisPeriodCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    end_date: Annotated[
        Optional[date],
        Field(
            alias="endDate", description="The last day of the period under analysis."
        ),
    ] = None
    interim_as_at_date: Annotated[
        Optional[date],
        Field(
            alias="interimAsAtDate",
            description="The last day of the interim period under analysis.",
        ),
    ] = None
    start_date: Annotated[
        Optional[date],
        Field(
            alias="startDate", description="The first day of the period under analysis."
        ),
    ] = None


class ApiAnalysisPeriodRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    end_date: Annotated[
        Optional[date],
        Field(
            alias="endDate", description="The last day of the period under analysis."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    interim_as_at_date: Annotated[
        Optional[date],
        Field(
            alias="interimAsAtDate",
            description="The last day of the interim period under analysis.",
        ),
    ] = None
    start_date: Annotated[
        Optional[date],
        Field(
            alias="startDate", description="The first day of the period under analysis."
        ),
    ] = None


class ApiAnalysisPeriodUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    end_date: Annotated[
        Optional[date],
        Field(
            alias="endDate", description="The last day of the period under analysis."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    interim_as_at_date: Annotated[
        Optional[date],
        Field(
            alias="interimAsAtDate",
            description="The last day of the interim period under analysis.",
        ),
    ] = None
    start_date: Annotated[
        Optional[date],
        Field(
            alias="startDate", description="The first day of the period under analysis."
        ),
    ] = None


class Status1(str, Enum):
    """The current state of the analysis source."""

    IMPORTING = "IMPORTING"
    UPLOADING = "UPLOADING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class ApiAnalysisSourceStatusRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_source_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisSourceTypeId",
            description="Identifies the analysis source type.",
        ),
    ] = None
    period_id: Annotated[
        Optional[str],
        Field(
            alias="periodId",
            description="Identifies the analysis period within the analysis.",
        ),
    ] = None
    source_id: Annotated[
        Optional[str],
        Field(alias="sourceId", description="Identifies the analysis source object."),
    ] = None
    status: Annotated[
        Optional[Status1],
        Field(description="The current state of the analysis source."),
    ] = None


class Feature(str, Enum):
    FORMAT_DETECTION = "FORMAT_DETECTION"
    DATA_VALIDATION = "DATA_VALIDATION"
    COLUMN_MAPPING = "COLUMN_MAPPING"
    EFFECTIVE_DATE_METRICS = "EFFECTIVE_DATE_METRICS"
    TRANSACTION_ID_SELECTION = "TRANSACTION_ID_SELECTION"
    PARSE = "PARSE"
    CONFIRM_SETTINGS = "CONFIRM_SETTINGS"
    REVIEW_FUNDS = "REVIEW_FUNDS"


class TargetWorkflowState(str, Enum):
    """The state that the current workflow will advance to."""

    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    STARTED = "STARTED"
    DETECTING_FORMAT = "DETECTING_FORMAT"
    ANALYZING_COLUMNS = "ANALYZING_COLUMNS"
    CHECKING_INTEGRITY = "CHECKING_INTEGRITY"
    PARSING = "PARSING"
    ANALYZING_EFFECTIVE_DATE_METRICS = "ANALYZING_EFFECTIVE_DATE_METRICS"
    FORMAT_DETECTION_COMPLETED = "FORMAT_DETECTION_COMPLETED"
    COLUMN_MAPPINGS_CONFIRMED = "COLUMN_MAPPINGS_CONFIRMED"
    SETTINGS_CONFIRMED = "SETTINGS_CONFIRMED"
    ANALYSIS_PERIOD_SELECTED = "ANALYSIS_PERIOD_SELECTED"
    FUNDS_REVIEWED = "FUNDS_REVIEWED"
    RUNNING = "RUNNING"
    UNPACK_COMPLETE = "UNPACK_COMPLETE"
    UPLOADED = "UPLOADED"
    FORMAT_DETECTED = "FORMAT_DETECTED"
    COLUMNS_ANALYZED = "COLUMNS_ANALYZED"
    INTEGRITY_CHECKED = "INTEGRITY_CHECKED"
    PARSED = "PARSED"
    AUTHENTICATED = "AUTHENTICATED"
    CONFIGURED = "CONFIGURED"
    EFFECTIVE_DATE_METRICS_ANALYZED = "EFFECTIVE_DATE_METRICS_ANALYZED"
    DATA_VALIDATION_CONFIRMED = "DATA_VALIDATION_CONFIRMED"


class DetectedFormat(str, Enum):
    """The data format that MindBridge detected."""

    QUICKBOOKS_JOURNAL = "QUICKBOOKS_JOURNAL"
    QUICKBOOKS_JOURNAL_2024 = "QUICKBOOKS_JOURNAL_2024"
    QUICKBOOKS_TRANSACTION_DETAIL_BY_ACCOUNT = (
        "QUICKBOOKS_TRANSACTION_DETAIL_BY_ACCOUNT"
    )
    SAGE50_LEDGER = "SAGE50_LEDGER"
    SAGE50_TRANSACTIONS = "SAGE50_TRANSACTIONS"
    CCH_ACCOUNT_LIST = "CCH_ACCOUNT_LIST"
    MS_DYNAMICS_JOURNAL = "MS_DYNAMICS_JOURNAL"
    SAGE50_UK = "SAGE50_UK"


class WorkflowState(str, Enum):
    """The current state of the workflow."""

    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    STARTED = "STARTED"
    DETECTING_FORMAT = "DETECTING_FORMAT"
    ANALYZING_COLUMNS = "ANALYZING_COLUMNS"
    CHECKING_INTEGRITY = "CHECKING_INTEGRITY"
    PARSING = "PARSING"
    ANALYZING_EFFECTIVE_DATE_METRICS = "ANALYZING_EFFECTIVE_DATE_METRICS"
    FORMAT_DETECTION_COMPLETED = "FORMAT_DETECTION_COMPLETED"
    COLUMN_MAPPINGS_CONFIRMED = "COLUMN_MAPPINGS_CONFIRMED"
    SETTINGS_CONFIRMED = "SETTINGS_CONFIRMED"
    ANALYSIS_PERIOD_SELECTED = "ANALYSIS_PERIOD_SELECTED"
    FUNDS_REVIEWED = "FUNDS_REVIEWED"
    RUNNING = "RUNNING"
    UNPACK_COMPLETE = "UNPACK_COMPLETE"
    UPLOADED = "UPLOADED"
    FORMAT_DETECTED = "FORMAT_DETECTED"
    COLUMNS_ANALYZED = "COLUMNS_ANALYZED"
    INTEGRITY_CHECKED = "INTEGRITY_CHECKED"
    PARSED = "PARSED"
    AUTHENTICATED = "AUTHENTICATED"
    CONFIGURED = "CONFIGURED"
    EFFECTIVE_DATE_METRICS_ANALYZED = "EFFECTIVE_DATE_METRICS_ANALYZED"
    DATA_VALIDATION_CONFIRMED = "DATA_VALIDATION_CONFIRMED"


class PreflightError(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    NOT_READY = "NOT_READY"
    ARCHIVED = "ARCHIVED"
    REQUIRED_FILES_MISSING = "REQUIRED_FILES_MISSING"
    SOURCES_NOT_READY = "SOURCES_NOT_READY"
    SOURCE_ERROR = "SOURCE_ERROR"
    UNVERIFIED_ACCOUNT_MAPPINGS = "UNVERIFIED_ACCOUNT_MAPPINGS"
    ANALYSIS_PERIOD_OVERLAP = "ANALYSIS_PERIOD_OVERLAP"
    SOURCE_WARNINGS_PRESENT = "SOURCE_WARNINGS_PRESENT"


class Status2(str, Enum):
    """The current state of the analysis."""

    NOT_STARTED = "NOT_STARTED"
    IMPORTING_FILE = "IMPORTING_FILE"
    PREPARING_DATA = "PREPARING_DATA"
    PROCESSING = "PROCESSING"
    CONSOLIDATING_RESULTS = "CONSOLIDATING_RESULTS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApiAnalysisStatusRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="Identifies the associated analysis."),
    ] = None
    analysis_type_id: Annotated[
        Optional[str],
        Field(alias="analysisTypeId", description="Identifies the type of analysis."),
    ] = None
    available_features: Annotated[
        Optional[dict[str, bool]],
        Field(
            alias="availableFeatures",
            description="Details about the various analysis capabilities available in MindBridge. [Learn more](https://support.mindbridge.ai/hc/en-us/articles/360056395234)",
        ),
    ] = None
    inferred_account_mapping_count: Annotated[
        Optional[int],
        Field(
            alias="inferredAccountMappingCount",
            description="The number of inferred account mapping; this can be considered a warning on partial matches.",
        ),
    ] = None
    mapped_account_mapping_count: Annotated[
        Optional[int],
        Field(
            alias="mappedAccountMappingCount",
            description="The number of mapped accounts.",
        ),
    ] = None
    preflight_errors: Annotated[
        Optional[list[PreflightError]],
        Field(
            alias="preflightErrors",
            description="The errors that occurred before the analysis was run.",
        ),
    ] = None
    re_run_ready: Annotated[
        Optional[bool],
        Field(
            alias="reRunReady",
            description="Indicates whether or not the analysis is ready to be run again.",
        ),
    ] = None
    ready: Annotated[
        Optional[bool],
        Field(description="Indicates whether or not the analysis is ready to be run."),
    ] = None
    source_statuses: Annotated[
        Optional[list[ApiAnalysisSourceStatusRead]],
        Field(
            alias="sourceStatuses",
            description="Details about the state of each analysis source.",
        ),
    ] = None
    status: Annotated[
        Optional[Status2], Field(description="The current state of the analysis.")
    ] = None
    unmapped_account_mapping_count: Annotated[
        Optional[int],
        Field(
            alias="unmappedAccountMappingCount",
            description="The number of unmapped accounts.",
        ),
    ] = None


class ApiAnalysisCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_periods: Annotated[
        Optional[list[ApiAnalysisPeriodCreate]],
        Field(
            alias="analysisPeriods",
            description="Details about the specific analysis periods under audit.",
        ),
    ] = None
    analysis_type_id: Annotated[
        Optional[str],
        Field(alias="analysisTypeId", description="Identifies the type of analysis."),
    ] = None
    currency_code: Annotated[
        Optional[str],
        Field(
            alias="currencyCode",
            description="The currency to be displayed across the analysis results.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    interim: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis is using an interim time frame."
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the analysis.", max_length=80, min_length=0),
    ] = None
    periodic: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis is using a periodic time frame."
        ),
    ] = None
    reference_id: Annotated[
        Optional[str],
        Field(
            alias="referenceId",
            description="A reference ID to identify the analysis.",
            max_length=256,
            min_length=0,
        ),
    ] = None


class ApiAnalysisUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_periods: Annotated[
        Optional[list[ApiAnalysisPeriodUpdate]],
        Field(
            alias="analysisPeriods",
            description="Details about the specific analysis periods under audit.",
        ),
    ] = None
    archived: Annotated[
        Optional[bool],
        Field(description="Indicates whether or not the analysis has been archived."),
    ] = None
    currency_code: Annotated[
        Optional[str],
        Field(
            alias="currencyCode",
            description="The currency to be displayed across the analysis results.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the analysis.", max_length=80, min_length=0),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class Permission(str, Enum):
    API_ORGANIZATIONS_READ = "api.organizations.read"
    API_ORGANIZATIONS_WRITE = "api.organizations.write"
    API_ORGANIZATIONS_DELETE = "api.organizations.delete"
    API_ENGAGEMENTS_READ = "api.engagements.read"
    API_ENGAGEMENTS_WRITE = "api.engagements.write"
    API_ENGAGEMENTS_DELETE = "api.engagements.delete"
    API_ANALYSES_READ = "api.analyses.read"
    API_ANALYSES_WRITE = "api.analyses.write"
    API_ANALYSES_DELETE = "api.analyses.delete"
    API_ANALYSES_RUN = "api.analyses.run"
    API_ANALYSIS_SOURCES_READ = "api.analysis-sources.read"
    API_ANALYSIS_SOURCES_WRITE = "api.analysis-sources.write"
    API_ANALYSIS_SOURCES_DELETE = "api.analysis-sources.delete"
    API_FILE_MANAGER_READ = "api.file-manager.read"
    API_FILE_MANAGER_WRITE = "api.file-manager.write"
    API_FILE_MANAGER_DELETE = "api.file-manager.delete"
    API_LIBRARIES_READ = "api.libraries.read"
    API_LIBRARIES_WRITE = "api.libraries.write"
    API_LIBRARIES_DELETE = "api.libraries.delete"
    API_ACCOUNT_GROUPINGS_READ = "api.account-groupings.read"
    API_ACCOUNT_GROUPINGS_WRITE = "api.account-groupings.write"
    API_ACCOUNT_GROUPINGS_DELETE = "api.account-groupings.delete"
    API_ENGAGEMENT_ACCOUNT_GROUPINGS_READ = "api.engagement-account-groupings.read"
    API_ENGAGEMENT_ACCOUNT_GROUPINGS_WRITE = "api.engagement-account-groupings.write"
    API_ENGAGEMENT_ACCOUNT_GROUPINGS_DELETE = "api.engagement-account-groupings.delete"
    API_USERS_READ = "api.users.read"
    API_USERS_WRITE = "api.users.write"
    API_USERS_DELETE = "api.users.delete"
    API_DATA_TABLES_READ = "api.data-tables.read"
    API_API_TOKENS_READ = "api.api-tokens.read"
    API_API_TOKENS_WRITE = "api.api-tokens.write"
    API_API_TOKENS_DELETE = "api.api-tokens.delete"
    API_TASKS_READ = "api.tasks.read"
    API_TASKS_WRITE = "api.tasks.write"
    API_TASKS_DELETE = "api.tasks.delete"
    API_ADMIN_REPORTS_RUN = "api.admin-reports.run"
    API_ANALYSIS_TYPES_READ = "api.analysis-types.read"
    API_ANALYSIS_SOURCE_TYPES_READ = "api.analysis-source-types.read"
    API_ANALYSIS_TYPE_CONFIGURATION_READ = "api.analysis-type-configuration.read"
    API_ANALYSIS_TYPE_CONFIGURATION_WRITE = "api.analysis-type-configuration.write"
    API_ANALYSIS_TYPE_CONFIGURATION_DELETE = "api.analysis-type-configuration.delete"
    API_RISK_RANGES_READ = "api.risk-ranges.read"
    API_RISK_RANGES_WRITE = "api.risk-ranges.write"
    API_RISK_RANGES_DELETE = "api.risk-ranges.delete"
    API_FILTERS_READ = "api.filters.read"
    API_FILTERS_WRITE = "api.filters.write"
    API_FILTERS_DELETE = "api.filters.delete"
    API_FILE_INFOS_READ = "api.file-infos.read"
    API_WEBHOOKS_READ = "api.webhooks.read"
    API_WEBHOOKS_WRITE = "api.webhooks.write"
    API_WEBHOOKS_DELETE = "api.webhooks.delete"
    SCIM_USER_READ = "scim.user.read"
    SCIM_USER_WRITE = "scim.user.write"
    SCIM_USER_DELETE = "scim.user.delete"
    SCIM_USER_SCHEMA = "scim.user.schema"


class ApiApiTokenCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    allowed_addresses: Annotated[
        Optional[list[str]],
        Field(
            alias="allowedAddresses",
            description="Indicates the set of addresses that are allowed to use this token. If empty, any address may use it.",
        ),
    ] = None
    expiry: Annotated[
        Optional[AwareDatetime],
        Field(description="The day on which the API token expires."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The token record’s name. This will also be used as the API Token User’s name."
        ),
    ] = None
    permissions: Annotated[
        Optional[list[Permission]],
        Field(
            description="The set of permissions that inform which endpoints this token is authorized to access."
        ),
    ] = None


class ApiApiTokenUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str],
        Field(
            description="The token record’s name. This will also be used as the API Token User’s name."
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class EntityType(str, Enum):
    """Identifies the entity type used in the job."""

    ORGANIZATION = "ORGANIZATION"
    ENGAGEMENT = "ENGAGEMENT"
    ANALYSIS = "ANALYSIS"
    ANALYSIS_RESULT = "ANALYSIS_RESULT"
    ANALYSIS_SOURCE = "ANALYSIS_SOURCE"
    FILE_RESULT = "FILE_RESULT"
    GDPDU_UNPACK_JOB = "GDPDU_UNPACK_JOB"
    ACCOUNT_GROUPING = "ACCOUNT_GROUPING"
    ENGAGEMENT_ACCOUNT_GROUPING = "ENGAGEMENT_ACCOUNT_GROUPING"
    FILE_MANAGER_FILE = "FILE_MANAGER_FILE"


class Status3(str, Enum):
    """Indicates the current state of the job."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class Type3(str, Enum):
    """Indicates the type of job being run."""

    ANALYSIS_RUN = "ANALYSIS_RUN"
    ANALYSIS_SOURCE_INGESTION = "ANALYSIS_SOURCE_INGESTION"
    ADMIN_REPORT = "ADMIN_REPORT"
    DATA_TABLE_EXPORT = "DATA_TABLE_EXPORT"
    ANALYSIS_ROLL_FORWARD = "ANALYSIS_ROLL_FORWARD"
    GDPDU_UNPACK_JOB = "GDPDU_UNPACK_JOB"
    ACCOUNT_GROUPING_EXPORT = "ACCOUNT_GROUPING_EXPORT"
    ACCOUNT_MAPPING_EXPORT = "ACCOUNT_MAPPING_EXPORT"
    DATA_TRANSFORMATION_JOB = "DATA_TRANSFORMATION_JOB"


class State(str, Enum):
    """Validation state of the metric within its context."""

    PASS_ = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class ApiChunkedFilePart(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    offset: Annotated[
        Optional[int],
        Field(
            description="Indicates the start position of the file part in the chunked file.",
            ge=0,
        ),
    ] = None
    size: Annotated[
        Optional[int], Field(description="The size of the file part.", ge=0)
    ] = None


class ApiChunkedFilePartRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    offset: Annotated[
        Optional[int],
        Field(
            description="Indicates the start position of the file part in the chunked file.",
            ge=0,
        ),
    ] = None
    size: Annotated[
        Optional[int], Field(description="The size of the file part.", ge=0)
    ] = None


class ApiChunkedFileCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str], Field(description="The name of the chunked file.")
    ] = None
    size: Annotated[
        Optional[int], Field(description="The size of the chunked file.", ge=0)
    ] = None


class ApiColumnDateTimeFormat(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    custom_format_pattern: Annotated[
        Optional[str],
        Field(
            alias="customFormatPattern", description="The pattern of this date format."
        ),
    ] = None
    sample_converted_values: Annotated[
        Optional[list[AwareDatetime]],
        Field(
            alias="sampleConvertedValues",
            description="A list of date time values derived by parsing the text using this format.",
        ),
    ] = None
    sample_raw_values: Annotated[
        Optional[list[str]],
        Field(alias="sampleRawValues", description="A list of values in this column."),
    ] = None
    selected: Annotated[
        Optional[bool],
        Field(
            description="If true, this format was selected during column mapping as the correct format for this column."
        ),
    ] = None


class ApiColumnDateTimeFormatRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    custom_format_pattern: Annotated[
        Optional[str],
        Field(
            alias="customFormatPattern", description="The pattern of this date format."
        ),
    ] = None
    sample_converted_values: Annotated[
        Optional[list[AwareDatetime]],
        Field(
            alias="sampleConvertedValues",
            description="A list of date time values derived by parsing the text using this format.",
        ),
    ] = None
    sample_raw_values: Annotated[
        Optional[list[str]],
        Field(alias="sampleRawValues", description="A list of values in this column."),
    ] = None
    selected: Annotated[
        Optional[bool],
        Field(
            description="If true, this format was selected during column mapping as the correct format for this column."
        ),
    ] = None


class Type5(str, Enum):
    """The type of data this column accepts."""

    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    UNKNOWN = "UNKNOWN"
    FLOAT64 = "FLOAT64"


class ApiColumnDefinitionRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    allow_blanks: Annotated[
        Optional[bool],
        Field(
            alias="allowBlanks",
            description="Indicates whether or not this column allows the source column to contain blank values.",
        ),
    ] = None
    alternative_mappings: Annotated[
        Optional[list[str]],
        Field(
            alias="alternativeMappings",
            description="A list of alternative mappings, identified by their `mindbridgeFieldName`. If all of the alternatives are mapped, then this mapping’s `required` constraint is considered satisfied. \n\n**Note**: This column may not be mapped if any alternative is also mapped.",
        ),
    ] = None
    default_value: Annotated[
        Optional[str],
        Field(
            alias="defaultValue",
            description="A value that is substituted for blank values when `allowBlanks` is false.",
        ),
    ] = None
    mindbridge_field_name: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeFieldName",
            description="The internal name of the analysis source type’s column.",
        ),
    ] = None
    mindbridge_field_name_for_non_mac_groupings: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeFieldNameForNonMacGroupings",
            description="The alternative column name when a non-MAC based account grouping is used.",
        ),
    ] = None
    required: Annotated[
        Optional[bool],
        Field(description="Indicates whether or not this column is required."),
    ] = None
    required_for_non_mac_groupings: Annotated[
        Optional[bool],
        Field(
            alias="requiredForNonMacGroupings",
            description="Indicates whether or not this column is required when using a non-MAC based account grouping.",
        ),
    ] = None
    type: Annotated[
        Optional[Type5], Field(description="The type of data this column accepts.")
    ] = None


class MappingType(str, Enum):
    """The method used to map the column."""

    AUTO = "AUTO"
    NOT_MAPPED = "NOT_MAPPED"
    MANUAL = "MANUAL"


class ApiColumnMappingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_column_name: Annotated[
        Optional[str],
        Field(
            alias="additionalColumnName",
            description="Additional columns of data that were added to the analysis.",
        ),
    ] = None
    field: Annotated[Optional[str], Field(description="The column name.")] = None
    mapping_type: Annotated[
        Optional[MappingType],
        Field(alias="mappingType", description="The method used to map the column."),
    ] = None
    mindbridge_field: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeField",
            description="The MindBridge field that the data column was mapped to.",
        ),
    ] = None
    position: Annotated[
        Optional[int], Field(description="The position of the column mapping.")
    ] = None


class ApiColumnMappingUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_column_name: Annotated[
        Optional[str],
        Field(
            alias="additionalColumnName",
            description="Additional columns of data that were added to the analysis.",
        ),
    ] = None
    mindbridge_field: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeField",
            description="The MindBridge field that the data column was mapped to.",
        ),
    ] = None
    position: Annotated[
        Optional[int], Field(description="The position of the column mapping.")
    ] = None


class ApiCsvConfiguration(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    delimiter: Annotated[
        Optional[str], Field(description="The character used to separate entries.")
    ] = None
    quote: Annotated[
        Optional[str], Field(description="The character used to encapsulate an entry.")
    ] = None
    quote_escape: Annotated[
        Optional[str],
        Field(
            alias="quoteEscape",
            description="The character used to escape the quote character.",
        ),
    ] = None
    quote_escape_escape: Annotated[
        Optional[str],
        Field(
            alias="quoteEscapeEscape",
            description="The character used to escape the quote escape character.",
        ),
    ] = None


class ApiCurrencyFormat(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ambiguous_delimiters: Annotated[
        Optional[list[str]],
        Field(
            alias="ambiguousDelimiters",
            description="A list of possible delimiter characters, if multiple possible candidates are available.",
        ),
    ] = None
    decimal_character: Annotated[
        Optional[str],
        Field(
            alias="decimalCharacter",
            description="The character used as a decimal separator.",
        ),
    ] = None
    example: Annotated[Optional[str], Field(description="An example value.")] = None
    non_decimal_delimiters: Annotated[
        Optional[list[str]],
        Field(
            alias="nonDecimalDelimiters",
            description="Non decimal separator special characters, including currency and grouping characters.",
        ),
    ] = None


class ApiCurrencyFormatRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ambiguous_delimiters: Annotated[
        Optional[list[str]],
        Field(
            alias="ambiguousDelimiters",
            description="A list of possible delimiter characters, if multiple possible candidates are available.",
        ),
    ] = None
    decimal_character: Annotated[
        Optional[str],
        Field(
            alias="decimalCharacter",
            description="The character used as a decimal separator.",
        ),
    ] = None
    example: Annotated[Optional[str], Field(description="An example value.")] = None
    non_decimal_delimiters: Annotated[
        Optional[list[str]],
        Field(
            alias="nonDecimalDelimiters",
            description="Non decimal separator special characters, including currency and grouping characters.",
        ),
    ] = None


class ApiDataPreview(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    column: Annotated[
        Optional[int], Field(description="The column index within the row.")
    ] = None
    data: Annotated[
        Optional[str], Field(description="The value within the target row.")
    ] = None
    row: Annotated[
        Optional[int], Field(description="The row number within the table.")
    ] = None


class ApiDataPreviewRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    column: Annotated[
        Optional[int], Field(description="The column index within the row.")
    ] = None
    data: Annotated[
        Optional[str], Field(description="The value within the target row.")
    ] = None
    row: Annotated[
        Optional[int], Field(description="The row number within the table.")
    ] = None


class Type6(str, Enum):
    """The type of data found in the column."""

    STRING = "STRING"
    DATE = "DATE"
    DATE_TIME = "DATE_TIME"
    BOOLEAN = "BOOLEAN"
    INT16 = "INT16"
    INT32 = "INT32"
    INT64 = "INT64"
    FLOAT32 = "FLOAT32"
    FLOAT64 = "FLOAT64"
    MONEY_100 = "MONEY_100"
    PERCENTAGE_FIXED_POINT = "PERCENTAGE_FIXED_POINT"
    ARRAY_STRINGS = "ARRAY_STRINGS"
    ARRAY_INT64 = "ARRAY_INT64"
    KEYWORD_SEARCH = "KEYWORD_SEARCH"
    OBJECTID = "OBJECTID"
    BOOLEAN_FLAGS = "BOOLEAN_FLAGS"
    MAP_SCALARS = "MAP_SCALARS"
    LEGACY_ACCOUNT_TAG_EFFECTS = "LEGACY_ACCOUNT_TAG_EFFECTS"
    JSONB = "JSONB"


class ApiDataTableColumnRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    case_insensitive_prefix_search: Annotated[
        Optional[bool],
        Field(
            alias="caseInsensitivePrefixSearch",
            description="Indicates whether or not a case insensitive search can be performed on a prefix.",
        ),
    ] = None
    case_insensitive_substring_search: Annotated[
        Optional[bool],
        Field(
            alias="caseInsensitiveSubstringSearch",
            description="Indicates whether or not a case insensitive search can be performed on a substring.",
        ),
    ] = None
    contains_search: Annotated[
        Optional[bool],
        Field(
            alias="containsSearch",
            description="Indicates whether or not a value-based search can be performed.",
        ),
    ] = None
    equality_search: Annotated[
        Optional[bool],
        Field(
            alias="equalitySearch",
            description="Indicates whether or not a search can be performed based on two equal operands.",
        ),
    ] = None
    field: Annotated[Optional[str], Field(description="The column name.")] = None
    filter_only: Annotated[
        Optional[bool],
        Field(
            alias="filterOnly",
            description="Indicates whether a field can only be used as part of a filter.",
        ),
    ] = None
    keyword_search: Annotated[
        Optional[bool],
        Field(
            alias="keywordSearch",
            description="Indicates whether or not a keyword search can be performed.",
        ),
    ] = None
    mind_bridge_field: Annotated[
        Optional[str],
        Field(
            alias="mindBridgeField",
            description="The MindBridge field name that this column is mapped to.",
        ),
    ] = None
    nullable: Annotated[
        Optional[bool],
        Field(description="Indicates whether or not NULL values are allowed."),
    ] = None
    original_name: Annotated[
        Optional[str],
        Field(
            alias="originalName",
            description="The original field name, derived from the source file, risk score name, or similar source.",
        ),
    ] = None
    range_search: Annotated[
        Optional[bool],
        Field(
            alias="rangeSearch",
            description="Indicates whether or not a search can be performed on a value-based comparison.",
        ),
    ] = None
    sortable: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the data table can be sorted by this column."
        ),
    ] = None
    type: Annotated[
        Optional[Type6], Field(description="The type of data found in the column.")
    ] = None
    typeahead_data_table_id: Annotated[
        Optional[str],
        Field(
            alias="typeaheadDataTableId",
            description="The ID of the typeahead table that this column references.",
        ),
    ] = None


class ApiDataTablePage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[dict[str, Any]]] = None


class Direction(str, Enum):
    """How the column will be sorted."""

    ASC = "ASC"
    DESC = "DESC"


class ApiDataTableQuerySortOrder(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    direction: Annotated[
        Optional[Direction], Field(description="How the column will be sorted.")
    ] = None
    field: Annotated[Optional[str], Field(description="The data table column.")] = None


class ApiDataTableQuerySortOrderRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    direction: Annotated[
        Optional[Direction], Field(description="How the column will be sorted.")
    ] = None
    field: Annotated[Optional[str], Field(description="The data table column.")] = None


class ApiDataTableRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="Identifies the associated analysis."),
    ] = None
    analysis_result_id: Annotated[
        Optional[str],
        Field(
            alias="analysisResultId",
            description="Identifies the associated analysis results.",
        ),
    ] = None
    columns: Annotated[
        Optional[list[ApiDataTableColumnRead]],
        Field(description="Details about the data table columns."),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    logical_name: Annotated[
        Optional[str],
        Field(alias="logicalName", description="The name of the data table."),
    ] = None
    type: Annotated[Optional[str], Field(description="The type of data table.")] = None


class DetectedType(str, Enum):
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    UNKNOWN = "UNKNOWN"
    FLOAT64 = "FLOAT64"


class DominantType(str, Enum):
    """The type determined to be the most prevalent in this column."""

    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    UNKNOWN = "UNKNOWN"
    FLOAT64 = "FLOAT64"


class ApiDeleteUnusedAccountMappingsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="The unique identifier of the engagement to delete unused account mappings for.",
        ),
    ] = None


class ApiDensityMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    blanks: Annotated[
        Optional[int], Field(description="The number of blank values.")
    ] = None
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    density: Annotated[
        Optional[float],
        Field(
            description="The percentage density of values against blanks, represented as decimal between 1 and 0."
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiDensityMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    blanks: Annotated[
        Optional[int], Field(description="The number of blank values.")
    ] = None
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    density: Annotated[
        Optional[float],
        Field(
            description="The percentage density of values against blanks, represented as decimal between 1 and 0."
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiDistinctValueMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiDistinctValueMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class PeriodType(str, Enum):
    """Indicates the time period by which the histogram has been broken down."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class ApiEffectiveDateMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    credits_in_period: Annotated[
        Optional[int],
        Field(
            alias="creditsInPeriod",
            description="The total credit amount that occurred within the source period’s date range.",
        ),
    ] = None
    debits_in_period: Annotated[
        Optional[int],
        Field(
            alias="debitsInPeriod",
            description="The total debit amount that occurred within the source period’s date range.",
        ),
    ] = None
    entries_in_period: Annotated[
        Optional[int],
        Field(
            alias="entriesInPeriod",
            description="The number of entries that occurred within the source period’s date range.",
        ),
    ] = None
    entries_out_of_period: Annotated[
        Optional[int],
        Field(
            alias="entriesOutOfPeriod",
            description="The number of entries that occurred outside of the source period’s date range.",
        ),
    ] = None
    in_period_count_histogram: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="inPeriodCountHistogram",
            description="A map showing the total number of entries that occurred within each indicated date period.",
        ),
    ] = None
    out_of_period_count_histogram: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="outOfPeriodCountHistogram",
            description="A map showing the total number of entries that occurred outside of each indicated date period.",
        ),
    ] = None
    period_type: Annotated[
        Optional[PeriodType],
        Field(
            alias="periodType",
            description="Indicates the time period by which the histogram has been broken down.",
        ),
    ] = None


class ApiEngagementAccountGroupCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    alias: Annotated[
        Optional[str],
        Field(
            description="A replacement value used when displaying the account description.\n\nThis does not have any effect on automatic column mapping."
        ),
    ] = None
    code: Annotated[
        Optional[str], Field(description="The account code for this account group.")
    ] = None
    description: Annotated[
        Optional[dict[str, str]],
        Field(description="A description of the account code for this account group."),
    ] = None
    engagement_account_grouping_id: Annotated[
        Optional[str],
        Field(
            alias="engagementAccountGroupingId",
            description="The unique identifier for the engagement account grouping that the engagement account group belongs to.",
        ),
    ] = None
    hidden: Annotated[
        Optional[bool],
        Field(
            description="When `true` this account is hidden, and can’t be used in account mapping. Additionally this account won’t be suggested when automatically mapping accounts during file import."
        ),
    ] = None
    mac_code: Annotated[
        Optional[str],
        Field(
            alias="macCode", description="The MAC code mapped to this account group."
        ),
    ] = None
    parent_code: Annotated[
        Optional[str],
        Field(
            alias="parentCode", description="The parent code for this account group."
        ),
    ] = None


class Origin(str, Enum):
    """The process that lead to the creation of the account group."""

    IMPORTED_FROM_LIBRARY = "IMPORTED_FROM_LIBRARY"
    IMPORTED_FROM_ENGAGEMENT = "IMPORTED_FROM_ENGAGEMENT"
    ADDED_ON_ENGAGEMENT = "ADDED_ON_ENGAGEMENT"


class ApiEngagementAccountGroupRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_tags: Annotated[
        Optional[list[str]],
        Field(
            alias="accountTags",
            description="A list of account tags assigned to this account group.",
        ),
    ] = None
    alias: Annotated[
        Optional[str],
        Field(
            description="A replacement value used when displaying the account description.\n\nThis does not have any effect on automatic column mapping."
        ),
    ] = None
    code: Annotated[
        Optional[str], Field(description="The account code for this account group.")
    ] = None
    description: Annotated[
        Optional[dict[str, str]],
        Field(description="A description of the account code for this account group."),
    ] = None
    engagement_account_grouping_id: Annotated[
        Optional[str],
        Field(
            alias="engagementAccountGroupingId",
            description="The unique identifier for the engagement account grouping that the engagement account group belongs to.",
        ),
    ] = None
    errors: Annotated[
        Optional[list[ApiAccountGroupErrorRead]],
        Field(description="A list of errors associated with this account group."),
    ] = None
    hidden: Annotated[
        Optional[bool],
        Field(
            description="When `true` this account is hidden, and can’t be used in account mapping. Additionally this account won’t be suggested when automatically mapping accounts during file import."
        ),
    ] = None
    hierarchy: Annotated[
        Optional[list[str]],
        Field(description="A list of the parent codes for this account group."),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    lowest_level: Annotated[Optional[bool], Field(alias="lowestLevel")] = None
    mac_code: Annotated[
        Optional[str],
        Field(
            alias="macCode", description="The MAC code mapped to this account group."
        ),
    ] = None
    order_index: Annotated[
        Optional[int],
        Field(
            alias="orderIndex",
            description="The order in which this account group is displayed, relative to other account groups with the same parent.",
        ),
    ] = None
    origin: Annotated[
        Optional[Origin],
        Field(
            description="The process that lead to the creation of the account group."
        ),
    ] = None
    parent_code: Annotated[
        Optional[str],
        Field(
            alias="parentCode", description="The parent code for this account group."
        ),
    ] = None
    published_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="publishedDate",
            description="The date this account group was published. If not set, this account group is not published.\n\nPublished account groups cannot be updated.",
        ),
    ] = None


class ApiEngagementAccountGroupUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    alias: Annotated[
        Optional[str],
        Field(
            description="A replacement value used when displaying the account description.\n\nThis does not have any effect on automatic column mapping."
        ),
    ] = None
    code: Annotated[
        Optional[str], Field(description="The account code for this account group.")
    ] = None
    hidden: Annotated[
        Optional[bool],
        Field(
            description="When `true` this account is hidden, and can’t be used in account mapping. Additionally this account won’t be suggested when automatically mapping accounts during file import."
        ),
    ] = None
    mac_code: Annotated[
        Optional[str],
        Field(
            alias="macCode", description="The MAC code mapped to this account group."
        ),
    ] = None


class ApiEngagementRollForwardRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(
            alias="analysisId", description="Identifies the analysis to roll forward."
        ),
    ] = None
    interim: Annotated[
        Optional[bool],
        Field(
            description="When `true`, the new analysis period will use an interim time frame."
        ),
    ] = None
    target_engagement_id: Annotated[
        Optional[str],
        Field(
            alias="targetEngagementId",
            description="Identifies the engagement that the analysis will be rolled forward into.",
        ),
    ] = None


class ApiEngagementCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    accounting_package: Annotated[
        Optional[str],
        Field(
            alias="accountingPackage",
            description="The ERP or financial management system that your client is using.",
        ),
    ] = None
    accounting_period: Annotated[
        Optional[ApiAccountingPeriodCreate],
        Field(
            alias="accountingPeriod", description="Details about the accounting period."
        ),
    ] = None
    audit_period_end_date: Annotated[
        Optional[date],
        Field(
            alias="auditPeriodEndDate",
            description="The last day of the occurring audit.",
        ),
    ] = None
    auditor_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="auditorIds",
            description="Identifies the users who will act as auditors in the engagement.",
        ),
    ] = None
    billing_code: Annotated[
        Optional[str],
        Field(
            alias="billingCode",
            description="A unique code that associates engagements and analyses with clients to ensure those clients are billed appropriately for MindBridge usage.",
        ),
    ] = None
    engagement_lead_id: Annotated[
        Optional[str],
        Field(
            alias="engagementLeadId",
            description="Identifies the user who will lead the engagement.",
        ),
    ] = None
    industry: Annotated[
        Optional[str],
        Field(description="The type of industry that your client operates within."),
    ] = None
    library_id: Annotated[
        Optional[str], Field(alias="libraryId", description="Identifies the library.")
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the engagement.", max_length=80, min_length=0),
    ] = None
    organization_id: Annotated[
        Optional[str],
        Field(alias="organizationId", description="Identifies the organization."),
    ] = None
    settings_based_on_engagement_id: Annotated[
        Optional[str],
        Field(
            alias="settingsBasedOnEngagementId",
            description="Identifies the engagement that the settings are based on.",
        ),
    ] = None


class ApiEngagementUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    accounting_package: Annotated[
        Optional[str],
        Field(
            alias="accountingPackage",
            description="The ERP or financial management system that your client is using.",
        ),
    ] = None
    accounting_period: Annotated[
        Optional[ApiAccountingPeriodUpdate],
        Field(
            alias="accountingPeriod", description="Details about the accounting period."
        ),
    ] = None
    audit_period_end_date: Annotated[
        Optional[date],
        Field(
            alias="auditPeriodEndDate",
            description="The last day of the occurring audit.",
        ),
    ] = None
    auditor_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="auditorIds",
            description="Identifies the users who will act as auditors in the engagement.",
        ),
    ] = None
    billing_code: Annotated[
        Optional[str],
        Field(
            alias="billingCode",
            description="A unique code that associates engagements and analyses with clients to ensure those clients are billed appropriately for MindBridge usage.",
        ),
    ] = None
    engagement_lead_id: Annotated[
        Optional[str],
        Field(
            alias="engagementLeadId",
            description="Identifies the user who will lead the engagement.",
        ),
    ] = None
    industry: Annotated[
        Optional[str],
        Field(description="The type of industry that your client operates within."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the engagement.", max_length=80, min_length=0),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiExportAccountsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[Optional[str], Field(alias="engagementId")] = None


class Format(str, Enum):
    """The grouped format that was detected."""

    QUICKBOOKS_JOURNAL = "QUICKBOOKS_JOURNAL"
    QUICKBOOKS_JOURNAL_2024 = "QUICKBOOKS_JOURNAL_2024"
    QUICKBOOKS_TRANSACTION_DETAIL_BY_ACCOUNT = (
        "QUICKBOOKS_TRANSACTION_DETAIL_BY_ACCOUNT"
    )
    SAGE50_LEDGER = "SAGE50_LEDGER"
    SAGE50_TRANSACTIONS = "SAGE50_TRANSACTIONS"
    CCH_ACCOUNT_LIST = "CCH_ACCOUNT_LIST"
    MS_DYNAMICS_JOURNAL = "MS_DYNAMICS_JOURNAL"
    SAGE50_UK = "SAGE50_UK"


class Type7(str, Enum):
    """The type of file info entity."""

    FILE_INFO = "FILE_INFO"
    TABULAR_FILE_INFO = "TABULAR_FILE_INFO"


class ApiFileManagerDirectoryCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    name: Annotated[Optional[str], Field(description="The name of the directory.")] = (
        None
    )
    parent_file_manager_entity_id: Annotated[
        Optional[str],
        Field(
            alias="parentFileManagerEntityId",
            description="Identifies the parent directory. If NULL, the directory is positioned at the root level.",
        ),
    ] = None


class Type9(str, Enum):
    """Indicates whether the object is a DIRECTORY or a FILE."""

    DIRECTORY = "DIRECTORY"
    FILE = "FILE"


class ApiFileManagerEntityUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    parent_file_manager_entity_id: Annotated[
        Optional[str],
        Field(
            alias="parentFileManagerEntityId",
            description="Identifies the parent directory. If NULL, the directory is positioned at the root level.",
        ),
    ] = None
    type: Annotated[
        Optional[Type9],
        Field(description="Indicates whether the object is a DIRECTORY or a FILE."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiFileManagerFileCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The current name of the file, excluding the extension."),
    ] = None
    parent_file_manager_entity_id: Annotated[
        Optional[str],
        Field(
            alias="parentFileManagerEntityId",
            description="Identifies the parent directory. If NULL, the directory is positioned at the root level.",
        ),
    ] = None


class StatusEnum(str, Enum):
    MODIFIED = "MODIFIED"
    ROLLED_FORWARD = "ROLLED_FORWARD"


class ApiFileManagerFileUpdate(ApiFileManagerEntityUpdate):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str],
        Field(description="The current name of the file, excluding the extension."),
    ] = None
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiFileMergeRequestCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    file_column_mappings: Annotated[
        Optional[dict[str, list[int]]],
        Field(
            alias="fileColumnMappings",
            description="Reference to the files and the columns to include in the merge operation.",
        ),
    ] = None
    output_file_name: Annotated[
        Optional[str],
        Field(
            alias="outputFileName",
            description="The name of the file being generated in the requested merge operation.",
        ),
    ] = None
    parent_file_manager_entity_id: Annotated[
        Optional[str],
        Field(
            alias="parentFileManagerEntityId",
            description="Identifies the parent directory. If NULL, the directory is positioned at the root level.",
        ),
    ] = None


class Type11(str, Enum):
    GROUP = "GROUP"
    STRING = "STRING"
    STRING_ARRAY = "STRING_ARRAY"
    CONTROL_POINT = "CONTROL_POINT"
    ACCOUNT_NODE_ARRAY = "ACCOUNT_NODE_ARRAY"
    TYPEAHEAD_ENTRY = "TYPEAHEAD_ENTRY"
    POPULATIONS = "POPULATIONS"
    RISK_SCORE = "RISK_SCORE"
    MONETARY_FLOW = "MONETARY_FLOW"
    MONEY = "MONEY"
    MATERIALITY = "MATERIALITY"
    NUMERICAL = "NUMERICAL"
    DATE = "DATE"


class ApiFilterAccountSelection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: Annotated[
        Optional[str],
        Field(
            description="The account grouping code or account ID of the selected account."
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The display name of the account being selected."),
    ] = None
    use_account_id: Annotated[
        Optional[bool],
        Field(
            alias="useAccountId",
            description="If `true` then the selected account will be identified by the account ID rather than the grouping code.",
        ),
    ] = None


class MonetaryFlowType(str, Enum):
    SIMPLE_FLOW = "SIMPLE_FLOW"
    COMPLEX_FLOW = "COMPLEX_FLOW"
    SPECIFIC_FLOW = "SPECIFIC_FLOW"


class ApiFilterComplexMonetaryFlowCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    monetary_flow_type: Annotated[
        Optional[MonetaryFlowType],
        Field(alias="monetaryFlowType", title="Filter Monetary Flow Type"),
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class RiskLevel(str, Enum):
    """The risk level of the selected control points."""

    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_RISK = "LOW_RISK"


class ApiFilterControlPointSelection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Annotated[
        Optional[str], Field(description="The ID of the selected control point.")
    ] = None
    name: Annotated[
        Optional[str], Field(description="The display name of the control point.")
    ] = None
    rules_based: Annotated[Optional[bool], Field(alias="rulesBased")] = None
    symbolic_name: Annotated[
        Optional[str],
        Field(
            alias="symbolicName",
            description="The symbolic name of the target control point. For custom control points this is the symbolic name of the control point it is based on.",
        ),
    ] = None


class DateType(str, Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    SPECIFIC_VALUE = "SPECIFIC_VALUE"
    BETWEEN = "BETWEEN"


class ApiFilterDateRangeCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    date_type: Annotated[
        Optional[DateType], Field(alias="dateType", title="Filter Date Type")
    ] = None
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    range_end: Annotated[
        Optional[date],
        Field(
            alias="rangeEnd",
            description="The end of an ISO date range to compare entries to.",
        ),
    ] = None
    range_start: Annotated[
        Optional[date],
        Field(
            alias="rangeStart",
            description="The start of an ISO date range to compare entries to.",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterDateValueCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    date_type: Annotated[
        Optional[DateType], Field(alias="dateType", title="Filter Date Type")
    ] = None
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[date], Field(description="An ISO date value to compare entries to.")
    ] = None


class Operator(str, Enum):
    """The operator to be applied to conditions within this group."""

    AND_ = "AND"
    OR_ = "OR"


class ApiFilterGroupCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    operator: Annotated[
        Optional[Operator],
        Field(
            description="The operator to be applied to conditions within this group.",
            title="Filter Group Operator",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class MaterialityOption(str, Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    PERCENTAGE = "PERCENTAGE"


class ApiFilterMaterialityOptionCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    materiality_option: Annotated[
        Optional[MaterialityOption],
        Field(alias="materialityOption", title="Filter Materiality Value Options"),
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterMaterialityValueCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    materiality_option: Annotated[
        Optional[MaterialityOption],
        Field(alias="materialityOption", title="Filter Materiality Value Options"),
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[float],
        Field(
            description="The percentage value, as a decimal number, with 100.00 being 100%."
        ),
    ] = None


class MonetaryValueType(str, Enum):
    MORE_THAN = "MORE_THAN"
    LESS_THAN = "LESS_THAN"
    SPECIFIC_VALUE = "SPECIFIC_VALUE"
    BETWEEN = "BETWEEN"


class ApiFilterMonetaryValueRangeCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    monetary_value_type: Annotated[
        Optional[MonetaryValueType],
        Field(alias="monetaryValueType", title="Filter Monetary Type"),
    ] = None
    negated: Optional[bool] = None
    range_end: Annotated[
        Optional[int],
        Field(
            alias="rangeEnd",
            description="The end of the range, as a MONEY_100 formatted number to compare with entries.",
        ),
    ] = None
    range_start: Annotated[
        Optional[int],
        Field(
            alias="rangeStart",
            description="The start of the range, as a MONEY_100 formatted number to compare with entries.",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterMonetaryValueValueCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    monetary_value_type: Annotated[
        Optional[MonetaryValueType],
        Field(alias="monetaryValueType", title="Filter Monetary Type"),
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[int],
        Field(description="The MONEY_100 formatted number to compare with entries."),
    ] = None


class NumericalValueType(str, Enum):
    MORE_THAN = "MORE_THAN"
    LESS_THAN = "LESS_THAN"
    SPECIFIC_VALUE = "SPECIFIC_VALUE"
    BETWEEN = "BETWEEN"


class ApiFilterNumericalValueRangeCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    numerical_value_type: Annotated[
        Optional[NumericalValueType],
        Field(alias="numericalValueType", title="Filter Numerical Value Type"),
    ] = None
    range_end: Annotated[
        Optional[int],
        Field(
            alias="rangeEnd",
            description="The end value of a range to compare entries to.",
        ),
    ] = None
    range_start: Annotated[
        Optional[int],
        Field(
            alias="rangeStart",
            description="The start value of a range to compare entries to.",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterNumericalValueValueCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    numerical_value_type: Annotated[
        Optional[NumericalValueType],
        Field(alias="numericalValueType", title="Filter Numerical Value Type"),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[int], Field(description="A value to compare entries to.")
    ] = None


class ApiFilterPopulationsCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    population_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="populationIds",
            description="A list of population IDs and category names to be used in the filter.",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class RiskScoreType(str, Enum):
    PERCENT = "PERCENT"
    HML = "HML"


class Value(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNSCORED = "UNSCORED"


class ApiFilterRiskScoreHMLCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    risk_score_id: Annotated[Optional[str], Field(alias="riskScoreId")] = None
    risk_score_label: Annotated[Optional[str], Field(alias="riskScoreLabel")] = None
    risk_score_type: Annotated[
        Optional[RiskScoreType],
        Field(alias="riskScoreType", title="Filter Risk Score Type"),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    values: Annotated[
        Optional[list[Value]],
        Field(description="A list of HML options to include in the filter."),
    ] = None


class RiskScorePercentType(str, Enum):
    MORE_THAN = "MORE_THAN"
    LESS_THAN = "LESS_THAN"
    BETWEEN = "BETWEEN"
    CUSTOM_RANGE = "CUSTOM_RANGE"
    UNSCORED = "UNSCORED"


class ApiFilterRiskScorePercentRangeCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    range_end: Annotated[
        Optional[int],
        Field(
            alias="rangeEnd",
            description="The end of the number range between 0 and 10,000.",
        ),
    ] = None
    range_start: Annotated[
        Optional[int],
        Field(
            alias="rangeStart",
            description="The start of the number range between 0 and 10,000.",
        ),
    ] = None
    risk_score_id: Annotated[Optional[str], Field(alias="riskScoreId")] = None
    risk_score_label: Annotated[Optional[str], Field(alias="riskScoreLabel")] = None
    risk_score_percent_type: Annotated[
        Optional[RiskScorePercentType],
        Field(alias="riskScorePercentType", title="Filter Risk Score Percent Type"),
    ] = None
    risk_score_type: Annotated[
        Optional[RiskScoreType],
        Field(alias="riskScoreType", title="Filter Risk Score Type"),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterRiskScorePercentUnscoredCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    risk_score_id: Annotated[Optional[str], Field(alias="riskScoreId")] = None
    risk_score_label: Annotated[Optional[str], Field(alias="riskScoreLabel")] = None
    risk_score_percent_type: Annotated[
        Optional[RiskScorePercentType],
        Field(alias="riskScorePercentType", title="Filter Risk Score Percent Type"),
    ] = None
    risk_score_type: Annotated[
        Optional[RiskScoreType],
        Field(alias="riskScoreType", title="Filter Risk Score Type"),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterRiskScorePercentValueCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    risk_score_id: Annotated[Optional[str], Field(alias="riskScoreId")] = None
    risk_score_label: Annotated[Optional[str], Field(alias="riskScoreLabel")] = None
    risk_score_percent_type: Annotated[
        Optional[RiskScorePercentType],
        Field(alias="riskScorePercentType", title="Filter Risk Score Percent Type"),
    ] = None
    risk_score_type: Annotated[
        Optional[RiskScoreType],
        Field(alias="riskScoreType", title="Filter Risk Score Type"),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[int],
        Field(
            description="A number between 0 and 10,000 used as part of a more than, or less than filter."
        ),
    ] = None


class ApiFilterSimpleMonetaryFlowCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    monetary_flow_type: Annotated[
        Optional[MonetaryFlowType],
        Field(alias="monetaryFlowType", title="Filter Monetary Flow Type"),
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class SpecificMonetaryFlowType(str, Enum):
    SPECIFIC_VALUE = "SPECIFIC_VALUE"
    MORE_THAN = "MORE_THAN"
    BETWEEN = "BETWEEN"


class ApiFilterSpecificMonetaryFlowRangeCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    credit_account: Annotated[
        Optional[ApiFilterAccountSelection], Field(alias="creditAccount")
    ] = None
    debit_account: Annotated[
        Optional[ApiFilterAccountSelection], Field(alias="debitAccount")
    ] = None
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    monetary_flow_type: Annotated[
        Optional[MonetaryFlowType],
        Field(alias="monetaryFlowType", title="Filter Monetary Flow Type"),
    ] = None
    negated: Optional[bool] = None
    range_end: Annotated[
        Optional[int],
        Field(
            alias="rangeEnd",
            description="The end of the range, as a MONEY_100 formatted number to compare with entries.",
        ),
    ] = None
    range_start: Annotated[
        Optional[int],
        Field(
            alias="rangeStart",
            description="The start of the range, as a MONEY_100 formatted number to compare with entries.",
        ),
    ] = None
    specific_monetary_flow_type: Annotated[
        Optional[SpecificMonetaryFlowType],
        Field(
            alias="specificMonetaryFlowType", title="Filter Specific Monetary Flow Type"
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterSpecificMonetaryFlowValueCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    credit_account: Annotated[
        Optional[ApiFilterAccountSelection], Field(alias="creditAccount")
    ] = None
    debit_account: Annotated[
        Optional[ApiFilterAccountSelection], Field(alias="debitAccount")
    ] = None
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    monetary_flow_type: Annotated[
        Optional[MonetaryFlowType],
        Field(alias="monetaryFlowType", title="Filter Monetary Flow Type"),
    ] = None
    negated: Optional[bool] = None
    specific_monetary_flow_type: Annotated[
        Optional[SpecificMonetaryFlowType],
        Field(
            alias="specificMonetaryFlowType", title="Filter Specific Monetary Flow Type"
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[int],
        Field(description="The MONEY_100 formatted number to compare with entries."),
    ] = None


class ApiFilterStringArrayCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    values: Annotated[
        Optional[list[str]],
        Field(description="The set of text values used to filter entries."),
    ] = None


class ApiFilterStringCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    value: Annotated[
        Optional[str], Field(description="The text value used to filter entries.")
    ] = None


class ApiFilterValidateRequestCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data_table_id: Annotated[Optional[str], Field(alias="dataTableId")] = None
    filter_id: Annotated[Optional[str], Field(alias="filterId")] = None


class DataType(str, Enum):
    """The intended data type for this filter."""

    TRANSACTIONS = "TRANSACTIONS"
    ENTRIES = "ENTRIES"
    LIBRARY = "LIBRARY"


class FilterType(str, Enum):
    """The type of this filter. Determines in which context analyses can access it."""

    LIBRARY = "LIBRARY"
    ORGANIZATION = "ORGANIZATION"
    PRIVATE = "PRIVATE"
    ENGAGEMENT = "ENGAGEMENT"


class ApiHistogramMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    histogram: Annotated[
        Optional[dict[str, int]],
        Field(
            description="A map of the number of columns to the number of rows with that many columns, in the case of unevenColumnsMetrics."
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiHistogramMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    histogram: Annotated[
        Optional[dict[str, int]],
        Field(
            description="A map of the number of columns to the number of rows with that many columns, in the case of unevenColumnsMetrics."
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class Type37(str, Enum):
    """The type of account grouping file being imported."""

    MINDBRIDGE_TEMPLATE = "MINDBRIDGE_TEMPLATE"
    CCH_GROUP_TRIAL_BALANCE = "CCH_GROUP_TRIAL_BALANCE"


class ApiImportAccountGroupingParamsCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    chunked_file_id: Annotated[
        Optional[str],
        Field(
            alias="chunkedFileId",
            description="The unique identifier of the chunked file that contains the account grouping data.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the new account grouping.")
    ] = None
    type: Annotated[
        Optional[Type37],
        Field(description="The type of account grouping file being imported."),
    ] = None


class ApiImportAccountGroupingParamsUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    chunked_file_id: Annotated[
        Optional[str],
        Field(
            alias="chunkedFileId",
            description="The unique identifier of the chunked file that contains the account grouping data.",
        ),
    ] = None


class RiskScoreDisplay(str, Enum):
    """Determines whether risk scores will be presented as percentages (%), or using High, Medium, and Low label indicators."""

    HIGH_MEDIUM_LOW = "HIGH_MEDIUM_LOW"
    PERCENTAGE = "PERCENTAGE"


class ApiLibraryCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_grouping_id: Annotated[
        Optional[str],
        Field(
            alias="accountGroupingId",
            description="Identifies the account grouping used.",
        ),
    ] = None
    analysis_type_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="analysisTypeIds",
            description="Identifies the analysis types used in the library.",
        ),
    ] = None
    based_on_library_id: Annotated[
        Optional[str],
        Field(
            alias="basedOnLibraryId",
            description="Identifies the library that the new library is based on. This may be a user-created library or a MindBridge system library.",
        ),
    ] = None
    control_point_selection_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointSelectionPermission",
            description="When set to `true`, control points can be added or removed within each risk score.",
        ),
    ] = None
    control_point_settings_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointSettingsPermission",
            description="When set to `true`, individual control point settings can be adjusted within each risk score.",
        ),
    ] = None
    control_point_weight_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointWeightPermission",
            description="When set to `true`, the weight of each control point can be adjusted within each risk score.",
        ),
    ] = None
    convert_settings: Annotated[
        Optional[bool],
        Field(
            alias="convertSettings",
            description="Indicates whether or not settings from the selected base library should be converted for use with the selected account grouping.",
        ),
    ] = None
    default_delimiter: Annotated[
        Optional[str],
        Field(
            alias="defaultDelimiter",
            description="Identifies the default delimiter used in imported CSV files.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The current name of the library.", max_length=80, min_length=0
        ),
    ] = None
    risk_range_edit_permission: Annotated[
        Optional[bool], Field(alias="riskRangeEditPermission")
    ] = None
    risk_score_and_groups_selection_permission: Annotated[
        Optional[bool],
        Field(
            alias="riskScoreAndGroupsSelectionPermission",
            description="When set to `true`, risk scores and groups can be disabled, and accounts associated with risk scores can be edited.",
        ),
    ] = None
    risk_score_display: Annotated[
        Optional[RiskScoreDisplay],
        Field(
            alias="riskScoreDisplay",
            description="Determines whether risk scores will be presented as percentages (%), or using High, Medium, and Low label indicators.",
        ),
    ] = None
    warnings_dismissed: Annotated[
        Optional[bool],
        Field(
            alias="warningsDismissed",
            description="When set to `true`, any conversion warnings for this library will not be displayed in the **Libraries** tab in the UI.",
        ),
    ] = None


class ApiLibraryUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_type_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="analysisTypeIds",
            description="Identifies the analysis types used in the library.",
        ),
    ] = None
    archived: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the library is archived. Archived libraries cannot be selected when creating an engagement."
        ),
    ] = None
    control_point_selection_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointSelectionPermission",
            description="When set to `true`, control points can be added or removed within each risk score.",
        ),
    ] = None
    control_point_settings_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointSettingsPermission",
            description="When set to `true`, individual control point settings can be adjusted within each risk score.",
        ),
    ] = None
    control_point_weight_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointWeightPermission",
            description="When set to `true`, the weight of each control point can be adjusted within each risk score.",
        ),
    ] = None
    default_delimiter: Annotated[
        Optional[str],
        Field(
            alias="defaultDelimiter",
            description="Identifies the default delimiter used in imported CSV files.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The current name of the library.", max_length=80, min_length=0
        ),
    ] = None
    risk_range_edit_permission: Annotated[
        Optional[bool], Field(alias="riskRangeEditPermission")
    ] = None
    risk_score_and_groups_selection_permission: Annotated[
        Optional[bool],
        Field(
            alias="riskScoreAndGroupsSelectionPermission",
            description="When set to `true`, risk scores and groups can be disabled, and accounts associated with risk scores can be edited.",
        ),
    ] = None
    risk_score_display: Annotated[
        Optional[RiskScoreDisplay],
        Field(
            alias="riskScoreDisplay",
            description="Determines whether risk scores will be presented as percentages (%), or using High, Medium, and Low label indicators.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None
    warnings_dismissed: Annotated[
        Optional[bool],
        Field(
            alias="warningsDismissed",
            description="When set to `true`, any conversion warnings for this library will not be displayed in the **Libraries** tab in the UI.",
        ),
    ] = None


class ApiLoginRecordRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ip_address: Annotated[
        Optional[str],
        Field(
            alias="ipAddress",
            description="The IP address used when logging in or when making a request with an API token.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(
            description="The time when the user logged in or the API token was used."
        ),
    ] = None


class ApiMessageRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: Annotated[
        Optional[str], Field(description="Identifies the message type.")
    ] = None
    default_message: Annotated[
        Optional[str],
        Field(
            alias="defaultMessage",
            description="The message as it appears in MindBridge.",
        ),
    ] = None


class ApiOrganizationCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    external_client_code: Annotated[
        Optional[str],
        Field(
            alias="externalClientCode",
            description="The unique client ID applied to this organization.",
            max_length=80,
            min_length=0,
        ),
    ] = None
    manager_user_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="managerUserIds",
            description="Identifies users assigned to the organization manager role.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the organization.", max_length=80, min_length=0),
    ] = None


class ApiOrganizationUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    external_client_code: Annotated[
        Optional[str],
        Field(
            alias="externalClientCode",
            description="The unique client ID applied to this organization.",
            max_length=80,
            min_length=0,
        ),
    ] = None
    manager_user_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="managerUserIds",
            description="Identifies users assigned to the organization manager role.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the organization.", max_length=80, min_length=0),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiOverallDataTypeMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    blank_records: Annotated[
        Optional[int],
        Field(alias="blankRecords", description="The number of blank values."),
    ] = None
    cell_type_counts: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="cellTypeCounts",
            description="A map of data types to the number of cells in the table of that data type.",
        ),
    ] = None
    column_count: Annotated[
        Optional[int], Field(alias="columnCount", description="The number of columns.")
    ] = None
    column_type_counts: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="columnTypeCounts",
            description="A map of data types to the number of columns in the table of that data type.",
        ),
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None
    total_records: Annotated[
        Optional[int],
        Field(alias="totalRecords", description="The total number of values."),
    ] = None
    total_rows: Annotated[
        Optional[int], Field(alias="totalRows", description="The total number of rows.")
    ] = None


class ApiOverallDataTypeMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    blank_records: Annotated[
        Optional[int],
        Field(alias="blankRecords", description="The number of blank values."),
    ] = None
    cell_type_counts: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="cellTypeCounts",
            description="A map of data types to the number of cells in the table of that data type.",
        ),
    ] = None
    column_count: Annotated[
        Optional[int], Field(alias="columnCount", description="The number of columns.")
    ] = None
    column_type_counts: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="columnTypeCounts",
            description="A map of data types to the number of columns in the table of that data type.",
        ),
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None
    total_records: Annotated[
        Optional[int],
        Field(alias="totalRecords", description="The total number of values."),
    ] = None
    total_rows: Annotated[
        Optional[int], Field(alias="totalRows", description="The total number of rows.")
    ] = None


class ApiProposedAmbiguousColumnResolutionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    position: Annotated[
        Optional[int],
        Field(
            description="The position of the column with the proposed resolution.", ge=0
        ),
    ] = None
    selected_format: Annotated[
        Optional[str],
        Field(
            alias="selectedFormat",
            description="The selected format of the proposed resolution.",
        ),
    ] = None


class ApiProposedAmbiguousColumnResolutionRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    position: Annotated[
        Optional[int],
        Field(
            description="The position of the column with the proposed resolution.", ge=0
        ),
    ] = None
    selected_format: Annotated[
        Optional[str],
        Field(
            alias="selectedFormat",
            description="The selected format of the proposed resolution.",
        ),
    ] = None


class ApiProposedAmbiguousColumnResolutionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    position: Annotated[
        Optional[int],
        Field(
            description="The position of the column with the proposed resolution.", ge=0
        ),
    ] = None
    selected_format: Annotated[
        Optional[str],
        Field(
            alias="selectedFormat",
            description="The selected format of the proposed resolution.",
        ),
    ] = None


class ApiProposedColumnMappingCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_column_name: Annotated[
        Optional[str],
        Field(
            alias="additionalColumnName",
            description="Proposed additional columns of data to be added to the analysis.",
        ),
    ] = None
    column_position: Annotated[
        Optional[int],
        Field(
            alias="columnPosition",
            description="The position of the proposed column mapping in the original input file.",
        ),
    ] = None
    mindbridge_field: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeField",
            description="The MindBridge field that the data column should be mapped to.",
        ),
    ] = None
    virtual_column_index: Annotated[
        Optional[int],
        Field(
            alias="virtualColumnIndex",
            description="The position of the proposed virtual columns within the `proposedVirtualColumns` list.",
        ),
    ] = None


class ApiProposedColumnMappingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_column_name: Annotated[
        Optional[str],
        Field(
            alias="additionalColumnName",
            description="Proposed additional columns of data to be added to the analysis.",
        ),
    ] = None
    column_position: Annotated[
        Optional[int],
        Field(
            alias="columnPosition",
            description="The position of the proposed column mapping in the original input file.",
        ),
    ] = None
    mindbridge_field: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeField",
            description="The MindBridge field that the data column should be mapped to.",
        ),
    ] = None
    virtual_column_index: Annotated[
        Optional[int],
        Field(
            alias="virtualColumnIndex",
            description="The position of the proposed virtual columns within the `proposedVirtualColumns` list.",
        ),
    ] = None


class ApiProposedColumnMappingUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_column_name: Annotated[
        Optional[str],
        Field(
            alias="additionalColumnName",
            description="Proposed additional columns of data to be added to the analysis.",
        ),
    ] = None
    column_position: Annotated[
        Optional[int],
        Field(
            alias="columnPosition",
            description="The position of the proposed column mapping in the original input file.",
        ),
    ] = None
    mindbridge_field: Annotated[
        Optional[str],
        Field(
            alias="mindbridgeField",
            description="The MindBridge field that the data column should be mapped to.",
        ),
    ] = None
    virtual_column_index: Annotated[
        Optional[int],
        Field(
            alias="virtualColumnIndex",
            description="The position of the proposed virtual columns within the `proposedVirtualColumns` list.",
        ),
    ] = None


class Type38(str, Enum):
    """The type of proposed virtual column."""

    DUPLICATE = "DUPLICATE"
    SPLIT_BY_POSITION = "SPLIT_BY_POSITION"
    SPLIT_BY_DELIMITER = "SPLIT_BY_DELIMITER"
    JOIN = "JOIN"


class ApiProposedVirtualColumnCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str], Field(description="The name of the proposed virtual column.")
    ] = None
    type: Annotated[
        Optional[Type38], Field(description="The type of proposed virtual column.")
    ] = None


class ApiProposedVirtualColumnRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str], Field(description="The name of the proposed virtual column.")
    ] = None
    type: Annotated[
        Optional[Type38], Field(description="The type of proposed virtual column.")
    ] = None


class ApiProposedVirtualColumnUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str], Field(description="The name of the proposed virtual column.")
    ] = None
    type: Annotated[
        Optional[Type38], Field(description="The type of proposed virtual column.")
    ] = None


class ApiRiskGroupFilterRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    values: Annotated[
        Optional[list[str]],
        Field(description="A list of accounts to include in the risk group."),
    ] = None


class ApiRiskGroupFilterUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    values: Annotated[
        Optional[list[str]],
        Field(description="A list of accounts to include in the risk group."),
    ] = None


class RiskAssertionCategory(str, Enum):
    """Identifies the risk assertion category of the risk group."""

    GENERAL = "GENERAL"
    ASSETS = "ASSETS"
    LIABILITIES_EQUITY = "LIABILITIES_EQUITY"
    PROFIT_LOSS = "PROFIT_LOSS"


class ApiRiskGroupRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisTypeId",
            description="Identifies the analysis type that the risk group is associated with.",
        ),
    ] = None
    applicable_risk_ranges: Annotated[
        Optional[list[str]],
        Field(
            alias="applicableRiskRanges",
            description="A list of risk ranges that are applicable to the risk group.",
        ),
    ] = None
    category: Annotated[
        Optional[dict[str, str]],
        Field(description="Identifies the risk group’s category."),
    ] = None
    control_point_bundle_version: Annotated[
        Optional[str],
        Field(
            alias="controlPointBundleVersion",
            description="The version of the control point bundle used in this risk group.",
        ),
    ] = None
    control_point_weights: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="controlPointWeights",
            description="A map of control point names to their weights within the risk group.",
        ),
    ] = None
    description: Annotated[
        Optional[dict[str, str]],
        Field(
            description="A map of localized risk group descriptions, keyed by language code."
        ),
    ] = None
    disabled: Annotated[
        Optional[bool],
        Field(description="Indicates whether the risk group is disabled."),
    ] = None
    filter: Annotated[
        Optional[ApiRiskGroupFilterRead],
        Field(
            description="A filter based on account hierarchy used to determine which entries are included in the risk group."
        ),
    ] = None
    id: Annotated[
        Optional[str],
        Field(description="The unique object identifier for this risk group."),
    ] = None
    name: Annotated[
        Optional[dict[str, str]],
        Field(
            description="A map of localized risk group names, keyed by language code."
        ),
    ] = None
    risk_assertion_category: Annotated[
        Optional[RiskAssertionCategory],
        Field(
            alias="riskAssertionCategory",
            description="Identifies the risk assertion category of the risk group.",
        ),
    ] = None
    selected_risk_range: Annotated[
        Optional[str],
        Field(
            alias="selectedRiskRange",
            description="The selected risk range for the risk group. The selected value must be part of the applicable risk ranges.",
        ),
    ] = None
    system: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether the risk group is a MindBridge system risk group."
        ),
    ] = None


class ApiRiskGroupUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    applicable_risk_ranges: Annotated[
        Optional[list[str]],
        Field(
            alias="applicableRiskRanges",
            description="A list of risk ranges that are applicable to the risk group.",
        ),
    ] = None
    control_point_weights: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="controlPointWeights",
            description="A map of control point names to their weights within the risk group.",
        ),
    ] = None
    disabled: Annotated[
        Optional[bool],
        Field(description="Indicates whether the risk group is disabled."),
    ] = None
    filter: Annotated[
        Optional[ApiRiskGroupFilterUpdate],
        Field(
            description="A filter based on account hierarchy used to determine which entries are included in the risk group."
        ),
    ] = None
    id: Annotated[
        Optional[str],
        Field(description="The unique object identifier for this risk group."),
    ] = None
    selected_risk_range: Annotated[
        Optional[str],
        Field(
            alias="selectedRiskRange",
            description="The selected risk range for the risk group. The selected value must be part of the applicable risk ranges.",
        ),
    ] = None


class ApiRiskRangeBoundsCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    high_threshold: Annotated[
        Optional[int],
        Field(
            alias="highThreshold",
            description="The high threshold of the risk range.",
            ge=0,
            le=10000,
        ),
    ] = None
    low_threshold: Annotated[
        Optional[int],
        Field(
            alias="lowThreshold",
            description="The low threshold of the risk range.",
            ge=0,
            le=10000,
        ),
    ] = None


class ApiRiskRangeBoundsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    high_threshold: Annotated[
        Optional[int],
        Field(
            alias="highThreshold",
            description="The high threshold of the risk range.",
            ge=0,
            le=10000,
        ),
    ] = None
    low_threshold: Annotated[
        Optional[int],
        Field(
            alias="lowThreshold",
            description="The low threshold of the risk range.",
            ge=0,
            le=10000,
        ),
    ] = None


class ApiRiskRangeBoundsUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    high_threshold: Annotated[
        Optional[int],
        Field(
            alias="highThreshold",
            description="The high threshold of the risk range.",
            ge=0,
            le=10000,
        ),
    ] = None
    low_threshold: Annotated[
        Optional[int],
        Field(
            alias="lowThreshold",
            description="The low threshold of the risk range.",
            ge=0,
            le=10000,
        ),
    ] = None


class ApiRiskRangesCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisTypeId",
            description="Identifies the analysis type associated with this risk range.",
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Field(
            description="The description of the risk range.",
            max_length=250,
            min_length=0,
        ),
    ] = None
    high: Annotated[
        Optional[ApiRiskRangeBoundsCreate], Field(description="The high range bounds.")
    ] = None
    library_id: Annotated[
        Optional[str],
        Field(
            alias="libraryId",
            description="Identifies the library associated with this risk range.",
        ),
    ] = None
    low: Annotated[
        Optional[ApiRiskRangeBoundsCreate], Field(description="The low range bounds.")
    ] = None
    medium: Annotated[
        Optional[ApiRiskRangeBoundsCreate],
        Field(description="The medium range bounds."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the risk range.", max_length=80, min_length=0),
    ] = None


class ApiRiskRangesRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisTypeId",
            description="Identifies the analysis type associated with this risk range.",
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Field(
            description="The description of the risk range.",
            max_length=250,
            min_length=0,
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="Identifies the engagement associated with this risk range.",
        ),
    ] = None
    high: Annotated[
        Optional[ApiRiskRangeBoundsRead], Field(description="The high range bounds.")
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    library_id: Annotated[
        Optional[str],
        Field(
            alias="libraryId",
            description="Identifies the library associated with this risk range.",
        ),
    ] = None
    low: Annotated[
        Optional[ApiRiskRangeBoundsRead], Field(description="The low range bounds.")
    ] = None
    medium: Annotated[
        Optional[ApiRiskRangeBoundsRead], Field(description="The medium range bounds.")
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the risk range.", max_length=80, min_length=0),
    ] = None
    system: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the risk ranges are a MindBridge system risk range."
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiRiskRangesUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    description: Annotated[
        Optional[str],
        Field(
            description="The description of the risk range.",
            max_length=250,
            min_length=0,
        ),
    ] = None
    high: Annotated[
        Optional[ApiRiskRangeBoundsUpdate], Field(description="The high range bounds.")
    ] = None
    low: Annotated[
        Optional[ApiRiskRangeBoundsUpdate], Field(description="The low range bounds.")
    ] = None
    medium: Annotated[
        Optional[ApiRiskRangeBoundsUpdate],
        Field(description="The medium range bounds."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the risk range.", max_length=80, min_length=0),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiSheetMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    sheet_names: Annotated[
        Optional[list[str]],
        Field(
            alias="sheetNames",
            description="A list of sheet names within the underlying Excel file.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None
    valid_sheets: Annotated[
        Optional[list[str]],
        Field(
            alias="validSheets",
            description="A list of usable sheet names within the underlying Excel file.",
        ),
    ] = None


class ApiSheetMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    sheet_names: Annotated[
        Optional[list[str]],
        Field(
            alias="sheetNames",
            description="A list of sheet names within the underlying Excel file.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None
    valid_sheets: Annotated[
        Optional[list[str]],
        Field(
            alias="validSheets",
            description="A list of usable sheet names within the underlying Excel file.",
        ),
    ] = None


class SourceScope(str, Enum):
    """Indicates whether the source configuration applies to the current period, all of the prior periods, or the entire analysis.

    **Note**: Sources with an `ANALYSIS` scope should not provide an `analysisPeriodId`.
    """

    CURRENT_PERIOD = "CURRENT_PERIOD"
    PRIOR_PERIOD = "PRIOR_PERIOD"
    ANALYSIS = "ANALYSIS"


class ApiSourceConfigurationRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    allow_multiple: Annotated[
        Optional[bool],
        Field(
            alias="allowMultiple",
            description="When `true`, multiple versions of this analysis source type may be imported using this source scope.",
        ),
    ] = None
    allow_multiple_for_periodic: Annotated[
        Optional[bool],
        Field(
            alias="allowMultipleForPeriodic",
            description="When `true` and the periodic time frame is used, multiple versions of this analysis source type may be imported using this source scope.",
        ),
    ] = None
    alternative_required_source_types: Annotated[
        Optional[list[str]],
        Field(
            alias="alternativeRequiredSourceTypes",
            description="A list of alternative analysis source types. If one of the alternatives is present for this source scope, then the `required` constraint is considered satisfied.",
        ),
    ] = None
    disable_for_interim: Annotated[
        Optional[bool],
        Field(
            alias="disableForInterim",
            description="When `true` and the interim time frame is used (i.e., it has not been converted for use with a full time frame), new analysis sources of this source type and source scope cannot be added.",
        ),
    ] = None
    interim_only: Annotated[
        Optional[bool],
        Field(
            alias="interimOnly",
            description="When `true`, this source configuration only applies when the interim time frame is used (i.e., it has not been converted for use with a full time frame).",
        ),
    ] = None
    post_analysis: Annotated[
        Optional[bool],
        Field(
            alias="postAnalysis",
            description="When `true`, this source configuration will be enabled after an analysis is run (not before).",
        ),
    ] = None
    required: Annotated[
        Optional[bool],
        Field(
            description="When `true`, the analysis cannot be run until at least one analysis source with this source type in this source scope is present."
        ),
    ] = None
    source_scope: Annotated[
        Optional[SourceScope],
        Field(
            alias="sourceScope",
            description="Indicates whether the source configuration applies to the current period, all of the prior periods, or the entire analysis.\n\n**Note**: Sources with an `ANALYSIS` scope should not provide an `analysisPeriodId`.",
        ),
    ] = None
    source_type_id: Annotated[
        Optional[str],
        Field(
            alias="sourceTypeId",
            description="The source type ID selected as part of this configuration.",
        ),
    ] = None
    tracks_additional_data_entries: Annotated[
        Optional[bool],
        Field(
            alias="tracksAdditionalDataEntries",
            description="When `true`, the `additionalDataColumnField` field is required upon importing an analysis source type.",
        ),
    ] = None


class ApiTaskCommentCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    comment_text: Annotated[
        Optional[str],
        Field(alias="commentText", description="The text of the comment."),
    ] = None


class ApiTaskCommentRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    author_id: Annotated[
        Optional[str],
        Field(
            alias="authorId",
            description="The unique identifier of the user who created this comment.",
        ),
    ] = None
    captured: Annotated[
        Optional[AwareDatetime],
        Field(description="The timestamp when this comment was made."),
    ] = None
    comment_text: Annotated[
        Optional[str],
        Field(alias="commentText", description="The text of the comment."),
    ] = None


class FieldType(str, Enum):
    ARRAY = "ARRAY"
    ISO_DATE = "ISO_DATE"
    OBJECT = "OBJECT"
    STRING = "STRING"
    INTEGER = "INTEGER"


class ApiTaskHistoryEntryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_name: Annotated[Optional[str], Field(alias="fieldName")] = None
    field_type: Annotated[Optional[FieldType], Field(alias="fieldType")] = None
    new_value: Annotated[Optional[Any], Field(alias="newValue")] = None
    new_value_string: Annotated[Optional[str], Field(alias="newValueString")] = None
    previous_value: Annotated[Optional[Any], Field(alias="previousValue")] = None
    previous_value_string: Annotated[
        Optional[str], Field(alias="previousValueString")
    ] = None


class Operation(str, Enum):
    """The operation that was performed on the task."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    COMPLETED = "COMPLETED"
    DELETE = "DELETE"
    COMMENT = "COMMENT"
    ASSIGNMENT = "ASSIGNMENT"
    STATUS_CHANGE = "STATUS_CHANGE"
    MARKASNORMAL = "MARKASNORMAL"


class ApiTaskHistoryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    changes: Annotated[
        Optional[list[ApiTaskHistoryEntryRead]],
        Field(description="A list of changes that were made to the task."),
    ] = None
    date_time: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="dateTime",
            description="The date and time that the task history was created.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    operation: Annotated[
        Optional[Operation],
        Field(description="The operation that was performed on the task."),
    ] = None
    task_id: Annotated[
        Optional[str],
        Field(alias="taskId", description="Identifies the associated task."),
    ] = None
    user_id: Annotated[
        Optional[str],
        Field(
            alias="userId",
            description="The id of the user associated with the history record",
        ),
    ] = None
    user_name: Annotated[
        Optional[str],
        Field(
            alias="userName",
            description="Name of the user associated with the history record",
        ),
    ] = None


class Status5(str, Enum):
    """The current state of the task."""

    OPEN = "OPEN"
    NORMAL = "NORMAL"
    COMPLETED = "COMPLETED"
    DISMISSED = "DISMISSED"
    RESOLVED = "RESOLVED"


class TaskApprovalStatus(str, Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"


class Type41(str, Enum):
    """The type of entry this task is associated with."""

    ENTRY = "ENTRY"
    TRANSACTION = "TRANSACTION"
    AP_ENTRY = "AP_ENTRY"
    AR_ENTRY = "AR_ENTRY"
    AP_OUTSTANDING_ENTRY = "AP_OUTSTANDING_ENTRY"
    AR_OUTSTANDING_ENTRY = "AR_OUTSTANDING_ENTRY"
    TRA_ENTRY = "TRA_ENTRY"


class ApiTaskCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_result_id: Annotated[Optional[str], Field(alias="analysisResultId")] = None
    assertions: Annotated[
        Optional[list[str]],
        Field(description="Which assertions this task is associated with."),
    ] = None
    assigned_id: Annotated[
        Optional[str],
        Field(
            alias="assignedId", description="Identifies the user assigned to this task."
        ),
    ] = None
    audit_areas: Annotated[
        Optional[list[str]],
        Field(
            alias="auditAreas",
            description="Which audit areas this task is associated with.",
        ),
    ] = None
    description: Annotated[
        Optional[str], Field(description="A description of the task.")
    ] = None
    due_date: Annotated[Optional[date], Field(alias="dueDate")] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    row_id: Annotated[
        Optional[int],
        Field(alias="rowId", description="Identifies the associated entry."),
    ] = None
    sample: Annotated[
        Optional[str], Field(description="Which sample this task is a part of.")
    ] = None
    status: Annotated[
        Optional[Status5],
        Field(description="The current state of the task.", title="Task Status"),
    ] = None
    tags: Optional[list[str]] = None
    task_approval_status: Annotated[
        Optional[TaskApprovalStatus],
        Field(alias="taskApprovalStatus", title="Task Approval Status"),
    ] = None
    transaction_id: Annotated[
        Optional[int],
        Field(
            alias="transactionId", description="Identifies the associated transaction."
        ),
    ] = None
    type: Annotated[
        Optional[Type41],
        Field(
            description="The type of entry this task is associated with.",
            title="Task Type",
        ),
    ] = None


class SampleType(str, Enum):
    """The sampling method used to create this task."""

    RISK_BASED = "RISK_BASED"
    RANDOM = "RANDOM"
    MANUAL = "MANUAL"
    MONETARY_UNIT_SAMPLING = "MONETARY_UNIT_SAMPLING"


class ApiTaskUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    approver_id: Annotated[Optional[str], Field(alias="approverId")] = None
    assertions: Annotated[
        Optional[list[str]],
        Field(description="Which assertions this task is associated with."),
    ] = None
    assigned_id: Annotated[
        Optional[str],
        Field(
            alias="assignedId", description="Identifies the user assigned to this task."
        ),
    ] = None
    audit_areas: Annotated[
        Optional[list[str]],
        Field(
            alias="auditAreas",
            description="Which audit areas this task is associated with.",
        ),
    ] = None
    description: Annotated[
        Optional[str], Field(description="A description of the task.")
    ] = None
    due_date: Annotated[Optional[date], Field(alias="dueDate")] = None
    sample: Annotated[
        Optional[str], Field(description="Which sample this task is a part of.")
    ] = None
    status: Annotated[
        Optional[Status5],
        Field(description="The current state of the task.", title="Task Status"),
    ] = None
    tags: Optional[list[str]] = None
    task_approval_status: Annotated[
        Optional[TaskApprovalStatus],
        Field(alias="taskApprovalStatus", title="Task Approval Status"),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class Rating(str, Enum):
    """The quality of the indicator as rated by MindBridge."""

    BLOCK = "BLOCK"
    FAIL = "FAIL"
    POOR = "POOR"
    NEUTRAL = "NEUTRAL"
    GOOD = "GOOD"


class ApiTransactionIdPreviewRowRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    balance: Annotated[
        Optional[int], Field(description="The balance of the transaction.")
    ] = None
    detail_rows: Annotated[
        Optional[list[dict[str, Any]]],
        Field(
            alias="detailRows",
            description="The set of entries that appear within the transaction.",
        ),
    ] = None
    entry_count: Annotated[
        Optional[int],
        Field(
            alias="entryCount",
            description="The number of entries that appear within the transaction.",
        ),
    ] = None
    transaction_id: Annotated[
        Optional[str],
        Field(
            alias="transactionId",
            description="Identifies the transaction ID for this transaction.",
        ),
    ] = None


class OverallRating(str, Enum):
    """The quality of the transaction ID as rated by MindBridge."""

    BLOCK = "BLOCK"
    FAIL = "FAIL"
    POOR = "POOR"
    NEUTRAL = "NEUTRAL"
    GOOD = "GOOD"


class Type43(str, Enum):
    """The type used when selecting a transaction ID."""

    COMBINATION = "COMBINATION"
    RUNNING_TOTAL = "RUNNING_TOTAL"


class ApiTransactionIdSelectionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    apply_smart_splitter: Annotated[
        Optional[bool],
        Field(
            alias="applySmartSplitter",
            description="Indicates whether or not the Smart Splitter was run when selecting a transaction ID.",
        ),
    ] = None
    column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="columnSelection",
            description="The columns included when selecting a transaction ID.",
        ),
    ] = None
    type: Annotated[
        Optional[Type43],
        Field(description="The type used when selecting a transaction ID."),
    ] = None
    virtual_column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="virtualColumnSelection",
            description="The virtual columns included when selecting a transaction ID.",
        ),
    ] = None


class ApiTransactionIdSelectionRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    apply_smart_splitter: Annotated[
        Optional[bool],
        Field(
            alias="applySmartSplitter",
            description="Indicates whether or not the Smart Splitter was run when selecting a transaction ID.",
        ),
    ] = None
    column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="columnSelection",
            description="The columns included when selecting a transaction ID.",
        ),
    ] = None
    type: Annotated[
        Optional[Type43],
        Field(description="The type used when selecting a transaction ID."),
    ] = None
    virtual_column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="virtualColumnSelection",
            description="The virtual columns included when selecting a transaction ID.",
        ),
    ] = None


class ApiTransactionIdSelectionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    apply_smart_splitter: Annotated[
        Optional[bool],
        Field(
            alias="applySmartSplitter",
            description="Indicates whether or not the Smart Splitter was run when selecting a transaction ID.",
        ),
    ] = None
    column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="columnSelection",
            description="The columns included when selecting a transaction ID.",
        ),
    ] = None
    type: Annotated[
        Optional[Type43],
        Field(description="The type used when selecting a transaction ID."),
    ] = None
    virtual_column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="virtualColumnSelection",
            description="The virtual columns included when selecting a transaction ID.",
        ),
    ] = None


class ApiTypeaheadEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    display_name: Annotated[
        Optional[str],
        Field(
            alias="displayName", description="The display name of the selected entry."
        ),
    ] = None
    hide_lookup_id: Annotated[
        Optional[bool],
        Field(
            alias="hideLookupId",
            description="If `false` then the entry will be displayed with both the lookup ID and the display name. If `true` then only the display name will be used when displaying this entry.",
        ),
    ] = None
    lookup_id: Annotated[
        Optional[str],
        Field(alias="lookupId", description="The identifier of the selected entry."),
    ] = None


class ApiUserInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: Annotated[
        Optional[str], Field(alias="userId", description="Identifies the user.")
    ] = None
    user_name: Annotated[
        Optional[str], Field(alias="userName", description="The name of the user.")
    ] = None


class ApiUserInfoRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: Annotated[
        Optional[str], Field(alias="userId", description="Identifies the user.")
    ] = None
    user_name: Annotated[
        Optional[str], Field(alias="userName", description="The name of the user.")
    ] = None


class Role(str, Enum):
    """The MindBridge role assigned to the user. [Learn about user roles](https://support.mindbridge.ai/hc/en-us/articles/360056394954-User-roles-available-in-MindBridge)"""

    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_ORGANIZATION_ADMIN = "ROLE_ORGANIZATION_ADMIN"
    ROLE_USER = "ROLE_USER"
    ROLE_CLIENT = "ROLE_CLIENT"
    ROLE_MINDBRIDGE_SUPPORT = "ROLE_MINDBRIDGE_SUPPORT"
    ROLE_USER_ADMIN = "ROLE_USER_ADMIN"


class ApiUserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    email: Annotated[Optional[str], Field(description="The user’s email address.")] = (
        None
    )
    role: Annotated[
        Optional[Role],
        Field(
            description="The MindBridge role assigned to the user. [Learn about user roles](https://support.mindbridge.ai/hc/en-us/articles/360056394954-User-roles-available-in-MindBridge)"
        ),
    ] = None


class ApiUserRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    email: Annotated[Optional[str], Field(description="The user’s email address.")] = (
        None
    )
    enabled: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the user is enabled within this tenant."
        ),
    ] = None
    first_name: Annotated[
        Optional[str], Field(alias="firstName", description="The user’s first name.")
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    last_name: Annotated[
        Optional[str], Field(alias="lastName", description="The user’s last name.")
    ] = None
    recent_logins: Annotated[
        Optional[list[ApiLoginRecordRead]],
        Field(
            alias="recentLogins",
            description="A list of the latest successful logins or token usage events by IP address.",
        ),
    ] = None
    role: Annotated[
        Optional[Role],
        Field(
            description="The MindBridge role assigned to the user. [Learn about user roles](https://support.mindbridge.ai/hc/en-us/articles/360056394954-User-roles-available-in-MindBridge)"
        ),
    ] = None
    service_account: Annotated[
        Optional[bool],
        Field(
            alias="serviceAccount",
            description="Indicates whether or not this account is used as part of an API token.",
        ),
    ] = None
    validated: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the user has opened the account activation link after being created."
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiUserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    enabled: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the user is enabled within this tenant."
        ),
    ] = None
    role: Annotated[
        Optional[Role],
        Field(
            description="The MindBridge role assigned to the user. [Learn about user roles](https://support.mindbridge.ai/hc/en-us/articles/360056394954-User-roles-available-in-MindBridge)"
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiVerifyAccountsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="The unique identifier of the engagement to verify accounts for.",
        ),
    ] = None


class Type47(str, Enum):
    """The type of virtual column."""

    DUPLICATE = "DUPLICATE"
    SPLIT_BY_POSITION = "SPLIT_BY_POSITION"
    SPLIT_BY_DELIMITER = "SPLIT_BY_DELIMITER"
    JOIN = "JOIN"


class ApiVirtualColumnRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    index: Annotated[
        Optional[int], Field(description="The position of the virtual column.")
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the virtual column.")
    ] = None
    type: Annotated[
        Optional[Type47], Field(description="The type of virtual column.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiVirtualColumnUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str], Field(description="The name of the virtual column.")
    ] = None
    type: Annotated[
        Optional[Type47], Field(description="The type of virtual column.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class Status8(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    FAILED_PERMANENTLY = "FAILED_PERMANENTLY"
    DISCONNECTED = "DISCONNECTED"


class ApiWebhookEventLogRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attempt_start_date: Annotated[
        Optional[AwareDatetime], Field(alias="attemptStartDate")
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead], Field(alias="createdUserInfo")
    ] = None
    creation_date: Annotated[Optional[AwareDatetime], Field(alias="creationDate")] = (
        None
    )
    event_type: Annotated[Optional[str], Field(alias="eventType")] = None
    id: Optional[str] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime], Field(alias="lastModifiedDate")
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead], Field(alias="lastModifiedUserInfo")
    ] = None
    request_body: Annotated[Optional[str], Field(alias="requestBody")] = None
    request_headers: Annotated[
        Optional[dict[str, list[str]]], Field(alias="requestHeaders")
    ] = None
    request_id: Annotated[Optional[str], Field(alias="requestId")] = None
    response_headers: Annotated[
        Optional[dict[str, list[str]]], Field(alias="responseHeaders")
    ] = None
    response_status_code: Annotated[
        Optional[int], Field(alias="responseStatusCode")
    ] = None
    response_time_sec: Annotated[Optional[float], Field(alias="responseTimeSec")] = None
    retry_count: Annotated[Optional[int], Field(alias="retryCount")] = None
    status: Optional[Status8] = None
    url: Optional[str] = None
    version: Optional[int] = None
    webhook_id: Annotated[Optional[str], Field(alias="webhookId")] = None


class Event(str, Enum):
    EXPORT_READY = "EXPORT_READY"
    FILE_MANAGER_FILE_ADDED = "FILE_MANAGER_FILE_ADDED"
    INGESTION_COMPLETE = "INGESTION_COMPLETE"
    INGESTION_FAILED = "INGESTION_FAILED"
    INGESTION_ANALYSIS_COMPLETE = "INGESTION_ANALYSIS_COMPLETE"
    INGESTION_ANALYSIS_FAILED = "INGESTION_ANALYSIS_FAILED"
    UNMAPPED_ACCOUNTS_DETECTED = "UNMAPPED_ACCOUNTS_DETECTED"
    ENGAGEMENT_CREATED = "ENGAGEMENT_CREATED"
    ENGAGEMENT_UPDATED = "ENGAGEMENT_UPDATED"
    ENGAGEMENT_DELETED = "ENGAGEMENT_DELETED"
    ANALYSIS_CREATED = "ANALYSIS_CREATED"
    ANALYSIS_UPDATED = "ANALYSIS_UPDATED"
    ANALYSIS_DELETED = "ANALYSIS_DELETED"
    ANALYSIS_ARCHIVED = "ANALYSIS_ARCHIVED"
    ANALYSIS_UNARCHIVED = "ANALYSIS_UNARCHIVED"
    USER_INVITED = "USER_INVITED"
    USER_STATUS_UPDATED = "USER_STATUS_UPDATED"
    USER_ROLE_UPDATED = "USER_ROLE_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_LOGIN = "USER_LOGIN"


class Status9(str, Enum):
    """The current status of the webhook."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class ApiWebhookCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    events: Annotated[
        Optional[list[Event]],
        Field(
            description="A list of events that will trigger this webhook.",
            max_length=2147483647,
            min_length=1,
        ),
    ] = None
    name: Annotated[Optional[str], Field(description="The name of the webhook.")] = None
    status: Annotated[
        Optional[Status9], Field(description="The current status of the webhook.")
    ] = None
    technical_contact_id: Annotated[
        Optional[str],
        Field(
            alias="technicalContactId",
            description="A reference to an administrative user used to inform system administrators of issues with the webhooks.",
        ),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="The URL to which the webhook will send notifications."),
    ] = None


class ApiWebhookRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead], Field(alias="createdUserInfo")
    ] = None
    creation_date: Annotated[Optional[AwareDatetime], Field(alias="creationDate")] = (
        None
    )
    events: Annotated[
        Optional[list[Event]],
        Field(
            description="A list of events that will trigger this webhook.",
            max_length=2147483647,
            min_length=1,
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    key_generation_timestamp: Annotated[
        Optional[AwareDatetime], Field(alias="keyGenerationTimestamp")
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime], Field(alias="lastModifiedDate")
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead], Field(alias="lastModifiedUserInfo")
    ] = None
    name: Annotated[Optional[str], Field(description="The name of the webhook.")] = None
    public_key: Annotated[
        Optional[str],
        Field(
            alias="publicKey",
            description="The public key used to verify the webhook signature.",
        ),
    ] = None
    status: Annotated[
        Optional[Status9], Field(description="The current status of the webhook.")
    ] = None
    technical_contact_id: Annotated[
        Optional[str],
        Field(
            alias="technicalContactId",
            description="A reference to an administrative user used to inform system administrators of issues with the webhooks.",
        ),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="The URL to which the webhook will send notifications."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiWebhookUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    events: Annotated[
        Optional[list[Event]],
        Field(
            description="A list of events that will trigger this webhook.",
            max_length=2147483647,
            min_length=1,
        ),
    ] = None
    name: Annotated[Optional[str], Field(description="The name of the webhook.")] = None
    status: Annotated[
        Optional[Status9], Field(description="The current status of the webhook.")
    ] = None
    technical_contact_id: Annotated[
        Optional[str],
        Field(
            alias="technicalContactId",
            description="A reference to an administrative user used to inform system administrators of issues with the webhooks.",
        ),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="The URL to which the webhook will send notifications."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class CreateApiFileManagerFileFromJsonTableRequestCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="Identifies the associated engagement to import the formatted file into.",
        ),
    ] = None
    json_table_id: Annotated[
        Optional[str],
        Field(
            alias="jsonTableId",
            description="Identifies the JSON table to be formatted into a file.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the newly created file manager file."),
    ] = None
    parent_file_manager_entity_id: Annotated[
        Optional[str],
        Field(
            alias="parentFileManagerEntityId",
            description="Identifies the file manager entity that will be the parent of the newly created file.",
        ),
    ] = None


class CreateApiTokenResponseRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    allowed_addresses: Annotated[
        Optional[list[str]],
        Field(
            alias="allowedAddresses",
            description="Indicates the set of addresses that are allowed to use this token. If empty, any address may use it.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    expiry: Annotated[
        Optional[AwareDatetime],
        Field(description="The day on which the API token expires."),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The token record’s name. This will also be used as the API Token User’s name."
        ),
    ] = None
    partial_token: Annotated[
        Optional[str],
        Field(
            alias="partialToken",
            description="A partial representation of the API token.",
        ),
    ] = None
    permissions: Annotated[
        Optional[list[Permission]],
        Field(
            description="The set of permissions that inform which endpoints this token is authorized to access."
        ),
    ] = None
    token: Annotated[
        Optional[str],
        Field(
            description="The API token.\n\n**Note:** The security of the API token is paramount. If compromised, contact your **App Admin** immediately."
        ),
    ] = None
    user_id: Annotated[
        Optional[str],
        Field(
            alias="userId",
            description="Identifies the API Token User associated with this token.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class Type49(str, Enum):
    """The event type that triggered the webhook."""

    UNMAPPED_ACCOUNTS = "unmapped.accounts"


class Type50(str, Enum):
    """The event type that triggered the webhook."""

    ENGAGEMENT_CREATED = "engagement.created"
    ENGAGEMENT_UPDATED = "engagement.updated"
    ENGAGEMENT_DELETED = "engagement.deleted"


class Type51(str, Enum):
    """The event type that triggered the webhook."""

    DATA_ADDED = "data.added"
    EXPORT_READY = "export.ready"


class JsonTableBody1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class JsonTableBody(
    RootModel[Optional[list[Union[list[Union[int, float, bool, str]], JsonTableBody1]]]]
):
    model_config = ConfigDict(populate_by_name=True)
    root: Annotated[
        Optional[list[Union[list[Union[int, float, bool, str]], JsonTableBody1]]],
        Field(
            examples=[
                [
                    {"Account": "Accounts Receivable", "Amount": "100.00$"},
                    {"Account": "Accounts Payable", "Amount": "100.00$"},
                ]
            ]
        ),
    ] = None


class MindBridgeQueryTerm1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_eq: Annotated[Optional[Union[int, float, bool, str]], Field(alias="$eq")] = (
        None
    )


class MindBridgeQueryTerm2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_ne: Annotated[Optional[Union[int, float, bool, str]], Field(alias="$ne")] = (
        None
    )


class MindBridgeQueryTerm3(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_gt: Annotated[Optional[Union[int, float, str]], Field(alias="$gt")] = None


class MindBridgeQueryTerm4(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_gte: Annotated[Optional[Union[int, float, str]], Field(alias="$gte")] = None


class MindBridgeQueryTerm5(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_lt: Annotated[Optional[Union[int, float, str]], Field(alias="$lt")] = None


class MindBridgeQueryTerm6(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_lte: Annotated[Optional[Union[int, float, str]], Field(alias="$lte")] = None


class MindBridgeQueryTerm7(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_contains: Annotated[Optional[list[str]], Field(alias="$contains")] = None


class MindBridgeQueryTerm9(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_in: Annotated[
        Optional[list[Union[int, float, bool, str]]], Field(alias="$in")
    ] = None


class MindBridgeQueryTerm10(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_nin: Annotated[
        Optional[list[Union[int, float, bool, str]]], Field(alias="$nin")
    ] = None


class MindBridgeQueryTerm11(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_flags: Annotated[Optional[dict[str, bool]], Field(alias="$flags")] = None


class MindBridgeQueryTerm12(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_isubstr: Annotated[Optional[str], Field(alias="$isubstr")] = None


class MindBridgeQueryTerm13(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_iprefix: Annotated[Optional[str], Field(alias="$iprefix")] = None


class MindBridgeQueryTerm14(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_niprefix: Annotated[Optional[str], Field(alias="$niprefix")] = None


class MindBridgeQueryTerm17(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_keyword_prefix: Annotated[Optional[str], Field(alias="$keyword_prefix")] = (
        None
    )


class MindBridgeQueryTerm18(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_keyword_prefix_not: Annotated[
        Optional[str], Field(alias="$keyword_prefix_not")
    ] = None


class MoneyRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    amount: Optional[int] = None
    currency: Optional[str] = None


class ObjectId(RootModel[Optional[str]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[str] = None


class ProblemType(str, Enum):
    """The type of problem."""

    UNKNOWN = "UNKNOWN"
    ILLEGAL_ARGUMENT = "ILLEGAL_ARGUMENT"
    CANNOT_DELETE = "CANNOT_DELETE"
    GREATER_VALUE_REQUIRED = "GREATER_VALUE_REQUIRED"
    LESS_VALUE_REQUIRED = "LESS_VALUE_REQUIRED"
    NON_UNIQUE_VALUE = "NON_UNIQUE_VALUE"
    USER_EMAIL_ALREADY_EXISTS = "USER_EMAIL_ALREADY_EXISTS"
    INCORRECT_DATA_TYPE = "INCORRECT_DATA_TYPE"
    RATIO_CONVERSION_FAILED = "RATIO_CONVERSION_FAILED"
    RISK_SCORE_FILTER_CONVERSION_FAILED = "RISK_SCORE_FILTER_CONVERSION_FAILED"
    FILTER_CONVERSION_FAILED = "FILTER_CONVERSION_FAILED"
    POPULATION_CONVERSION_FAILED = "POPULATION_CONVERSION_FAILED"
    INSUFFICIENT_PERMISSION = "INSUFFICIENT_PERMISSION"
    ACCOUNT_GROUPING_NODES_CONTAIN_ERRORS = "ACCOUNT_GROUPING_NODES_CONTAIN_ERRORS"
    ACCOUNT_GROUPING_IN_USE_BY_LIBRARY = "ACCOUNT_GROUPING_IN_USE_BY_LIBRARY"
    INVALID_ACCOUNT_GROUPING_FILE = "INVALID_ACCOUNT_GROUPING_FILE"
    DELIVERY_FAILURE = "DELIVERY_FAILURE"
    INVALID_STATE = "INVALID_STATE"


class Severity(str, Enum):
    """Indicates how severe the problem is."""

    WARNING = "WARNING"
    ERROR = "ERROR"


class Problem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    entity_id: Annotated[
        Optional[str],
        Field(
            alias="entityId",
            description="Identifies the entity impacted by the problem.",
        ),
    ] = None
    entity_type: Annotated[
        Optional[str],
        Field(
            alias="entityType",
            description="The type of entity impacted by the problem.",
        ),
    ] = None
    identifier: Annotated[
        Optional[str], Field(description="Identifies the field causing the problem.")
    ] = None
    problem_count: Annotated[
        Optional[int],
        Field(
            alias="problemCount",
            description="The total number of occurrences of this problem.",
        ),
    ] = None
    problem_type: Annotated[
        Optional[ProblemType],
        Field(alias="problemType", description="The type of problem."),
    ] = None
    reason: Annotated[
        Optional[str], Field(description="The reason(s) why the problem occurred.")
    ] = None
    severity: Annotated[
        Optional[Severity], Field(description="Indicates how severe the problem is.")
    ] = None
    suggested_values: Annotated[
        Optional[list[str]],
        Field(
            alias="suggestedValues",
            description="A suggested set of values to assist in resolving the problem.",
        ),
    ] = None
    values: Annotated[
        Optional[list[str]],
        Field(description="Identifies the values causing the problem."),
    ] = None


class ProblemRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    entity_id: Annotated[
        Optional[str],
        Field(
            alias="entityId",
            description="Identifies the entity impacted by the problem.",
        ),
    ] = None
    entity_type: Annotated[
        Optional[str],
        Field(
            alias="entityType",
            description="The type of entity impacted by the problem.",
        ),
    ] = None
    identifier: Annotated[
        Optional[str], Field(description="Identifies the field causing the problem.")
    ] = None
    problem_count: Annotated[
        Optional[int],
        Field(
            alias="problemCount",
            description="The total number of occurrences of this problem.",
        ),
    ] = None
    problem_type: Annotated[
        Optional[ProblemType],
        Field(alias="problemType", description="The type of problem."),
    ] = None
    reason: Annotated[
        Optional[str], Field(description="The reason(s) why the problem occurred.")
    ] = None
    severity: Annotated[
        Optional[Severity], Field(description="Indicates how severe the problem is.")
    ] = None
    suggested_values: Annotated[
        Optional[list[str]],
        Field(
            alias="suggestedValues",
            description="A suggested set of values to assist in resolving the problem.",
        ),
    ] = None
    values: Annotated[
        Optional[list[str]],
        Field(description="Identifies the values causing the problem."),
    ] = None


class RangeBigDecimal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max: Optional[float] = None
    min: Optional[float] = None


class RangeBigDecimalRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max: Optional[float] = None
    min: Optional[float] = None


class RangeInteger(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max: Optional[int] = None
    min: Optional[int] = None


class RangeIntegerRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max: Optional[int] = None
    min: Optional[int] = None


class RangeZonedDateTime(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max: Optional[AwareDatetime] = None
    min: Optional[AwareDatetime] = None


class RangeZonedDateTimeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max: Optional[AwareDatetime] = None
    min: Optional[AwareDatetime] = None


class Category(str, Enum):
    ACCOUNT_GROUPING = "ACCOUNT_GROUPING"
    ACCOUNT_MAPPING = "ACCOUNT_MAPPING"
    ADMIN_REPORT = "ADMIN_REPORT"
    ANALYSIS = "ANALYSIS"
    ANALYSIS_SETTINGS = "ANALYSIS_SETTINGS"
    ANALYSIS_TYPE = "ANALYSIS_TYPE"
    API_TOKEN = "API_TOKEN"
    AUDIT_ANNOTATION = "AUDIT_ANNOTATION"
    COLLECTION_ASSIGNMENT = "COLLECTION_ASSIGNMENT"
    CUSTOM_CONTROL_POINT = "CUSTOM_CONTROL_POINT"
    ENGAGEMENT = "ENGAGEMENT"
    ENGAGEMENT_ACCOUNT_GROUP = "ENGAGEMENT_ACCOUNT_GROUP"
    FILE_LOCKER = "FILE_LOCKER"
    FILE_MANAGER = "FILE_MANAGER"
    FILTER = "FILTER"
    GDPDU = "GDPDU"
    INGESTION = "INGESTION"
    INTEGRATIONS = "INTEGRATIONS"
    LIBRARY = "LIBRARY"
    MIGRATION = "MIGRATION"
    ORGANIZATION = "ORGANIZATION"
    POPULATION = "POPULATION"
    QUERY = "QUERY"
    RATIO = "RATIO"
    REPORT_BUILDER = "REPORT_BUILDER"
    REPORT = "REPORT"
    RESULTS_EXPORT = "RESULTS_EXPORT"
    RISK_RANGES = "RISK_RANGES"
    RISK_SEGMENTATION_DASHBOARD = "RISK_SEGMENTATION_DASHBOARD"
    SCIM_API = "SCIM_API"
    SUPPORT_ACCESS = "SUPPORT_ACCESS"
    TASK = "TASK"
    USER = "USER"
    WORKFLOW = "WORKFLOW"
    PAGE_VIEW = "PAGE_VIEW"
    ANALYSIS_SOURCE = "ANALYSIS_SOURCE"
    WEBHOOK = "WEBHOOK"
    CLOUD_ELEMENTS = "CLOUD_ELEMENTS"
    ENGAGEMENT_ACCOUNT_GROUPING_NODE = "ENGAGEMENT_ACCOUNT_GROUPING_NODE"


class RunActivityReportRequestRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    categories: Annotated[
        Optional[list[Category]],
        Field(
            description="The categories to include in the report. If empty, all categories will be included."
        ),
    ] = None
    end: Annotated[
        Optional[AwareDatetime],
        Field(description="The last date in the reporting timeframe."),
    ] = None
    only_completed_analyses: Annotated[
        Optional[bool],
        Field(
            alias="onlyCompletedAnalyses",
            description="Restrict entries to analysis complete events.",
        ),
    ] = None
    start: Annotated[
        Optional[AwareDatetime],
        Field(description="The first date in the reporting timeframe."),
    ] = None
    user_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="userIds",
            description="The users to include in the report. If empty, all users will be included.",
        ),
    ] = None


class RunAdminReportRequestRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    end: Annotated[
        Optional[AwareDatetime],
        Field(description="The last date in the reporting timeframe."),
    ] = None
    start: Annotated[
        Optional[AwareDatetime],
        Field(description="The first date in the reporting timeframe."),
    ] = None


class Operator4Enum(str, Enum):
    FIELD_EQ = "$eq"
    FIELD_NE = "$ne"
    FIELD_GT = "$gt"
    FIELD_GTE = "$gte"
    FIELD_LT = "$lt"
    FIELD_LTE = "$lte"
    FIELD_CONTAINS = "$contains"
    FIELD_NCONTAINS = "$ncontains"
    FIELD_IN = "$in"
    FIELD_NIN = "$nin"
    FIELD_FLAGS = "$flags"
    FIELD_KEYWORD_PREFIX = "$keyword_prefix"
    FIELD_KEYWORD_PREFIX_NOT = "$keyword_prefix_not"
    FIELD_ISUBSTR = "$isubstr"
    FIELD_IPREFIX = "$iprefix"
    FIELD_NIPREFIX = "$niprefix"
    FIELD_AND = "$and"
    FIELD_OR = "$or"
    FIELD_POPULATION = "$population"
    FIELD_NOT_POPULATION = "$not_population"


class Operator4(RootModel[Optional[Operator4Enum]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[Operator4Enum] = None


class ShieldQueryTerm(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    operator: Optional[Operator4] = None


class Operator5Enum(str, Enum):
    FIELD_EQ = "$eq"
    FIELD_NE = "$ne"
    FIELD_GT = "$gt"
    FIELD_GTE = "$gte"
    FIELD_LT = "$lt"
    FIELD_LTE = "$lte"
    FIELD_CONTAINS = "$contains"
    FIELD_NCONTAINS = "$ncontains"
    FIELD_IN = "$in"
    FIELD_NIN = "$nin"
    FIELD_FLAGS = "$flags"
    FIELD_KEYWORD_PREFIX = "$keyword_prefix"
    FIELD_KEYWORD_PREFIX_NOT = "$keyword_prefix_not"
    FIELD_ISUBSTR = "$isubstr"
    FIELD_IPREFIX = "$iprefix"
    FIELD_NIPREFIX = "$niprefix"
    FIELD_AND = "$and"
    FIELD_OR = "$or"
    FIELD_POPULATION = "$population"
    FIELD_NOT_POPULATION = "$not_population"


class Operator5(RootModel[Optional[Operator5Enum]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[Operator5Enum] = None


class ShieldQueryTermRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    operator: Optional[Operator5] = None


class SortnullRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    empty: Optional[bool] = None
    sorted: Optional[bool] = None
    unsorted: Optional[bool] = None


class UserLoginWebhookData(RootModel[Optional[Any]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[Any] = None


class Type52(str, Enum):
    """The event type that triggered the webhook."""

    USER_LOGIN = "user.login"


class UserLoginWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[UserLoginWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type52],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class UserStatusWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    status: Annotated[
        Optional[str],
        Field(
            description="Identifies the status change that triggered the webhook event."
        ),
    ] = None
    target_user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="targetUserId",
            description="The ID of the data associated with the webhook event.",
        ),
    ] = None


class Type53(str, Enum):
    """The event type that triggered the webhook."""

    USER_STATUS = "user.status"


class UserStatusWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[UserStatusWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type53],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class UserWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    target_user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="targetUserId",
            description="The ID of the data associated with the webhook event.",
        ),
    ] = None


class Type54(str, Enum):
    """The event type that triggered the webhook."""

    USER_INVITED = "user.invited"
    USER_ROLE = "user.role"
    USER_DELETED = "user.deleted"


class UserWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[UserWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type54],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class Type55(str, Enum):
    """The event type that triggered the webhook."""

    EXPORT_READY = "export.ready"
    DATA_ADDED = "data.added"
    INGESTION_COMPLETE = "ingestion.complete"
    INGESTION_FAILED = "ingestion.failed"
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    UNMAPPED_ACCOUNTS = "unmapped.accounts"
    ENGAGEMENT_CREATED = "engagement.created"
    ENGAGEMENT_UPDATED = "engagement.updated"
    ENGAGEMENT_DELETED = "engagement.deleted"
    ANALYSIS_CREATED = "analysis.created"
    ANALYSIS_UPDATED = "analysis.updated"
    ANALYSIS_DELETED = "analysis.deleted"
    ANALYSIS_ARCHIVED = "analysis.archived"
    ANALYSIS_UNARCHIVED = "analysis.unarchived"
    USER_INVITED = "user.invited"
    USER_STATUS = "user.status"
    USER_ROLE = "user.role"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"


class WebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type55],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class ApiFilterConditionCreate(RootModel[Optional[Any]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[Any] = None


class ApiFilterConditionRead(RootModel[Optional[Any]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[Any] = None


class ApiFilterConditionUpdate(RootModel[Optional[Any]]):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[Any] = None


class ActionableErrorResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    entity_id: Annotated[
        Optional[str],
        Field(
            alias="entityId", description="Identifies the entity impacted by the error."
        ),
    ] = None
    entity_type: Annotated[
        Optional[str],
        Field(
            alias="entityType", description="The type of entity impacted by the error."
        ),
    ] = None
    instance: Annotated[
        Optional[str], Field(description="A unique identifier for this request.")
    ] = None
    origin: Annotated[
        Optional[str],
        Field(description="The endpoint where this request originated from."),
    ] = None
    problem_count: Annotated[
        Optional[int],
        Field(alias="problemCount", description="The total number of problems."),
    ] = None
    problems: Annotated[
        Optional[list[Problem]],
        Field(description="The reason(s) why the error occurred."),
    ] = None
    status: Annotated[
        Optional[int],
        Field(description="The HTTP status code determined by the error type."),
    ] = None
    title: Annotated[
        Optional[str], Field(description="A description of the error.")
    ] = None
    type: Annotated[
        Optional[str],
        Field(
            description="Indicates the type of error that occurred. Type values are formatted as URLs."
        ),
    ] = None


class AnalysisResultWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="analysisId",
            description="The ID of the Analysis associated with the webhook event.",
        ),
    ] = None
    analysis_result_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="analysisResultId",
            description="The ID of the Analysis Result associated with the webhook event.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="engagementId",
            description="The ID of the Engagement associated with the webhook event.",
        ),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None


class AnalysisResultWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[AnalysisResultWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type], Field(description="The event type that triggered the webhook.")
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class AnalysisSourceWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="analysisId",
            description="The ID of the Analysis associated with the webhook event.",
        ),
    ] = None
    analysis_source_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="analysisSourceId",
            description="The ID of the Analysis Source associated with the event.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="engagementId",
            description="The ID of the Engagement associated with the webhook event.",
        ),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None


class AnalysisSourceWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[AnalysisSourceWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type1], Field(description="The event type that triggered the webhook.")
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class AnalysisWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="analysisId",
            description="The ID of the Analysis associated with the webhook event.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="engagementId",
            description="The ID of the Engagement associated with the webhook event.",
        ),
    ] = None


class ApiAccountGrouping(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    archived: Annotated[
        Optional[bool],
        Field(description="When `true`, the account grouping is archived."),
    ] = None
    code_display_name: Annotated[
        Optional[dict[str, str]],
        Field(
            alias="codeDisplayName",
            description="The name of the account code hierarchy system used within the dataset.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfo],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The delimiter character used to separate each category level in an account grouping code."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfo],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    mac: Annotated[
        Optional[bool],
        Field(
            description="When `true`, the account grouping is based on the MAC code system."
        ),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of the account grouping.")
    ] = None
    publish_status: Annotated[
        Optional[PublishStatus],
        Field(
            alias="publishStatus",
            description="The current status of the account grouping.",
        ),
    ] = None
    published_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="publishedDate",
            description="The date that the account grouping was published.",
        ),
    ] = None
    system: Annotated[
        Optional[bool],
        Field(
            description="When `true`, the account grouping is a system account grouping and cannot be modified."
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class ApiAccountGroupingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    archived: Annotated[
        Optional[bool],
        Field(description="When `true`, the account grouping is archived."),
    ] = None
    code_display_name: Annotated[
        Optional[dict[str, str]],
        Field(
            alias="codeDisplayName",
            description="The name of the account code hierarchy system used within the dataset.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The delimiter character used to separate each category level in an account grouping code."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    mac: Annotated[
        Optional[bool],
        Field(
            description="When `true`, the account grouping is based on the MAC code system."
        ),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of the account grouping.")
    ] = None
    publish_status: Annotated[
        Optional[PublishStatus],
        Field(
            alias="publishStatus",
            description="The current status of the account grouping.",
        ),
    ] = None
    published_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="publishedDate",
            description="The date that the account grouping was published.",
        ),
    ] = None
    system: Annotated[
        Optional[bool],
        Field(
            description="When `true`, the account grouping is a system account grouping and cannot be modified."
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class ApiAccountMappingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account: Annotated[
        Optional[str],
        Field(description="The account name as provided in the source data."),
    ] = None
    account_description: Annotated[
        Optional[str],
        Field(
            alias="accountDescription",
            description="The description of the account as provided in the source data.",
        ),
    ] = None
    account_tags: Annotated[
        Optional[list[str]],
        Field(
            alias="accountTags",
            description="A list of account tags associated with this account.",
        ),
    ] = None
    code: Annotated[
        Optional[str],
        Field(description="The account grouping code mapped to this account."),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    fund_id: Annotated[
        Optional[str],
        Field(alias="fundId", description="The fund that includes this account."),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    status: Annotated[
        Optional[Status],
        Field(description="Indicates the current status of the account mapping."),
    ] = None
    used_by_analysis_sources: Annotated[
        Optional[list[str]],
        Field(
            alias="usedByAnalysisSources",
            description="A list of analysis sources that use this account.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class ApiAnalysisConfigRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    risk_groups: Annotated[
        Optional[list[ApiRiskGroupRead]],
        Field(
            alias="riskGroups",
            description="The list of risk groups associated with this analysis config.",
        ),
    ] = None


class ApiAnalysisConfigUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    risk_groups: Annotated[
        Optional[list[ApiRiskGroupUpdate]],
        Field(
            alias="riskGroups",
            description="The list of risk groups associated with this analysis config.",
        ),
    ] = None


class ApiAnalysisResultRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="Identifies the associated analysis."),
    ] = None
    analysis_periods: Annotated[
        Optional[list[ApiAnalysisPeriodRead]],
        Field(
            alias="analysisPeriods",
            description="Details about the specific analysis periods under audit.",
        ),
    ] = None
    analysis_type_id: Annotated[
        Optional[str],
        Field(alias="analysisTypeId", description="Identifies the type of analysis."),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    interim: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis is using an interim time frame."
        ),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class ApiAnalysisSourceTypeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    archived: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis source type is archived."
        ),
    ] = None
    column_definitions: Annotated[
        Optional[list[ApiColumnDefinitionRead]],
        Field(
            alias="columnDefinitions",
            description="A list of MindBridge column definitions that this analysis source type supports.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    features: Annotated[
        Optional[list[Feature]],
        Field(
            description="A list of the features used when importing data for this analysis source type."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    interim_name: Annotated[
        Optional[str],
        Field(
            alias="interimName",
            description="The name of the analysis source type when the analysis uses an interim time frame.",
        ),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the analysis source type.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiAnalysisTypeConfigurationRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(
            alias="analysisId",
            description="Identifies the analysis associated with this configuration.",
        ),
    ] = None
    analysis_type_id: Annotated[
        Optional[str],
        Field(alias="analysisTypeId", description="Identifies the type of analysis."),
    ] = None
    configuration: Annotated[
        Optional[ApiAnalysisConfigRead],
        Field(description="The configuration details for this analysis type."),
    ] = None
    control_point_bundle_version: Annotated[
        Optional[str],
        Field(
            alias="controlPointBundleVersion",
            description="The version of the control point bundle used in this configuration.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    library_id: Annotated[
        Optional[str],
        Field(
            alias="libraryId",
            description="Identifies the library associated with this configuration.",
        ),
    ] = None
    system: Optional[bool] = None
    template: Annotated[
        Optional[bool],
        Field(description="Indicates whether this configuration is a template."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiAnalysisTypeConfigurationUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    configuration: Annotated[
        Optional[ApiAnalysisConfigUpdate],
        Field(description="The configuration details for this analysis type."),
    ] = None
    system: Optional[bool] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiAnalysisTypeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_mapping_required: Annotated[
        Optional[bool],
        Field(
            alias="accountMappingRequired",
            description="Indicates whether or not account mapping must be performed.",
        ),
    ] = None
    archived: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis type has been archived."
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    description: Annotated[
        Optional[str], Field(description="The description of the analysis type.")
    ] = None
    fund_supported: Annotated[
        Optional[bool],
        Field(
            alias="fundSupported",
            description="Indicates whether or not the analysis supports restricted and unrestricted funds.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    interim_name: Annotated[
        Optional[str],
        Field(
            alias="interimName",
            description="The name of the analysis type when the analysis uses an interim time frame.",
        ),
    ] = None
    interim_supported: Annotated[
        Optional[bool],
        Field(
            alias="interimSupported",
            description="Indicates whether or not the analysis supports the interim time frame.",
        ),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    max_period: Annotated[
        Optional[int],
        Field(
            alias="maxPeriod",
            description="A configuration value for the max analysis period.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the analysis type.")
    ] = None
    periodic_supported: Annotated[
        Optional[bool],
        Field(
            alias="periodicSupported",
            description="Indicates whether or not the analysis supports the periodic time frame.",
        ),
    ] = None
    source_configurations: Annotated[
        Optional[list[ApiSourceConfigurationRead]],
        Field(
            alias="sourceConfigurations",
            description="A list of analysis source configurations that can be imported into the analysis, as determined by the analysis type.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiAnalysisRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_period_gaps: Annotated[
        Optional[list[ApiAnalysisPeriodGapRead]],
        Field(
            alias="analysisPeriodGaps",
            description="Details about the gap in time between two analysis periods.",
        ),
    ] = None
    analysis_periods: Annotated[
        Optional[list[ApiAnalysisPeriodRead]],
        Field(
            alias="analysisPeriods",
            description="Details about the specific analysis periods under audit.",
        ),
    ] = None
    analysis_type_id: Annotated[
        Optional[str],
        Field(alias="analysisTypeId", description="Identifies the type of analysis."),
    ] = None
    archived: Annotated[
        Optional[bool],
        Field(description="Indicates whether or not the analysis has been archived."),
    ] = None
    converted: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not an interim analysis time frame has been converted to a full analysis time frame."
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    currency_code: Annotated[
        Optional[str],
        Field(
            alias="currencyCode",
            description="The currency to be displayed across the analysis results.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    important_columns: Annotated[
        Optional[list[ApiAnalysisImportantColumnRead]],
        Field(
            alias="importantColumns",
            description="Additional data columns that can be used when importing additional data.",
        ),
    ] = None
    interim: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis is using an interim time frame."
        ),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    latest_analysis_result_id: Annotated[
        Optional[str], Field(alias="latestAnalysisResultId")
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the analysis.", max_length=80, min_length=0),
    ] = None
    periodic: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the analysis is using a periodic time frame."
        ),
    ] = None
    reference_id: Annotated[
        Optional[str],
        Field(
            alias="referenceId",
            description="A reference ID to identify the analysis.",
            max_length=256,
            min_length=0,
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiApiTokenRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    allowed_addresses: Annotated[
        Optional[list[str]],
        Field(
            alias="allowedAddresses",
            description="Indicates the set of addresses that are allowed to use this token. If empty, any address may use it.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    expiry: Annotated[
        Optional[AwareDatetime],
        Field(description="The day on which the API token expires."),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The token record’s name. This will also be used as the API Token User’s name."
        ),
    ] = None
    partial_token: Annotated[
        Optional[str],
        Field(
            alias="partialToken",
            description="A partial representation of the API token.",
        ),
    ] = None
    permissions: Annotated[
        Optional[list[Permission]],
        Field(
            description="The set of permissions that inform which endpoints this token is authorized to access."
        ),
    ] = None
    user_id: Annotated[
        Optional[str],
        Field(
            alias="userId",
            description="Identifies the API Token User associated with this token.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiAsyncResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfo],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    entity_id: Annotated[
        Optional[str],
        Field(alias="entityId", description="Identifies the entity used in the job."),
    ] = None
    entity_type: Annotated[
        Optional[EntityType],
        Field(
            alias="entityType",
            description="Identifies the entity type used in the job.",
        ),
    ] = None
    error: Annotated[
        Optional[str], Field(description="The reason why the async job failed.")
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfo],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    status: Annotated[
        Optional[Status3], Field(description="Indicates the current state of the job.")
    ] = None
    type: Annotated[
        Optional[Type3], Field(description="Indicates the type of job being run.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiAsyncResultRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    entity_id: Annotated[
        Optional[str],
        Field(alias="entityId", description="Identifies the entity used in the job."),
    ] = None
    entity_type: Annotated[
        Optional[EntityType],
        Field(
            alias="entityType",
            description="Identifies the entity type used in the job.",
        ),
    ] = None
    error: Annotated[
        Optional[str], Field(description="The reason why the async job failed.")
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    status: Annotated[
        Optional[Status3], Field(description="Indicates the current state of the job.")
    ] = None
    type: Annotated[
        Optional[Type3], Field(description="Indicates the type of job being run.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiBasicMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiBasicMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiChunkedFileRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    chunked_file_parts: Annotated[
        Optional[list[ApiChunkedFilePartRead]],
        Field(
            alias="chunkedFileParts",
            description="The offset and size of the chunked file parts.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the chunked file.")
    ] = None
    size: Annotated[
        Optional[int], Field(description="The size of the chunked file.", ge=0)
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiCountMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiCountMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    count: Annotated[
        Optional[int], Field(description="The amount of a given metric.")
    ] = None
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None


class ApiDateTypeDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ambiguous_date_time_formats: Annotated[
        Optional[list[ApiColumnDateTimeFormat]],
        Field(
            alias="ambiguousDateTimeFormats",
            description="A list of possible date time formats, if multiple possible candidates are available.",
        ),
    ] = None
    range: Annotated[
        Optional[RangeZonedDateTime],
        Field(
            description="A pair of values representing the earliest and latest values within this column."
        ),
    ] = None
    unambiguous_date_time_formats: Annotated[
        Optional[list[ApiColumnDateTimeFormat]],
        Field(
            alias="unambiguousDateTimeFormats",
            description="A list of possible date time formats, if multiple possible candidates are available.",
        ),
    ] = None


class ApiDateTypeDetailsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ambiguous_date_time_formats: Annotated[
        Optional[list[ApiColumnDateTimeFormatRead]],
        Field(
            alias="ambiguousDateTimeFormats",
            description="A list of possible date time formats, if multiple possible candidates are available.",
        ),
    ] = None
    range: Annotated[
        Optional[RangeZonedDateTimeRead],
        Field(
            description="A pair of values representing the earliest and latest values within this column."
        ),
    ] = None
    unambiguous_date_time_formats: Annotated[
        Optional[list[ApiColumnDateTimeFormatRead]],
        Field(
            alias="unambiguousDateTimeFormats",
            description="A list of possible date time formats, if multiple possible candidates are available.",
        ),
    ] = None


class ApiDuplicateVirtualColumnRead(ApiVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the duplicated column."
        ),
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiDuplicateVirtualColumnUpdate(ApiVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the duplicated column."
        ),
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiEngagementAccountGroupingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_grouping_id: Annotated[
        Optional[str],
        Field(
            alias="accountGroupingId",
            description="The unique identifier of the account grouping on which this is based.",
        ),
    ] = None
    code_display_name: Annotated[
        Optional[dict[str, str]],
        Field(
            alias="codeDisplayName",
            description="The name of the account code hierarchy system used within the dataset.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The delimiter character used to separate each category level in an account grouping code."
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="The unique identifier of the engagement that this engagement account grouping belongs to.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of the account grouping.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class ApiEngagementRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    accounting_package: Annotated[
        Optional[str],
        Field(
            alias="accountingPackage",
            description="The ERP or financial management system that your client is using.",
        ),
    ] = None
    accounting_period: Annotated[
        Optional[ApiAccountingPeriodRead],
        Field(
            alias="accountingPeriod", description="Details about the accounting period."
        ),
    ] = None
    audit_period_end_date: Annotated[
        Optional[date],
        Field(
            alias="auditPeriodEndDate",
            description="The last day of the occurring audit.",
        ),
    ] = None
    auditor_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="auditorIds",
            description="Identifies the users who will act as auditors in the engagement.",
        ),
    ] = None
    billing_code: Annotated[
        Optional[str],
        Field(
            alias="billingCode",
            description="A unique code that associates engagements and analyses with clients to ensure those clients are billed appropriately for MindBridge usage.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    engagement_lead_id: Annotated[
        Optional[str],
        Field(
            alias="engagementLeadId",
            description="Identifies the user who will lead the engagement.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    industry: Annotated[
        Optional[str],
        Field(description="The type of industry that your client operates within."),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    library_id: Annotated[
        Optional[str], Field(alias="libraryId", description="Identifies the library.")
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the engagement.", max_length=80, min_length=0),
    ] = None
    organization_id: Annotated[
        Optional[str],
        Field(alias="organizationId", description="Identifies the organization."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiFileExportRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the file export.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    file_name: Annotated[
        Optional[str], Field(alias="fileName", description="The name of the file.")
    ] = None
    id: Annotated[
        Optional[str], Field(description="The unique file export identifier.")
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the file export.",
        ),
    ] = None
    size: Annotated[Optional[int], Field(description="The size of the file.")] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiFileInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    format: Annotated[
        Optional[Format], Field(description="The grouped format that was detected.")
    ] = None
    format_detected: Annotated[
        Optional[bool],
        Field(
            alias="formatDetected",
            description="When `true` a known grouped format was detected.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the underlying file or table.")
    ] = None
    type: Annotated[
        Optional[Type7],
        Field(description="The type of file info entity.", title="File Info Type"),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiFileInfoRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    format: Annotated[
        Optional[Format], Field(description="The grouped format that was detected.")
    ] = None
    format_detected: Annotated[
        Optional[bool],
        Field(
            alias="formatDetected",
            description="When `true` a known grouped format was detected.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str], Field(description="The name of the underlying file or table.")
    ] = None
    type: Annotated[
        Optional[Type7],
        Field(description="The type of file info entity.", title="File Info Type"),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiFileManagerDirectoryUpdate(ApiFileManagerEntityUpdate):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[Optional[str], Field(description="The name of the directory.")] = (
        None
    )
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiFileManagerEntityRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    parent_file_manager_entity_id: Annotated[
        Optional[str],
        Field(
            alias="parentFileManagerEntityId",
            description="Identifies the parent directory. If NULL, the directory is positioned at the root level.",
        ),
    ] = None
    type: Annotated[
        Optional[Type9],
        Field(description="Indicates whether the object is a DIRECTORY or a FILE."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiFileManagerFileRead(ApiFileManagerEntityRead):
    model_config = ConfigDict(populate_by_name=True)
    extension: Annotated[
        Optional[str], Field(description="The suffix used at the end of the file.")
    ] = None
    file_info_id: Annotated[
        Optional[str],
        Field(alias="fileInfoId", description="Identifies the associated file info."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The current name of the file, excluding the extension."),
    ] = None
    original_name: Annotated[
        Optional[str],
        Field(
            alias="originalName",
            description="The name of the file as it appeared when first imported, including the extension.",
        ),
    ] = None
    status: Annotated[
        Optional[list[StatusEnum]],
        Field(description="The status of the file as it appears in MindBridge."),
    ] = None
    engagement_id: Annotated[
        str,
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiFilterAccountCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_selections: Annotated[
        Optional[list[ApiFilterAccountSelection]], Field(alias="accountSelections")
    ] = None
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterControlPointCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    control_points: Annotated[
        Optional[list[ApiFilterControlPointSelection]],
        Field(alias="controlPoints", description="A list of control point selections."),
    ] = None
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    risk_level: Annotated[
        Optional[RiskLevel],
        Field(
            alias="riskLevel",
            description="The risk level of the selected control points.",
            title="Filter Control Point Risk Level",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterGroupConditionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conditions: Annotated[
        Optional[list[ApiFilterConditionCreate]],
        Field(description="The entries within this condition group."),
    ] = None
    operator: Annotated[
        Optional[Operator],
        Field(
            description="The operator to be applied to conditions within this group.",
            title="Filter Group Operator",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterGroupConditionRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conditions: Annotated[
        Optional[list[ApiFilterConditionRead]],
        Field(description="The entries within this condition group."),
    ] = None
    operator: Annotated[
        Optional[Operator],
        Field(
            description="The operator to be applied to conditions within this group.",
            title="Filter Group Operator",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterGroupConditionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conditions: Annotated[
        Optional[list[ApiFilterConditionUpdate]],
        Field(description="The entries within this condition group."),
    ] = None
    operator: Annotated[
        Optional[Operator],
        Field(
            description="The operator to be applied to conditions within this group.",
            title="Filter Group Operator",
        ),
    ] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None


class ApiFilterTypeaheadEntryCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field: Optional[str] = None
    field_label: Annotated[Optional[str], Field(alias="fieldLabel")] = None
    full_condition_description: Annotated[
        Optional[str], Field(alias="fullConditionDescription")
    ] = None
    negated: Optional[bool] = None
    type: Annotated[Optional[Type11], Field(title="Filter Condition Type")] = None
    values: Annotated[
        Optional[list[ApiTypeaheadEntry]],
        Field(
            description="A list of typeahead entry selections to be used in the filter."
        ),
    ] = None


class ApiFilterCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisTypeId",
            description="Identifies the associated analysis type.",
        ),
    ] = None
    category: Annotated[
        Optional[dict[str, str]], Field(description="The category of this filter.")
    ] = None
    condition: Annotated[
        Optional[ApiFilterGroupConditionCreate],
        Field(
            description="A group filter containing all the conditions included in this filter."
        ),
    ] = None
    data_type: Annotated[
        Optional[DataType],
        Field(
            alias="dataType",
            description="The intended data type for this filter.",
            title="Filter Data Type",
        ),
    ] = None
    display_currency_code: Annotated[
        Optional[str],
        Field(
            alias="displayCurrencyCode",
            description="The ISO 4217 3 digit currency code used to determine how currency values are formatted for display. Defaults to `USD` if no value is selected.",
        ),
    ] = None
    display_locale: Annotated[
        Optional[str],
        Field(
            alias="displayLocale",
            description="The ISO 639 locale identifier used when formatting some display values. Defaults to `en-us` if no value is specified.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="Identifies the parent engagement, if applicable. Can only be set if `filterType` is `ENGAGEMENT`.",
        ),
    ] = None
    filter_type: Annotated[
        Optional[FilterType],
        Field(
            alias="filterType",
            description="The type of this filter. Determines in which context analyses can access it.",
            title="Filter Type",
        ),
    ] = None
    library_id: Annotated[
        Optional[str],
        Field(
            alias="libraryId",
            description="Identifies the parent library, if applicable. Can only be set if `filterType` is `LIBRARY`.",
        ),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of this filter.")
    ] = None
    organization_id: Annotated[
        Optional[str],
        Field(
            alias="organizationId",
            description="Identifies the parent organization, if applicable. Can only be set if `filterType` is `ORGANIZATION` or `PRIVATE`.",
        ),
    ] = None


class ApiFilterRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisTypeId",
            description="Identifies the associated analysis type.",
        ),
    ] = None
    category: Annotated[
        Optional[dict[str, str]], Field(description="The category of this filter.")
    ] = None
    condition: Annotated[
        Optional[ApiFilterGroupConditionRead],
        Field(
            description="A group filter containing all the conditions included in this filter."
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    data_type: Annotated[
        Optional[DataType],
        Field(
            alias="dataType",
            description="The intended data type for this filter.",
            title="Filter Data Type",
        ),
    ] = None
    display_currency_code: Annotated[
        Optional[str],
        Field(
            alias="displayCurrencyCode",
            description="The ISO 4217 3 digit currency code used to determine how currency values are formatted for display. Defaults to `USD` if no value is selected.",
        ),
    ] = None
    display_locale: Annotated[
        Optional[str],
        Field(
            alias="displayLocale",
            description="The ISO 639 locale identifier used when formatting some display values. Defaults to `en-us` if no value is specified.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId",
            description="Identifies the parent engagement, if applicable. Can only be set if `filterType` is `ENGAGEMENT`.",
        ),
    ] = None
    filter_type: Annotated[
        Optional[FilterType],
        Field(
            alias="filterType",
            description="The type of this filter. Determines in which context analyses can access it.",
            title="Filter Type",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    legacy_filter_format: Annotated[
        Optional[bool],
        Field(
            alias="legacyFilterFormat",
            description="If `true` this filter is saved in a legacy format that can’t be represented in the  API.",
        ),
    ] = None
    library_id: Annotated[
        Optional[str],
        Field(
            alias="libraryId",
            description="Identifies the parent library, if applicable. Can only be set if `filterType` is `LIBRARY`.",
        ),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of this filter.")
    ] = None
    organization_id: Annotated[
        Optional[str],
        Field(
            alias="organizationId",
            description="Identifies the parent organization, if applicable. Can only be set if `filterType` is `ORGANIZATION` or `PRIVATE`.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiFilterUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category: Annotated[
        Optional[dict[str, str]], Field(description="The category of this filter.")
    ] = None
    condition: Annotated[
        Optional[ApiFilterGroupConditionUpdate],
        Field(
            description="A group filter containing all the conditions included in this filter."
        ),
    ] = None
    display_currency_code: Annotated[
        Optional[str],
        Field(
            alias="displayCurrencyCode",
            description="The ISO 4217 3 digit currency code used to determine how currency values are formatted for display. Defaults to `USD` if no value is selected.",
        ),
    ] = None
    display_locale: Annotated[
        Optional[str],
        Field(
            alias="displayLocale",
            description="The ISO 639 locale identifier used when formatting some display values. Defaults to `en-us` if no value is specified.",
        ),
    ] = None
    filter_type: Annotated[
        Optional[FilterType],
        Field(
            alias="filterType",
            description="The type of this filter. Determines in which context analyses can access it.",
            title="Filter Type",
        ),
    ] = None
    name: Annotated[
        Optional[dict[str, str]], Field(description="The name of this filter.")
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="Data integrity version to ensure data consistency."),
    ] = None


class ApiJoinVirtualColumnRead(ApiVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_indices: Annotated[
        Optional[list[int]],
        Field(alias="columnIndices", description="The position of the joined column."),
    ] = None
    delimiter: Annotated[
        Optional[str], Field(description="The character(s) used to separate values.")
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiJoinVirtualColumnUpdate(ApiVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_indices: Annotated[
        Optional[list[int]],
        Field(alias="columnIndices", description="The position of the joined column."),
    ] = None
    delimiter: Annotated[
        Optional[str], Field(description="The character(s) used to separate values.")
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiJsonTableRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    current_size: Annotated[
        Optional[int],
        Field(
            alias="currentSize",
            description="The combined size of all data that has been appended to this JSON table.",
        ),
    ] = None
    headers: Optional[list[str]] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(description="The data integrity version, to ensure data consistency."),
    ] = None


class ApiLibraryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account_grouping_id: Annotated[
        Optional[str],
        Field(
            alias="accountGroupingId",
            description="Identifies the account grouping used.",
        ),
    ] = None
    analysis_type_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="analysisTypeIds",
            description="Identifies the analysis types used in the library.",
        ),
    ] = None
    archived: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the library is archived. Archived libraries cannot be selected when creating an engagement."
        ),
    ] = None
    based_on_library_id: Annotated[
        Optional[str],
        Field(
            alias="basedOnLibraryId",
            description="Identifies the library that the new library is based on. This may be a user-created library or a MindBridge system library.",
        ),
    ] = None
    control_point_selection_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointSelectionPermission",
            description="When set to `true`, control points can be added or removed within each risk score.",
        ),
    ] = None
    control_point_settings_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointSettingsPermission",
            description="When set to `true`, individual control point settings can be adjusted within each risk score.",
        ),
    ] = None
    control_point_weight_permission: Annotated[
        Optional[bool],
        Field(
            alias="controlPointWeightPermission",
            description="When set to `true`, the weight of each control point can be adjusted within each risk score.",
        ),
    ] = None
    conversion_warnings: Annotated[
        Optional[list[ProblemRead]],
        Field(
            alias="conversionWarnings",
            description="A list of accounts that failed to convert the selected base library’s setting to the selected account grouping.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    default_delimiter: Annotated[
        Optional[str],
        Field(
            alias="defaultDelimiter",
            description="Identifies the default delimiter used in imported CSV files.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The current name of the library.", max_length=80, min_length=0
        ),
    ] = None
    original_system_library_id: Annotated[
        Optional[str],
        Field(
            alias="originalSystemLibraryId",
            description="Identifies the original MindBridge-supplied library.",
        ),
    ] = None
    risk_range_edit_permission: Annotated[
        Optional[bool], Field(alias="riskRangeEditPermission")
    ] = None
    risk_score_and_groups_selection_permission: Annotated[
        Optional[bool],
        Field(
            alias="riskScoreAndGroupsSelectionPermission",
            description="When set to `true`, risk scores and groups can be disabled, and accounts associated with risk scores can be edited.",
        ),
    ] = None
    risk_score_display: Annotated[
        Optional[RiskScoreDisplay],
        Field(
            alias="riskScoreDisplay",
            description="Determines whether risk scores will be presented as percentages (%), or using High, Medium, and Low label indicators.",
        ),
    ] = None
    system: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether or not the library is a MindBridge system library."
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None
    warnings_dismissed: Annotated[
        Optional[bool],
        Field(
            alias="warningsDismissed",
            description="When set to `true`, any conversion warnings for this library will not be displayed in the **Libraries** tab in the UI.",
        ),
    ] = None


class ApiNumericTypeDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    capped_max: Annotated[
        Optional[bool],
        Field(
            alias="cappedMax",
            description="If `true` then at least one individual value is larger than 10e<sup>50</sup>.",
        ),
    ] = None
    capped_sum: Annotated[
        Optional[bool],
        Field(
            alias="cappedSum",
            description="If `true` then the sum is larger than 10e<sup>50</sup>.",
        ),
    ] = None
    currency_format: Annotated[
        Optional[ApiCurrencyFormat],
        Field(
            alias="currencyFormat",
            description="Metadata on the detected number format of this column.",
        ),
    ] = None
    example_pair_from_currency_formatter: Annotated[
        Optional[list[str]],
        Field(
            alias="examplePairFromCurrencyFormatter",
            description="A pair of values as examples in the event that two or more unambiguous number formats are detected in the same column.",
        ),
    ] = None
    range: Annotated[
        Optional[RangeBigDecimal],
        Field(
            description="A pair of values representing the min and max values within this column."
        ),
    ] = None
    sum: Annotated[
        Optional[float],
        Field(
            description="The sum of all values in this column, up to a maximum of 10e<sup>50</sup>. Values smaller than 10e<sup>-50</sup> will be rounded up."
        ),
    ] = None


class ApiNumericTypeDetailsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    capped_max: Annotated[
        Optional[bool],
        Field(
            alias="cappedMax",
            description="If `true` then at least one individual value is larger than 10e<sup>50</sup>.",
        ),
    ] = None
    capped_sum: Annotated[
        Optional[bool],
        Field(
            alias="cappedSum",
            description="If `true` then the sum is larger than 10e<sup>50</sup>.",
        ),
    ] = None
    currency_format: Annotated[
        Optional[ApiCurrencyFormatRead],
        Field(
            alias="currencyFormat",
            description="Metadata on the detected number format of this column.",
        ),
    ] = None
    example_pair_from_currency_formatter: Annotated[
        Optional[list[str]],
        Field(
            alias="examplePairFromCurrencyFormatter",
            description="A pair of values as examples in the event that two or more unambiguous number formats are detected in the same column.",
        ),
    ] = None
    range: Annotated[
        Optional[RangeBigDecimalRead],
        Field(
            description="A pair of values representing the min and max values within this column."
        ),
    ] = None
    sum: Annotated[
        Optional[float],
        Field(
            description="The sum of all values in this column, up to a maximum of 10e<sup>50</sup>. Values smaller than 10e<sup>-50</sup> will be rounded up."
        ),
    ] = None


class ApiOrganizationRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    external_client_code: Annotated[
        Optional[str],
        Field(
            alias="externalClientCode",
            description="The unique client ID applied to this organization.",
            max_length=80,
            min_length=0,
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    manager_user_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="managerUserIds",
            description="Identifies users assigned to the organization manager role.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the organization.", max_length=80, min_length=0),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiPageableRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    offset: Annotated[
        Optional[int],
        Field(description="Indicates by how many pages the first page is offset."),
    ] = None
    page_number: Annotated[
        Optional[int], Field(alias="pageNumber", description="The current page number.")
    ] = None
    page_size: Annotated[
        Optional[int],
        Field(
            alias="pageSize", description="The number of requested elements on a page."
        ),
    ] = None
    sort: Annotated[
        Optional[SortnullRead],
        Field(description="Indicates how the data will be sorted."),
    ] = None


class ApiPopulationTagCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="The ID of the parent analysis."),
    ] = None
    analysis_type_id: Annotated[Optional[str], Field(alias="analysisTypeId")] = None
    base_population_id: Annotated[
        Optional[str],
        Field(
            alias="basePopulationId",
            description="The ID of the population the current population is based on.",
        ),
    ] = None
    category: Annotated[
        Optional[str],
        Field(
            description="The category of the population.", max_length=80, min_length=0
        ),
    ] = None
    condition: Annotated[
        Optional[ApiFilterGroupConditionCreate],
        Field(
            description="The filter condition used to determine which entries are included in the population."
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Field(
            description="A description of the population.", max_length=250, min_length=0
        ),
    ] = None
    disabled: Optional[bool] = None
    display_currency_code: Annotated[
        Optional[str],
        Field(
            alias="displayCurrencyCode",
            description="The ISO 4217 three-digit currency code that determines how currency values are formatted. Defaults to `USD` if not specified.",
        ),
    ] = None
    display_locale: Annotated[
        Optional[str],
        Field(
            alias="displayLocale",
            description="The ISO 639 locale identifier used to format display values. Defaults to `en-us` if not specified.",
        ),
    ] = None
    library_id: Annotated[
        Optional[str],
        Field(alias="libraryId", description="The ID of the parent library."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the population.", max_length=80, min_length=0),
    ] = None


class ApiPopulationTagRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="The ID of the parent analysis."),
    ] = None
    analysis_type_id: Annotated[Optional[str], Field(alias="analysisTypeId")] = None
    base_population_id: Annotated[
        Optional[str],
        Field(
            alias="basePopulationId",
            description="The ID of the population the current population is based on.",
        ),
    ] = None
    category: Annotated[
        Optional[str],
        Field(
            description="The category of the population.", max_length=80, min_length=0
        ),
    ] = None
    cloned_from: Annotated[
        Optional[str],
        Field(
            alias="clonedFrom",
            description="Identifies the population the current population was cloned from.",
        ),
    ] = None
    condition: Annotated[
        Optional[ApiFilterGroupConditionRead],
        Field(
            description="The filter condition used to determine which entries are included in the population."
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    derived_from_engagement: Annotated[
        Optional[bool],
        Field(
            alias="derivedFromEngagement",
            description="Indicates whether the analysis population was derived from an engagement.",
        ),
    ] = None
    derived_from_library: Annotated[
        Optional[bool],
        Field(
            alias="derivedFromLibrary",
            description="Indicates that the engagement population was derived from a library.",
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Field(
            description="A description of the population.", max_length=250, min_length=0
        ),
    ] = None
    disabled: Optional[bool] = None
    disabled_for_analysis_ids: Annotated[
        Optional[list[str]],
        Field(
            alias="disabledForAnalysisIds",
            description="Lists the analysis IDs where the engagement population is disabled.",
        ),
    ] = None
    display_currency_code: Annotated[
        Optional[str],
        Field(
            alias="displayCurrencyCode",
            description="The ISO 4217 three-digit currency code that determines how currency values are formatted. Defaults to `USD` if not specified.",
        ),
    ] = None
    display_locale: Annotated[
        Optional[str],
        Field(
            alias="displayLocale",
            description="The ISO 639 locale identifier used to format display values. Defaults to `en-us` if not specified.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(alias="engagementId", description="The ID of the parent engagement."),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    legacy_filter_format: Annotated[
        Optional[bool],
        Field(
            alias="legacyFilterFormat",
            description="If `true`, this population uses a legacy filter format that cannot be represented in the current condition format.",
        ),
    ] = None
    library_id: Annotated[
        Optional[str],
        Field(alias="libraryId", description="The ID of the parent library."),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the population.", max_length=80, min_length=0),
    ] = None
    promoted_from_analysis_id: Annotated[
        Optional[str],
        Field(
            alias="promotedFromAnalysisId",
            description="Identifies the analysis from which the engagement population was promoted.",
        ),
    ] = None
    reason_for_change: Annotated[
        Optional[str],
        Field(
            alias="reasonForChange",
            description="The reason for the latest change made to the population.",
            max_length=250,
            min_length=0,
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiPopulationTagUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category: Annotated[
        Optional[str],
        Field(
            description="The category of the population.", max_length=80, min_length=0
        ),
    ] = None
    condition: Annotated[
        Optional[ApiFilterGroupConditionUpdate],
        Field(
            description="The filter condition used to determine which entries are included in the population."
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Field(
            description="A description of the population.", max_length=250, min_length=0
        ),
    ] = None
    disabled: Optional[bool] = None
    display_currency_code: Annotated[
        Optional[str],
        Field(
            alias="displayCurrencyCode",
            description="The ISO 4217 three-digit currency code that determines how currency values are formatted. Defaults to `USD` if not specified.",
        ),
    ] = None
    display_locale: Annotated[
        Optional[str],
        Field(
            alias="displayLocale",
            description="The ISO 639 locale identifier used to format display values. Defaults to `en-us` if not specified.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the population.", max_length=80, min_length=0),
    ] = None
    reason_for_change: Annotated[
        Optional[str],
        Field(
            alias="reasonForChange",
            description="The reason for the latest change made to the population.",
            max_length=250,
            min_length=0,
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiProposedDuplicateVirtualColumnCreate(ApiProposedVirtualColumnCreate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex",
            description="The position of the column to be duplicated.",
        ),
    ] = None


class ApiProposedDuplicateVirtualColumnRead(ApiProposedVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex",
            description="The position of the column to be duplicated.",
        ),
    ] = None


class ApiProposedDuplicateVirtualColumnUpdate(ApiProposedVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex",
            description="The position of the column to be duplicated.",
        ),
    ] = None


class ApiProposedJoinVirtualColumnCreate(ApiProposedVirtualColumnCreate):
    model_config = ConfigDict(populate_by_name=True)
    column_indices: Annotated[
        Optional[list[int]],
        Field(
            alias="columnIndices",
            description="The positions of the columns to be joined.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The character(s) that should be inserted to separate values."
        ),
    ] = None


class ApiProposedJoinVirtualColumnRead(ApiProposedVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_indices: Annotated[
        Optional[list[int]],
        Field(
            alias="columnIndices",
            description="The positions of the columns to be joined.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The character(s) that should be inserted to separate values."
        ),
    ] = None


class ApiProposedJoinVirtualColumnUpdate(ApiProposedVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_indices: Annotated[
        Optional[list[int]],
        Field(
            alias="columnIndices",
            description="The positions of the columns to be joined.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The character(s) that should be inserted to separate values."
        ),
    ] = None


class ApiProposedSplitByDelimiterVirtualColumnCreate(ApiProposedVirtualColumnCreate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the column to be split."
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The character(s) that should be used to separate the string into parts."
        ),
    ] = None
    split_index: Annotated[
        Optional[int],
        Field(
            alias="splitIndex",
            description="The position of the part to be used as a virtual column.",
        ),
    ] = None


class ApiProposedSplitByDelimiterVirtualColumnRead(ApiProposedVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the column to be split."
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The character(s) that should be used to separate the string into parts."
        ),
    ] = None
    split_index: Annotated[
        Optional[int],
        Field(
            alias="splitIndex",
            description="The position of the part to be used as a virtual column.",
        ),
    ] = None


class ApiProposedSplitByDelimiterVirtualColumnUpdate(ApiProposedVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the column to be split."
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The character(s) that should be used to separate the string into parts."
        ),
    ] = None
    split_index: Annotated[
        Optional[int],
        Field(
            alias="splitIndex",
            description="The position of the part to be used as a virtual column.",
        ),
    ] = None


class ApiProposedSplitByPositionVirtualColumnCreate(ApiProposedVirtualColumnCreate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the column to be split."
        ),
    ] = None
    end_position: Annotated[
        Optional[int],
        Field(
            alias="endPosition",
            description="The ending position of the substring to be used as the new column. **Exclusive**.",
        ),
    ] = None
    start_position: Annotated[
        Optional[int],
        Field(
            alias="startPosition",
            description="The starting position of the substring to be used as the new column. **Inclusive**.",
        ),
    ] = None


class ApiProposedSplitByPositionVirtualColumnRead(ApiProposedVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the column to be split."
        ),
    ] = None
    end_position: Annotated[
        Optional[int],
        Field(
            alias="endPosition",
            description="The ending position of the substring to be used as the new column. **Exclusive**.",
        ),
    ] = None
    start_position: Annotated[
        Optional[int],
        Field(
            alias="startPosition",
            description="The starting position of the substring to be used as the new column. **Inclusive**.",
        ),
    ] = None


class ApiProposedSplitByPositionVirtualColumnUpdate(ApiProposedVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(
            alias="columnIndex", description="The position of the column to be split."
        ),
    ] = None
    end_position: Annotated[
        Optional[int],
        Field(
            alias="endPosition",
            description="The ending position of the substring to be used as the new column. **Exclusive**.",
        ),
    ] = None
    start_position: Annotated[
        Optional[int],
        Field(
            alias="startPosition",
            description="The starting position of the substring to be used as the new column. **Inclusive**.",
        ),
    ] = None


class ApiSplitByDelimiterVirtualColumnRead(ApiVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(alias="columnIndex", description="The position of the split column."),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(description="The character(s) used to separate the string into parts."),
    ] = None
    split_index: Annotated[
        Optional[int],
        Field(
            alias="splitIndex",
            description="The position of the part used as a virtual column.",
        ),
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiSplitByDelimiterVirtualColumnUpdate(ApiVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(alias="columnIndex", description="The position of the split column."),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(description="The character(s) used to separate the string into parts."),
    ] = None
    split_index: Annotated[
        Optional[int],
        Field(
            alias="splitIndex",
            description="The position of the part used as a virtual column.",
        ),
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiSplitByPositionVirtualColumnRead(ApiVirtualColumnRead):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(alias="columnIndex", description="The position of the split column."),
    ] = None
    end_position: Annotated[
        Optional[int],
        Field(
            alias="endPosition",
            description="The ending position of the substring in the new column. **Exclusive**.",
        ),
    ] = None
    start_position: Annotated[
        Optional[int],
        Field(
            alias="startPosition",
            description="The starting position of the substring in the new column. **Inclusive**.",
        ),
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiSplitByPositionVirtualColumnUpdate(ApiVirtualColumnUpdate):
    model_config = ConfigDict(populate_by_name=True)
    column_index: Annotated[
        Optional[int],
        Field(alias="columnIndex", description="The position of the split column."),
    ] = None
    end_position: Annotated[
        Optional[int],
        Field(
            alias="endPosition",
            description="The ending position of the substring in the new column. **Exclusive**.",
        ),
    ] = None
    start_position: Annotated[
        Optional[int],
        Field(
            alias="startPosition",
            description="The starting position of the substring in the new column. **Inclusive**.",
        ),
    ] = None
    name: Annotated[str, Field(description="The name of the virtual column.")]
    type: Annotated[Type47, Field(description="The type of virtual column.")]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiTableMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    cell_length_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="cellLengthMetrics",
            description="Metrics regarding cells that are larger than 2000 characters in the table.",
        ),
    ] = None
    density_metrics: Annotated[
        Optional[ApiDensityMetrics],
        Field(
            alias="densityMetrics", description="Metrics regarding whole table density."
        ),
    ] = None
    inconsistent_date_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="inconsistentDateMetrics",
            description="Metrics regarding inconsistent date formats within columns for the entire table.",
        ),
    ] = None
    null_value_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="nullValueMetrics",
            description="Metrics regarding “null” values across the entire table.",
        ),
    ] = None
    numeric_column_metrics: Annotated[
        Optional[ApiBasicMetrics],
        Field(
            alias="numericColumnMetrics",
            description="Metrics regarding numeric columns within the table.",
        ),
    ] = None
    overall_data_type_metrics: Annotated[
        Optional[ApiOverallDataTypeMetrics],
        Field(
            alias="overallDataTypeMetrics",
            description="Metrics regarding detected data types across the entire table.",
        ),
    ] = None
    scientific_notation_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="scientificNotationMetrics",
            description="Metrics regarding scientific notation across the entire table.",
        ),
    ] = None
    sheet_metrics: Annotated[
        Optional[ApiSheetMetrics],
        Field(
            alias="sheetMetrics",
            description="Metrics regarding excel sheets within the underlying excel file.",
        ),
    ] = None
    special_character_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="specialCharacterMetrics",
            description="Metrics regarding special characters across the entire table.",
        ),
    ] = None
    uneven_columns_metrics: Annotated[
        Optional[ApiHistogramMetrics],
        Field(
            alias="unevenColumnsMetrics",
            description="Metrics regarding column length by row.",
        ),
    ] = None


class ApiTableMetadataRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    cell_length_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="cellLengthMetrics",
            description="Metrics regarding cells that are larger than 2000 characters in the table.",
        ),
    ] = None
    density_metrics: Annotated[
        Optional[ApiDensityMetricsRead],
        Field(
            alias="densityMetrics", description="Metrics regarding whole table density."
        ),
    ] = None
    inconsistent_date_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="inconsistentDateMetrics",
            description="Metrics regarding inconsistent date formats within columns for the entire table.",
        ),
    ] = None
    null_value_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="nullValueMetrics",
            description="Metrics regarding “null” values across the entire table.",
        ),
    ] = None
    numeric_column_metrics: Annotated[
        Optional[ApiBasicMetricsRead],
        Field(
            alias="numericColumnMetrics",
            description="Metrics regarding numeric columns within the table.",
        ),
    ] = None
    overall_data_type_metrics: Annotated[
        Optional[ApiOverallDataTypeMetricsRead],
        Field(
            alias="overallDataTypeMetrics",
            description="Metrics regarding detected data types across the entire table.",
        ),
    ] = None
    scientific_notation_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="scientificNotationMetrics",
            description="Metrics regarding scientific notation across the entire table.",
        ),
    ] = None
    sheet_metrics: Annotated[
        Optional[ApiSheetMetricsRead],
        Field(
            alias="sheetMetrics",
            description="Metrics regarding excel sheets within the underlying excel file.",
        ),
    ] = None
    special_character_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="specialCharacterMetrics",
            description="Metrics regarding special characters across the entire table.",
        ),
    ] = None
    uneven_columns_metrics: Annotated[
        Optional[ApiHistogramMetricsRead],
        Field(
            alias="unevenColumnsMetrics",
            description="Metrics regarding column length by row.",
        ),
    ] = None


class ApiTaskRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    amounts: Optional[dict[str, MoneyRead]] = None
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="Identifies the associated analysis."),
    ] = None
    analysis_result_id: Annotated[Optional[str], Field(alias="analysisResultId")] = None
    analysis_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisTypeId",
            description="Identifies the associated analysis type.",
        ),
    ] = None
    approver_id: Annotated[Optional[str], Field(alias="approverId")] = None
    assertions: Annotated[
        Optional[list[str]],
        Field(description="Which assertions this task is associated with."),
    ] = None
    assigned_id: Annotated[
        Optional[str],
        Field(
            alias="assignedId", description="Identifies the user assigned to this task."
        ),
    ] = None
    audit_areas: Annotated[
        Optional[list[str]],
        Field(
            alias="auditAreas",
            description="Which audit areas this task is associated with.",
        ),
    ] = None
    comments: Annotated[
        Optional[list[ApiTaskCommentRead]],
        Field(
            description="A list of all the comments that have been made on this task."
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    credit_value: Annotated[
        Optional[int],
        Field(
            alias="creditValue",
            description="The credit value of the associated transaction or entry, formatted as MONEY_100.",
        ),
    ] = None
    customer_name: Annotated[
        Optional[str],
        Field(
            alias="customerName",
            description="For AR analyses this is the customer name for the associated entry.",
        ),
    ] = None
    debit_value: Annotated[
        Optional[int],
        Field(
            alias="debitValue",
            description="The debit value of the associated transaction or entry, formatted as MONEY_100.",
        ),
    ] = None
    description: Annotated[
        Optional[str], Field(description="A description of the task.")
    ] = None
    due_date: Annotated[Optional[date], Field(alias="dueDate")] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    entry_type: Annotated[
        Optional[str],
        Field(
            alias="entryType",
            description="For AP and AR analyses this is the entry type for the associated entry.",
        ),
    ] = None
    filter_statement: Annotated[
        Optional[str],
        Field(
            alias="filterStatement",
            description="The filter statement that was applied when creating this task via a bulk task creation.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    invoice_ref: Annotated[
        Optional[str],
        Field(
            alias="invoiceRef",
            description="For AP and AR analyses this is the Invoice ref value for the associated entry.",
        ),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    name: Annotated[
        Optional[str],
        Field(
            description="The task's name. Generated based on on the related entry or transaction."
        ),
    ] = None
    risk_scores: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="riskScores",
            description="A map of ensemble names or IDs mapped to their risk score value. The value is a PERCENTAGE_FIXED_POINT type.",
        ),
    ] = None
    row_id: Annotated[
        Optional[int],
        Field(alias="rowId", description="Identifies the associated entry."),
    ] = None
    sample: Annotated[
        Optional[str], Field(description="Which sample this task is a part of.")
    ] = None
    sample_type: Annotated[
        Optional[SampleType],
        Field(
            alias="sampleType",
            description="The sampling method used to create this task.",
            title="Sample Type",
        ),
    ] = None
    status: Annotated[
        Optional[Status5],
        Field(description="The current state of the task.", title="Task Status"),
    ] = None
    tags: Optional[list[str]] = None
    task_approval_status: Annotated[
        Optional[TaskApprovalStatus],
        Field(alias="taskApprovalStatus", title="Task Approval Status"),
    ] = None
    transaction: Annotated[
        Optional[str], Field(description="The name of the associated transaction.")
    ] = None
    transaction_id: Annotated[
        Optional[int],
        Field(
            alias="transactionId", description="Identifies the associated transaction."
        ),
    ] = None
    type: Annotated[
        Optional[Type41],
        Field(
            description="The type of entry this task is associated with.",
            title="Task Type",
        ),
    ] = None
    vendor_name: Annotated[
        Optional[str],
        Field(
            alias="vendorName",
            description="For AP analyses this is the vendor name for the associated entry.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class ApiTextTypeDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    range: Annotated[
        Optional[RangeInteger],
        Field(
            description="A pair of values representing the min and max length of text values within this column."
        ),
    ] = None


class ApiTextTypeDetailsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    range: Annotated[
        Optional[RangeIntegerRead],
        Field(
            description="A pair of values representing the min and max length of text values within this column."
        ),
    ] = None


class ApiTransactionIdPreviewIndicatorRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[list[ApiTransactionIdPreviewRowRead]],
        Field(description="The set of transactions related to a specific indicator."),
    ] = None
    rating: Annotated[
        Optional[Rating],
        Field(description="The quality of the indicator as rated by MindBridge."),
    ] = None
    value: Annotated[
        Optional[Any], Field(description="A value for this specific indicator.")
    ] = None


class ApiTransactionIdPreviewRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    analysis_id: Annotated[Optional[str], Field(alias="analysisId")] = None
    analysis_source_id: Annotated[
        Optional[str],
        Field(
            alias="analysisSourceId",
            description="The unique identifier of the associated analysis source.",
        ),
    ] = None
    column_selection: Annotated[
        Optional[list[int]],
        Field(
            alias="columnSelection",
            description="The list of columns used to generate the transaction ID.",
        ),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    engagement_id: Annotated[Optional[str], Field(alias="engagementId")] = None
    entry_previews: Annotated[
        Optional[list[ApiTransactionIdPreviewRowRead]],
        Field(
            alias="entryPreviews",
            description="Details about the transactions generated by this transaction ID selection.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    indicators: Annotated[
        Optional[dict[str, ApiTransactionIdPreviewIndicatorRead]],
        Field(
            description="The data integrity checks used when selecting a transaction ID."
        ),
    ] = None
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    overall_rating: Annotated[
        Optional[OverallRating],
        Field(
            alias="overallRating",
            description="The quality of the transaction ID as rated by MindBridge.",
        ),
    ] = None
    smart_splitter: Annotated[
        Optional[bool],
        Field(
            alias="smartSplitter",
            description="Indicates whether or not the Smart Splitter was run when selecting a transaction ID.",
        ),
    ] = None
    type: Annotated[
        Optional[Type43],
        Field(description="The type used when selecting a transaction ID."),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None


class EngagementSubscriptionWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="engagementId",
            description="The ID of the Engagement associated with the webhook event.",
        ),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    target_user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="targetUserId",
            description="The ID of the user associated with the webhook event.",
        ),
    ] = None


class EngagementSubscriptionWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[EngagementSubscriptionWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type49],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class EngagementWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    engagement_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="engagementId",
            description="The ID of the Engagement associated with the webhook event.",
        ),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None


class EngagementWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[EngagementWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type50],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class FileManagerWebhookData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    file_export_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="fileExportId",
            description="The ID of the file export associated with the webhook event.",
        ),
    ] = None
    file_manager_file_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="fileManagerFileId",
            description="The ID of the data associated with the webhook event.",
        ),
    ] = None


class FileManagerWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Annotated[
        Optional[FileManagerWebhookData],
        Field(description="The data associated with the webhook event."),
    ] = None
    event_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="eventId",
            description="The ID of the event that triggered the outbound request.",
        ),
    ] = None
    sender_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="senderId",
            description="The ID of the registered webhook configuration that initiated the outbound request.",
        ),
    ] = None
    tenant_id: Annotated[
        Optional[str],
        Field(
            alias="tenantId",
            description="The name of the tenant that triggered the webhook.",
        ),
    ] = None
    timestamp: Annotated[
        Optional[AwareDatetime],
        Field(description="The time that the webhook was triggered."),
    ] = None
    type: Annotated[
        Optional[Type51],
        Field(description="The event type that triggered the webhook."),
    ] = None
    user_id: Annotated[
        Optional[ObjectId],
        Field(
            alias="userId",
            description="The ID of the user that initiated the event that triggered the webhook.",
        ),
    ] = None


class PageablenullRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    offset: Optional[int] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    paged: Optional[bool] = None
    sort: Optional[SortnullRead] = None
    unpaged: Optional[bool] = None


class ApiAnalysisSourceCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_data_column_field: Annotated[
        Optional[str],
        Field(
            alias="additionalDataColumnField",
            description="When creating an additional data source type, this indicates which additional data column is being targeted.",
        ),
    ] = None
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="Identifies the associated analysis."),
    ] = None
    analysis_period_id: Annotated[
        Optional[str],
        Field(
            alias="analysisPeriodId",
            description="Identifies the analysis period within MindBridge.",
        ),
    ] = None
    analysis_source_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisSourceTypeId",
            description="Identifies the analysis source type.",
        ),
    ] = None
    apply_degrouper: Annotated[
        Optional[bool],
        Field(
            alias="applyDegrouper",
            description="Indicates whether or not the degrouper should be applied.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    file_manager_file_id: Annotated[
        Optional[str],
        Field(
            alias="fileManagerFileId",
            description="Identifies the specific file manager file within MindBridge.",
        ),
    ] = None
    proposed_ambiguous_column_resolutions: Annotated[
        Optional[list[ApiProposedAmbiguousColumnResolutionCreate]],
        Field(
            alias="proposedAmbiguousColumnResolutions",
            description="Details about the virtual columns added during file ingestion.",
        ),
    ] = None
    proposed_column_mappings: Annotated[
        Optional[list[ApiProposedColumnMappingCreate]],
        Field(
            alias="proposedColumnMappings",
            description="Details about the proposed column mapping.",
        ),
    ] = None
    proposed_transaction_id_selection: Annotated[
        Optional[ApiTransactionIdSelectionCreate],
        Field(
            alias="proposedTransactionIdSelection",
            description="The proposed columns to include when selecting a transaction ID.",
        ),
    ] = None
    proposed_virtual_columns: Annotated[
        Optional[
            list[
                Union[
                    ApiProposedDuplicateVirtualColumnCreate,
                    ApiProposedJoinVirtualColumnCreate,
                    ApiProposedSplitByDelimiterVirtualColumnCreate,
                    ApiProposedSplitByPositionVirtualColumnCreate,
                ]
            ]
        ],
        Field(
            alias="proposedVirtualColumns",
            description="Details about the proposed virtual columns added during the file import process.",
        ),
    ] = None
    target_workflow_state: Annotated[
        Optional[TargetWorkflowState],
        Field(
            alias="targetWorkflowState",
            description="The state that the current workflow will advance to.",
        ),
    ] = None
    warnings_ignored: Annotated[
        Optional[bool],
        Field(
            alias="warningsIgnored",
            description="Indicates whether or not warnings should be ignored.",
        ),
    ] = None


class ApiAnalysisSourceUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ambiguous_column_resolutions: Annotated[
        Optional[list[ApiAmbiguousColumnUpdate]],
        Field(
            alias="ambiguousColumnResolutions",
            description="Details about resolutions to ambiguity in a column.",
        ),
    ] = None
    apply_degrouper: Annotated[
        Optional[bool],
        Field(
            alias="applyDegrouper",
            description="Indicates whether or not the degrouper should be applied.",
        ),
    ] = None
    column_mappings: Annotated[
        Optional[list[ApiColumnMappingUpdate]],
        Field(alias="columnMappings", description="Details about column mapping."),
    ] = None
    proposed_ambiguous_column_resolutions: Annotated[
        Optional[list[ApiProposedAmbiguousColumnResolutionUpdate]],
        Field(
            alias="proposedAmbiguousColumnResolutions",
            description="Details about the virtual columns added during file ingestion.",
        ),
    ] = None
    proposed_column_mappings: Annotated[
        Optional[list[ApiProposedColumnMappingUpdate]],
        Field(
            alias="proposedColumnMappings",
            description="Details about the proposed column mapping.",
        ),
    ] = None
    proposed_transaction_id_selection: Annotated[
        Optional[ApiTransactionIdSelectionUpdate],
        Field(
            alias="proposedTransactionIdSelection",
            description="The proposed columns to include when selecting a transaction ID.",
        ),
    ] = None
    proposed_virtual_columns: Annotated[
        Optional[
            list[
                Union[
                    ApiProposedDuplicateVirtualColumnUpdate,
                    ApiProposedJoinVirtualColumnUpdate,
                    ApiProposedSplitByDelimiterVirtualColumnUpdate,
                    ApiProposedSplitByPositionVirtualColumnUpdate,
                ]
            ]
        ],
        Field(
            alias="proposedVirtualColumns",
            description="Details about the proposed virtual columns added during the file import process.",
        ),
    ] = None
    target_workflow_state: Annotated[
        Optional[TargetWorkflowState],
        Field(
            alias="targetWorkflowState",
            description="The state that the current workflow will advance to.",
        ),
    ] = None
    transaction_id_selection: Annotated[
        Optional[ApiTransactionIdSelectionUpdate],
        Field(
            alias="transactionIdSelection",
            description="Details about transaction ID selection.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None
    virtual_columns: Annotated[
        Optional[
            list[
                Union[
                    ApiDuplicateVirtualColumnUpdate,
                    ApiJoinVirtualColumnUpdate,
                    ApiSplitByDelimiterVirtualColumnUpdate,
                    ApiSplitByPositionVirtualColumnUpdate,
                ]
            ]
        ],
        Field(
            alias="virtualColumns",
            description="Details about the virtual columns added during file ingestion. ",
        ),
    ] = None
    warnings_ignored: Annotated[
        Optional[bool],
        Field(
            alias="warningsIgnored",
            description="Indicates whether or not warnings should be ignored.",
        ),
    ] = None


class ApiDataTypeMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data_previews: Annotated[
        Optional[list[ApiDataPreview]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    date_type_details: Annotated[
        Optional[ApiDateTypeDetails],
        Field(
            alias="dateTypeDetails",
            description="Metrics regarding the date type values in this column.",
        ),
    ] = None
    detected_types: Annotated[
        Optional[list[DetectedType]],
        Field(
            alias="detectedTypes",
            description="A list of all detected types in this column.",
        ),
    ] = None
    dominant_type: Annotated[
        Optional[DominantType],
        Field(
            alias="dominantType",
            description="The type determined to be the most prevalent in this column.",
        ),
    ] = None
    non_null_value_count: Annotated[
        Optional[int],
        Field(
            alias="nonNullValueCount",
            description="The number of non-null values in this column.",
        ),
    ] = None
    numeric_type_details: Annotated[
        Optional[ApiNumericTypeDetails],
        Field(
            alias="numericTypeDetails",
            description="Metrics regarding the number type values in this column.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None
    text_type_details: Annotated[
        Optional[ApiTextTypeDetails],
        Field(
            alias="textTypeDetails",
            description="Metrics regarding the text type values in this column.",
        ),
    ] = None
    type_counts: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="typeCounts",
            description="A map of column type to number of occurrences. A single column value can match multiple types.",
        ),
    ] = None


class ApiDataTypeMetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data_previews: Annotated[
        Optional[list[ApiDataPreviewRead]],
        Field(
            alias="dataPreviews",
            description="A list of values within the table relevant to the metric.",
        ),
    ] = None
    date_type_details: Annotated[
        Optional[ApiDateTypeDetailsRead],
        Field(
            alias="dateTypeDetails",
            description="Metrics regarding the date type values in this column.",
        ),
    ] = None
    detected_types: Annotated[
        Optional[list[DetectedType]],
        Field(
            alias="detectedTypes",
            description="A list of all detected types in this column.",
        ),
    ] = None
    dominant_type: Annotated[
        Optional[DominantType],
        Field(
            alias="dominantType",
            description="The type determined to be the most prevalent in this column.",
        ),
    ] = None
    non_null_value_count: Annotated[
        Optional[int],
        Field(
            alias="nonNullValueCount",
            description="The number of non-null values in this column.",
        ),
    ] = None
    numeric_type_details: Annotated[
        Optional[ApiNumericTypeDetailsRead],
        Field(
            alias="numericTypeDetails",
            description="Metrics regarding the number type values in this column.",
        ),
    ] = None
    state: Annotated[
        Optional[State],
        Field(description="Validation state of the metric within its context."),
    ] = None
    text_type_details: Annotated[
        Optional[ApiTextTypeDetailsRead],
        Field(
            alias="textTypeDetails",
            description="Metrics regarding the text type values in this column.",
        ),
    ] = None
    type_counts: Annotated[
        Optional[dict[str, int]],
        Field(
            alias="typeCounts",
            description="A map of column type to number of occurrences. A single column value can match multiple types.",
        ),
    ] = None


class ApiFileManagerDirectoryRead(ApiFileManagerEntityRead):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[Optional[str], Field(description="The name of the directory.")] = (
        None
    )
    engagement_id: Annotated[
        str,
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ]
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiPageApiAccountGroupRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAccountGroupRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAccountGroupingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAccountGroupingRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAccountMappingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAccountMappingRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAnalysisSourceTypeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAnalysisSourceTypeRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAnalysisTypeConfigurationRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAnalysisTypeConfigurationRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAnalysisTypeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAnalysisTypeRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAnalysisRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAnalysisRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiApiTokenRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiApiTokenRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiAsyncResultRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAsyncResultRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiChunkedFileRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiChunkedFileRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiDataTableRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiDataTableRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiEngagementAccountGroupRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiEngagementAccountGroupRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiEngagementAccountGroupingRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiEngagementAccountGroupingRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiEngagementRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiEngagementRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiFileExportRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiFileExportRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiFileManagerEntityRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[
        list[Union[ApiFileManagerDirectoryRead, ApiFileManagerFileRead]]
    ] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiFilterRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiFilterRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiLibraryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiLibraryRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiOrganizationRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiOrganizationRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiPopulationTagRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiPopulationTagRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiRiskRangesRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiRiskRangesRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiTaskHistoryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiTaskHistoryRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiTaskRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiTaskRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiTransactionIdPreviewRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiTransactionIdPreviewRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiUserRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiUserRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiWebhookEventLogRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiWebhookEventLogRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiWebhookRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiWebhookRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class PageApiAnalysisResultRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAnalysisResultRead]] = None
    empty: Optional[bool] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    pageable: Optional[PageablenullRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiColumnMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    cell_length_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="cellLengthMetrics",
            description="Metrics regarding cells that are larger than 2000 characters in the column.",
        ),
    ] = None
    data_type_metrics: Annotated[
        Optional[ApiDataTypeMetrics],
        Field(
            alias="dataTypeMetrics",
            description="Metrics regarding the data types of column values.",
        ),
    ] = None
    density_metrics: Annotated[
        Optional[ApiDensityMetrics],
        Field(
            alias="densityMetrics",
            description="Metrics regarding the density of column values.",
        ),
    ] = None
    distinct_value_metrics: Annotated[
        Optional[ApiDistinctValueMetrics],
        Field(
            alias="distinctValueMetrics",
            description="Metrics regarding the uniqueness of column values.",
        ),
    ] = None
    null_value_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="nullValueMetrics",
            description="Metrics regarding “null” values in the column.",
        ),
    ] = None
    scientific_notation_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="scientificNotationMetrics",
            description="Metrics regarding the use of scientific notation in the column.",
        ),
    ] = None
    special_character_metrics: Annotated[
        Optional[ApiCountMetrics],
        Field(
            alias="specialCharacterMetrics",
            description="Metrics regarding the use of special characters in the column.",
        ),
    ] = None


class ApiColumnMetadataRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    cell_length_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="cellLengthMetrics",
            description="Metrics regarding cells that are larger than 2000 characters in the column.",
        ),
    ] = None
    data_type_metrics: Annotated[
        Optional[ApiDataTypeMetricsRead],
        Field(
            alias="dataTypeMetrics",
            description="Metrics regarding the data types of column values.",
        ),
    ] = None
    density_metrics: Annotated[
        Optional[ApiDensityMetricsRead],
        Field(
            alias="densityMetrics",
            description="Metrics regarding the density of column values.",
        ),
    ] = None
    distinct_value_metrics: Annotated[
        Optional[ApiDistinctValueMetricsRead],
        Field(
            alias="distinctValueMetrics",
            description="Metrics regarding the uniqueness of column values.",
        ),
    ] = None
    null_value_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="nullValueMetrics",
            description="Metrics regarding “null” values in the column.",
        ),
    ] = None
    scientific_notation_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="scientificNotationMetrics",
            description="Metrics regarding the use of scientific notation in the column.",
        ),
    ] = None
    special_character_metrics: Annotated[
        Optional[ApiCountMetricsRead],
        Field(
            alias="specialCharacterMetrics",
            description="Metrics regarding the use of special characters in the column.",
        ),
    ] = None


class ApiColumnData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    column_metadata: Annotated[
        Optional[ApiColumnMetadata],
        Field(alias="columnMetadata", description="A collection of metrics."),
    ] = None
    column_name: Annotated[
        Optional[str], Field(alias="columnName", description="The name of the column.")
    ] = None
    position: Annotated[
        Optional[int], Field(description="The index of the column.")
    ] = None
    row_sample: Annotated[
        Optional[list[str]],
        Field(
            alias="rowSample",
            description="A list of values from this column across multiple rows. All values are distinct.",
        ),
    ] = None
    synthetic: Annotated[
        Optional[bool],
        Field(
            description="If `true` this column was generated, as opposed to being a part of the original data."
        ),
    ] = None


class ApiColumnDataRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    column_metadata: Annotated[
        Optional[ApiColumnMetadataRead],
        Field(alias="columnMetadata", description="A collection of metrics."),
    ] = None
    column_name: Annotated[
        Optional[str], Field(alias="columnName", description="The name of the column.")
    ] = None
    position: Annotated[
        Optional[int], Field(description="The index of the column.")
    ] = None
    row_sample: Annotated[
        Optional[list[str]],
        Field(
            alias="rowSample",
            description="A list of values from this column across multiple rows. All values are distinct.",
        ),
    ] = None
    synthetic: Annotated[
        Optional[bool],
        Field(
            description="If `true` this column was generated, as opposed to being a part of the original data."
        ),
    ] = None


class ApiTabularFileInfo(ApiFileInfo):
    model_config = ConfigDict(populate_by_name=True)
    column_data: Annotated[
        Optional[list[ApiColumnData]],
        Field(
            alias="columnData",
            description="A list of column metadata entities, describing each column.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The delimiter character used to separate cells. Only populated when the underlying file is a CSV file."
        ),
    ] = None
    first_line: Annotated[
        Optional[str],
        Field(alias="firstLine", description="The first line of the table."),
    ] = None
    header_row_index: Annotated[
        Optional[int],
        Field(
            alias="headerRowIndex",
            description="The row number of the first detected header.",
        ),
    ] = None
    last_non_blank_row_index: Annotated[
        Optional[int],
        Field(
            alias="lastNonBlankRowIndex",
            description="The row number of the last row that isn’t blank.",
        ),
    ] = None
    row_content_snippets: Annotated[
        Optional[list[list[str]]],
        Field(
            alias="rowContentSnippets",
            description="A list of sample rows from the underlying file.",
        ),
    ] = None
    table_metadata: Annotated[
        Optional[ApiTableMetadata],
        Field(
            alias="tableMetadata",
            description="A collection of metadata describing the table as a whole.",
        ),
    ] = None
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiTabularFileInfoRead(ApiFileInfoRead, ApiFileInfo):
    model_config = ConfigDict(populate_by_name=True)
    column_data: Annotated[
        Optional[list[ApiColumnDataRead]],
        Field(
            alias="columnData",
            description="A list of column metadata entities, describing each column.",
        ),
    ] = None
    delimiter: Annotated[
        Optional[str],
        Field(
            description="The delimiter character used to separate cells. Only populated when the underlying file is a CSV file."
        ),
    ] = None
    first_line: Annotated[
        Optional[str],
        Field(alias="firstLine", description="The first line of the table."),
    ] = None
    header_row_index: Annotated[
        Optional[int],
        Field(
            alias="headerRowIndex",
            description="The row number of the first detected header.",
        ),
    ] = None
    last_non_blank_row_index: Annotated[
        Optional[int],
        Field(
            alias="lastNonBlankRowIndex",
            description="The row number of the last row that isn’t blank.",
        ),
    ] = None
    row_content_snippets: Annotated[
        Optional[list[list[str]]],
        Field(
            alias="rowContentSnippets",
            description="A list of sample rows from the underlying file.",
        ),
    ] = None
    table_metadata: Annotated[
        Optional[ApiTableMetadataRead],
        Field(
            alias="tableMetadata",
            description="A collection of metadata describing the table as a whole.",
        ),
    ] = None
    version: Annotated[
        int, Field(description="Data integrity version to ensure data consistency.")
    ]


class ApiAnalysisSourceRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    additional_data_column_field: Annotated[
        Optional[str],
        Field(
            alias="additionalDataColumnField",
            description="When creating an additional data source type, this indicates which additional data column is being targeted.",
        ),
    ] = None
    ambiguous_column_resolutions: Annotated[
        Optional[list[ApiAmbiguousColumnRead]],
        Field(
            alias="ambiguousColumnResolutions",
            description="Details about resolutions to ambiguity in a column.",
        ),
    ] = None
    analysis_id: Annotated[
        Optional[str],
        Field(alias="analysisId", description="Identifies the associated analysis."),
    ] = None
    analysis_period_id: Annotated[
        Optional[str],
        Field(
            alias="analysisPeriodId",
            description="Identifies the analysis period within MindBridge.",
        ),
    ] = None
    analysis_source_type_id: Annotated[
        Optional[str],
        Field(
            alias="analysisSourceTypeId",
            description="Identifies the analysis source type.",
        ),
    ] = None
    apply_degrouper: Annotated[
        Optional[bool],
        Field(
            alias="applyDegrouper",
            description="Indicates whether or not the degrouper should be applied.",
        ),
    ] = None
    column_mappings: Annotated[
        Optional[list[ApiColumnMappingRead]],
        Field(alias="columnMappings", description="Details about column mapping."),
    ] = None
    created_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="createdUserInfo",
            description="Details about the user who created the object.",
        ),
    ] = None
    creation_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="creationDate",
            description="The date that the object was originally created.",
        ),
    ] = None
    degrouper_applied: Annotated[
        Optional[bool],
        Field(
            alias="degrouperApplied",
            description="Indicates whether or not the degrouper was applied.",
        ),
    ] = None
    detected_format: Annotated[
        Optional[DetectedFormat],
        Field(
            alias="detectedFormat",
            description="The data format that MindBridge detected.",
        ),
    ] = None
    engagement_id: Annotated[
        Optional[str],
        Field(
            alias="engagementId", description="Identifies the associated engagement."
        ),
    ] = None
    errors: Annotated[
        Optional[list[ApiMessageRead]],
        Field(
            description="Details about the errors associated with the specific source."
        ),
    ] = None
    file_info: Annotated[
        Optional[Union[ApiFileInfoRead, ApiTabularFileInfoRead]],
        Field(
            alias="fileInfo",
            description="Details about the file being imported into MindBridge.",
        ),
    ] = None
    file_info_versions: Annotated[
        Optional[dict[str, str]],
        Field(
            alias="fileInfoVersions",
            description="A map of providing a set of file info IDs by their Analysis Source File Version.",
        ),
    ] = None
    file_manager_file_id: Annotated[
        Optional[str],
        Field(
            alias="fileManagerFileId",
            description="Identifies the specific file manager file within MindBridge.",
        ),
    ] = None
    file_manager_files: Annotated[
        Optional[dict[str, str]],
        Field(
            alias="fileManagerFiles",
            description="A map of providing a set of file manager file IDs by their Analysis Source File Version.",
        ),
    ] = None
    id: Annotated[Optional[str], Field(description="The unique object identifier.")] = (
        None
    )
    last_modified_date: Annotated[
        Optional[AwareDatetime],
        Field(
            alias="lastModifiedDate",
            description="The date that the object was last updated or modified.",
        ),
    ] = None
    last_modified_user_info: Annotated[
        Optional[ApiUserInfoRead],
        Field(
            alias="lastModifiedUserInfo",
            description="Details about the user who last modified or updated the object.",
        ),
    ] = None
    proposed_ambiguous_column_resolutions: Annotated[
        Optional[list[ApiProposedAmbiguousColumnResolutionRead]],
        Field(
            alias="proposedAmbiguousColumnResolutions",
            description="Details about the virtual columns added during file ingestion.",
        ),
    ] = None
    proposed_column_mappings: Annotated[
        Optional[list[ApiProposedColumnMappingRead]],
        Field(
            alias="proposedColumnMappings",
            description="Details about the proposed column mapping.",
        ),
    ] = None
    proposed_transaction_id_selection: Annotated[
        Optional[ApiTransactionIdSelectionRead],
        Field(
            alias="proposedTransactionIdSelection",
            description="The proposed columns to include when selecting a transaction ID.",
        ),
    ] = None
    proposed_virtual_columns: Annotated[
        Optional[
            list[
                Union[
                    ApiProposedDuplicateVirtualColumnRead,
                    ApiProposedJoinVirtualColumnRead,
                    ApiProposedSplitByDelimiterVirtualColumnRead,
                    ApiProposedSplitByPositionVirtualColumnRead,
                ]
            ]
        ],
        Field(
            alias="proposedVirtualColumns",
            description="Details about the proposed virtual columns added during the file import process.",
        ),
    ] = None
    target_workflow_state: Annotated[
        Optional[TargetWorkflowState],
        Field(
            alias="targetWorkflowState",
            description="The state that the current workflow will advance to.",
        ),
    ] = None
    transaction_id_selection: Annotated[
        Optional[ApiTransactionIdSelectionRead],
        Field(
            alias="transactionIdSelection",
            description="Details about transaction ID selection.",
        ),
    ] = None
    version: Annotated[
        Optional[int],
        Field(
            description="Indicates the data integrity version to ensure data consistency."
        ),
    ] = None
    virtual_columns: Annotated[
        Optional[
            list[
                Union[
                    ApiDuplicateVirtualColumnRead,
                    ApiJoinVirtualColumnRead,
                    ApiSplitByDelimiterVirtualColumnRead,
                    ApiSplitByPositionVirtualColumnRead,
                ]
            ]
        ],
        Field(
            alias="virtualColumns",
            description="Details about the virtual columns added during file ingestion. ",
        ),
    ] = None
    warnings: Annotated[
        Optional[list[ApiMessageRead]],
        Field(description="Details about the warnings associated with the source."),
    ] = None
    warnings_ignored: Annotated[
        Optional[bool],
        Field(
            alias="warningsIgnored",
            description="Indicates whether or not warnings should be ignored.",
        ),
    ] = None
    workflow_state: Annotated[
        Optional[WorkflowState],
        Field(alias="workflowState", description="The current state of the workflow."),
    ] = None


class ApiPageApiAnalysisSourceRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[ApiAnalysisSourceRead]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiPageApiFileInfoRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: Optional[list[Union[ApiFileInfoRead, ApiTabularFileInfoRead]]] = None
    first: Optional[bool] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    number_of_elements: Annotated[Optional[int], Field(alias="numberOfElements")] = None
    page_number: Annotated[Optional[int], Field(alias="pageNumber")] = None
    page_size: Annotated[Optional[int], Field(alias="pageSize")] = None
    pageable: Optional[ApiPageableRead] = None
    size: Optional[int] = None
    sort: Optional[SortnullRead] = None
    total_elements: Annotated[Optional[int], Field(alias="totalElements")] = None
    total_pages: Annotated[Optional[int], Field(alias="totalPages")] = None


class ApiDataTableExportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    csv_configuration: Annotated[
        Optional[ApiCsvConfiguration],
        Field(
            alias="csvConfiguration",
            description="The configuration to use when generating the CSV file.",
        ),
    ] = None
    fields: Annotated[
        Optional[list[str]],
        Field(description="The data table fields to be included in the results."),
    ] = None
    inner_list_csv_configuration: Annotated[
        Optional[ApiCsvConfiguration],
        Field(
            alias="innerListCsvConfiguration",
            description="The configuration to use when formatting lists within cells in the CSV file.",
        ),
    ] = None
    limit: Annotated[
        Optional[int], Field(description="The number of results to be returned.", ge=1)
    ] = None
    query: Annotated[
        Optional[MindBridgeQueryTerm],
        Field(
            description="The MindBridge QL query used to filter data in the data table."
        ),
    ] = None
    sort: Annotated[
        Optional[ApiDataTableQuerySortOrder],
        Field(
            description="Indicates how the data will be sorted.\n\nDefault sort order = ascending"
        ),
    ] = None


class ApiDataTableQueryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    exclude_fields: Annotated[Optional[list[str]], Field(alias="excludeFields")] = None
    fields: Annotated[
        Optional[list[str]],
        Field(description="The data table fields to be included in the results."),
    ] = None
    page: Annotated[
        Optional[int],
        Field(
            description="The specific page of results. This operates on a zero-based page index (0..N).",
            ge=0,
        ),
    ] = None
    page_size: Annotated[
        Optional[int],
        Field(
            alias="pageSize",
            description="The number of results to be returned on each page.",
            ge=1,
            le=100,
        ),
    ] = None
    query: Annotated[
        Optional[MindBridgeQueryTerm],
        Field(
            description="The MindBridge QL query used to filter data in the data table."
        ),
    ] = None
    sort: Annotated[
        Optional[ApiDataTableQuerySortOrderRead],
        Field(
            description="Indicates how the data will be sorted.\n\nDefault sort order = ascending"
        ),
    ] = None


class MindBridgeQueryTerm15(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_and: Annotated[Optional[list[MindBridgeQueryTerm]], Field(alias="$and")] = (
        None
    )


class MindBridgeQueryTerm16(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_or: Annotated[Optional[list[MindBridgeQueryTerm]], Field(alias="$or")] = None


class MindBridgeQueryTerm(
    RootModel[
        Optional[
            Union[
                dict[str, Union[int, float, bool, str]],
                dict[str, MindBridgeQueryTerm1],
                dict[str, MindBridgeQueryTerm2],
                dict[str, MindBridgeQueryTerm3],
                dict[str, MindBridgeQueryTerm4],
                dict[str, MindBridgeQueryTerm5],
                dict[str, MindBridgeQueryTerm6],
                dict[str, MindBridgeQueryTerm7],
                dict[str, MindBridgeQueryTerm9],
                dict[str, MindBridgeQueryTerm10],
                dict[str, MindBridgeQueryTerm11],
                dict[str, MindBridgeQueryTerm12],
                dict[str, MindBridgeQueryTerm13],
                dict[str, MindBridgeQueryTerm14],
                MindBridgeQueryTerm15,
                MindBridgeQueryTerm16,
                MindBridgeQueryTerm17,
                MindBridgeQueryTerm18,
                dict[str, Any],
            ]
        ]
    ]
):
    model_config = ConfigDict(populate_by_name=True)
    root: Optional[
        Union[
            dict[str, Union[int, float, bool, str]],
            dict[str, MindBridgeQueryTerm1],
            dict[str, MindBridgeQueryTerm2],
            dict[str, MindBridgeQueryTerm3],
            dict[str, MindBridgeQueryTerm4],
            dict[str, MindBridgeQueryTerm5],
            dict[str, MindBridgeQueryTerm6],
            dict[str, MindBridgeQueryTerm7],
            dict[str, MindBridgeQueryTerm9],
            dict[str, MindBridgeQueryTerm10],
            dict[str, MindBridgeQueryTerm11],
            dict[str, MindBridgeQueryTerm12],
            dict[str, MindBridgeQueryTerm13],
            dict[str, MindBridgeQueryTerm14],
            MindBridgeQueryTerm15,
            MindBridgeQueryTerm16,
            MindBridgeQueryTerm17,
            MindBridgeQueryTerm18,
            dict[str, Any],
        ]
    ] = None


ApiDataTableExportRequest.model_rebuild()
ApiDataTableQueryRead.model_rebuild()
MindBridgeQueryTerm15.model_rebuild()
MindBridgeQueryTerm16.model_rebuild()
