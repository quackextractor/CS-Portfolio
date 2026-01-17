using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;

namespace BankNode.Network.Strategies
{
    public class BasicCommandStrategy : ICommandStrategy
    {
        private readonly AppConfig _config;
        private readonly IAccountService _accountService;
        private readonly BankNode.Translation.ITranslationStrategy _translator;

        public BasicCommandStrategy(AppConfig config, IAccountService accountService, BankNode.Translation.ITranslationStrategy translator)
        {
            _config = config;
            _accountService = accountService;
            _translator = translator;
        }

        public System.Collections.Generic.IEnumerable<string> SupportedCommands => new[] { "BC", "BA", "BN" };

        public bool CanHandle(string commandCode)
        {
            return System.Linq.Enumerable.Contains(SupportedCommands, commandCode);
        }

        public async Task<string> ExecuteAsync(string[] args)
        {
            var command = args[0];

            switch (command)
            {
                case "BC":
                    return $"BC {_config.NodeIp}";
                case "BA":
                    var total = await _accountService.GetTotalBankBalanceAsync();
                    return $"BA {total}";
                case "BN":
                    var count = await _accountService.GetClientCountAsync();
                    return $"BN {count}";
                default:
                    return $"ER {_translator.GetError("UNKNOWN_COMMAND")}";
            }
        }
    }
}
