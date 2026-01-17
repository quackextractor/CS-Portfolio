using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class RequestLoggingDecorator : ICommandProcessor
    {
        private readonly ICommandProcessor _inner;
        private readonly ILogger<RequestLoggingDecorator> _logger;

        public RequestLoggingDecorator(ICommandProcessor inner, ILogger<RequestLoggingDecorator> logger)
        {
            _inner = inner;
            _logger = logger;
        }

        public async Task<string> ProcessCommandAsync(string rawCommand, string clientIp)
        {
            var commandCode = rawCommand.Split(' ')[0];
            _logger.LogInformation("[{Time}] Incoming request from {Ip}: {Method}", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), clientIp, commandCode);

            var stopwatch = Stopwatch.StartNew();
            
            var response = await _inner.ProcessCommandAsync(rawCommand, clientIp);

            stopwatch.Stop();

            _logger.LogInformation("[{Time}] Response: {Response} sent in {ElapsedMilliseconds}ms", 
                DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), 
                response.Length > 20 ? response.Substring(0, 20) + "..." : response, 
                stopwatch.ElapsedMilliseconds);

            return response;
        }
    }
}
