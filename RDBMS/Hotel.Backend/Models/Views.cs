using Hotel.Backend.Data;
using System.ComponentModel.DataAnnotations.Schema;

namespace Hotel.Backend.Models;

[Table("v_GuestBookings")]
public class GuestBookingReport : ActiveRecordBase<GuestBookingReport>
{
    public int BookingId { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string RoomNumber { get; set; } = string.Empty;
    public DateTime CheckIn { get; set; }
    public DateTime CheckOut { get; set; }
}

[Table("v_RoomAvailability")]
public class RoomAvailabilityReport : ActiveRecordBase<RoomAvailabilityReport>
{
    public int RoomId { get; set; }
    public string RoomNumber { get; set; } = string.Empty;
    public string RoomType { get; set; } = string.Empty;
    public decimal BasePrice { get; set; }
}

[Table("v_ServiceUsageStats")]
public class ServiceUsageStatsReport : ActiveRecordBase<ServiceUsageStatsReport>
{
    public string ServiceName { get; set; } = string.Empty;
    public int UsageCount { get; set; }
    public decimal TotalRevenue { get; set; }
}

[Table("v_RevenueByRoomType")]
public class RevenueByRoomTypeReport : ActiveRecordBase<RevenueByRoomTypeReport>
{
    public string RoomTypeName { get; set; } = string.Empty;
    public int TotalBookings { get; set; }
    public decimal TotalRevenue { get; set; }
}
