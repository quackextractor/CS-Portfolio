using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BankNode.Network.Strategies;
using BankNode.Translation;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class CommandParser : ICommandProcessor
    {
        private readonly IEnumerable<ICommandStrategy> _strategies;
        private readonly ITranslationStrategy _translator;
        private readonly ILogger<CommandParser> _logger;

        public CommandParser(IEnumerable<ICommandStrategy> strategies, ITranslationStrategy translator, ILogger<CommandParser> logger)
        {
            _strategies = strategies;
            _translator = translator;
            _logger = logger;
        }

        public async Task<string> ProcessCommandAsync(string rawCommand)
        {
            if (string.IsNullOrWhiteSpace(rawCommand))
            {
                return string.Empty;
            }

            var parts = rawCommand.Trim().Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            var commandCode = parts[0].ToUpperInvariant();
            parts[0] = commandCode; // Ensure strategy receives uppercase command



            var strategy = _strategies.FirstOrDefault(s => s.CanHandle(commandCode));

            if (strategy == null)
            {
                _logger.LogWarning($"Unknown command: {commandCode}");
                
                var allCommands = _strategies.SelectMany(s => s.SupportedCommands).Distinct();
                var bestMatch = allCommands
                    .Select(cmd => new { Command = cmd, Distance = LevenshteinDistance(commandCode, cmd) })
                    .OrderBy(x => x.Distance)
                    .FirstOrDefault();

                string suggestion = "";
                if (bestMatch != null && bestMatch.Distance <= 2)
                {
                    suggestion = $" {_translator.GetMessage("DID_YOU_MEAN").Replace("{0}", bestMatch.Command)}";
                }

                return $"ER {_translator.GetError("UNKNOWN_COMMAND")}{suggestion}\r\n{_translator.GetMessage("HELP_HINT")}";
            }

            try
            {
                return await strategy.ExecuteAsync(parts);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing command.");
                return $"ER {_translator.GetError("INTERNAL_ERROR")}";
            }
        }


        private int LevenshteinDistance(string s, string t)
        {
            if (string.IsNullOrEmpty(s)) return string.IsNullOrEmpty(t) ? 0 : t.Length;
            if (string.IsNullOrEmpty(t)) return s.Length;

            int n = s.Length;
            int m = t.Length;
            int[,] d = new int[n + 1, m + 1];

            for (int i = 0; i <= n; d[i, 0] = i++) { }
            for (int j = 0; j <= m; d[0, j] = j++) { }

            for (int i = 1; i <= n; i++)
            {
                for (int j = 1; j <= m; j++)
                {
                    int cost = (t[j - 1] == s[i - 1]) ? 0 : 1;
                    d[i, j] = Math.Min(Math.Min(d[i - 1, j] + 1, d[i, j - 1] + 1), d[i - 1, j - 1] + cost);
                }
            }

            return d[n, m];
        }
    }
}
