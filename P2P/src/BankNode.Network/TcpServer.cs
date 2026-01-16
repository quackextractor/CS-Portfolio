using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class TcpServer
    {
        private readonly AppConfig _config;
        private readonly ICommandProcessor _commandProcessor;
        private readonly ILogger<TcpServer> _logger;
        private TcpListener? _listener;

        public TcpServer(AppConfig config, ICommandProcessor commandProcessor, ILogger<TcpServer> logger)
        {
            _config = config;
            _commandProcessor = commandProcessor;

            _logger = logger;
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            _listener = new TcpListener(IPAddress.Any, _config.Port);
            _listener.Start();
            _logger.LogInformation($"TCP Server started on port {_config.Port}");

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
                stream.ReadTimeout = _config.Timeout;
                stream.WriteTimeout = _config.Timeout;

                try
                {
                    using (var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true))
                    using (var writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true })
                    {
                        var command = await reader.ReadLineAsync(); // ReadLineAsync doesn't support CancellationToken effectively in netstandard sometimes without extension, but net9 is fine.
                        
                        if (command != null)
                        {
                            var response = await _commandProcessor.ProcessCommandAsync(command);
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
