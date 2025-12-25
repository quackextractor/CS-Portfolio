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
    public IEnumerable<RoomAvailabilityReport> GetAvailability()
    {
        return RoomAvailabilityReport.All();
    }

    [HttpGet("revenue-by-room-type")]
    public IEnumerable<RevenueByRoomTypeReport> GetRevenueByRoomType()
    {
        return RevenueByRoomTypeReport.All();
    }
}
