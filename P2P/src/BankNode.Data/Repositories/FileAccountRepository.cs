using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;

namespace BankNode.Data.Repositories
{
    public class FileAccountRepository : IAccountRepository
    {
        private readonly string _filePath;
        private List<Account> _accounts;
        private readonly object _lock = new object();

        public FileAccountRepository(string filePath = "accounts.json")
        {
            _filePath = filePath;
            _accounts = LoadAccounts();
        }

        private List<Account> LoadAccounts()
        {
            if (!File.Exists(_filePath))
            {
                return new List<Account>();
            }

            try
            {
                var json = File.ReadAllText(_filePath);
                return JsonSerializer.Deserialize<List<Account>>(json) ?? new List<Account>();
            }
            catch
            {
                return new List<Account>();
            }
        }

        private void SaveAccounts()
        {
            var json = JsonSerializer.Serialize(_accounts, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_filePath, json);
        }

        public Account? GetByAccountNumber(string accountNumber)
        {
            lock (_lock)
            {
                return _accounts.FirstOrDefault(a => a.AccountNumber == accountNumber);
            }
        }

        public IEnumerable<Account> GetAll()
        {
            lock (_lock)
            {
                return _accounts.ToList(); // Return copy
            }
        }

        public void Add(Account account)
        {
            lock (_lock)
            {
                if (_accounts.Any(a => a.AccountNumber == account.AccountNumber))
                {
                    throw new InvalidOperationException("Account already exists.");
                }
                _accounts.Add(account);
                SaveAccounts();
            }
        }

        public void Update(Account account)
        {
            lock (_lock)
            {
                var index = _accounts.FindIndex(a => a.AccountNumber == account.AccountNumber);
                if (index != -1)
                {
                    _accounts[index] = account;
                    SaveAccounts();
                }
            }
        }

        public void Remove(string accountNumber)
        {
            lock (_lock)
            {
                var account = _accounts.FirstOrDefault(a => a.AccountNumber == accountNumber);
                if (account != null)
                {
                    _accounts.Remove(account);
                    SaveAccounts();
                }
            }
        }

        public int GetCount()
        {
            lock (_lock)
            {
                return _accounts.Count;
            }
        }

        public decimal GetTotalBalance()
        {
            lock (_lock)
            {
                return _accounts.Sum(a => a.Balance);
            }
        }
    }
}
