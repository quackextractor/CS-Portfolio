namespace Hotel.Backend.Services;

public class BookingLogic
{
    public bool ValidateDates(DateTime checkIn, DateTime checkOut)
    {
        return checkIn < checkOut;
    }

    public decimal CalculateRoomPrice(decimal basePrice, DateTime checkIn, DateTime checkOut)
    {
        // Simple logic: BasePrice * Nights. 
        // If same day (day use), charge 1 night? Usually hotels charge 1 night.
        var nights = (checkOut - checkIn).Days;
        if (nights < 1) nights = 1; 
        
        return basePrice * nights;
    }

    public decimal CalculateTotalPrice(decimal roomTotal, List<decimal> servicePrices)
    {
       return roomTotal + servicePrices.Sum();
    }
}
