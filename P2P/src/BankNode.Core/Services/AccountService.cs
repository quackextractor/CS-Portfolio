using System;
using System.Threading;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;

namespace BankNode.Core.Services
{
    public class AccountService : IAccountService, IDisposable
    {
        private readonly IAccountRepository _repository;
        private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
        private readonly Random _random = new Random();

        public AccountService(IAccountRepository repository)
        {
            _repository = repository;
        }

        public Account CreateAccount(string bankIp)
        {
            _lock.EnterWriteLock();
            try
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
            finally
            {
                _lock.ExitWriteLock();
            }
        }

        public void Deposit(string accountNumber, decimal amount)
        {
            if (amount < 0) throw new ArgumentException("Amount cannot be negative.");

            _lock.EnterWriteLock();
            try
            {
                var account = _repository.GetByAccountNumber(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                account.Balance += amount;
                _repository.Update(account);
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }

        public void Withdraw(string accountNumber, decimal amount)
        {
            if (amount < 0) throw new ArgumentException("Amount cannot be negative.");

            _lock.EnterWriteLock();
            try
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
            finally
            {
                _lock.ExitWriteLock();
            }
        }

        public decimal GetBalance(string accountNumber)
        {
            _lock.EnterReadLock();
            try
            {
                var account = _repository.GetByAccountNumber(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");
                return account.Balance;
            }
            finally
            {
                _lock.ExitReadLock();
            }
        }

        public void RemoveAccount(string accountNumber)
        {
            _lock.EnterWriteLock();
            try
            {
                var account = _repository.GetByAccountNumber(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                if (account.Balance != 0)
                {
                    throw new InvalidOperationException("Cannot remove account with non-zero balance.");
                }

                _repository.Remove(accountNumber);
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }

        public decimal GetTotalBankBalance()
        {
            _lock.EnterReadLock();
            try
            {
                return _repository.GetTotalBalance();
            }
            finally
            {
                _lock.ExitReadLock();
            }
        }

        public int GetClientCount()
        {
            _lock.EnterReadLock();
            try
            {
                return _repository.GetCount();
            }
            finally
            {
                _lock.ExitReadLock();
            }
        }

        public bool AccountExists(string accountNumber)
        {
            _lock.EnterReadLock();
            try
            {
                return _repository.GetByAccountNumber(accountNumber) != null;
            }
            finally
            {
                _lock.ExitReadLock();
            }
        }

        public void Dispose()
        {
            _lock?.Dispose();
        }
    }
}
