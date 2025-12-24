# Error Scenario (Scenario 3)

**Goal**: Verify system resilience against invalid inputs and failures (Transaction rollback).

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
