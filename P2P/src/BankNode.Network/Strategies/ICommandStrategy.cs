using System.Threading.Tasks;

namespace BankNode.Network.Strategies
{
    public interface ICommandStrategy
    {
        bool CanHandle(string commandCode);
        Task<string> ExecuteAsync(string[] args);
        System.Collections.Generic.IEnumerable<string> SupportedCommands { get; }

    }
}
