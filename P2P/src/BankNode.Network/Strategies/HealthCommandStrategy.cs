using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BankNode.Core.Interfaces;
using System.Diagnostics;
using System.Text.Json;

namespace BankNode.Network.Strategies
{
    public class HealthCommandStrategy : ICommandStrategy
    {
        private readonly IAccountService _accountService;

        public HealthCommandStrategy(IAccountService accountService)
        {
            _accountService = accountService;
        }

        public IEnumerable<string> SupportedCommands => new[] { "HC" };

        public bool CanHandle(string commandCode)
        {
            return commandCode == "HC";
        }

        public Task<string> ExecuteAsync(string[] args)
        {
            var health = new
            {
                Status = "OK",
                Uptime = DateTime.Now - Process.GetCurrentProcess().StartTime,
                Memory = $"{GC.GetTotalMemory(false) / 1024 / 1024}MB",
                Accounts = _accountService.GetClientCount(),
                TotalBalance = _accountService.GetTotalBankBalance()
            };

            return Task.FromResult($"HC {JsonSerializer.Serialize(health)}");
        }
    }
}
