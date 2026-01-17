using System.Collections.Generic;
using BankNode.Core.Models;

namespace BankNode.Core.Interfaces
{
    public interface IAccountRepository
    {
        Task<Account?> GetByAccountNumberAsync(string accountNumber);
        Task<IEnumerable<Account>> GetAllAsync();
        Task AddAsync(Account account);
        Task UpdateAsync(Account account);
        Task RemoveAsync(string accountNumber);
        Task<int> GetCountAsync();
        Task<decimal> GetTotalBalanceAsync();
    }
}
