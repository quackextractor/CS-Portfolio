using System.Collections.Generic;
using System.Threading.Tasks;
using BankNode.Network;
using BankNode.Network.Strategies;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace BankNode.Tests.Unit
{
    public class CommandParserTests
    {
        [Fact]
        public async Task ProcessCommand_ShouldReturnError_WhenCommandIsUnknown()
        {
            // Arrange
            var strategies = new List<ICommandStrategy>();
            var logger = new Mock<ILogger<CommandParser>>();
            var translator = new Mock<BankNode.Translation.ITranslationStrategy>();
            translator.Setup(t => t.GetError("UNKNOWN_COMMAND")).Returns("Unknown command.");
            
            var parser = new CommandParser(strategies, translator.Object, logger.Object);

            // Act
            var result = await parser.ProcessCommandAsync("XYZ 123", "127.0.0.1");

            // Assert
            Assert.Contains("ER Unknown command", result);
        }

        [Fact]
        public async Task ProcessCommand_ShouldDispatchToCorrectStrategy()
        {
            // Arrange
            var mockStrategy = new Mock<ICommandStrategy>();
            mockStrategy.Setup(s => s.CanHandle("TEST")).Returns(true);
            mockStrategy.Setup(s => s.ExecuteAsync(It.IsAny<string[]>())).ReturnsAsync("TEST OK");

            var strategies = new List<ICommandStrategy> { mockStrategy.Object };
            var logger = new Mock<ILogger<CommandParser>>();
            var translator = new Mock<BankNode.Translation.ITranslationStrategy>();
            
            var parser = new CommandParser(strategies, translator.Object, logger.Object);

            // Act
            var result = await parser.ProcessCommandAsync("TEST arg1", "127.0.0.1");

            // Assert
            Assert.Equal("TEST OK", result);
            mockStrategy.Verify(s => s.ExecuteAsync(It.Is<string[]>(args => args[0] == "TEST" && args[1] == "arg1")), Times.Once);
        }
    }
}
