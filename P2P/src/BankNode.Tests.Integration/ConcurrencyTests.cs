using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Core.Interfaces;
using BankNode.Core.Models;
using BankNode.Core.Services;
using BankNode.Data.Repositories;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace BankNode.Tests.Integration
{
    public class ConcurrencyTests
    {
        [Fact]
        public async Task AccountService_ShouldHandle_ConcurrentDeposits()
        {
            // Arrange
            var logger = Mock.Of<ILogger<FileAccountRepository>>();
            // Use a unique file for this test
            var testFile = $"concurrency_test_{Guid.NewGuid()}.json";
            using var repo = new FileAccountRepository(logger, testFile);
            using var service = new AccountService(repo);

            var account = await service.CreateAccountAsync("127.0.0.1");
            var accNum = account.AccountNumber;
            int tasksCount = 50;
            decimal depositAmount = 10;

            // Act
            var tasks = Enumerable.Range(0, tasksCount).Select(i => Task.Run(async () =>
            {
                await service.DepositAsync(accNum, depositAmount);
            }));

            await Task.WhenAll(tasks);

            // Assert
            var finalAccount = await service.GetBalanceAsync(accNum);
            Assert.Equal(tasksCount * depositAmount, finalAccount);

            // Cleanup
            if (System.IO.File.Exists(testFile)) System.IO.File.Delete(testFile);
        }

        [Fact]
        public async Task AccountService_ShouldHandle_ConcurrentReadsAndWrites()
        {
            // Arrange
            var logger = Mock.Of<ILogger<FileAccountRepository>>();
            var testFile = $"concurrency_rw_test_{Guid.NewGuid()}.json";
            using var repo = new FileAccountRepository(logger, testFile);
            using var service = new AccountService(repo);

            var account = await service.CreateAccountAsync("127.0.0.1");
            var accNum = account.AccountNumber;
            
            // Act
            var writeTask = Task.Run(async () =>
            {
                for (int i = 0; i < 50; i++)
                {
                    await service.DepositAsync(accNum, 10);
                    await Task.Delay(5);
                }
            });

            var readTask = Task.Run(async () =>
            {
                for (int i = 0; i < 50; i++)
                {
                    var balance = await service.GetBalanceAsync(accNum);
                    Assert.True(balance >= 0);
                    await Task.Delay(5);
                }
            });

            await Task.WhenAll(writeTask, readTask);

            // Assert
            var finalBalance = await service.GetBalanceAsync(accNum);
            Assert.Equal(500, finalBalance);

            // Cleanup
            if (System.IO.File.Exists(testFile)) System.IO.File.Delete(testFile);
        }
    }
}
