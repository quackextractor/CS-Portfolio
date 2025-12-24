using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;

namespace Hotel.Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ReportsController : ControllerBase
{
    [HttpGet("guest-bookings")]
    public IEnumerable<GuestBookingReport> GetGuestBookings()
    {
        return GuestBookingReport.All();
    }

    [HttpGet("availability")]
        return RoomAvailabilityReport.All();
    }

    [HttpGet("service-stats")]
    public IEnumerable<ServiceUsageStatsReport> GetServiceStats()
    {
        return ServiceUsageStatsReport.All();
    }
}
