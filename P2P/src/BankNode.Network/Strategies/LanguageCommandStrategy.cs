using System;
using System.Linq;
using System.Threading.Tasks;
using BankNode.Translation;

namespace BankNode.Network.Strategies
{
    public class LanguageCommandStrategy : ICommandStrategy
    {
        private readonly ITranslationStrategy _translator;

        public LanguageCommandStrategy(ITranslationStrategy translator)
        {
            _translator = translator;
        }

        public System.Collections.Generic.IEnumerable<string> SupportedCommands => new[] { "LANG" };

        public bool CanHandle(string commandCode)
        {
            return commandCode == "LANG";
        }

        public Task<string> ExecuteAsync(string[] args)
        {
            try
            {
                if (args.Length == 1)
                {
                    // List available languages
                    var languages = _translator.GetAvailableLanguages();
                    if (!languages.Any())
                    {
                        return Task.FromResult($"ER {_translator.GetError("LANG_NOT_FOUND")}");
                    }
                    var langList = string.Join(", ", languages);
                    return Task.FromResult($"{_translator.GetMessage("LANG_AVAILABLE")}: {langList}");
                }
                else if (args.Length == 2)
                {
                    // Switch language
                    var newLang = args[1].ToLowerInvariant();
                    try
                    {
                        _translator.SetLanguage(newLang);
                        return Task.FromResult($"{_translator.GetMessage("LANG_CHANGED")} {newLang}");
                    }
                    catch (ArgumentException)
                    {
                        return Task.FromResult($"ER {_translator.GetError("LANG_NOT_FOUND")}");
                    }
                    catch (Exception ex)
                    {
                        return Task.FromResult($"ER {_translator.GetError("LANG_UPDATE_ERROR")}: {ex.Message}");
                    }
                }
                else
                {
                    return Task.FromResult($"ER {_translator.GetError("INVALID_FORMAT")}");
                }
            }
            catch (Exception ex)
            {
                return Task.FromResult($"ER {ex.Message}");
            }
        }
    }
}
