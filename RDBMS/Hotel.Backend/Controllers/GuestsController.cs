using Hotel.Backend.Data;
using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

namespace Hotel.Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class GuestsController : ControllerBase
{
    [HttpGet]
    public IEnumerable<Guest> Get()
    {
        return Guest.All();
    }

    [HttpGet("{id}")]
    public ActionResult<Guest> Get(int id)
    {
        var guest = Guest.Find(id);
        if (guest == null)
        {
            return NotFound();
        }
        return guest;
    }

    [HttpPost]
    public ActionResult<Guest> Post([FromBody] Guest guest)
    {
        guest.Save();
        return CreatedAtAction(nameof(Get), new { id = guest.Id }, guest);
    }

    [HttpPut("{id}")]
    public IActionResult Put(int id, [FromBody] Guest guest)
    {
        if (id != guest.Id)
        {
            return BadRequest();
        }

        var existing = Guest.Find(id);
        if (existing == null)
        {
            return NotFound();
        }

        guest.Save();
        return NoContent();
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        using var conn = new SqlConnection(DbConfig.ConnectionString);
        conn.Open();
        using var transaction = conn.BeginTransaction();

        try
        {
            var guest = Guest.Find(id, transaction);
            if (guest == null) return NotFound();

            // Cascade: Find all bookings for this guest
            var bookings = Booking.Where("GuestId = @gid", new Dictionary<string, object> { { "@gid", id } }, transaction);
            
            foreach (var booking in bookings)
            {
                // Delete Booking
                booking.Delete(transaction);
            }

            // Finally delete the guest
            guest.Delete(transaction);

            transaction.Commit();
            return NoContent();
        }
        catch (Exception ex)
        {
            transaction.Rollback();
            return StatusCode(500, ex.Message);
        }
    }
}
