using System;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;

namespace BankNode.Core.Services
{
    public class AccountService : IAccountService
    {
        private readonly IAccountRepository _repository;
        private readonly object _lock = new object();
        private readonly Random _random = new Random();

        public AccountService(IAccountRepository repository)
        {
            _repository = repository;
        }

        public Account CreateAccount(string bankIp)
        {
            lock (_lock)
            {
                string accountNumber;
                do
                {
                    accountNumber = _random.Next(10000, 100000).ToString();
                } while (_repository.GetByAccountNumber(accountNumber) != null);

                var account = new Account
                {
                    AccountNumber = accountNumber,
                    Balance = 0,
                    BankCode = bankIp
                };

                _repository.Add(account);
                return account;
            }
        }

        public void Deposit(string accountNumber, decimal amount)
        {
            if (amount < 0) throw new ArgumentException("Amount cannot be negative.");

            lock (_lock)
            {
                var account = _repository.GetByAccountNumber(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                account.Balance += amount;
                _repository.Update(account);
            }
        }

        public void Withdraw(string accountNumber, decimal amount)
        {
            if (amount < 0) throw new ArgumentException("Amount cannot be negative.");

            lock (_lock)
            {
                var account = _repository.GetByAccountNumber(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                if (account.Balance < amount)
                {
                    throw new InvalidOperationException("Insufficient funds.");
                }

                account.Balance -= amount;
                _repository.Update(account);
            }
        }

        public decimal GetBalance(string accountNumber)
        {
            var account = _repository.GetByAccountNumber(accountNumber);
            if (account == null) throw new InvalidOperationException("Account not found.");
            return account.Balance;
        }

        public void RemoveAccount(string accountNumber)
        {
            lock (_lock)
            {
                var account = _repository.GetByAccountNumber(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                if (account.Balance != 0)
                {
                    throw new InvalidOperationException("Cannot remove account with non-zero balance.");
                }

                _repository.Remove(accountNumber);
            }
        }

        public decimal GetTotalBankBalance()
        {
            return _repository.GetTotalBalance();
        }

        public int GetClientCount()
        {
            return _repository.GetCount();
        }

        public bool AccountExists(string accountNumber)
        {
            return _repository.GetByAccountNumber(accountNumber) != null;
        }
    }
}
