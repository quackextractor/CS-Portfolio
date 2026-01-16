using System;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;
using BankNode.Core.Services;
using BankNode.Data.Repositories;
using BankNode.Data.Repositories;
using BankNode.Network;
using BankNode.Shared.Logging;
using BankNode.Network.Strategies;
using BankNode.Translation;
using BankNode.Translation.Strategies;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

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

            var logger = serviceProvider.GetRequiredService<ILogger<Program>>();
            logger.LogInformation($"Bank Node initializing... IP: {config.NodeIp}, Port: {config.Port}");

            var server = serviceProvider.GetRequiredService<TcpServer>();
            var cancellationTokenSource = new CancellationTokenSource();

            Console.CancelKeyPress += (s, e) =>
            {
                e.Cancel = true;
                cancellationTokenSource.Cancel();
            };

            await server.StartAsync(cancellationTokenSource.Token);
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
            services.AddSingleton<IAccountRepository, FileAccountRepository>();
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
            services.AddSingleton<ITranslationStrategy, CzechTranslationStrategy>();
            
            // Strategies
            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>();
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
        }
    }
}
