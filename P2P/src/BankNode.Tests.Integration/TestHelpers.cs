using System.IO;
using System.Text.Json;
using System.Collections.Generic;

namespace BankNode.Tests.Integration
{
    public static class TestHelpers
    {
        private static readonly object _lock = new object();

        public static void EnsureLanguageFile()
        {
            lock (_lock)
            {
                var dir = "languages";
                if (!Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }
                
                var path = Path.Combine(dir, "cs.json");
                if (!File.Exists(path))
                {
                    File.WriteAllText(path, @"
{
    ""UNKNOWN_COMMAND"": ""Neznámý příkaz."",
    ""INVALID_FORMAT"": ""Neplatný formát."",
    ""INVALID_ACCOUNT_FORMAT"": ""Neplatný formát účtu."",
    ""INVALID_AMOUNT"": ""Neplatná částka."",
    ""INSUFFICIENT_FUNDS"": ""Nedostatek finančních prostředků."",
    ""CONNECTION_TIMEOUT"": ""Vypršel časový limit připojení."",
    ""RESPONSE_TIMEOUT"": ""Vypršel časový limit odpovědi."",
    ""NO_RESPONSE"": ""Žádná odpověď."",
    ""CONNECTION_FAILED"": ""Připojení selhalo."",
    ""ROBBERY_PLAN"": ""Plán loupeže"",
    ""HELP_HINT"": ""napište HELP pro nápovědu"",
    ""DID_YOU_MEAN"": ""Mysleli jste {0}?"",
    ""WELCOME_MESSAGE"": ""Vítejte v BankNode! Pro nápovědu napište HELP."",
    ""HELP_HEADER"": ""Dostupné příkazy:"",
    ""HELP_AC"": ""Vytvořit nový účet"",
    ""HELP_BC"": ""Zkontrolovat IP/Status uzlu"",
    ""HELP_AB"": ""Zkontrolovat zůstatek účtu: AB <účet>/<ip>"",
    ""HELP_AD"": ""Vložit peníze: AD <účet>/<ip> <částka>"",
    ""HELP_AW"": ""Vybrat peníze: AW <účet>/<ip> <částka>"",
    ""HELP_AR"": ""Odstranit účet (pokud je zůstatek 0): AR <účet>/<ip>"",
    ""HELP_BA"": ""Získat celkovou částku v bance"",
    ""HELP_BN"": ""Získat počet klientů"",
    ""HELP_RP"": ""Naplánovat loupež (Hacker Edition): RP <částka>""
}");
                }

                path = Path.Combine(dir, "en.json");
                if (!File.Exists(path))
                {
                     File.WriteAllText(path, @"
{
    ""UNKNOWN_COMMAND"": ""Unknown command."",
    ""INVALID_FORMAT"": ""Invalid format."",
    ""INVALID_ACCOUNT_FORMAT"": ""Invalid account format."",
    ""INVALID_AMOUNT"": ""Invalid amount."",
    ""INSUFFICIENT_FUNDS"": ""Insufficient funds."",
    ""CONNECTION_TIMEOUT"": ""Connection timeout."",
    ""RESPONSE_TIMEOUT"": ""Response timeout."",
    ""NO_RESPONSE"": ""No response."",
    ""CONNECTION_FAILED"": ""Connection failed."",
    ""ROBBERY_PLAN"": ""Robbery Plan"",
    ""HELP_HINT"": ""type HELP for help"",
    ""DID_YOU_MEAN"": ""Did you mean {0}?"",
    ""WELCOME_MESSAGE"": ""Welcome to BankNode! Type HELP for help."",
    ""HELP_HEADER"": ""Available commands:"",
    ""HELP_AC"": ""Create new account"",
    ""HELP_BC"": ""Check IP/Node Status"",
    ""HELP_AB"": ""Check account balance: AB <account>/<ip>"",
    ""HELP_AD"": ""Deposit money: AD <account>/<ip> <amount>"",
    ""HELP_AW"": ""Withdraw money: AW <account>/<ip> <amount>"",
    ""HELP_AR"": ""Remove account (if balance 0): AR <account>/<ip>"",
    ""HELP_BA"": ""Get total bank amount"",
    ""HELP_BN"": ""Get client count"",
    ""HELP_RP"": ""Plan robbery (Hacker Edition): RP <amount>"",
    ""HELP_EXIT"": ""Close connection"",
    ""HELP_LANG"": ""Switch language: LANG <code|list>"",
    ""HELP_HELP"": ""Show this help""
}");
                }
            }
        }
    }
}
