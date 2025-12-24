using Xunit;
using Hotel.Backend.Services;
using System.Collections.Generic;
using System;

namespace Hotel.Tests;

public class BookingLogicTests
{
    private readonly BookingLogic _logic;

    public BookingLogicTests()
    {
        _logic = new BookingLogic();
    }

    [Fact]
    public void ValidateDates_ShouldReturnFalse_WhenCheckInAfterCheckOut()
    {
        var checkIn = DateTime.Now.AddDays(1);
        var checkOut = DateTime.Now;
        Assert.False(_logic.ValidateDates(checkIn, checkOut));
    }

    [Fact]
    public void ValidateDates_ShouldReturnTrue_WhenCheckInBeforeCheckOut()
    {
        var checkIn = DateTime.Now;
        var checkOut = DateTime.Now.AddDays(1);
        Assert.True(_logic.ValidateDates(checkIn, checkOut));
    }

    [Fact]
    public void CalculateRoomPrice_ShouldCalculateCorrectly()
    {
        decimal basePrice = 100m;
        var checkIn = new DateTime(2023, 1, 1);
        var checkOut = new DateTime(2023, 1, 3); // 2 nights
        
        var price = _logic.CalculateRoomPrice(basePrice, checkIn, checkOut);
        
        Assert.Equal(200m, price);
    }

    [Fact]
    public void CalculateTotalPrice_ShouldSumRoomAndServices()
    {
        decimal roomPrice = 200m;
        var services = new List<decimal> { 50m, 25m };
        
        var total = _logic.CalculateTotalPrice(roomPrice, services);
        
        Assert.Equal(275m, total);
    }
}
