using BankNode.Core.Models;
using System.Collections.Generic;

namespace BankNode.Data.Repositories
{
    public interface IAccountRepository
    {
        Account GetByNumber(string accountNumber);
        void Save(Account account);
        void Delete(string accountNumber);
        IEnumerable<Account> GetAll();
        long GetTotalBalance();
        int Count();
    }
}
