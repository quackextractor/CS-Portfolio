using System.Collections.Generic;
using System.Threading.Tasks;
using BankNode.Network.Strategies;
using BankNode.Translation;
using Moq;
using Xunit;

namespace BankNode.Tests.Unit
{
    public class LanguageCommandStrategyTests
    {
        private readonly Mock<ITranslationStrategy> _mockTranslator;
        private readonly LanguageCommandStrategy _strategy;

        public LanguageCommandStrategyTests()
        {
            _mockTranslator = new Mock<ITranslationStrategy>();
            _strategy = new LanguageCommandStrategy(_mockTranslator.Object);
        }

        [Fact]
        public void CanHandle_ReturnsTrueForLang()
        {
            Assert.True(_strategy.CanHandle("LANG"));
        }

        [Fact]
        public async Task ExecuteAsync_NoArgs_ListsLanguages()
        {
            // Arrange
            _mockTranslator.Setup(t => t.GetAvailableLanguages()).Returns(new List<string> { "en", "cz" });
            _mockTranslator.Setup(t => t.GetMessage("LANG_AVAILABLE")).Returns("Available");

            // Act
            var result = await _strategy.ExecuteAsync(new[] { "LANG" });

            // Assert
            Assert.Contains("Available: en, cz", result);
        }

        [Fact]
        public async Task ExecuteAsync_NoLanguagesFound_ReturnsError()
        {
             // Arrange
            _mockTranslator.Setup(t => t.GetAvailableLanguages()).Returns(new List<string>());
            _mockTranslator.Setup(t => t.GetError("LANG_NOT_FOUND")).Returns("Not found");

            // Act
            var result = await _strategy.ExecuteAsync(new[] { "LANG" });

            // Assert
            Assert.Contains("ER Not found", result);
        }

        [Fact]
        public async Task ExecuteAsync_WithLanguage_SwitchSuccess()
        {
            // Arrange
            _mockTranslator.Setup(t => t.SetLanguage("cz"));
            _mockTranslator.Setup(t => t.GetMessage("LANG_CHANGED")).Returns("Changed to");

            // Act
            var result = await _strategy.ExecuteAsync(new[] { "LANG", "cz" });

            // Assert
            _mockTranslator.Verify(t => t.SetLanguage("cz"), Times.Once);
            Assert.Contains("Changed to cz", result);
        }

        [Fact]
        public async Task ExecuteAsync_WithInvalidLanguage_ReturnsError()
        {
            // Arrange
            _mockTranslator.Setup(t => t.SetLanguage("xyz")).Throws(new System.ArgumentException());
            _mockTranslator.Setup(t => t.GetError("LANG_NOT_FOUND")).Returns("Not found");

            // Act
            var result = await _strategy.ExecuteAsync(new[] { "LANG", "xyz" });

            // Assert
            Assert.Contains("ER Not found", result);
        }
    }
}
