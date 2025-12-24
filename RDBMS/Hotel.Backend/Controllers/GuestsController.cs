using Hotel.Backend.Data;
using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;

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
        var guest = Guest.Find(id);
        if (guest == null)
        {
            return NotFound();
        }

        guest.Delete();
        return NoContent();
    }
}
