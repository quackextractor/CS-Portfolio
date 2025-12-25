using Hotel.Backend.Data;
using System.ComponentModel.DataAnnotations.Schema;

namespace Hotel.Backend.Models;

[Table("RoomTypes")]
public class RoomType : ActiveRecordBase<RoomType>
{
    public string Name { get; set; } = string.Empty;
    public decimal BasePrice { get; set; }
    public string Description { get; set; } = string.Empty;
}

[Table("Rooms")]
public class Room : ActiveRecordBase<Room>
{
    public string RoomNumber { get; set; } = string.Empty;
    public int RoomTypeId { get; set; }
    public DateTime? LastMaintenance { get; set; }
}

[Table("Services")]
public class Service : ActiveRecordBase<Service>
{
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public bool IsActive { get; set; } = true;
}

public enum BookingStatus
{
    Pending,
    Confirmed,
    Cancelled,
    Completed
}

[Table("Bookings")]
public class Booking : ActiveRecordBase<Booking>
{
    public int GuestId { get; set; }
    public int RoomId { get; set; }
    public DateTime CheckIn { get; set; }
    public DateTime CheckOut { get; set; }
    public decimal TotalPrice { get; set; }
    public BookingStatus Status { get; set; } = BookingStatus.Pending;
    public DateTime CreatedAt { get; set; } = DateTime.Now;
}

[Table("BookingServices")]
public class BookingService : ActiveRecordBase<BookingService>
{
    public int BookingId { get; set; }
    public int ServiceId { get; set; }
    public decimal SubTotal { get; set; }
    public DateTime ServiceDate { get; set; } = DateTime.Now;
}
