using Hotel.Backend.Data;
using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;

namespace Hotel.Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RoomsController : ControllerBase
{
    [HttpGet]
    public IEnumerable<Room> Get()
    {
        return Room.All();
    }

    [HttpPost]
    public IActionResult Post([FromBody] Room room)
    {
        try
        {
            var existing = Room.All().FirstOrDefault(r => r.RoomNumber == room.RoomNumber);
            if (existing != null)
                return Conflict("Room number already exists.");

            room.Save();
            return Ok(room);
        }
        catch (Microsoft.Data.SqlClient.SqlException ex) when (ex.Number == 2627 || ex.Number == 2601)
        {
            return Conflict("Room number already exists.");
        }
    }

    [HttpPut("{id}")]
    public IActionResult Put(int id, [FromBody] Room room)
    {
        if (id != room.Id)
        {
            return BadRequest("ID mismatch");
        }

        var existing = Room.Find(id);
        if (existing == null)
        {
            return NotFound();
        }

        try
        {
            // Check for room number conflict if changed
            if (existing.RoomNumber != room.RoomNumber)
            {
                var conflict = Room.All().FirstOrDefault(r => r.RoomNumber == room.RoomNumber);
                if (conflict != null)
                    return Conflict("Room number already exists.");
            }

            room.Save();
            return NoContent();
        }
        catch (Microsoft.Data.SqlClient.SqlException ex) when (ex.Number == 2627 || ex.Number == 2601)
        {
            return Conflict("Room number already exists.");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        var room = Room.Find(id);
        if (room == null) return NotFound();

        try
        {
            room.Delete();
            return NoContent();
        }
        catch (Microsoft.Data.SqlClient.SqlException ex) when (ex.Number == 547) // FK Constraint
        {
            return Conflict("Cannot delete room because it has associated bookings.");
        }
    }
}
