using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;
using BankNode.Shared.IO;
using Microsoft.Extensions.Logging;

namespace BankNode.Data.Repositories
{
    public class FileAccountRepository : IAccountRepository, IDisposable
    {
        private readonly ILogger<FileAccountRepository> _logger;
        private readonly string _filePath;
        private List<Account> _accounts;
        private readonly SemaphoreSlim _semaphore = new SemaphoreSlim(1, 1);

        public FileAccountRepository(ILogger<FileAccountRepository> logger, string filePath = "accounts.json")
        {
            _logger = logger;
            _filePath = filePath;
            _accounts = LoadAccounts();
        }

        private List<Account> LoadAccounts()
        {
            var accounts = new List<Account>();
            // Using existing synchronous iterator for startup
            var iterator = new FileChunkIterator(_filePath);

            foreach (var line in iterator.ReadChuncked())
            {
                try
                {
                    var account = JsonSerializer.Deserialize<Account>(line);
                    if (account != null)
                    {
                        accounts.Add(account);
                    }
                }
                catch (JsonException ex)
                {
                    _logger.LogWarning("Malformed account line skipped in {FilePath}: {Message}", _filePath, ex.Message);
                }
            }
            return accounts;
        }

        private async Task SaveAccountsAsync()
        {
            var tempPath = _filePath + ".tmp";
            
            try 
            {
                using (var stream = new FileStream(tempPath, FileMode.Create, FileAccess.Write, FileShare.None, 4096, useAsync: true))
                using (var writer = new StreamWriter(stream))
                {
                    foreach (var account in _accounts)
                    {
                        var json = JsonSerializer.Serialize(account);
                        await writer.WriteLineAsync(json);
                    }
                }

                // Atomic replacement
                if (File.Exists(_filePath)) File.Delete(_filePath);
                File.Move(tempPath, _filePath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to save accounts to {FilePath}", _filePath);
                throw;
            }
        }

        public async Task<Account?> GetByAccountNumberAsync(string accountNumber)
        {
            await _semaphore.WaitAsync();
            try
            {
                return _accounts.FirstOrDefault(a => a.AccountNumber == accountNumber);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<IEnumerable<Account>> GetAllAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                return _accounts.ToList(); // Return copy
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task AddAsync(Account account)
        {
            await _semaphore.WaitAsync();
            try
            {
                if (_accounts.Any(a => a.AccountNumber == account.AccountNumber))
                {
                    throw new InvalidOperationException("Account already exists.");
                }
                _accounts.Add(account);
                await SaveAccountsAsync();
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task UpdateAsync(Account account)
        {
            await _semaphore.WaitAsync();
            try
            {
                var index = _accounts.FindIndex(a => a.AccountNumber == account.AccountNumber);
                if (index != -1)
                {
                    _accounts[index] = account;
                    await SaveAccountsAsync();
                }
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task RemoveAsync(string accountNumber)
        {
            await _semaphore.WaitAsync();
            try
            {
                var account = _accounts.FirstOrDefault(a => a.AccountNumber == accountNumber);
                if (account != null)
                {
                    _accounts.Remove(account);
                    await SaveAccountsAsync();
                }
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<int> GetCountAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                return _accounts.Count;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<decimal> GetTotalBalanceAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                return _accounts.Sum(a => a.Balance);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public void Dispose()
        {
            _semaphore?.Dispose();
        }
    }
}
