using Hotel.Backend.Data;
using Hotel.Backend.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using System.Text.Json;

namespace Hotel.Backend.Controllers;

public class GuestImportDto
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Phone { get; set; } = string.Empty;
    public DateTime DateOfBirth { get; set; }
}

public class ServiceImportDto
{
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
}

[ApiController]
[Route("api/[controller]")]
public class ImportController : ControllerBase
{
    [HttpPost("guests")]
    public async Task<IActionResult> ImportGuests([FromForm] IFormFile file)
    {
        if (file == null || file.Length == 0)
            return BadRequest("File is empty.");

        try
        {
            using var stream = file.OpenReadStream();
            var guests = await JsonSerializer.DeserializeAsync<List<GuestImportDto>>(stream, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            if (guests == null || !guests.Any())
                return BadRequest("No guests found in JSON.");

            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();
            using var transaction = conn.BeginTransaction();

            try
            {
                foreach (var g in guests)
                {
                    if (string.IsNullOrWhiteSpace(g.FirstName) || string.IsNullOrWhiteSpace(g.LastName))
                        throw new Exception("Invalid guest data: FirstName and LastName are required.");

                    var guest = new Guest
                    {
                        FirstName = g.FirstName,
                        LastName = g.LastName,
                        Email = g.Email,
                        Phone = g.Phone,
                        DateOfBirth = g.DateOfBirth,
                        IsActive = true
                    };
                    guest.Save(transaction);
                }
                transaction.Commit();
                return Ok(new { Count = guests.Count, Message = "Import successful" });
            }
            catch (Exception ex)
            {
                transaction.Rollback();
                return BadRequest(ex.Message);
            }
        }
        catch (JsonException ex)
        {
            return BadRequest($"Invalid JSON: {ex.Message}");
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }
}
