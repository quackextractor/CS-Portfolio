using System;
using System.Linq;
using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;

namespace BankNode.Network.Strategies
{
    public class AccountCommandStrategy : ICommandStrategy
    {
        private readonly AppConfig _config;
        private readonly IAccountService _accountService;
        private readonly NetworkClient _networkClient;

        public AccountCommandStrategy(AppConfig config, IAccountService accountService, NetworkClient networkClient)
        {
            _config = config;
            _accountService = accountService;
            _networkClient = networkClient;
        }

        public bool CanHandle(string commandCode)
        {
            return new[] { "AC", "AD", "AW", "AB", "AR" }.Contains(commandCode);
        }

        public async Task<string> ExecuteAsync(string[] args)
        {
            var command = args[0];

            try
            {
                switch (command)
                {
                    case "AC":
                        return HandleCreate();
                    case "AD": // AD <acc>/<ip> <amount>
                        return await HandleDeposit(args);
                    case "AW": // AW <acc>/<ip> <amount>
                        return await HandleWithdraw(args);
                    case "AB": // AB <acc>/<ip>
                        return await HandleBalance(args);
                    case "AR": // AR <acc>/<ip>
                        return await HandleRemove(args);
                    default:
                        return "ER Unknown command.";
                }
            }
            catch (Exception ex)
            {
                return $"ER {ex.Message}";
            }
        }

        private string HandleCreate()
        {
            var account = _accountService.CreateAccount(_config.NodeIp);
            return $"AC {account.FullAccountNumber}";
        }

        private async Task<string> HandleDeposit(string[] args)
        {
            if (args.Length < 3) return "ER Invalid format.";
            if (!ParseAccount(args[1], out var accNum, out var ip)) return "ER Invalid account format.";
            if (!decimal.TryParse(args[2], out var amount)) return "ER Invalid amount.";

            if (IsRemote(ip))
            {
                // Relay entire command
                return await _networkClient.SendCommandAsync(ip, _config.Port, string.Join(" ", args));
            }

            _accountService.Deposit(accNum, amount);
            return "AD";
        }

        private async Task<string> HandleWithdraw(string[] args)
        {
            if (args.Length < 3) return "ER Invalid format.";
            if (!ParseAccount(args[1], out var accNum, out var ip)) return "ER Invalid account format.";
            if (!decimal.TryParse(args[2], out var amount)) return "ER Invalid amount.";

            if (IsRemote(ip))
            {
                return await _networkClient.SendCommandAsync(ip, _config.Port, string.Join(" ", args));
            }

            _accountService.Withdraw(accNum, amount);
            return "AW";
        }

        private async Task<string> HandleBalance(string[] args)
        {
            if (args.Length < 2) return "ER Invalid format.";
            if (!ParseAccount(args[1], out var accNum, out var ip)) return "ER Invalid account format.";

            if (IsRemote(ip))
            {
                return await _networkClient.SendCommandAsync(ip, _config.Port, string.Join(" ", args));
            }

            var balance = _accountService.GetBalance(accNum);
            return $"AB {balance}";
        }

        private async Task<string> HandleRemove(string[] args)
        {
            if (args.Length < 2) return "ER Invalid format.";
            if (!ParseAccount(args[1], out var accNum, out var ip)) return "ER Invalid account format.";

            if (IsRemote(ip))
            {
                return await _networkClient.SendCommandAsync(ip, _config.Port, string.Join(" ", args));
            }

            _accountService.RemoveAccount(accNum);
            return "AR";
        }

        private bool IsRemote(string ip)
        {
            // Simple check. If IP is different from Config IP, treat as remote.
            // Note: In a real scenario, we might need more robust IP matching (e.g. 127.0.0.1 vs actual IP).
            // For this assignment, assuming exact string match or if we are proxying, we rely on the IP string.
            return ip != _config.NodeIp;
        }

        private bool ParseAccount(string fullAccount, out string accountNumber, out string ip)
        {
            accountNumber = string.Empty;
            ip = string.Empty;
            
            var parts = fullAccount.Split('/');
            if (parts.Length != 2) return false;

            accountNumber = parts[0];
            ip = parts[1];
            return true;
        }
    }
}
