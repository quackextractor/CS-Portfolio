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

3. **Import Data (Guests & Rooms)**
   - Click "Import" in the navigation bar (or navigate to `/import` if not in menu).
   - create a `guests.json` file with content: `[{"firstName": "Bob", "lastName": "Builder", "email": "bob@build.com", "phone": "123", "dateOfBirth": "1990-01-01"}]`.
   - Select the file under "Import Guests" and click "Import Guests".
   - **Verification**: Message "Import successful" appears. Bob is listed in "Guests" page.
   - Create a `rooms.json` file with content: `[{"roomNumber": "999", "roomTypeId": 1}]`.
   - Select the file under "Import Rooms" and click "Import Rooms".
   - **Verification**: Message "Import successful" appears. Room 999 is available in "Book Room" selection.

4. **Edit a Guest**
   - In the Guest List table, find "Alice Wonderland".
   - Click the "Edit" button in the Actions column.
   - Change the **First Name** to "Alice" and **Last Name** to "Smith".
   - Click "Update Guest".
   - **Verification**: The name in the table should now read "Alice Smith".

5. **Check Room Availability**
   - Click "Reports" in the navigation bar.
   - Check "Room Availability" table.
   - Note down an available Room Number (e.g., "101", "201", or "999").

6. **Create a Booking**
   - Click "Bookings" in the navigation bar.
   - **Form Input**:
     - **Guest**: Select "Alice Smith".
     - **Room**: Select Room "101".
     - **Check-in**: Select today's date.
     - **Check-out**: Select tomorrow's date.
     - **Services**: Select "Breakfast" ($15) and "Parking" ($5).
   - Click "Create Booking".
   - **Verification**: An alert "Booking Created Successfully!" should appear.

7. **Verify Reports**
   - Navigate back to "Reports".
   - **Verification**: 
     - "Guest Bookings" table should show a new entry for Alice in Room 101.
     - Status should be "1" (Confirmed).

8. **Delete Booking & Guest**
   - Go to "Bookings" page.
   - Find the booking for "Alice Smith" (Room 101).
   - Click the "Trash/Delete" icon. Confirm deletion.
   - Go to "Guests" page.
   - Click the "Trash/Delete" icon for "Alice Smith".
   - Confirm the deletion.
   - **Verification**: Guest should be removed from the list.
