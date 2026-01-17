using System.Text;
using System.Threading.Tasks;
using BankNode.Translation;

namespace BankNode.Network.Strategies
{
    public class HelpCommandStrategy : ICommandStrategy
    {
        private readonly ITranslationStrategy _translator;

        public HelpCommandStrategy(ITranslationStrategy translator)
        {
            _translator = translator;
        }

        public System.Collections.Generic.IEnumerable<string> SupportedCommands => new[] { "HELP" };

        public bool CanHandle(string commandCode)
        {
            return commandCode == "HELP";
        }

        public Task<string> ExecuteAsync(string[] args)
        {
            var sb = new StringBuilder();
            sb.AppendLine(_translator.GetMessage("HELP_HEADER"));
            sb.AppendLine($"  AC                    - {_translator.GetMessage("HELP_AC")}");
            sb.AppendLine($"  BC                    - {_translator.GetMessage("HELP_BC")}");
            sb.AppendLine($"  AB <account>/<ip>     - {_translator.GetMessage("HELP_AB")}");
            sb.AppendLine($"  AD <account>/<ip> <amount> - {_translator.GetMessage("HELP_AD")}");
            sb.AppendLine($"  AW <account>/<ip> <amount> - {_translator.GetMessage("HELP_AW")}");
            sb.AppendLine($"  AR <account>/<ip>     - {_translator.GetMessage("HELP_AR")}");
            sb.AppendLine($"  BA                    - {_translator.GetMessage("HELP_BA")}");
            sb.AppendLine($"  BN                    - {_translator.GetMessage("HELP_BN")}");
            sb.AppendLine($"  RP <amount>           - {_translator.GetMessage("HELP_RP")}");
            sb.AppendLine($"  EXIT                  - {_translator.GetMessage("HELP_EXIT")}");
            sb.AppendLine($"  LANG                  - {_translator.GetMessage("HELP_LANG")}");
            sb.AppendLine($"  HELP                  - {_translator.GetMessage("HELP_HELP")}");
            
            return Task.FromResult(sb.ToString());
        }
    }
}
