using System.Collections.Generic;
using BankNode.Core.Models;

namespace BankNode.Core.Interfaces
{
    public interface IAccountRepository
    {
        Account? GetByAccountNumber(string accountNumber);
        IEnumerable<Account> GetAll();
        void Add(Account account);
        void Update(Account account);
        void Remove(string accountNumber);
        int GetCount();
        decimal GetTotalBalance();
    }
}
