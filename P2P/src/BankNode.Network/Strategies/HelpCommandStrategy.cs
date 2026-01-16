using System.Text;
using System.Threading.Tasks;

namespace BankNode.Network.Strategies
{
    public class HelpCommandStrategy : ICommandStrategy
    {
        public System.Collections.Generic.IEnumerable<string> SupportedCommands => new[] { "HELP" };

        public bool CanHandle(string commandCode)
        {
            return commandCode == "HELP";
        }

        public Task<string> ExecuteAsync(string[] args)
        {
            var sb = new StringBuilder();
            sb.AppendLine("Available Commands:");
            sb.AppendLine("  AC                    - Create a new account");
            sb.AppendLine("  BC                    - Check node IP/Status");
            sb.AppendLine("  AB <account>/<ip>     - Check account balance");
            sb.AppendLine("  AD <account>/<ip> <amount> - Deposit money");
            sb.AppendLine("  AW <account>/<ip> <amount> - Withdraw money");
            sb.AppendLine("  AR <account>/<ip>     - Remove account (if balance is 0)");
            sb.AppendLine("  BA                    - Get total bank amount");
            sb.AppendLine("  BN                    - Get number of clients");
            sb.AppendLine("  RP <amount>           - Plan robbery (Hacker Edition)");
            sb.AppendLine("  EXIT                  - Close connection");
            sb.AppendLine("  HELP                  - Show this help message");
            
            return Task.FromResult(sb.ToString());
        }
    }
}
