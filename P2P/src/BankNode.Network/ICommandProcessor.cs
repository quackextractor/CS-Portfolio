using System.Threading.Tasks;

namespace BankNode.Network
{
    public interface ICommandProcessor
    {
        Task<string> ProcessCommandAsync(string rawCommand);
    }
}
