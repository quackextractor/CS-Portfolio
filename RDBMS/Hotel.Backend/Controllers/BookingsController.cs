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
            
            booking.Save(transaction); // Insert Booking

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
