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
using Moq;
using Xunit;

namespace BankNode.Tests.Integration
{
    public class ProxyIntegrationTests
    {
        private readonly int _port = 65533;
        
        [Fact]
        public async Task Server_ShouldProxy_Command_To_Remote_Ip()
        {
            // Arrange
            var services = new ServiceCollection();
            TestHelpers.EnsureLanguageFile();
            var config = new AppConfig { Port = _port, NodeIp = "127.0.0.1", Language = "cs" };
            services.AddSingleton(config);
            services.AddLogging(c => c.AddConsole());

            // Mock implementation to avoid actual networking but verify the Call
            var mockClient = new Mock<INetworkClient>();
            mockClient.Setup(c => c.SendCommandAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<string>()))
                      .ReturnsAsync("AD"); // Simulate remote success

            services.AddSingleton<INetworkClient>(mockClient.Object);
            
            services.AddSingleton<IAccountRepository>(sp => 
                new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), "proxy_test.json"));
            services.AddSingleton<IAccountService, AccountService>();
            
            services.AddSingleton<TcpServer>();
            services.AddSingleton<CommandParser>();
             services.AddSingleton<ICommandProcessor>(p => 
                new RequestLoggingDecorator(
                    p.GetRequiredService<CommandParser>(),
                    p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                ));

            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.JsonFileTranslationStrategy>();

            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>(); // This contains the logic: IsRemote -> SendCommandAsync
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
            
            var sp = services.BuildServiceProvider();
            var server = sp.GetRequiredService<TcpServer>();
            var cts = new CancellationTokenSource();
            var serverTask = server.StartAsync(cts.Token);
            await Task.Delay(500);

            // Act - We need a REAL client to talk to THIS server
            // We can't use the mockClient here because that's what the SERVER uses to talk to Others.
            // We need a separate client to talk to the server.
            var translator = sp.GetRequiredService<BankNode.Translation.ITranslationStrategy>();
            var realClient = new NetworkClient(new AppConfig(), sp.GetRequiredService<ILogger<NetworkClient>>(), translator); // config doesn't matter for client send
            
            // Send a command destined for 127.0.0.2 (Remote)
            var targetIp = "127.0.0.2";
            var response = await realClient.SendCommandAsync("127.0.0.1", _port, $"AD 10001/{targetIp} 500");

            // Cleanup
            cts.Cancel();
            try { await serverTask; } catch { }

            // Assert
            Assert.Contains("AD", response);
            
            // Verify the server tried to contact 127.0.0.2
            mockClient.Verify(x => x.SendCommandAsync(targetIp, _port, $"AD 10001/{targetIp} 500"), Times.Once);
        }
    }
}
