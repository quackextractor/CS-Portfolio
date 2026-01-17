using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;
using BankNode.Shared;

namespace BankNode.Network.Strategies
{
    public class BackupCommandStrategy : ICommandStrategy
    {
        private readonly IAccountRepository _repository;
        private readonly BankNode.Translation.ITranslationStrategy _translator;

        public BackupCommandStrategy(IAccountRepository repository, BankNode.Translation.ITranslationStrategy translator)
        {
            _repository = repository;
            _translator = translator;
        }

        public IEnumerable<string> SupportedCommands => new[] { "BACKUP", "RESTORE" };

        public bool CanHandle(string commandCode)
        {
            return commandCode == "BACKUP" || commandCode == "RESTORE";
        }

        public async Task<string> ExecuteAsync(string[] args)
        {
            if (args[0] == "BACKUP")
            {
                var backupPath = args.Length > 1 ? args[1] : $"backup_{DateTime.Now:yyyyMMdd_HHmmss}.json";
                await BackupAccountsAsync(backupPath);
                return $"BACKUP Created: {backupPath}";
            }
            else if (args[0] == "RESTORE")
            {
                if (args.Length < 2) return $"ER {_translator.GetError("INVALID_ARGUMENTS")}";
                
                try
                {
                    await RestoreAccountsAsync(args[1]);
                    return "RESTORE Completed";
                }
                catch (FileNotFoundException)
                {
                     return $"ER {_translator.GetError("FILE_NOT_FOUND")}";
                }
                catch (Exception ex)
                {
                    return $"ER {_translator.GetError("INTERNAL_ERROR")} {ex.Message}";
                }
            }
            
            return $"ER {_translator.GetError("UNKNOWN_COMMAND")}";
        }

        private async Task BackupAccountsAsync(string path)
        {
            var accounts = await _repository.GetAllAsync();
            var options = new JsonSerializerOptions { WriteIndented = true };
            var json = JsonSerializer.Serialize(accounts, options);
            await File.WriteAllTextAsync(path, json);
        }

        private async Task RestoreAccountsAsync(string path)
        {
            if (!File.Exists(path)) throw new FileNotFoundException(path);

            var json = await File.ReadAllTextAsync(path);
            var accounts = JsonSerializer.Deserialize<List<Account>>(json);

            if (accounts == null) return;

            // Clear existing (Inefficient but interface-compliant)
            var existing = await _repository.GetAllAsync();
            foreach (var acc in existing)
            {
                await _repository.RemoveAsync(acc.AccountNumber);
            }

            // Add new
            foreach (var acc in accounts)
            {
                await _repository.AddAsync(acc);
            }
        }
    }
}
