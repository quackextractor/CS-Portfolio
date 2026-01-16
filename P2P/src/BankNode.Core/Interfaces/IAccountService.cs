using BankNode.Core.Models;
using System.Collections.Generic;

namespace BankNode.Core.Interfaces
{
    public interface IAccountService
    {
        string CreateAccount(string ip);
        void Deposit(string accountId, string ip, long amount);
        void Withdraw(string accountId, string ip, long amount);
        long GetBalance(string accountId, string ip);
        void RemoveAccount(string accountId, string ip);
        long GetTotalAmount();
        int GetClientCount();
    }
}
