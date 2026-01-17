using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using Microsoft.Extensions.Logging;

namespace BankNode.Network
{
    public class ConnectionPooledNetworkClient : INetworkClient, IDisposable
    {
        private readonly AppConfig _config;
        private readonly ILogger<ConnectionPooledNetworkClient> _logger;
        private readonly BankNode.Translation.ITranslationStrategy _translator;
        private readonly ConcurrentDictionary<string, EndpointConnection> _connections = new();

        public ConnectionPooledNetworkClient(AppConfig config, ILogger<ConnectionPooledNetworkClient> logger, BankNode.Translation.ITranslationStrategy translator)
        {
            _config = config;
            _logger = logger;
            _translator = translator;
        }

        public async Task<string> SendCommandAsync(string ip, int port, string command)
        {
            var key = $"{ip}:{port}";
            var connection = _connections.GetOrAdd(key, _ => new EndpointConnection(ip, port, _config, _logger, _translator));
            return await connection.SendCommandAsync(command);
        }

        public void Dispose()
        {
            foreach (var conn in _connections.Values)
            {
                conn.Dispose();
            }
            _connections.Clear();
        }

        private class EndpointConnection : IDisposable
        {
            private readonly string _ip;
            private readonly int _port;
            private readonly AppConfig _config;
            private readonly ILogger _logger;
            private readonly BankNode.Translation.ITranslationStrategy _translator;
            
            private TcpClient? _client;
            private StreamWriter? _writer;
            private StreamReader? _reader;
            private readonly SemaphoreSlim _lock = new(1, 1);

            public EndpointConnection(string ip, int port, AppConfig config, ILogger logger, BankNode.Translation.ITranslationStrategy translator)
            {
                _ip = ip;
                _port = port;
                _config = config;
                _logger = logger;
                _translator = translator;
            }

            public async Task<string> SendCommandAsync(string command)
            {
                await _lock.WaitAsync();
                try
                {
                    if (!IsConnected())
                    {
                        await ConnectAsync();
                    }

                    try
                    {
                        // Send command
                        await _writer!.WriteLineAsync(command.AsMemory(), CancellationToken.None);
                        
                        // Read response
                        using var cts = new CancellationTokenSource(_config.Timeout);
                        var response = await _reader!.ReadLineAsync(cts.Token);

                        if (response == null)
                        {
                            // Connection closed by server?
                            DisposeClient();
                            return $"ER {_translator.GetError("NO_RESPONSE")}";
                        }
                        
                        return response;
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Communication error with {Ip}:{Port}, resetting connection.", _ip, _port);
                        DisposeClient();
                        return $"ER {_translator.GetError("CONNECTION_FAILED")}";
                    }
                }
                catch (Exception ex)
                {
                     _logger.LogError(ex, "Failed to send command to {Ip}:{Port}", _ip, _port);
                     return $"ER {_translator.GetError("CONNECTION_FAILED")}";
                }
                finally
                {
                    _lock.Release();
                }
            }

            private bool IsConnected()
            {
                return _client != null && _client.Connected;
            }

            private async Task ConnectAsync()
            {
                DisposeClient(); // Ensure clean state

                _client = new TcpClient();
                using var cts = new CancellationTokenSource(_config.Timeout);
                await _client.ConnectAsync(_ip, _port, cts.Token);

                var stream = _client.GetStream();
                stream.ReadTimeout = _config.Timeout;
                stream.WriteTimeout = _config.Timeout;

                _writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true };
                _reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true);

                // Consume welcome message
                using var ctsWelcome = new CancellationTokenSource(_config.Timeout);
                await _reader.ReadLineAsync(ctsWelcome.Token);
            }

            private void DisposeClient()
            {
                try { _writer?.Dispose(); } catch {}
                try { _reader?.Dispose(); } catch {}
                try { _client?.Close(); _client?.Dispose(); } catch {}
                _client = null;
                _writer = null;
                _reader = null;
            }

            public void Dispose()
            {
                _lock.Wait(); // Ensure we don't dispose while in use if possible, or just force it
                try 
                {
                    DisposeClient();
                }
                finally
                {
                    _lock.Dispose();
                }
            }
        }
    }
}
