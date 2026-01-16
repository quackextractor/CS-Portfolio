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

        private void LoadTranslations()
        {
            var lang = _config.Language;
            var path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "languages", $"{lang}.json");

            if (!File.Exists(path))
            {
                // Try fallback to 'languages' folder in current directory if not in base
                path = Path.Combine("languages", $"{lang}.json");
            }

            if (File.Exists(path))
            {
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
                    Console.WriteLine($"Error loading translations: {ex.Message}");
                }
            }
            else
            {
                Console.WriteLine($"Warning: Translation file not found at {path}");
            }
        }

        public string GetMessage(string key)
        {
            return _messages.TryGetValue(key, out var value) ? value : key;
        }

        public string GetError(string key)
        {
            return _messages.TryGetValue(key, out var value) ? value : key;
        }
    }
}
