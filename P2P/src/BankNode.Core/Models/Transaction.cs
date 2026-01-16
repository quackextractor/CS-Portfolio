using System;

namespace BankNode.Core.Models
{
    public class Transaction
    {
        public Guid Id { get; set; }
        public string FromAccount { get; set; } // Could be internal or external
        public string ToAccount { get; set; }
        public long Amount { get; set; }
        public DateTime Timestamp { get; set; }
        public string Type { get; set; } // Deposit, Withdrawal
    }
}
