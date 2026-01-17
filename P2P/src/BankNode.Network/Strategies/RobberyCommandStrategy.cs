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

        public System.Collections.Generic.IEnumerable<string> SupportedCommands => new[] { "RP" };

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
            var port = _config.Port;
            string baseIp;
            int myLastOctet = -1;

            try 
            {
                var parts = _config.NodeIp.Split('.');
                if (parts.Length == 4)
                {
                    baseIp = $"{parts[0]}.{parts[1]}.{parts[2]}.";
                    if (int.TryParse(parts[3], out int octet))
                    {
                        myLastOctet = octet;
                    }
                }
                else
                {
                    // Fallback for localhost or other formats
                    baseIp = "127.0.0."; 
                }
            }
            catch
            {
                baseIp = "127.0.0.";
            }

            var tasks = new List<Task<BankInfo?>>();
            using var semaphore = new System.Threading.SemaphoreSlim(_config.RobberyConcurrency); // Limit concurrency

            for (int i = 1; i <= 254; i++)
            {
                if (i == myLastOctet) continue; // Skip self
                
                var ip = $"{baseIp}{i}";
                
                tasks.Add(Task.Run(async () => 
                {
                    await semaphore.WaitAsync();
                    try
                    {
                        return await ProbeBankAsync(ip, port);
                    }
                    finally
                    {
                        semaphore.Release();
                    }
                }));
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
            var sorted = banks.OrderByDescending(b => b.ClientCount == 0 ? double.MaxValue : (double)b.TotalAmount / b.ClientCount).ToList();
            
            decimal currentAmount = 0;
            int victimCount = 0;
            var victims = new List<BankInfo>();

            foreach (var bank in sorted)
            {
                if (currentAmount >= targetAmount) break;
                
                currentAmount += bank.TotalAmount;
                victimCount += bank.ClientCount;
                victims.Add(bank);
            }

            if (currentAmount < targetAmount)
            {
                return $"Unable to reach {targetAmount}. Max possible: {currentAmount} from {victims.Count} banks.";
            }

            var sb = new System.Text.StringBuilder();
            sb.AppendLine("RP PLANNED:");
            foreach (var bank in victims)
            {
                sb.AppendLine($"Target: {bank.Ip,-15} | Loot: ${bank.TotalAmount,8} | Clients: {bank.ClientCount,3}");
            }
            sb.Append($"Total: ${currentAmount} (Victims: {victimCount})");
            return sb.ToString(); 
        }



        private class BankInfo
        {
            public string Ip { get; set; } = "";
            public decimal TotalAmount { get; set; }
            public int ClientCount { get; set; }
        }
    }
}
