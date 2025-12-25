# Import Examples

This directory contains example JSON files for importing data into the Hotel Management System.

## Files

### `guests-example.json`
Example format for importing guests. Each guest requires:
- `firstName` (string, required)
- `lastName` (string, required)
- `email` (string)
- `phone` (string)
- `dateOfBirth` (DateTime in ISO 8601 format)

### `rooms-example.json`
Example format for importing rooms. Each room requires:
- `roomNumber` (string, required)
- `roomTypeId` (integer, required, must be > 0)

**Note:** The `roomTypeId` must reference an existing room type in your database:
- 1 = Single
- 2 = Double
- 3 = Suite

**Important:** Room numbers must be unique. The example uses room numbers that don't conflict with the existing seed data (101, 102, 201, 202, 301).

## Usage

1. Navigate to the **Import** page in the Hotel Manager application
2. Click "Choose File" and select one of the example JSON files
3. Click the corresponding import button (Import Guests or Import Rooms)
4. The system will validate and import the data using ACID-compliant transactions

## Validation

- All required fields must be present
- Invalid data will cause the entire import to rollback
- Detailed error messages will be displayed if validation fails
