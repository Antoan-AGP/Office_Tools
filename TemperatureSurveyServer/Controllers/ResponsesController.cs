using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;

[Route("api/[controller]")]
[ApiController]
public class ResponsesController : ControllerBase
{
    // In-memory storage for demonstration purposes
    private static readonly List<string> _responses = new();

    // POST: api/responses
    [HttpPost]
    public IActionResult PostResponse([FromBody] ResponseModel response)
    {
        // Add the response to the in-memory list
        _responses.Add(response.Response);
        Console.WriteLine($"Received response: {response.Response}"); // Log to console
        return Ok();
    }

}

public class ResponseModel
{
    public required string? Response { get; set; }
}
