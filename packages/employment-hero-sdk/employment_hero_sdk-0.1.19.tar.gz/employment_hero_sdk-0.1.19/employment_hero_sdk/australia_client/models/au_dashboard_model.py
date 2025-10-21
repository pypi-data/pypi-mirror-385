import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel
    from ..models.au_features_model import AuFeaturesModel
    from ..models.classification_select_model import ClassificationSelectModel
    from ..models.ess_current_expenses_model import EssCurrentExpensesModel
    from ..models.ess_current_shift_model import EssCurrentShiftModel
    from ..models.ess_current_timesheets_model import EssCurrentTimesheetsModel
    from ..models.ess_leave_category_model import EssLeaveCategoryModel
    from ..models.ess_payslip_model import EssPayslipModel
    from ..models.ess_satisfaction_survey import EssSatisfactionSurvey
    from ..models.ess_work_type_model import EssWorkTypeModel
    from ..models.expense_category_response_model import ExpenseCategoryResponseModel
    from ..models.journal_service_tax_code import JournalServiceTaxCode
    from ..models.leave_balance_model import LeaveBalanceModel
    from ..models.location_model import LocationModel
    from ..models.standard_hours_model import StandardHoursModel
    from ..models.title_view_model import TitleViewModel


T = TypeVar("T", bound="AuDashboardModel")


@_attrs_define
class AuDashboardModel:
    """
    Attributes:
        features (Union[Unset, AuFeaturesModel]):
        next_shift (Union[Unset, AuEssRosterShiftModel]):
        current_shift (Union[Unset, EssCurrentShiftModel]):
        latest_payslip (Union[Unset, EssPayslipModel]):
        leave_balances (Union[Unset, List['LeaveBalanceModel']]):
        titles (Union[Unset, List['TitleViewModel']]):
        work_types (Union[Unset, List['EssWorkTypeModel']]):
        shift_conditions (Union[Unset, List['EssWorkTypeModel']]):
        locations (Union[Unset, List['LocationModel']]):
        classifications (Union[Unset, List['ClassificationSelectModel']]):
        leave_categories (Union[Unset, List['EssLeaveCategoryModel']]):
        current_week_satisfaction_survey (Union[Unset, EssSatisfactionSurvey]):
        timesheets (Union[Unset, EssCurrentTimesheetsModel]):
        timesheet_entry_period_end (Union[Unset, datetime.datetime]):
        expense_categories (Union[Unset, List['ExpenseCategoryResponseModel']]):
        tax_codes (Union[Unset, List['JournalServiceTaxCode']]):
        expenses (Union[Unset, EssCurrentExpensesModel]):
        pending_shift_count (Union[Unset, int]):
        proposed_swap_count (Union[Unset, int]):
        pending_leave_count (Union[Unset, int]):
        documents_requiring_acknowledgement_count (Union[Unset, int]):
        region (Union[Unset, str]):
        biddable_shift_count (Union[Unset, int]):
        is_terminated (Union[Unset, bool]):
        google_maps_api_key (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        standard_hours (Union[Unset, StandardHoursModel]):
        not_accepted_shifts_count (Union[Unset, int]):
    """

    features: Union[Unset, "AuFeaturesModel"] = UNSET
    next_shift: Union[Unset, "AuEssRosterShiftModel"] = UNSET
    current_shift: Union[Unset, "EssCurrentShiftModel"] = UNSET
    latest_payslip: Union[Unset, "EssPayslipModel"] = UNSET
    leave_balances: Union[Unset, List["LeaveBalanceModel"]] = UNSET
    titles: Union[Unset, List["TitleViewModel"]] = UNSET
    work_types: Union[Unset, List["EssWorkTypeModel"]] = UNSET
    shift_conditions: Union[Unset, List["EssWorkTypeModel"]] = UNSET
    locations: Union[Unset, List["LocationModel"]] = UNSET
    classifications: Union[Unset, List["ClassificationSelectModel"]] = UNSET
    leave_categories: Union[Unset, List["EssLeaveCategoryModel"]] = UNSET
    current_week_satisfaction_survey: Union[Unset, "EssSatisfactionSurvey"] = UNSET
    timesheets: Union[Unset, "EssCurrentTimesheetsModel"] = UNSET
    timesheet_entry_period_end: Union[Unset, datetime.datetime] = UNSET
    expense_categories: Union[Unset, List["ExpenseCategoryResponseModel"]] = UNSET
    tax_codes: Union[Unset, List["JournalServiceTaxCode"]] = UNSET
    expenses: Union[Unset, "EssCurrentExpensesModel"] = UNSET
    pending_shift_count: Union[Unset, int] = UNSET
    proposed_swap_count: Union[Unset, int] = UNSET
    pending_leave_count: Union[Unset, int] = UNSET
    documents_requiring_acknowledgement_count: Union[Unset, int] = UNSET
    region: Union[Unset, str] = UNSET
    biddable_shift_count: Union[Unset, int] = UNSET
    is_terminated: Union[Unset, bool] = UNSET
    google_maps_api_key: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    standard_hours: Union[Unset, "StandardHoursModel"] = UNSET
    not_accepted_shifts_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        features: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.features, Unset):
            features = self.features.to_dict()

        next_shift: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.next_shift, Unset):
            next_shift = self.next_shift.to_dict()

        current_shift: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.current_shift, Unset):
            current_shift = self.current_shift.to_dict()

        latest_payslip: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.latest_payslip, Unset):
            latest_payslip = self.latest_payslip.to_dict()

        leave_balances: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_balances, Unset):
            leave_balances = []
            for leave_balances_item_data in self.leave_balances:
                leave_balances_item = leave_balances_item_data.to_dict()
                leave_balances.append(leave_balances_item)

        titles: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.titles, Unset):
            titles = []
            for titles_item_data in self.titles:
                titles_item = titles_item_data.to_dict()
                titles.append(titles_item)

        work_types: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.work_types, Unset):
            work_types = []
            for work_types_item_data in self.work_types:
                work_types_item = work_types_item_data.to_dict()
                work_types.append(work_types_item)

        shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_conditions, Unset):
            shift_conditions = []
            for shift_conditions_item_data in self.shift_conditions:
                shift_conditions_item = shift_conditions_item_data.to_dict()
                shift_conditions.append(shift_conditions_item)

        locations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = []
            for locations_item_data in self.locations:
                locations_item = locations_item_data.to_dict()
                locations.append(locations_item)

        classifications: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.classifications, Unset):
            classifications = []
            for classifications_item_data in self.classifications:
                classifications_item = classifications_item_data.to_dict()
                classifications.append(classifications_item)

        leave_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_categories, Unset):
            leave_categories = []
            for leave_categories_item_data in self.leave_categories:
                leave_categories_item = leave_categories_item_data.to_dict()
                leave_categories.append(leave_categories_item)

        current_week_satisfaction_survey: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.current_week_satisfaction_survey, Unset):
            current_week_satisfaction_survey = self.current_week_satisfaction_survey.to_dict()

        timesheets: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.timesheets, Unset):
            timesheets = self.timesheets.to_dict()

        timesheet_entry_period_end: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_entry_period_end, Unset):
            timesheet_entry_period_end = self.timesheet_entry_period_end.isoformat()

        expense_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.expense_categories, Unset):
            expense_categories = []
            for expense_categories_item_data in self.expense_categories:
                expense_categories_item = expense_categories_item_data.to_dict()
                expense_categories.append(expense_categories_item)

        tax_codes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tax_codes, Unset):
            tax_codes = []
            for tax_codes_item_data in self.tax_codes:
                tax_codes_item = tax_codes_item_data.to_dict()
                tax_codes.append(tax_codes_item)

        expenses: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.expenses, Unset):
            expenses = self.expenses.to_dict()

        pending_shift_count = self.pending_shift_count

        proposed_swap_count = self.proposed_swap_count

        pending_leave_count = self.pending_leave_count

        documents_requiring_acknowledgement_count = self.documents_requiring_acknowledgement_count

        region = self.region

        biddable_shift_count = self.biddable_shift_count

        is_terminated = self.is_terminated

        google_maps_api_key = self.google_maps_api_key

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        standard_hours: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.standard_hours, Unset):
            standard_hours = self.standard_hours.to_dict()

        not_accepted_shifts_count = self.not_accepted_shifts_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if features is not UNSET:
            field_dict["features"] = features
        if next_shift is not UNSET:
            field_dict["nextShift"] = next_shift
        if current_shift is not UNSET:
            field_dict["currentShift"] = current_shift
        if latest_payslip is not UNSET:
            field_dict["latestPayslip"] = latest_payslip
        if leave_balances is not UNSET:
            field_dict["leaveBalances"] = leave_balances
        if titles is not UNSET:
            field_dict["titles"] = titles
        if work_types is not UNSET:
            field_dict["workTypes"] = work_types
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if locations is not UNSET:
            field_dict["locations"] = locations
        if classifications is not UNSET:
            field_dict["classifications"] = classifications
        if leave_categories is not UNSET:
            field_dict["leaveCategories"] = leave_categories
        if current_week_satisfaction_survey is not UNSET:
            field_dict["currentWeekSatisfactionSurvey"] = current_week_satisfaction_survey
        if timesheets is not UNSET:
            field_dict["timesheets"] = timesheets
        if timesheet_entry_period_end is not UNSET:
            field_dict["timesheetEntryPeriodEnd"] = timesheet_entry_period_end
        if expense_categories is not UNSET:
            field_dict["expenseCategories"] = expense_categories
        if tax_codes is not UNSET:
            field_dict["taxCodes"] = tax_codes
        if expenses is not UNSET:
            field_dict["expenses"] = expenses
        if pending_shift_count is not UNSET:
            field_dict["pendingShiftCount"] = pending_shift_count
        if proposed_swap_count is not UNSET:
            field_dict["proposedSwapCount"] = proposed_swap_count
        if pending_leave_count is not UNSET:
            field_dict["pendingLeaveCount"] = pending_leave_count
        if documents_requiring_acknowledgement_count is not UNSET:
            field_dict["documentsRequiringAcknowledgementCount"] = documents_requiring_acknowledgement_count
        if region is not UNSET:
            field_dict["region"] = region
        if biddable_shift_count is not UNSET:
            field_dict["biddableShiftCount"] = biddable_shift_count
        if is_terminated is not UNSET:
            field_dict["isTerminated"] = is_terminated
        if google_maps_api_key is not UNSET:
            field_dict["googleMapsApiKey"] = google_maps_api_key
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if standard_hours is not UNSET:
            field_dict["standardHours"] = standard_hours
        if not_accepted_shifts_count is not UNSET:
            field_dict["notAcceptedShiftsCount"] = not_accepted_shifts_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel
        from ..models.au_features_model import AuFeaturesModel
        from ..models.classification_select_model import ClassificationSelectModel
        from ..models.ess_current_expenses_model import EssCurrentExpensesModel
        from ..models.ess_current_shift_model import EssCurrentShiftModel
        from ..models.ess_current_timesheets_model import EssCurrentTimesheetsModel
        from ..models.ess_leave_category_model import EssLeaveCategoryModel
        from ..models.ess_payslip_model import EssPayslipModel
        from ..models.ess_satisfaction_survey import EssSatisfactionSurvey
        from ..models.ess_work_type_model import EssWorkTypeModel
        from ..models.expense_category_response_model import ExpenseCategoryResponseModel
        from ..models.journal_service_tax_code import JournalServiceTaxCode
        from ..models.leave_balance_model import LeaveBalanceModel
        from ..models.location_model import LocationModel
        from ..models.standard_hours_model import StandardHoursModel
        from ..models.title_view_model import TitleViewModel

        d = src_dict.copy()
        _features = d.pop("features", UNSET)
        features: Union[Unset, AuFeaturesModel]
        if isinstance(_features, Unset):
            features = UNSET
        else:
            features = AuFeaturesModel.from_dict(_features)

        _next_shift = d.pop("nextShift", UNSET)
        next_shift: Union[Unset, AuEssRosterShiftModel]
        if isinstance(_next_shift, Unset):
            next_shift = UNSET
        else:
            next_shift = AuEssRosterShiftModel.from_dict(_next_shift)

        _current_shift = d.pop("currentShift", UNSET)
        current_shift: Union[Unset, EssCurrentShiftModel]
        if isinstance(_current_shift, Unset):
            current_shift = UNSET
        else:
            current_shift = EssCurrentShiftModel.from_dict(_current_shift)

        _latest_payslip = d.pop("latestPayslip", UNSET)
        latest_payslip: Union[Unset, EssPayslipModel]
        if isinstance(_latest_payslip, Unset):
            latest_payslip = UNSET
        else:
            latest_payslip = EssPayslipModel.from_dict(_latest_payslip)

        leave_balances = []
        _leave_balances = d.pop("leaveBalances", UNSET)
        for leave_balances_item_data in _leave_balances or []:
            leave_balances_item = LeaveBalanceModel.from_dict(leave_balances_item_data)

            leave_balances.append(leave_balances_item)

        titles = []
        _titles = d.pop("titles", UNSET)
        for titles_item_data in _titles or []:
            titles_item = TitleViewModel.from_dict(titles_item_data)

            titles.append(titles_item)

        work_types = []
        _work_types = d.pop("workTypes", UNSET)
        for work_types_item_data in _work_types or []:
            work_types_item = EssWorkTypeModel.from_dict(work_types_item_data)

            work_types.append(work_types_item)

        shift_conditions = []
        _shift_conditions = d.pop("shiftConditions", UNSET)
        for shift_conditions_item_data in _shift_conditions or []:
            shift_conditions_item = EssWorkTypeModel.from_dict(shift_conditions_item_data)

            shift_conditions.append(shift_conditions_item)

        locations = []
        _locations = d.pop("locations", UNSET)
        for locations_item_data in _locations or []:
            locations_item = LocationModel.from_dict(locations_item_data)

            locations.append(locations_item)

        classifications = []
        _classifications = d.pop("classifications", UNSET)
        for classifications_item_data in _classifications or []:
            classifications_item = ClassificationSelectModel.from_dict(classifications_item_data)

            classifications.append(classifications_item)

        leave_categories = []
        _leave_categories = d.pop("leaveCategories", UNSET)
        for leave_categories_item_data in _leave_categories or []:
            leave_categories_item = EssLeaveCategoryModel.from_dict(leave_categories_item_data)

            leave_categories.append(leave_categories_item)

        _current_week_satisfaction_survey = d.pop("currentWeekSatisfactionSurvey", UNSET)
        current_week_satisfaction_survey: Union[Unset, EssSatisfactionSurvey]
        if isinstance(_current_week_satisfaction_survey, Unset):
            current_week_satisfaction_survey = UNSET
        else:
            current_week_satisfaction_survey = EssSatisfactionSurvey.from_dict(_current_week_satisfaction_survey)

        _timesheets = d.pop("timesheets", UNSET)
        timesheets: Union[Unset, EssCurrentTimesheetsModel]
        if isinstance(_timesheets, Unset):
            timesheets = UNSET
        else:
            timesheets = EssCurrentTimesheetsModel.from_dict(_timesheets)

        _timesheet_entry_period_end = d.pop("timesheetEntryPeriodEnd", UNSET)
        timesheet_entry_period_end: Union[Unset, datetime.datetime]
        if isinstance(_timesheet_entry_period_end, Unset):
            timesheet_entry_period_end = UNSET
        else:
            timesheet_entry_period_end = isoparse(_timesheet_entry_period_end)

        expense_categories = []
        _expense_categories = d.pop("expenseCategories", UNSET)
        for expense_categories_item_data in _expense_categories or []:
            expense_categories_item = ExpenseCategoryResponseModel.from_dict(expense_categories_item_data)

            expense_categories.append(expense_categories_item)

        tax_codes = []
        _tax_codes = d.pop("taxCodes", UNSET)
        for tax_codes_item_data in _tax_codes or []:
            tax_codes_item = JournalServiceTaxCode.from_dict(tax_codes_item_data)

            tax_codes.append(tax_codes_item)

        _expenses = d.pop("expenses", UNSET)
        expenses: Union[Unset, EssCurrentExpensesModel]
        if isinstance(_expenses, Unset):
            expenses = UNSET
        else:
            expenses = EssCurrentExpensesModel.from_dict(_expenses)

        pending_shift_count = d.pop("pendingShiftCount", UNSET)

        proposed_swap_count = d.pop("proposedSwapCount", UNSET)

        pending_leave_count = d.pop("pendingLeaveCount", UNSET)

        documents_requiring_acknowledgement_count = d.pop("documentsRequiringAcknowledgementCount", UNSET)

        region = d.pop("region", UNSET)

        biddable_shift_count = d.pop("biddableShiftCount", UNSET)

        is_terminated = d.pop("isTerminated", UNSET)

        google_maps_api_key = d.pop("googleMapsApiKey", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _standard_hours = d.pop("standardHours", UNSET)
        standard_hours: Union[Unset, StandardHoursModel]
        if isinstance(_standard_hours, Unset):
            standard_hours = UNSET
        else:
            standard_hours = StandardHoursModel.from_dict(_standard_hours)

        not_accepted_shifts_count = d.pop("notAcceptedShiftsCount", UNSET)

        au_dashboard_model = cls(
            features=features,
            next_shift=next_shift,
            current_shift=current_shift,
            latest_payslip=latest_payslip,
            leave_balances=leave_balances,
            titles=titles,
            work_types=work_types,
            shift_conditions=shift_conditions,
            locations=locations,
            classifications=classifications,
            leave_categories=leave_categories,
            current_week_satisfaction_survey=current_week_satisfaction_survey,
            timesheets=timesheets,
            timesheet_entry_period_end=timesheet_entry_period_end,
            expense_categories=expense_categories,
            tax_codes=tax_codes,
            expenses=expenses,
            pending_shift_count=pending_shift_count,
            proposed_swap_count=proposed_swap_count,
            pending_leave_count=pending_leave_count,
            documents_requiring_acknowledgement_count=documents_requiring_acknowledgement_count,
            region=region,
            biddable_shift_count=biddable_shift_count,
            is_terminated=is_terminated,
            google_maps_api_key=google_maps_api_key,
            start_date=start_date,
            standard_hours=standard_hours,
            not_accepted_shifts_count=not_accepted_shifts_count,
        )

        au_dashboard_model.additional_properties = d
        return au_dashboard_model

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
