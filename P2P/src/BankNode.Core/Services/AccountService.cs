using System;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;

namespace BankNode.Core.Services
{
    public class AccountService : IAccountService, IDisposable
    {
        private readonly IAccountRepository _repository;
        private readonly SemaphoreSlim _semaphore = new SemaphoreSlim(1, 1);
        private readonly Random _random = new Random();

        public AccountService(IAccountRepository repository)
        {
            _repository = repository;
        }

        public async Task<Account> CreateAccountAsync(string bankIp)
        {
            await _semaphore.WaitAsync();
            try
            {
                string accountNumber;
                do
                {
                    accountNumber = _random.Next(10000, 100000).ToString();
                } while (await _repository.GetByAccountNumberAsync(accountNumber) != null);

                var account = new Account
                {
                    AccountNumber = accountNumber,
                    Balance = 0,
                    BankCode = bankIp
                };

                await _repository.AddAsync(account);
                return account;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task DepositAsync(string accountNumber, decimal amount)
        {
            if (amount < 0) throw new ArgumentException("Amount cannot be negative.");

            await _semaphore.WaitAsync();
            try
            {
                var account = await _repository.GetByAccountNumberAsync(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                account.Balance += amount;
                await _repository.UpdateAsync(account);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task WithdrawAsync(string accountNumber, decimal amount)
        {
            if (amount < 0) throw new ArgumentException("Amount cannot be negative.");

            await _semaphore.WaitAsync();
            try
            {
                var account = await _repository.GetByAccountNumberAsync(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                if (account.Balance < amount)
                {
                    throw new InvalidOperationException("Insufficient funds.");
                }

                account.Balance -= amount;
                await _repository.UpdateAsync(account);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<decimal> GetBalanceAsync(string accountNumber)
        {
            // No lock needed, repo is thread safe for single reads
            var account = await _repository.GetByAccountNumberAsync(accountNumber);
            if (account == null) throw new InvalidOperationException("Account not found.");
            return account.Balance;
        }

        public async Task RemoveAccountAsync(string accountNumber)
        {
            await _semaphore.WaitAsync();
            try
            {
                var account = await _repository.GetByAccountNumberAsync(accountNumber);
                if (account == null) throw new InvalidOperationException("Account not found.");

                if (account.Balance != 0)
                {
                    throw new InvalidOperationException("Cannot remove account with non-zero balance.");
                }

                await _repository.RemoveAsync(accountNumber);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<decimal> GetTotalBankBalanceAsync()
        {
            return await _repository.GetTotalBalanceAsync();
        }

        public async Task<int> GetClientCountAsync()
        {
            return await _repository.GetCountAsync();
        }

        public async Task<bool> AccountExistsAsync(string accountNumber)
        {
            return await _repository.GetByAccountNumberAsync(accountNumber) != null;
        }

        public void Dispose()
        {
            _semaphore?.Dispose();
        }
    }
}
