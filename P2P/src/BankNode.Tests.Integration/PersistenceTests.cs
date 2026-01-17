using System;
using System.IO;
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
    public class PersistenceTests
    {
        private readonly int _port = 65530;
        
        [Fact]
        public async Task Data_ShouldPersist_BetweenRestarts()
        {
            // Arrange - Files
            var testFile = "persist_test.json";
            TestHelpers.EnsureLanguageFile();
            if (File.Exists(testFile)) File.Delete(testFile);

            // 1. Start Server A, Create Account, Deposit
            string accountNum = "";
            {
                var cts = new CancellationTokenSource();
                var services = CreateServices(_port, testFile);
                var sp = services.BuildServiceProvider();
                var server = sp.GetRequiredService<TcpServer>();
                var serverTask = server.StartAsync(cts.Token);
                await Task.Delay(2000); // Wait for start

                var client = sp.GetRequiredService<INetworkClient>();
                
                // Create
                var resAC = await client.SendCommandAsync("127.0.0.1", _port, "AC");
                Assert.StartsWith("AC", resAC);
                accountNum = resAC.Split(' ')[1]; // 10000/127.0.0.1

                // Deposit 500
                var resAD = await client.SendCommandAsync("127.0.0.1", _port, $"AD {accountNum} 500");
                Assert.StartsWith("AD", resAD);

                // Stop
                cts.Cancel();
                try { await serverTask; } catch { }
            }

            // 2. Start Server A AGAIN (Same file)
            {
                var cts = new CancellationTokenSource();
                var services = CreateServices(_port, testFile); // Same file
                var sp = services.BuildServiceProvider();
                var server = sp.GetRequiredService<TcpServer>();
                var serverTask = server.StartAsync(cts.Token);
                await Task.Delay(2000);

                var client = sp.GetRequiredService<INetworkClient>();

                // Check Balance
                var resAB = await client.SendCommandAsync("127.0.0.1", _port, $"AB {accountNum}");
                
                // Stop
                cts.Cancel();
                try { await serverTask; } catch { }

                // Assert
                Assert.Contains("AB 500", resAB);
            }

            // Cleanup
            if (File.Exists(testFile)) File.Delete(testFile);
        }

        private IServiceCollection CreateServices(int port, string filePath)
        {
            var services = new ServiceCollection();
            var config = new AppConfig { Port = port, NodeIp = "127.0.0.1", Language = "en" };
            services.AddSingleton(config);
            services.AddLogging(c => c.AddConsole());

            services.AddSingleton<IAccountRepository>(sp => 
                new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), filePath));
            services.AddSingleton<IAccountService, AccountService>();
            
            services.AddSingleton<TcpServer>();
            services.AddSingleton<INetworkClient, NetworkClient>();
            services.AddSingleton<CommandParser>();
            // Use Parser directly as Processor for simplicity in this specific test or verify RequestLoggingDecorator if needed
            // Let's use RequestLoggingDecorator to match prod
             services.AddSingleton<ICommandProcessor>(p => 
                new RequestLoggingDecorator(
                    p.GetRequiredService<CommandParser>(),
                    p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                ));

            // Translation
            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.JsonFileTranslationStrategy>();

            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>();
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
            
            return services;
        }
    }
}
