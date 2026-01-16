namespace BankNode.Translation
{
    public interface ITranslationStrategy
    {
        string GetMessage(string key);
        string GetError(string key);
    }
}
