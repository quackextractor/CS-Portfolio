using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class NetworkClient : INetworkClient
    {
        private readonly AppConfig _config;
        private readonly ILogger<NetworkClient> _logger;
        private readonly BankNode.Translation.ITranslationStrategy _translator;

        public NetworkClient(AppConfig config, ILogger<NetworkClient> logger, BankNode.Translation.ITranslationStrategy translator)
        {
            _config = config;
            _logger = logger;
            _translator = translator;
        }

        public async Task<string> SendCommandAsync(string ip, int port, string command)
        {
            try
            {
                _logger.LogInformation($"Proxying command to {ip}:{port} -> {command}");

                using var client = new TcpClient();
                using var ctsConnect = new CancellationTokenSource(_config.Timeout);
                
                try 
                {
                    await client.ConnectAsync(ip, port, ctsConnect.Token);
                }
                catch (OperationCanceledException)
                {
                    _logger.LogWarning($"Connection timeout to {ip}:{port}");
                    return $"ER {_translator.GetError("CONNECTION_TIMEOUT")}";
                }

                using var stream = client.GetStream();
                // Stream timeouts are still good to have as backup
                stream.ReadTimeout = _config.Timeout;
                stream.WriteTimeout = _config.Timeout;

                using var writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true };
                using var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true);

                // Consume welcome message
                using var ctsWelcome = new CancellationTokenSource(_config.Timeout);
                try
                {
                    await reader.ReadLineAsync(ctsWelcome.Token);
                }
                catch (OperationCanceledException)
                {
                    _logger.LogWarning($"Timeout waiting for welcome message from {ip}:{port}");
                    return $"ER {_translator.GetError("CONNECTION_TIMEOUT")}";
                }

                await writer.WriteLineAsync(command.AsMemory(), CancellationToken.None); // Write is usually fast, but could use token too
                
                using var ctsRead = new CancellationTokenSource(_config.Timeout);
                string? response = null;
                try
                {
                    response = await reader.ReadLineAsync(ctsRead.Token);
                }
                catch (OperationCanceledException)
                {
                    _logger.LogWarning($"Response timeout from {ip}:{port}");
                    return $"ER {_translator.GetError("RESPONSE_TIMEOUT")}";
                }
                
                _logger.LogInformation($"Received response from {ip}:{port} <- {response ?? "null"}");
                return response ?? $"ER {_translator.GetError("NO_RESPONSE")}";
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Connection failed to {ip}:{port}");
                return $"ER {_translator.GetError("CONNECTION_FAILED")} {ex.Message}";
            }
        }
    }
}
