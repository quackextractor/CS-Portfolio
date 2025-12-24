# Happy Path Scenario

**Test Case ID:** HP_01
**Test Name:** Complete Booking Lifecycle
**Description:** Verify that a user can import guests, create a booking with services, and generate reports.

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Navigate to "Import" page. | Import form is displayed. |
| 2 | Select `guests.json` (valid structure) and click "Import Guests". | "Import successful" message appears. Guests are added to DB. |
| 3 | Navigate to "Guests" list. | The imported guests are visible in the list. |
| 4 | Click "Create Booking". | Booking form appears. |
| 5 | Select a Guest, a Room (e.g., 101), Dates, and Services (e.g., Breakfast). | Form validation passes. Total price is estimated (if implemented) or calculated on backend. |
| 6 | Submit the Booking. | Booking is created. User is redirected or success message shown. |
| 7 | Navigate to "Reports". | The new booking appears in "Guest Bookings". |
| 8 | Check "Revenue by Room Type" report. | The revenue and booking count for 'Single' (Room 101) has increased. |
| 9 | Check "Service Usage Stats" report. | 'Breakfast' usage count has increased. |

**Test Case ID:** HP_02
**Test Name:** Service Import
**Description:** Verify that a user can import services.

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Navigate to "Import" page. | Import form is displayed. |
| 2 | Select `services.json` and click "Import Services". | "Import successful" message appears. |
| 3 | Check Database or Service Stats. | New services are available/accounted for. |
