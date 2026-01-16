using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BankNode.Network.Strategies;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class CommandParser
    {
        private readonly IEnumerable<ICommandStrategy> _strategies;
        private readonly ILogger<CommandParser> _logger;

        public CommandParser(IEnumerable<ICommandStrategy> strategies, ILogger<CommandParser> logger)
        {
            _strategies = strategies;
            _logger = logger;
        }

        public async Task<string> ProcessCommandAsync(string rawCommand)
        {
            if (string.IsNullOrWhiteSpace(rawCommand))
            {
                return string.Empty;
            }

            var parts = rawCommand.Trim().Split(' ');
            var commandCode = parts[0];

            _logger.LogInformation($"Received command: {commandCode}");

            var strategy = _strategies.FirstOrDefault(s => s.CanHandle(commandCode));

            if (strategy == null)
            {
                _logger.LogWarning($"Unknown command: {commandCode}");
                return "ER Unknown command.";
            }

            try
            {
                return await strategy.ExecuteAsync(parts);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing command.");
                return $"ER {ex.Message}";
            }
        }
    }
}
