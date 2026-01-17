namespace BankNode.Translation
{
    public interface ITranslationStrategy
    {
        string GetMessage(string key);
        string GetError(string key);
        System.Collections.Generic.IEnumerable<string> GetAvailableLanguages();
        void SetLanguage(string languageCode);
        string? GetInitializationError();
    }
}
