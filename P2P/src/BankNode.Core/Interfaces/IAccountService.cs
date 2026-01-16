using System.Collections.Generic;
using BankNode.Core.Models;

namespace BankNode.Core.Interfaces
{
    public interface IAccountService
    {
        // Core operations
        Account CreateAccount(string bankIp);
        void Deposit(string accountNumber, decimal amount);
        void Withdraw(string accountNumber, decimal amount);
        decimal GetBalance(string accountNumber);
        void RemoveAccount(string accountNumber);
        
        // Bank stats
        decimal GetTotalBankBalance();
        int GetClientCount();
        
        // Helper for validation
        bool AccountExists(string accountNumber);
    }
}
