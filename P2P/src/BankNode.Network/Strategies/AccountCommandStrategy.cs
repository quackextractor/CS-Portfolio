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
        private readonly INetworkClient _networkClient;
        private readonly BankNode.Translation.ITranslationStrategy _translator;

        public AccountCommandStrategy(AppConfig config, IAccountService accountService, INetworkClient networkClient, BankNode.Translation.ITranslationStrategy translator)
        {
            _config = config;
            _accountService = accountService;
            _networkClient = networkClient;
            _translator = translator;
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
                        return $"ER {_translator.GetError("UNKNOWN_COMMAND")}";
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
            if (args.Length < 3) return $"ER {_translator.GetError("INVALID_FORMAT")}";
            if (!ParseAccount(args[1], out var accNum, out var ip, out var port)) return $"ER {_translator.GetError("INVALID_ACCOUNT_FORMAT")}";
            if (!decimal.TryParse(args[2], out var amount)) return $"ER {_translator.GetError("INVALID_AMOUNT")}";

            if (IsRemote(ip, port))
            {
                // Relay entire command
                return await _networkClient.SendCommandAsync(ip, port, string.Join(" ", args));
            }

            _accountService.Deposit(accNum, amount);
            return "AD";
        }

        private async Task<string> HandleWithdraw(string[] args)
        {
            if (args.Length < 3) return $"ER {_translator.GetError("INVALID_FORMAT")}";
            if (!ParseAccount(args[1], out var accNum, out var ip, out var port)) return $"ER {_translator.GetError("INVALID_ACCOUNT_FORMAT")}";
            if (!decimal.TryParse(args[2], out var amount)) return $"ER {_translator.GetError("INVALID_AMOUNT")}";

            if (IsRemote(ip, port))
            {
                return await _networkClient.SendCommandAsync(ip, port, string.Join(" ", args));
            }

            _accountService.Withdraw(accNum, amount);
            return "AW";
        }

        private async Task<string> HandleBalance(string[] args)
        {
            if (args.Length < 2) return $"ER {_translator.GetError("INVALID_FORMAT")}";
            if (!ParseAccount(args[1], out var accNum, out var ip, out var port)) return $"ER {_translator.GetError("INVALID_ACCOUNT_FORMAT")}";

            if (IsRemote(ip, port))
            {
                return await _networkClient.SendCommandAsync(ip, port, string.Join(" ", args));
            }

            var balance = _accountService.GetBalance(accNum);
            return $"AB {balance}";
        }

        private async Task<string> HandleRemove(string[] args)
        {
            if (args.Length < 2) return $"ER {_translator.GetError("INVALID_FORMAT")}";
            if (!ParseAccount(args[1], out var accNum, out var ip, out var port)) return $"ER {_translator.GetError("INVALID_ACCOUNT_FORMAT")}";

            if (IsRemote(ip, port))
            {
                return await _networkClient.SendCommandAsync(ip, port, string.Join(" ", args));
            }

            _accountService.RemoveAccount(accNum);
            return "AR";
        }

        private bool IsRemote(string ip, int port)
        {
            // If it's localhost, we check if the port matches our listening port.
            // If the port is different, it's considered remote (another node on the same machine).
            if ((ip == "127.0.0.1" || ip == "localhost" || ip == _config.NodeIp) && port == _config.Port)
            {
                return false;
            }
            return true;
        }

        private bool ParseAccount(string fullAccount, out string accountNumber, out string ip, out int port)
        {
            accountNumber = string.Empty;
            ip = string.Empty;
            port = _config.Port; // Default to our config port if not specified (standard P2P behavior)
            
            var parts = fullAccount.Split('/');
            if (parts.Length != 2) return false;

            accountNumber = parts[0];
            var addressPart = parts[1];

            // Check for Port
            if (addressPart.Contains(":"))
            {
                var ipParts = addressPart.Split(':');
                if (ipParts.Length == 2 && int.TryParse(ipParts[1], out var parsedPort))
                {
                    ip = ipParts[0];
                    port = parsedPort;
                }
                else
                {
                    return false; // Invalid format
                }
            }
            else
            {
                ip = addressPart;
            }

            return true;
        }
    }
}
