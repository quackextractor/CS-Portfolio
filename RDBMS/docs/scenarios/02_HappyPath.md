# Happy Path Scenario (Scenario 2)

**Goal**: Verify standard hotel operations: Adding a guest, creating a booking, and viewing reports.

## Steps

1. **Launch Application**
   - Ensure Backend and Frontend are running as per Setup Scenario.
   - Navigate to `http://localhost:5173`.

2. **Add a Guest**
   - Click "Guests" in the navigation bar.
   - In the "Add New Guest" form:
     - First Name: "Alice"
     - Last Name: "Wonderland"
     - Email: "alice@example.com"
     - Date of Birth: "1995-05-05"
   - Click "Create Guest".
   - **Verification**: The new guest should appear in the Guest List table below.

3. **Check Room Availability**
   - Click "Reports" in the navigation bar.
   - Check "Room Availability" table.
   - Note down an available Room Number (e.g., "101", "201").

4. **Create a Booking**
   - Click "Book Room" in the navigation bar.
   - **Form Input**:
     - **Guest**: Select "Alice Wonderland".
     - **Room**: Select Room "101".
     - **Check-in**: Select today's date.
     - **Check-out**: Select tomorrow's date.
     - **Services**: Check "Breakfast" ($15) and/or "Late Check-out" ($30).
   - Click "Create Booking".
   - **Verification**: An alert "Booking Created Successfully!" should appear.

5. **Verify Reports**
   - Navigate back to "Reports".
   - **Verification**: 
     - "Guest Bookings" table should show a new entry for Alice in Room 101.
     - Status should be "1" (Confirmed).
