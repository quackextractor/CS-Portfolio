using System.Collections.Generic;
using System.Threading.Tasks;

namespace BankNode.Network.Protocol
{
    public class CommandParser
    {
        private readonly IEnumerable<ICommandStrategy> _strategies;

        public CommandParser(IEnumerable<ICommandStrategy> strategies)
        {
            _strategies = strategies;
        }

        public async Task<string> ParseAndExecuteAsync(string commandLine)
        {
            // Placeholder: Parse command and find strategy
            return "ER Not implemented";
        }
    }
}
