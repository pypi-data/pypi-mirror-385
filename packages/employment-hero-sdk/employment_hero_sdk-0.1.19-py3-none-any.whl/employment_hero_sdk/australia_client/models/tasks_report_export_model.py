import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tasks_report_note_model import TasksReportNoteModel


T = TypeVar("T", bound="TasksReportExportModel")


@_attrs_define
class TasksReportExportModel:
    """
    Attributes:
        pay_run_task_id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        task_description (Union[Unset, str]):
        created_by (Union[Unset, str]):
        created_date (Union[Unset, datetime.datetime]):
        due_date (Union[Unset, datetime.datetime]):
        completed (Union[Unset, bool]):
        notes (Union[Unset, List['TasksReportNoteModel']]):
        completed_by (Union[Unset, str]):
        completed_date (Union[Unset, datetime.datetime]):
    """

    pay_run_task_id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    task_description: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET
    created_date: Union[Unset, datetime.datetime] = UNSET
    due_date: Union[Unset, datetime.datetime] = UNSET
    completed: Union[Unset, bool] = UNSET
    notes: Union[Unset, List["TasksReportNoteModel"]] = UNSET
    completed_by: Union[Unset, str] = UNSET
    completed_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_task_id = self.pay_run_task_id

        employee_name = self.employee_name

        employee_id = self.employee_id

        external_id = self.external_id

        task_description = self.task_description

        created_by = self.created_by

        created_date: Union[Unset, str] = UNSET
        if not isinstance(self.created_date, Unset):
            created_date = self.created_date.isoformat()

        due_date: Union[Unset, str] = UNSET
        if not isinstance(self.due_date, Unset):
            due_date = self.due_date.isoformat()

        completed = self.completed

        notes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.notes, Unset):
            notes = []
            for notes_item_data in self.notes:
                notes_item = notes_item_data.to_dict()
                notes.append(notes_item)

        completed_by = self.completed_by

        completed_date: Union[Unset, str] = UNSET
        if not isinstance(self.completed_date, Unset):
            completed_date = self.completed_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_task_id is not UNSET:
            field_dict["payRunTaskId"] = pay_run_task_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if task_description is not UNSET:
            field_dict["taskDescription"] = task_description
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if due_date is not UNSET:
            field_dict["dueDate"] = due_date
        if completed is not UNSET:
            field_dict["completed"] = completed
        if notes is not UNSET:
            field_dict["notes"] = notes
        if completed_by is not UNSET:
            field_dict["completedBy"] = completed_by
        if completed_date is not UNSET:
            field_dict["completedDate"] = completed_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.tasks_report_note_model import TasksReportNoteModel

        d = src_dict.copy()
        pay_run_task_id = d.pop("payRunTaskId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        external_id = d.pop("externalId", UNSET)

        task_description = d.pop("taskDescription", UNSET)

        created_by = d.pop("createdBy", UNSET)

        _created_date = d.pop("createdDate", UNSET)
        created_date: Union[Unset, datetime.datetime]
        if isinstance(_created_date, Unset):
            created_date = UNSET
        else:
            created_date = isoparse(_created_date)

        _due_date = d.pop("dueDate", UNSET)
        due_date: Union[Unset, datetime.datetime]
        if isinstance(_due_date, Unset):
            due_date = UNSET
        else:
            due_date = isoparse(_due_date)

        completed = d.pop("completed", UNSET)

        notes = []
        _notes = d.pop("notes", UNSET)
        for notes_item_data in _notes or []:
            notes_item = TasksReportNoteModel.from_dict(notes_item_data)

            notes.append(notes_item)

        completed_by = d.pop("completedBy", UNSET)

        _completed_date = d.pop("completedDate", UNSET)
        completed_date: Union[Unset, datetime.datetime]
        if isinstance(_completed_date, Unset):
            completed_date = UNSET
        else:
            completed_date = isoparse(_completed_date)

        tasks_report_export_model = cls(
            pay_run_task_id=pay_run_task_id,
            employee_name=employee_name,
            employee_id=employee_id,
            external_id=external_id,
            task_description=task_description,
            created_by=created_by,
            created_date=created_date,
            due_date=due_date,
            completed=completed,
            notes=notes,
            completed_by=completed_by,
            completed_date=completed_date,
        )

        tasks_report_export_model.additional_properties = d
        return tasks_report_export_model

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
