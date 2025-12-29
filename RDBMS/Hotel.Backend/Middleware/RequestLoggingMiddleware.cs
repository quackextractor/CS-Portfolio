using System.Diagnostics;

namespace Hotel.Backend.Middleware;

public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        _logger.LogInformation("[{Time}] Incoming request: {Method} {Path}", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), context.Request.Method, context.Request.Path);

        var stopwatch = Stopwatch.StartNew();
        
        await _next(context);

        stopwatch.Stop();

        _logger.LogInformation("[{Time}] Response: {StatusCode} sent in {ElapsedMilliseconds}ms", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), context.Response.StatusCode, stopwatch.ElapsedMilliseconds);
    }
}
