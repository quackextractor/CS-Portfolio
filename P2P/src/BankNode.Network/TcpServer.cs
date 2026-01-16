using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class TcpServer
    {
        private readonly int _port;
        private readonly CommandParser _commandParser;
        private readonly ILogger<TcpServer> _logger;
        private TcpListener? _listener;

        public TcpServer(int port, CommandParser commandParser, ILogger<TcpServer> logger)
        {
            _port = port;
            _commandParser = commandParser;
            _logger = logger;
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            _listener = new TcpListener(IPAddress.Any, _port);
            _listener.Start();
            _logger.LogInformation($"TCP Server started on port {_port}");

            try
            {
                while (!cancellationToken.IsCancellationRequested)
                {
                    var client = await _listener.AcceptTcpClientAsync(cancellationToken);
                    _ = HandleClientAsync(client, cancellationToken);
                }
            }
            catch (OperationCanceledException)
            {
                // Graceful shutdown
            }
            finally
            {
                _listener.Stop();
                _logger.LogInformation("TCP Server stopped.");
            }
        }

        private async Task HandleClientAsync(TcpClient client, CancellationToken cancellationToken)
        {
            using (client)
            {
                var stream = client.GetStream();
                // Set timeout (e.g. 5 seconds as per requirements, could be config driven)
                stream.ReadTimeout = 5000;
                stream.WriteTimeout = 5000;

                try
                {
                    using (var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true))
                    using (var writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true })
                    {
                        var command = await reader.ReadLineAsync(); // ReadLineAsync doesn't support CancellationToken effectively in netstandard sometimes without extension, but net9 is fine.
                        
                        if (command != null)
                        {
                            var response = await _commandParser.ProcessCommandAsync(command);
                            await writer.WriteLineAsync(response);
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error handling client.");
                    // In a real scenario, we might want to send an ER response if possible, but connection might be broken.
                }
            }
        }
    }
}
