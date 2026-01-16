using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
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
                var connectTask = client.ConnectAsync(ip, port);
                
                if (await Task.WhenAny(connectTask, Task.Delay(_config.Timeout)) != connectTask)
                {
                    _logger.LogWarning($"Connection timeout to {ip}:{port}");
                     return $"ER {_translator.GetError("CONNECTION_TIMEOUT")}";
                }
                await connectTask;

                using var stream = client.GetStream();
                stream.ReadTimeout = _config.Timeout;
                stream.WriteTimeout = _config.Timeout;

                using var writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true };
                using var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true);

                // Consume welcome message
                var welcomeTask = reader.ReadLineAsync();
                if (await Task.WhenAny(welcomeTask, Task.Delay(_config.Timeout)) != welcomeTask)
                {
                    _logger.LogWarning($"Timeout waiting for welcome message from {ip}:{port}");
                    return $"ER {_translator.GetError("CONNECTION_TIMEOUT")}";
                }

                await writer.WriteLineAsync(command);
                
                var readTask = reader.ReadLineAsync();
                if (await Task.WhenAny(readTask, Task.Delay(_config.Timeout)) != readTask)
                {
                    _logger.LogWarning($"Response timeout from {ip}:{port}");
                    return $"ER {_translator.GetError("RESPONSE_TIMEOUT")}";
                }
                
                var response = await readTask;
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
