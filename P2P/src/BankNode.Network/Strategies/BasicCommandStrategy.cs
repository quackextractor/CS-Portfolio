using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;

namespace BankNode.Network.Strategies
{
    public class BasicCommandStrategy : ICommandStrategy
    {
        private readonly AppConfig _config;
        private readonly IAccountService _accountService;

        public BasicCommandStrategy(AppConfig config, IAccountService accountService)
        {
            _config = config;
            _accountService = accountService;
        }

        public bool CanHandle(string commandCode)
        {
            return commandCode == "BC" || commandCode == "BA" || commandCode == "BN";
        }

        public Task<string> ExecuteAsync(string[] args)
        {
            var command = args[0];

            switch (command)
            {
                case "BC":
                    return Task.FromResult($"BC {_config.NodeIp}");
                case "BA":
                    var total = _accountService.GetTotalBankBalance();
                    return Task.FromResult($"BA {total}");
                case "BN":
                    var count = _accountService.GetClientCount();
                    return Task.FromResult($"BN {count}");
                default:
                    return Task.FromResult("ER Unknown command.");
            }
        }
    }
}
