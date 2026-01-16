using System.Threading.Tasks;

namespace BankNode.Network
{
    public interface INetworkClient
    {
        Task<string> SendCommandAsync(string ip, int port, string command);
    }
}
