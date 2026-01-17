using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
        private readonly BankNode.Translation.ITranslationStrategy _translator;
        private readonly ILogger<TcpServer> _logger;
        private TcpListener? _listener;
        private SemaphoreSlim? _connectionLimiter;

        public TcpServer(AppConfig config, ICommandProcessor commandProcessor, BankNode.Translation.ITranslationStrategy translator, ILogger<TcpServer> logger)
        {
            _config = config;
            _commandProcessor = commandProcessor;
            _translator = translator;
            _logger = logger;
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            _listener = new TcpListener(IPAddress.Any, _config.Port);
            _listener.Start();
            _logger.LogInformation($"TCP Server started on port {_config.Port}");
            
            _connectionLimiter = new SemaphoreSlim(_config.MaxConcurrentConnections, _config.MaxConcurrentConnections);

            try
            {
                while (!cancellationToken.IsCancellationRequested)
                {
                    await _connectionLimiter.WaitAsync(cancellationToken);
                    
                    try 
                    {
                        var client = await _listener.AcceptTcpClientAsync(cancellationToken);
                        _ = HandleClientAsync(client, cancellationToken).ContinueWith(t => _connectionLimiter.Release());
                    }
                    catch
                    {
                        _connectionLimiter.Release();
                        throw;
                    }
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
                // Use ClientIdleTimeout for client interactions (allows longer idle time for typing)
                // Fallback to Timeout if ClientIdleTimeout is not set or valid, but AppConfig ensures it.
                stream.ReadTimeout = _config.ClientIdleTimeout; 
                stream.WriteTimeout = _config.Timeout; // Write should still be fast

                var history = new List<string>();

                try
                {
                    using (var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true))
                    using (var writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true })
                    {
                        var welcome = _translator.GetMessage("WELCOME_MESSAGE");
                        var initError = _translator.GetInitializationError();
                        if (!string.IsNullOrEmpty(initError))
                        {
                            welcome += $"\r\n{initError}";
                        }
                        await writer.WriteLineAsync(welcome);

                        string? command;
                        while ((command = await reader.ReadLineAsync()) != null)
                        {
                            if (string.IsNullOrWhiteSpace(command))
                            {
                                await writer.WriteLineAsync("");
                                continue;
                            }

                            // Command Length Validation
                            if (command.Length > 1024)
                            {
                                await writer.WriteLineAsync($"ER {_translator.GetError("INVALID_FORMAT")} (Command too long)");
                                continue;
                            }

                            if (command.Trim().Equals("EXIT", StringComparison.OrdinalIgnoreCase))
                            {
                                break;
                            }

                            // HISTORY Command
                            if (command.Trim().Equals("HISTORY", StringComparison.OrdinalIgnoreCase))
                            {
                                if (history.Count == 0)
                                {
                                    await writer.WriteLineAsync("No history.");
                                }
                                else
                                {
                                    for (int i = 0; i < history.Count; i++)
                                    {
                                        await writer.WriteLineAsync($"{i + 1}: {history[i]}");
                                    }
                                }
                                continue;
                            }

                            // EXECUTE Command
                            if (command.Trim().StartsWith("EXECUTE ", StringComparison.OrdinalIgnoreCase))
                            {
                                var path = command.Substring(8).Trim();
                                if (File.Exists(path))
                                {
                                    try 
                                    {
                                        var lines = await File.ReadAllLinesAsync(path);
                                        foreach (var line in lines)
                                        {
                                            if (string.IsNullOrWhiteSpace(line)) continue;
                                            
                                            // Process script line
                                            var scriptResponse = await ProcessCommandInternal(line, client, history);
                                            await writer.WriteLineAsync(scriptResponse);
                                        }
                                    }
                                    catch (Exception ex)
                                    {
                                         await writer.WriteLineAsync($"ER Failed to execute script: {ex.Message}");
                                    }
                                }
                                else
                                {
                                    await writer.WriteLineAsync($"ER File not found: {path}");
                                }
                                history.Add(command); // Add EXECUTE itself to history
                                continue;
                            }

                            // Normal Command Processing
                            var response = await ProcessCommandInternal(command, client, history);
                            await writer.WriteLineAsync(response);
                        }
                    }
                }
                catch (IOException ex) when (ex.InnerException is SocketException se && se.SocketErrorCode == SocketError.TimedOut)
                {
                     _logger.LogInformation("Client timed out.");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error handling client.");
                }
            }
        }

        private async Task<string> ProcessCommandInternal(string command, TcpClient client, List<string> history)
        {
             history.Add(command);
             if (history.Count > 10) history.RemoveAt(0);

             var clientEndPoint = client.Client.RemoteEndPoint as IPEndPoint;
             var clientIp = clientEndPoint?.Address.ToString() ?? "Unknown";

             return await _commandProcessor.ProcessCommandAsync(command, clientIp);
        }
    }
}
