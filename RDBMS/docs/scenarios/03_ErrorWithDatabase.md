# Error Scenario (Scenario 3)

**Goal**: Verify system resilience against invalid inputs and failures (Transaction rollback).

**Prerequisites**: 
- System must be running with valid database connection. (REFER TO 01_Setup.md)
- Database must be in a clean state (no bookings, no guests, no rooms).

## 4. Database Connection Failure (Simulated)
1. Stop your SQL Server instance or disable the network adapter used to connect to the DB.
2. Refresh the application page (e.g., Guests list).
3. **Expected Result**:
   - The application should gracefully handle the timeout/connection error.
   - An error message (e.g., "Failed to load guests", "Database unavailable") should be displayed in the UI (via the Alert Dialog).
   - The app should NOT crash completely (white screen of death).

## 4. Import Error (Invalid Data)
1. Create a `bad_guests.json` file with content: `[{"firstName": "", "lastName": ""}]` (Missing required fields).
2. Go to "Import" page.
3. Select this file and click "Import Guests".
4. **Expected Result**: 
   - UI displays an error message: "Invalid guest data: FirstName and LastName are required."
   - No data is added to the database.

## 5. Import Error (Malformed JSON)
1. Create a `broken.json` file with content: `[{ "firstName": "Broken"`.
2. Go to "Import" page.
3. Select this file and click "Import Guests".
4. **Expected Result**:
   - UI displays an error message: "Invalid JSON..."
   - No data is added.

## 6. Configuration Error
1. Stop the Backend.
2. Open `config.json` and change the `DefaultConnection` string to an invalid server or database name.
3. Start the Backend.
4. Attempt to run the application.
5. **Expected Result**:
   - The Backend might fail to start or log an error immediately.
   - If it starts, any DB operation should return a 500 or specific error code.
   - The Frontend should display an error saying it cannot reach the backend or the backend returned an error.

# 03_ErrorWithDatabase.md

## 1. Invalid Input (Frontend Validation)
1. Navigate to "Book Room".
2. Leave all fields empty.
3. Click "Create Booking".
4. **Expected Result**: An alert "Please fill all fields" should appear. No request is sent to the server.

## 2. Business Logic Error (Invalid Date Range)
1. Select a valid Guest and Room.
2. Select **Check-in**: "2025-12-30".
3. Select **Check-out**: "2025-12-29" (Before Check-in).
4. Click "Create Booking".
5. **Expected Result**: 
   - Backend returns `400 Bad Request`.
   - Frontend displays alert: "Error creating booking: Check-out must be after check-in." (or similar message).
   - No booking is created in the database.

## 3. Transaction Rollback (Simulated)
*Note: This requires modifying code to simulate a failure mid-transaction, or checking logs.*

**Scenario**: 
The `BookingsController.Create` method uses a SQL Transaction. It performs:
1. Insert Booking.
2. Insert Booking Services.
3. Update Totals.

If any step fails (e.g., Service ID invalid, though Frontend selects existing ones), the entire transaction rolls back.

**Test**:
1. (Advanced) Manually modify `BookingsController.cs` to throw an exception after `booking.Save(transaction)` but before `transaction.Commit()`.
2. Attempt to create a booking.
3. **Expected Result**:
   - API returns `500 Internal Server Error`.
   - **Verification**: Check Reports or Database. The Booking should **NOT** exist. The Guest should remain (if existed before), but the half-created booking is rolled back.
