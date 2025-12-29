using Hotel.Backend.Data;
using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

namespace Hotel.Backend.Controllers;

public class CreateBookingRequest
{
    public int GuestId { get; set; }
    public int RoomId { get; set; }
    public DateTime CheckIn { get; set; }
    public DateTime CheckOut { get; set; }
    public List<int> ServiceIds { get; set; } = new();
}

[ApiController]
[Route("api/[controller]")]
public class BookingsController : ControllerBase
{
    [HttpPost]
    public IActionResult Create([FromBody] CreateBookingRequest request)
    {
        // Logic
        var logic = new Services.BookingLogic();

        // Validation
        if (!logic.ValidateDates(request.CheckIn, request.CheckOut))
            return BadRequest("Check-out must be after check-in.");

        var room = Room.Find(request.RoomId);
        if (room == null) return BadRequest("Room not found.");

        // Transaction
        using var conn = new SqlConnection(DbConfig.ConnectionString);
        conn.Open();
        using var transaction = conn.BeginTransaction();

        try
        {
            // 1. Create Booking
            var booking = new Booking
            {
                GuestId = request.GuestId,
                RoomId = request.RoomId,
                CheckIn = request.CheckIn,
                CheckOut = request.CheckOut,
                TotalPrice = 0 // Will calculate
            };

            // Calculate base price
            var roomType = RoomType.Find(room.RoomTypeId, transaction);
            
            decimal roomPrice = 0;
            if (roomType != null)
            {
                roomPrice = logic.CalculateRoomPrice(roomType.BasePrice, request.CheckIn, request.CheckOut);
            }
            booking.TotalPrice = roomPrice;
            
            booking.Save(transaction); // Insert Booking to get ID

            // 2. Add Services
            if (request.ServiceIds != null && request.ServiceIds.Any())
            {
                foreach (var serviceId in request.ServiceIds)
                {
                    var service = Service.Find(serviceId, transaction);
                    if (service == null) throw new Exception($"Service {serviceId} not found");

                    var bookingService = new BookingService
                    {
                        BookingId = booking.Id,
                        ServiceId = serviceId,
                        ServiceDate = booking.CheckIn, // Default to check-in date
                        SubTotal = service.Price
                    };
                    bookingService.Save(transaction);
                    
                    booking.TotalPrice += service.Price;
                }
                // Update total price
                booking.Save(transaction); 
            }


            transaction.Commit();
            return Ok(booking);
        }
        catch (Exception ex)
        {
            transaction.Rollback();
            return StatusCode(500, ex.Message);
        }
    }

    [HttpGet]
    public IEnumerable<Booking> Get()
    {
        return Booking.All();
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        using var conn = new SqlConnection(DbConfig.ConnectionString);
        conn.Open();
        using var transaction = conn.BeginTransaction();

        try
        {
            var booking = Booking.Find(id, transaction);
            if (booking == null) return NotFound();

            // Remove Booking
            booking.Delete(transaction);
            
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
