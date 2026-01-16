using System;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;
using BankNode.Core.Services;
using BankNode.Data.Repositories;
using BankNode.Network;
using BankNode.Network.Strategies;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;

namespace BankNode.Tests.Integration
{
    public class ServerIntegrationTests
    {
        private readonly int _testPort = 65530; // Use a different port or dynamic
        private readonly CancellationTokenSource _cts = new CancellationTokenSource();

        [Fact]
        public async Task Server_ShouldRespondTo_BC_Command()
        {
            // Arrange (Setup Server)
            var services = new ServiceCollection();
            ConfigureServices(services, _testPort);
            var sp = services.BuildServiceProvider();
            var server = sp.GetRequiredService<TcpServer>();
            
            var serverTask = Task.Run(() => server.StartAsync(_cts.Token));
            
            // Give server time to start
            await Task.Delay(500);

            // Act (Client)
            var client = sp.GetRequiredService<NetworkClient>();
            var response = await client.SendCommandAsync("127.0.0.1", _testPort, "BC");

            // Cleanup
            _cts.Cancel();
            try { await serverTask; } catch { }

            // Assert
            Assert.Contains("BC 127.0.0.1", response);
        }

        [Fact]
        public async Task Server_ShouldCreateAccount()
        {
            // Arrange
            var port = 65531;
            var services = new ServiceCollection();
            ConfigureServices(services, port);
            var sp = services.BuildServiceProvider();
            var server = sp.GetRequiredService<TcpServer>();

            var serverTask = Task.Run(() => server.StartAsync(_cts.Token));
            await Task.Delay(500);

            // Act
            var client = sp.GetRequiredService<NetworkClient>();
            var response = await client.SendCommandAsync("127.0.0.1", port, "AC");

            // Cleanup
            _cts.Cancel();
            try { await serverTask; } catch { }

            // Assert
            Assert.StartsWith("AC", response);
            Assert.Contains("/", response);
        }

        private void ConfigureServices(IServiceCollection services, int port)
        {
            var config = new AppConfig { Port = port, NodeIp = "127.0.0.1" };
            services.AddSingleton(config);

            services.AddLogging(configure => configure.AddConsole());
            
            // Use in-memory repo logic if possible? No, we used FileAccountRepository.
            // We should use a different file per test or transient repo to avoid collisions.
            // But FileAccountRepository takes a path. We can inject a test-specific path.
            services.AddSingleton<IAccountRepository>(new FileAccountRepository($"test_accounts_{port}.json"));
            services.AddSingleton<IAccountService, AccountService>();

            services.AddSingleton<IAccountRepository>(new FileAccountRepository($"test_accounts_{port}.json"));
            services.AddSingleton<IAccountService, AccountService>();

            services.AddSingleton<TcpServer>();
            services.AddSingleton<NetworkClient>();
            services.AddSingleton<CommandParser>();

            // Translation
            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.CzechTranslationStrategy>();

            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>();
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
        }
    }
}
