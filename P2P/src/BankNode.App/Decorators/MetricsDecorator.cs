using System;
using System.Threading.Tasks;
using BankNode.Network;
using BankNode.Shared;

namespace BankNode.App.Decorators
{
    public class MetricsDecorator : ICommandProcessor
    {
        private readonly ICommandProcessor _inner;

        public MetricsDecorator(ICommandProcessor inner)
        {
            _inner = inner;
        }

        public async Task<string> ProcessCommandAsync(string rawCommand, string clientIp)
        {
            // Simple parsing to get command code
            var parts = rawCommand.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            var commandCode = parts.Length > 0 ? parts[0].ToUpperInvariant() : "UNKNOWN";

            try
            {
                var response = await _inner.ProcessCommandAsync(rawCommand, clientIp);
                var success = !response.StartsWith("ER");
                MetricsCollector.Instance.RecordCommand(commandCode, success);
                return response;
            }
            catch
            {
                MetricsCollector.Instance.RecordCommand(commandCode, false);
                throw;
            }
        }
    }
}
