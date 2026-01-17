using BankNode.Core.Interfaces;
using BankNode.Core.Services;
using BankNode.Core.Models;
using Moq;
using Xunit;
using System;

namespace BankNode.Tests.Unit
{
    public class AccountServiceTests
    {
        [Fact]
        public async Task CreateAccount_ShouldReturnNewAccount()
        {
            // Arrange
            var repo = new Mock<IAccountRepository>();
            repo.Setup(r => r.GetByAccountNumberAsync(It.IsAny<string>())).ReturnsAsync((Account?)null); // Always new
            repo.Setup(r => r.AddAsync(It.IsAny<Account>())).Returns(Task.CompletedTask);
            var service = new AccountService(repo.Object);

            // Act
            var account = await service.CreateAccountAsync("127.0.0.1");

            // Assert
            Assert.NotNull(account);
            Assert.Contains("/127.0.0.1", account.FullAccountNumber);
            repo.Verify(r => r.AddAsync(It.IsAny<Account>()), Times.Once);
        }

        [Fact]
        public async Task Deposit_ShouldIncreaseBalance()
        {
            // Arrange
            var account = new Account { AccountNumber = "123", Balance = 100 };
            var repo = new Mock<IAccountRepository>();
            repo.Setup(r => r.GetByAccountNumberAsync("123")).ReturnsAsync(account);
            repo.Setup(r => r.UpdateAsync(account)).Returns(Task.CompletedTask);
            var service = new AccountService(repo.Object);

            // Act
            await service.DepositAsync("123", 50);

            // Assert
            Assert.Equal(150, account.Balance);
            repo.Verify(r => r.UpdateAsync(account), Times.Once);
        }

        [Fact]
        public async Task Withdraw_ShouldThrow_WhenInsufficientFunds()
        {
            // Arrange
            var account = new Account { AccountNumber = "123", Balance = 100 };
            var repo = new Mock<IAccountRepository>();
            repo.Setup(r => r.GetByAccountNumberAsync("123")).ReturnsAsync(account);
            var service = new AccountService(repo.Object);

            // Act & Assert
            await Assert.ThrowsAsync<InvalidOperationException>(() => service.WithdrawAsync("123", 150));
        }
    }
}
