using Hotel.Backend.Data;
using System.ComponentModel.DataAnnotations.Schema;

namespace Hotel.Backend.Models;

public enum GuestType
{
    Regular,
    VIP,
    Corporate
}

[Table("Guests")]
public class Guest : ActiveRecordBase<Guest>
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Phone { get; set; } = string.Empty;
    public DateTime DateOfBirth { get; set; }
    public bool IsActive { get; set; } = true;
    public GuestType Type { get; set; } = GuestType.Regular;
    public double LoyaltyPoints { get; set; } = 0.0; // float equivalent
}
