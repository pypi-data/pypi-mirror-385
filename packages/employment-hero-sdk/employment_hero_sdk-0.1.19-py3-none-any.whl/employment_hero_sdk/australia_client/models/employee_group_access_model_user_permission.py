from enum import Enum


class EmployeeGroupAccessModelUserPermission(str, Enum):
    ADDEMPLOYEEFROMKIOSK = "AddEmployeeFromKiosk"
    APPROVEEXPENSES = "ApproveExpenses"
    APPROVELEAVEREQUESTS = "ApproveLeaveRequests"
    APPROVETIMESHEETS = "ApproveTimesheets"
    CREATEEXPENSES = "CreateExpenses"
    CREATELEAVEREQUESTS = "CreateLeaveRequests"
    CREATETASKS = "CreateTasks"
    CREATETIMESHEETS = "CreateTimesheets"
    EDITALLEMPLOYEEDETAILS = "EditAllEmployeeDetails"
    EDITBASICEMPLOYEEDETAILS = "EditBasicEmployeeDetails"
    EMPLOYEENOTES = "EmployeeNotes"
    INITIATEEMPLOYEESELFSETUP = "InitiateEmployeeSelfSetup"
    MANAGEEMPLOYEEDOCUMENTS = "ManageEmployeeDocuments"
    MANAGEEMPLOYEEQUALIFICATIONS = "ManageEmployeeQualifications"
    MANAGEROSTERS = "ManageRosters"
    VIEWEMPLOYEEDETAILS = "ViewEmployeeDetails"
    VIEWEMPLOYEEDOCUMENTS = "ViewEmployeeDocuments"
    VIEWEMPLOYEEQUALIFICATIONS = "ViewEmployeeQualifications"
    VIEWEXPENSES = "ViewExpenses"
    VIEWLEAVEREQUESTS = "ViewLeaveRequests"
    VIEWROSTERS = "ViewRosters"
    VIEWSHIFTCOSTS = "ViewShiftCosts"
    VIEWTIMESHEETREPORTS = "ViewTimesheetReports"

    def __str__(self) -> str:
        return str(self.value)
