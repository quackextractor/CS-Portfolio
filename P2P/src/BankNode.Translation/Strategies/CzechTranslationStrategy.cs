using System.Collections.Generic;

namespace BankNode.Translation.Strategies
{
    public class CzechTranslationStrategy : ITranslationStrategy
    {
        private readonly Dictionary<string, string> _messages = new Dictionary<string, string>
        {
            // Info
            
            // Errors
            { "UNKNOWN_COMMAND", "Neznámý příkaz." },
            { "INVALID_FORMAT", "Neplatný formát." },
            { "INVALID_ACCOUNT_FORMAT", "Neplatný formát účtu." },
            { "INVALID_AMOUNT", "Neplatná částka." },
            { "INSUFFICIENT_FUNDS", "Nedostatek finančních prostředků." },
            { "CONNECTION_TIMEOUT", "Vypršel časový limit připojení." },
            { "RESPONSE_TIMEOUT", "Vypršel časový limit odpovědi." },
            { "NO_RESPONSE", "Žádná odpověď." },
            { "CONNECTION_FAILED", "Připojení selhalo." },
            { "ROBBERY_PLAN", "Plán loupeže" },
            { "HELP_HINT", "help" }
        };

        public string GetMessage(string key) 
        {
            return _messages.ContainsKey(key) ? _messages[key] : key;
        }

        public string GetError(string key) 
        {
            return _messages.ContainsKey(key) ? _messages[key] : key;
        }
    }
}
