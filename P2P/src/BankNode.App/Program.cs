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
            var logger = serviceProvider.GetRequiredService<ILogger<Program>>();

            // Load Config
            var config = serviceProvider.GetRequiredService<AppConfig>();
            try 
            {
                config.Load();
            }
            catch (Exception ex)
            {
                logger.LogError($"Configuration Error: {ex.Message}");
                return;
            }
            
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
                            var count = await repo.GetCountAsync();
                            var balance = await repo.GetTotalBalanceAsync();
                            logger.LogInformation($"Local Accounts: {count}, Total Balance: {balance}");
                            break;

                        case "LOG":
                            var switcher = serviceProvider.GetRequiredService<LogLevelSwitch>();
                            if (switcher.MinimumLevel == LogLevel.Information)
                            {
                                switcher.MinimumLevel = LogLevel.Debug;
                                logger.LogInformation("Log Level set to DEBUG");
                            }
                            else
                            {
                                switcher.MinimumLevel = LogLevel.Information;
                                logger.LogInformation("Log Level set to INFO");
                            }
                            break;
                            
                        case "HELP":
                            Console.WriteLine("Available Local Commands:");
                            Console.WriteLine("  EXIT - Stop the server");
                            Console.WriteLine("  BN   - Show local bank stats");
                            Console.WriteLine("  LOG  - Toggle logging verbosity (INFO/DEBUG)");
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
            var logLevelSwitch = new LogLevelSwitch();
            services.AddSingleton(logLevelSwitch);
            
            services.AddLogging(configure =>
            {
                configure.AddConsole();
                configure.AddFile("node.log");
                configure.SetMinimumLevel(LogLevel.Trace); // Allow all, filter with switch
                configure.AddFilter((provider, category, level) => level >= logLevelSwitch.MinimumLevel);
            });

            // Core
            services.AddSingleton<IAccountRepository>(sp => 
                new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>()));
            services.AddSingleton<IAccountService, AccountService>();

            // Network
            services.AddSingleton<TcpServer>();
            // Use Connection Pooled Client for better performance
            services.AddSingleton<INetworkClient, ConnectionPooledNetworkClient>();
            services.AddSingleton<CommandParser>();
            services.AddSingleton<ICommandProcessor>(p => 
                new BankNode.App.Decorators.MetricsDecorator( // Metrics
                        new BankNode.App.Decorators.RateLimitingDecorator( // Rate Limit
                            new RequestLoggingDecorator( // Logging
                                p.GetRequiredService<CommandParser>(),
                                p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                            ),
                            p.GetRequiredService<ILogger<BankNode.App.Decorators.RateLimitingDecorator>>(),
                            p.GetRequiredService<AppConfig>()
                        )
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
            services.AddSingleton<ICommandStrategy, BackupCommandStrategy>();
        }
    }

    public class LogLevelSwitch
    {
        public LogLevel MinimumLevel { get; set; } = LogLevel.Information;
    }
}
