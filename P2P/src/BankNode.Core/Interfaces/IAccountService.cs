using System.Collections.Generic;
using BankNode.Core.Models;

namespace BankNode.Core.Interfaces
{
    public interface IAccountService
    {
        // Core operations
        Task<Account> CreateAccountAsync(string bankIp);
        Task DepositAsync(string accountNumber, decimal amount);
        Task WithdrawAsync(string accountNumber, decimal amount);
        Task<decimal> GetBalanceAsync(string accountNumber);
        Task RemoveAccountAsync(string accountNumber);
        
        // Bank stats
        Task<decimal> GetTotalBankBalanceAsync();
        Task<int> GetClientCountAsync();
        
        // Helper for validation
        Task<bool> AccountExistsAsync(string accountNumber);
    }
}
