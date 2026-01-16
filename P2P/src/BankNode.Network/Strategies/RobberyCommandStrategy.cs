using System.Collections.Generic;
using System.Linq;
using System.Net.NetworkInformation;
using System.Threading.Tasks;
using BankNode.Shared;

namespace BankNode.Network.Strategies
{
    public class RobberyCommandStrategy : ICommandStrategy
    {
        private readonly INetworkClient _client;
        private readonly AppConfig _config;
        private readonly BankNode.Translation.ITranslationStrategy _translator;

        public RobberyCommandStrategy(INetworkClient client, AppConfig config, BankNode.Translation.ITranslationStrategy translator)
        {
            _client = client;
            _config = config;
            _translator = translator;
        }

        public bool CanHandle(string commandCode)
        {
            return commandCode == "RP";
        }

        public async Task<string> ExecuteAsync(string[] args)
        {
            if (args.Length < 2 || !long.TryParse(args[1], out var targetAmount))
            {
                return $"ER {_translator.GetError("INVALID_AMOUNT")}";
            }

            // 1. Scan Network
            var banks = await ScanNetworkAsync();

            // 2. Calculate Plan
            var plan = CalculateRobberyPlan(banks, targetAmount);

            return $"RP {plan}";
        }

        private async Task<List<BankInfo>> ScanNetworkAsync()
        {
            var banks = new List<BankInfo>();
            var baseIp = GetBaseIp(_config.NodeIp); // e.g., 192.168.1.
            var port = _config.Port;

            // Scanning usually takes time. For this demo, we might limit range or parallelism.
            // We'll scan 10 IPs around our own IP for speed in this implementation, 
            // or 1..254 if we want full coverage (but slow).
            // Let's do a smart scan: +/- 5 addresses and some fixed ones if needed.
            // In a real classroom environment, maybe we just scan all 254.
            
            var tasks = new List<Task<BankInfo?>>();
            
            // Getting just the last octet of current IP
            var myLastOctet = int.Parse(_config.NodeIp.Split('.').Last());
            
            // Scan narrow range for demo purposes (speed), but logic supports full subnet
            // In full implementation: loop i = 1 to 254
            for (int i = 1; i <= 254; i++)
            {
                if (i == myLastOctet) continue; // Skip self
                
                var ip = $"{baseIp}{i}";
                tasks.Add(ProbeBankAsync(ip, port));
            }

            var results = await Task.WhenAll(tasks);
            return results.Where(b => b != null).ToList()!;
        }

        private async Task<BankInfo?> ProbeBankAsync(string ip, int port)
        {
            try
            {
                // Verify it's a bank logic:
                // 1. Send BC (fast check)
                // 2. If response BC, send BA and BN
                
                var bcResp = await _client.SendCommandAsync(ip, port, "BC");
                if (!bcResp.StartsWith("BC")) return null;

                var baResp = await _client.SendCommandAsync(ip, port, "BA");
                if (!baResp.StartsWith("BA")) return null;
                
                var bnResp = await _client.SendCommandAsync(ip, port, "BN");
                if (!bnResp.StartsWith("BN")) return null;

                if (decimal.TryParse(baResp.Substring(3), out var amount) && 
                    int.TryParse(bnResp.Substring(3), out var clients))
                {
                    return new BankInfo { Ip = ip, TotalAmount = amount, ClientCount = clients };
                }
            }
            catch
            {
                // Ignore connection errors
            }
            return null;
        }

        private string CalculateRobberyPlan(List<BankInfo> banks, long targetAmount)
        {
            // Goal: Sum(Amount) >= targetAmount, Min(Sum(Clients))
            // This is a variation of Knapsack (Min weight for at least Value).
            // Since N is small (number of banks), we can brute force or use DP? 
            // Actually, we want MIN clients.
            
            // Heuristic: Sort by Density? (Amount / Client)? High money, low clients first.
            var sorted = banks.OrderByDescending(b => b.ClientCount == 0 ? double.MaxValue : (double)b.TotalAmount / b.ClientCount).ToList();
            
            decimal currentAmount = 0;
            int victimCount = 0;
            var victims = new List<string>();

            foreach (var bank in sorted)
            {
                if (currentAmount >= targetAmount) break;
                
                currentAmount += bank.TotalAmount;
                victimCount += bank.ClientCount;
                victims.Add(bank.Ip);
            }

            if (currentAmount < targetAmount)
            {
                return $"Unable to reach {targetAmount}. Max possible: {currentAmount} from {victims.Count} banks.";
            }

            return $"To reach {targetAmount} execute robbery on: {string.Join(", ", victims)}. Hits {victimCount} clients.";
        }

        private string GetBaseIp(string ip)
        {
            var parts = ip.Split('.');
            return $"{parts[0]}.{parts[1]}.{parts[2]}.";
        }

        private class BankInfo
        {
            public string Ip { get; set; } = "";
            public decimal TotalAmount { get; set; }
            public int ClientCount { get; set; }
        }
    }
}
