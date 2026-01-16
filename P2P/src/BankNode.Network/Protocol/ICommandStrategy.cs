using System.Threading.Tasks;

namespace BankNode.Network.Protocol
{
    public interface ICommandStrategy
    {
        string CommandCode { get; }
        Task<string> ExecuteAsync(string[] args);
    }
}
