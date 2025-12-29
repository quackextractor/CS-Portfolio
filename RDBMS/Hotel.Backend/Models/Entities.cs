using Hotel.Backend.Data;
using System.ComponentModel.DataAnnotations.Schema;

namespace Hotel.Backend.Models;

[Table("RoomTypes")]
public class RoomType : ActiveRecordBase<RoomType>
{
    public string Name { get; set; } = string.Empty;
    public decimal BasePrice { get; set; }
}

[Table("Rooms")]
public class Room : ActiveRecordBase<Room>
{
    public string RoomNumber { get; set; } = string.Empty;
    public int RoomTypeId { get; set; }
}

[Table("Bookings")]
public class Booking : ActiveRecordBase<Booking>
{
    public int GuestId { get; set; }
    public int RoomId { get; set; }
    public DateTime CheckIn { get; set; }
    public DateTime CheckOut { get; set; }
    public decimal TotalPrice { get; set; }
}

[Table("Services")]
public class Service : ActiveRecordBase<Service>
{
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
}

[Table("BookingServices")]
public class BookingService : ActiveRecordBase<BookingService>
{
    public int BookingId { get; set; }
    public int ServiceId { get; set; }
    public DateTime ServiceDate { get; set; }
    public decimal SubTotal { get; set; }
}
