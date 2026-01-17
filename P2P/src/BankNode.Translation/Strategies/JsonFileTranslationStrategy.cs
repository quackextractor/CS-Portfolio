using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using BankNode.Shared;

namespace BankNode.Translation.Strategies
{
    public class JsonFileTranslationStrategy : ITranslationStrategy
    {
        private readonly Dictionary<string, string> _messages = new Dictionary<string, string>();
        private readonly AppConfig _config;

        public JsonFileTranslationStrategy(AppConfig config)
        {
            _config = config;
            LoadTranslations();
        }

        public string GetMessage(string key)
        {
            return _messages.TryGetValue(key, out var value) ? value : key;
        }

        public string GetError(string key)
        {
            return _messages.TryGetValue(key, out var value) ? value : key;
        }

        public IEnumerable<string> GetAvailableLanguages()
        {
            var languagesDir = GetLanguagesDirectory();
            if (Directory.Exists(languagesDir))
            {
                return Directory.GetFiles(languagesDir, "*.json")
                                .Select(Path.GetFileNameWithoutExtension)
                                .Where(x => x != null)
                                .Select(x => x!)
                                .ToList();
            }
            return new List<string>();
        }

        public void SetLanguage(string languageCode)
        {
            var languages = GetAvailableLanguages();
            if (!languages.Contains(languageCode))
            {
                throw new ArgumentException($"Language '{languageCode}' is not available.");
            }

            _config.Language = languageCode;
            _config.Save();
            LoadTranslations(); // Reload with new language
        }

        private string? _initializationError;

        public string? GetInitializationError()
        {
            return _initializationError;
        }

        private string GetLanguagesDirectory()
        {
            var path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "languages");
            if (!Directory.Exists(path))
            {
                // Fallback to local 'languages' folder if not in base directory (e.g. dev environment)
                path = Path.Combine(Directory.GetCurrentDirectory(), "languages");
            }
            return path;
        }

        private void LoadTranslations()
        {
            _messages.Clear();
            _initializationError = null;

            var lang = _config.Language;
            var languagesDir = GetLanguagesDirectory();
            var path = Path.Combine(languagesDir, $"{lang}.json");

            if (!File.Exists(path))
            {
                // Fallback to english if configured language is missing
                _initializationError = $"Warning: Configured language '{lang}' not found. Falling back to 'en'.";
                Console.WriteLine(_initializationError);
                
                lang = "en";
                path = Path.Combine(languagesDir, $"{lang}.json");
                
                // If english is also missing, we have a bigger problem, but let's try
                if (!File.Exists(path))
                {
                    _initializationError = "Error: Language files not found. Application may not show correct text.";
                    Console.WriteLine(_initializationError);
                    return;
                }
            }

            try
            {
                var json = File.ReadAllText(path);
                var dict = JsonSerializer.Deserialize<Dictionary<string, string>>(json);
                if (dict != null)
                {
                    foreach (var kvp in dict)
                    {
                        _messages[kvp.Key] = kvp.Value;
                    }
                }
            }
            catch (Exception ex)
            {
                _initializationError = $"Error loading translations for '{lang}': {ex.Message}";
                Console.WriteLine(_initializationError);
            }
        }
    }
}
