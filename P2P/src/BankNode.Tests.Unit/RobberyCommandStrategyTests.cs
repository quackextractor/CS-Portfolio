using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BankNode.Network;
using BankNode.Network.Strategies;
using BankNode.Shared;
using BankNode.Translation;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace BankNode.Tests.Unit
{
    public class RobberyCommandStrategyTests
    {
        private readonly Mock<INetworkClient> _mockClient;
        private readonly Mock<ITranslationStrategy> _mockTranslator;
        private readonly AppConfig _config;
        private readonly RobberyCommandStrategy _strategy;

        public RobberyCommandStrategyTests()
        {
            _mockClient = new Mock<INetworkClient>();
            _mockTranslator = new Mock<ITranslationStrategy>();
            _config = new AppConfig { NodeIp = "10.0.0.1", Port = 65525 };
            
            _strategy = new RobberyCommandStrategy(_mockClient.Object, _config, _mockTranslator.Object);
        }

        [Fact]
        public async Task ExecuteAsync_ShouldReturnError_WhenAmountIsInvalid()
        {
            // Arrange
            _mockTranslator.Setup(t => t.GetError("INVALID_AMOUNT")).Returns("Invalid amount.");

            // Act
            var result = await _strategy.ExecuteAsync(new[] { "RP", "invalid" });

            // Assert
            Assert.Contains("ER Invalid amount", result);
        }

        [Fact]
        public async Task ExecuteAsync_ShouldReturnPlan_WhenNetworkScanned()
        {
            // Arrange
            // Target: 1000.  Bank1: 600 (2 clients), Bank2: 500 (1 client). 
            // Bank2 is better density (500/1=500 vs 600/2=300). Should pick Bank2 first?
            // Density sort in code: TotalAmount / ClientCount descending.
            // Bank1: 600/2 = 300.
            // Bank2: 500/1 = 500.
            // Sorted: Bank2, Bank1.
            // Need 1000.
            // Pick Bank2 (500). Remaining 500.
            // Pick Bank1 (600). Total 1100 >= 1000. Stop.
            // Victims: Bank2, Bank1.

            ConfigureMockResponse("10.0.0.2", "600", "2"); // Bank 1
            ConfigureMockResponse("10.0.0.3", "500", "1"); // Bank 2

            // Act
            var result = await _strategy.ExecuteAsync(new[] { "RP", "1000" });

            // Assert
            Assert.StartsWith("RP", result);
            Assert.Contains("10.0.0.3", result);
            Assert.Contains("10.0.0.2", result);
        }

        private void ConfigureMockResponse(string ip, string amount, string clients)
        {
            _mockClient.Setup(c => c.SendCommandAsync(ip, It.IsAny<int>(), "BC"))
                .ReturnsAsync($"BC {ip}");
            _mockClient.Setup(c => c.SendCommandAsync(ip, It.IsAny<int>(), "BA"))
                .ReturnsAsync($"BA {amount}");
            _mockClient.Setup(c => c.SendCommandAsync(ip, It.IsAny<int>(), "BN"))
                .ReturnsAsync($"BN {clients}");
        }
    }
}
