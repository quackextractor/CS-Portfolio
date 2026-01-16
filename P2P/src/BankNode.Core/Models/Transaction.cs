using System;

namespace BankNode.Core.Models
{
    public class Transaction
    {
        public Guid Id { get; set; }
        public string FromAccount { get; set; } = string.Empty; // Could be internal or external
        public string ToAccount { get; set; } = string.Empty;
        public long Amount { get; set; }
        public DateTime Timestamp { get; set; }
        public string Type { get; set; } = string.Empty; // Deposit, Withdrawal
    }
}
