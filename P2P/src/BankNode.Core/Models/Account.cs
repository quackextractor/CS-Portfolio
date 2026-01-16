namespace BankNode.Core.Models
{
    public class Account
    {
        public string AccountNumber { get; set; }
        public string BankIp { get; set; }
        public long Balance { get; set; }

        public string FullAccountId => $"{AccountNumber}/{BankIp}";
    }
}
