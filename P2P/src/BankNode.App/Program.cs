using System;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;
using BankNode.Core.Services;
using BankNode.Data.Repositories;
using BankNode.Network;
using BankNode.Shared.Logging;
using BankNode.Network.Strategies;
using BankNode.Translation;
using BankNode.Translation.Strategies;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System.Net.NetworkInformation;
using System.Net.Sockets;

namespace BankNode.App
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var services = new ServiceCollection();
            ConfigureServices(services);

            var serviceProvider = services.BuildServiceProvider();

            // Load Config
            var config = serviceProvider.GetRequiredService<AppConfig>();
            config.Load();
            
            // Allow override from args: --port 65526
            if (args.Length > 1 && args[0] == "--port" && int.TryParse(args[1], out int port))
            {
                config.Port = port;
            }
            
            // Allow manual IP override: --ip 192.168.1.5
            var ipIndex = Array.IndexOf(args, "--ip");
            if (ipIndex >= 0 && ipIndex + 1 < args.Length)
            {
                config.NodeIp = args[ipIndex + 1];
            }

            var logger = serviceProvider.GetRequiredService<ILogger<Program>>();
            
            // List all available IPs for user convenience
            logger.LogInformation("Available Network Interfaces:");
            foreach (var ni in NetworkInterface.GetAllNetworkInterfaces())
            {
                if (ni.OperationalStatus == OperationalStatus.Up)
                {
                    foreach (var ua in ni.GetIPProperties().UnicastAddresses)
                    {
                        if (ua.Address.AddressFamily == AddressFamily.InterNetwork)
                        {
                            logger.LogInformation($" - {ni.Name}: {ua.Address}");
                        }
                    }
                }
            }

            logger.LogInformation($"Bank Node initializing... Advertising IP: {config.NodeIp}, Port: {config.Port}");

            var server = serviceProvider.GetRequiredService<TcpServer>();
            var cancellationTokenSource = new CancellationTokenSource();

            Console.CancelKeyPress += (s, e) =>
            {
                e.Cancel = true;
                cancellationTokenSource.Cancel();
            };

            var serverTask = server.StartAsync(cancellationTokenSource.Token);
            
            // Interactive CLI
            Console.WriteLine("Server started. Type 'HELP' for commands.");
            
            while (!cancellationTokenSource.Token.IsCancellationRequested)
            {
                var input = Console.ReadLine();
                if (string.IsNullOrWhiteSpace(input)) continue;
                
                var cmd = input.Trim().ToUpper();
                try
                {
                    switch (cmd)
                    {
                        case "EXIT":
                            logger.LogInformation("Stopping server...");
                            cancellationTokenSource.Cancel();
                            break;
                            
                        case "BN":
                            var repo = serviceProvider.GetRequiredService<IAccountRepository>();
                            logger.LogInformation($"Local Accounts: {repo.GetCount()}, Total Balance: {repo.GetTotalBalance()}");
                            break;
                            
                        case "HELP":
                            Console.WriteLine("Available Local Commands:");
                            Console.WriteLine("  EXIT - Stop the server");
                            Console.WriteLine("  BN   - Show local bank stats");
                            Console.WriteLine("  HELP - Show this help");
                            break;
                            
                        default:
                            Console.WriteLine($"Unknown local command: {cmd}");
                            break;
                    }
                }
                catch (Exception ex)
                {
                    logger.LogError(ex, "Error executing local command");
                }
            }

            try 
            {
                await serverTask;
            }
            catch (OperationCanceledException)
            {
                // Normal shutdown
            }
        }

        private static void ConfigureServices(IServiceCollection services)
        {
            // Config
            services.AddSingleton<AppConfig>();

            // Logging
            services.AddLogging(configure =>
            {
                configure.AddConsole();
                configure.AddFile("node.log");
                configure.SetMinimumLevel(LogLevel.Information);
            });

            // Core
            services.AddSingleton<IAccountRepository>(sp => 
                new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>()));
            services.AddSingleton<IAccountService, AccountService>();

            // Network
            services.AddSingleton<TcpServer>();
            services.AddSingleton<INetworkClient, NetworkClient>();
            services.AddSingleton<CommandParser>();
            services.AddSingleton<ICommandProcessor>(p => 
                new RequestLoggingDecorator(
                    p.GetRequiredService<CommandParser>(),
                    p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                ));

            // Translation
            services.AddSingleton<ITranslationStrategy, JsonFileTranslationStrategy>();
            
            // Strategies
            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>();
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
            services.AddSingleton<ICommandStrategy, HealthCommandStrategy>();
            services.AddSingleton<ICommandStrategy, LanguageCommandStrategy>();
            services.AddSingleton<ICommandStrategy, HelpCommandStrategy>();
        }
    }
}
