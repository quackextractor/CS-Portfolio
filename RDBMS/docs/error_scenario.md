# Error Scenario

**Test Case ID:** ERR_01
**Test Name:** Invalid Booking Dates
**Description:** Verify that booking requires check-out to be after check-in.

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Go to "Create Booking". | Form appears. |
| 2 | Select Check-in: Today. Select Check-out: Yesterday. | Client-side or Server-side validation error. |
| 3 | Submit form. | Request fails. "Check-out must be after check-in" error is displayed to user. |

**Test Case ID:** ERR_02
**Test Name:** Database Connection Failure
**Description:** Verify system behavior when DB is unreachable.

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Stop the SQL Server instance or break the connection string in `appsettings.json`. | System handles connection loss. |
| 2 | Refresh "Guest List". | Error message "Database unreachable" or generic 500 error is shown gracefully (no crash). |

**Test Case ID:** ERR_03
**Test Name:** Import Invalid Data
**Description:** Verify import rejects malformed JSON.

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Go to "Import". | Form appears. |
| 2 | Upload a text file or invalid JSON. | "Invalid JSON" error message is displayed. |
| 3 | Upload JSON with missing required fields (e.g. missing LastName). | Database constraint error or validation error is returned and displayed. |
