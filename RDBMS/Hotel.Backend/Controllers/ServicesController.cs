using Hotel.Backend.Data;
using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;

namespace Hotel.Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ServicesController : ControllerBase
{
    [HttpGet]
    public IEnumerable<Service> Get()
    {
        return Service.All();
    }
}
