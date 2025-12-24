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
        room.Save();
        return Ok(room);
    }
    
    // Additional endpoints logic same as Guests...
}
