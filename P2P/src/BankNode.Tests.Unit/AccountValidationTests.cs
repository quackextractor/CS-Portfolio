using System.Threading.Tasks;
using BankNode.Core.Interfaces;
using BankNode.Network.Strategies;
using BankNode.Shared;
using BankNode.Network;
using Moq;
using Xunit;

namespace BankNode.Tests.Unit
{
    public class AccountValidationTests
    {
        private readonly Mock<IAccountService> _mockAccountService;
        private readonly Mock<INetworkClient> _mockNetworkClient;
        private readonly Mock<BankNode.Translation.ITranslationStrategy> _mockTranslator;
        private readonly AppConfig _config;
        private readonly AccountCommandStrategy _strategy;

        public AccountValidationTests()
        {
            _mockAccountService = new Mock<IAccountService>();
            _mockNetworkClient = new Mock<INetworkClient>();
            _mockTranslator = new Mock<BankNode.Translation.ITranslationStrategy>();
            _mockTranslator.Setup(t => t.GetError(It.IsAny<string>())).Returns((string key) => key);

            _config = new AppConfig { Port = 65525 };
            _strategy = new AccountCommandStrategy(_config, _mockAccountService.Object, _mockNetworkClient.Object, _mockTranslator.Object);
        }

        [Theory]
        [InlineData("AD 9999/localhost 100", "INVALID_ACCOUNT_FORMAT")]
        [InlineData("AD 100000/localhost 100", "INVALID_ACCOUNT_FORMAT")]
        [InlineData("AD abc/localhost 100", "INVALID_ACCOUNT_FORMAT")]
        [InlineData("AW 9999/localhost 100", "INVALID_ACCOUNT_FORMAT")]
        [InlineData("AB 9999/localhost", "INVALID_ACCOUNT_FORMAT")]
        [InlineData("AR 9999/localhost", "INVALID_ACCOUNT_FORMAT")]
        public async Task ExecuteAsync_ShouldReturnError_WhenAccountNumberIsOutOfRange(string command, string expectedErrorKey)
        {
            // Arrange
            var args = command.Split(' ');

            // Act
            var result = await _strategy.ExecuteAsync(args);

            // Assert
            Assert.Contains($"ER {expectedErrorKey}", result);
        }

        [Fact]
        public async Task ExecuteAsync_ShouldSucceed_WhenAccountNumberIsInRange()
        {
            // Arrange
            var command = "AD 10000/localhost 100";
            var args = command.Split(' ');
            _mockAccountService.Setup(s => s.DepositAsync(It.IsAny<string>(), It.IsAny<decimal>())).Returns(Task.CompletedTask);

            // Act
            var result = await _strategy.ExecuteAsync(args);

            // Assert
            Assert.Equal("AD", result);
        }
    }
}
