using System;
using System.Threading;
using System.Threading.Tasks;

namespace BankNode.Network
{
    public class TcpServer
    {
        private readonly int _port;

        public TcpServer(int port)
        {
            _port = port;
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            // Placeholder for TCP listener logic
            Console.WriteLine($"Starting TCP Server on port {_port}...");
            await Task.Delay(100, cancellationToken);
        }
    }
}
