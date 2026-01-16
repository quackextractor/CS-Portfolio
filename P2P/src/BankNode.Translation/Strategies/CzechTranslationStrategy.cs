namespace BankNode.Translation.Strategies
{
    public class CzechTranslationStrategy : ITranslationStrategy
    {
        public string GetMessage(string key) => $"CZ_MSG_{key}";
        public string GetError(string key) => $"CZ_ERR_{key}";
    }
}
