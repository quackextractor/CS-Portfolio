using System;

namespace BankNode.Core.Models
{
    public class Account
    {
        public string AccountNumber { get; set; } = string.Empty;
        public decimal Balance { get; set; }
        public string BankCode { get; set; } = string.Empty; // IP Address of the bank
        
        // Helper to get full identifier like 10001/10.1.2.3
        public string FullAccountNumber => $"{AccountNumber}/{BankCode}";
    }
}
