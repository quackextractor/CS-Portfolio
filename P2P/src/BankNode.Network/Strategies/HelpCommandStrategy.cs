using System.Text;
using System.Threading.Tasks;

namespace BankNode.Network.Strategies
{
    public class HelpCommandStrategy : ICommandStrategy
    {
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
            sb.AppendLine("  AB <account_id>       - Check account balance");
            sb.AppendLine("  AD <account_id> <amount> - Deposit money");
            sb.AppendLine("  AW <account_id> <amount> - Withdraw money");
            sb.AppendLine("  AR <target_ip> <port> - Attempt robbery (Hacker Edition)");
            sb.AppendLine("  EXIT                  - Close connection");
            sb.AppendLine("  HELP                  - Show this help message");
            
            return Task.FromResult(sb.ToString());
        }
    }
}
