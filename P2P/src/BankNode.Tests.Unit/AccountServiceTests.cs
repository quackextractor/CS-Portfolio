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
        public void CreateAccount_ShouldReturnNewAccount()
        {
            // Arrange
            var repo = new Mock<IAccountRepository>();
            repo.Setup(r => r.GetByAccountNumber(It.IsAny<string>())).Returns((Account?)null); // Always new
            var service = new AccountService(repo.Object);

            // Act
            var account = service.CreateAccount("127.0.0.1");

            // Assert
            Assert.NotNull(account);
            Assert.Contains("/127.0.0.1", account.FullAccountNumber);
            repo.Verify(r => r.Add(It.IsAny<Account>()), Times.Once);
        }

        [Fact]
        public void Deposit_ShouldIncreaseBalance()
        {
            // Arrange
            var account = new Account { AccountNumber = "123", Balance = 100 };
            var repo = new Mock<IAccountRepository>();
            repo.Setup(r => r.GetByAccountNumber("123")).Returns(account);
            var service = new AccountService(repo.Object);

            // Act
            service.Deposit("123", 50);

            // Assert
            Assert.Equal(150, account.Balance);
            repo.Verify(r => r.Update(account), Times.Once);
        }

        [Fact]
        public void Withdraw_ShouldThrow_WhenInsufficientFunds()
        {
            // Arrange
            var account = new Account { AccountNumber = "123", Balance = 100 };
            var repo = new Mock<IAccountRepository>();
            repo.Setup(r => r.GetByAccountNumber("123")).Returns(account);
            var service = new AccountService(repo.Object);

            // Act & Assert
            Assert.Throws<InvalidOperationException>(() => service.Withdraw("123", 150));
        }
    }
}
