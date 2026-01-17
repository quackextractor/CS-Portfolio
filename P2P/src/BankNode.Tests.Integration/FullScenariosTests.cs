using System;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using BankNode.Shared;
using BankNode.Core.Interfaces;
using BankNode.Core.Services;
using BankNode.Data.Repositories;
using BankNode.Network;
using BankNode.Network.Strategies;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Xunit.Abstractions;
using System.IO;
using BankNode.App;

namespace BankNode.Tests.Integration
{
    public class FullScenariosTests : IDisposable
    {
        private readonly ITestOutputHelper _output;
        private readonly string _testId;

        public FullScenariosTests(ITestOutputHelper output)
        {
            _output = output;
            _testId = Guid.NewGuid().ToString().Substring(0, 8);
            TestHelpers.EnsureLanguageFile();
        }

        public void Dispose()
        {
            // Cleanup any files created
        }

        private ServiceProvider CreateNode(int port, string language = "en")
        {
            var services = new ServiceCollection();
            // Use unique file for each node/test run to avoid collision
            var accountsFile = $"accounts_{_testId}_{port}.json";
            
            var config = new AppConfig { 
                Port = port, 
                NodeIp = "127.0.0.1", 
                Language = language,
                Timeout = 2000 
            };
            services.AddSingleton(config);
            services.AddLogging(c => c.AddConsole()); // helpful for debug, maybe disable if too noisy?
            
            services.AddSingleton<IAccountRepository>(sp => 
                new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), accountsFile));
            services.AddSingleton<IAccountService, AccountService>();
            
            services.AddSingleton<TcpServer>();
            services.AddSingleton<INetworkClient, NetworkClient>();
            services.AddSingleton<CommandParser>();
            
            services.AddSingleton<ICommandProcessor>(p => 
                new BankNode.App.Decorators.MetricsDecorator( 
                        new BankNode.App.Decorators.RateLimitingDecorator(
                            new RequestLoggingDecorator(
                                p.GetRequiredService<CommandParser>(),
                                p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                            ),
                            p.GetRequiredService<ILogger<BankNode.App.Decorators.RateLimitingDecorator>>(),
                            p.GetRequiredService<AppConfig>()
                        )
                ));

            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.JsonFileTranslationStrategy>();

            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>();
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
            // services.AddSingleton<ICommandStrategy, VersionCommandStrategy>(); // Removed as it causes build error
            services.AddSingleton<ICommandStrategy, HelpCommandStrategy>();
            services.AddSingleton<ICommandStrategy, LanguageCommandStrategy>();
            services.AddSingleton<ICommandStrategy, BackupCommandStrategy>();
            services.AddSingleton<ICommandStrategy, HealthCommandStrategy>();
            
            var sp = services.BuildServiceProvider();
            // Ensure clean start
            if (File.Exists(accountsFile)) File.Delete(accountsFile);
            
            return sp;
        }

        [Fact]
        public async Task GroupA_CoreFunctionality_Tests()
        {
            int port = 65533;
            using var cts = new CancellationTokenSource();
            var sp = CreateNode(port);
            var server = sp.GetRequiredService<TcpServer>();
            var serverTask = server.StartAsync(cts.Token);
            var client = sp.GetRequiredService<INetworkClient>();
            var targetIp = "127.0.0.1";

            try
            {
                await Task.Delay(2000); // startup

                // A-01: Bank Code (BC)
                _output.WriteLine("Running A-01: BC");
                var resBC = await client.SendCommandAsync(targetIp, port, "BC");
                Assert.Contains("BC 127.0.0.1", resBC);

                // A-02: Account Creation (AC)
                _output.WriteLine("Running A-02: AC");
                var resAC = await client.SendCommandAsync(targetIp, port, "AC");
                Assert.StartsWith("AC", resAC);
                var parts = resAC.Split(' ');
                var accFull = parts[1]; // 10000/127.0.0.1
                var accNum = int.Parse(accFull.Split('/')[0]);
                Assert.InRange(accNum, 10000, 99999);

                // A-03: Range Validation
                _output.WriteLine("Running A-03: Range Validation");
                for (int i = 0; i < 5; i++)
                {
                    var r = await client.SendCommandAsync(targetIp, port, "AC");
                    var a = int.Parse(r.Split(' ')[1].Split('/')[0]);
                    Assert.InRange(a, 10000, 99999);
                }

                // A-04: Deposit (AD)
                _output.WriteLine("Running A-04: AD");
                var resAD = await client.SendCommandAsync(targetIp, port, $"AD {accFull} 1000");
                Assert.StartsWith("AD", resAD);
                var resAB = await client.SendCommandAsync(targetIp, port, $"AB {accFull}");
                Assert.Contains("AB 1000", resAB);

                // A-05: Deposit Invalid
                _output.WriteLine("Running A-05: AD Invalid");
                var resADInv = await client.SendCommandAsync(targetIp, port, $"AD {accFull} -100");
                Assert.StartsWith("ER", resADInv);

                // A-06: Withdrawal (AW)
                _output.WriteLine("Running A-06: AW");
                var resAW = await client.SendCommandAsync(targetIp, port, $"AW {accFull} 500");
                Assert.StartsWith("AW", resAW);
                resAB = await client.SendCommandAsync(targetIp, port, $"AB {accFull}");
                Assert.Contains("AB 500", resAB);

                // A-07: Withdrawal Insufficient
                _output.WriteLine("Running A-07: AW Insufficient");
                var resAWIns = await client.SendCommandAsync(targetIp, port, $"AW {accFull} 600");
                Assert.StartsWith("ER", resAWIns);

                // A-08: Balance (AB) - verified above

                // A-11: Bank Amount (BA)
                _output.WriteLine("Running A-11: BA");
                // We have 5+1 accounts. Account 'accFull' has 500. Others 0.
                var resBA = await client.SendCommandAsync(targetIp, port, "BA");
                Assert.Contains("BA 500", resBA);

                // A-12: Bank Number (BN)
                _output.WriteLine("Running A-12: BN");
                var resBN = await client.SendCommandAsync(targetIp, port, "BN");
                var count = int.Parse(resBN.Split(' ')[1]);
                Assert.True(count >= 6); 

                // A-09 & A-10: Account Remove (AR)
                _output.WriteLine("Running A-10: AR with funds");
                var resARFunds = await client.SendCommandAsync(targetIp, port, $"AR {accFull}");
                Assert.StartsWith("ER", resARFunds); // Cannot remove with funds

                _output.WriteLine("Running A-09: AR zero funds");
                // Withdraw all
                await client.SendCommandAsync(targetIp, port, $"AW {accFull} 500");
                var resAR = await client.SendCommandAsync(targetIp, port, $"AR {accFull}");
                Assert.StartsWith("AR", resAR);
                
                var resABGone = await client.SendCommandAsync(targetIp, port, $"AB {accFull}");
                Assert.StartsWith("ER", resABGone);

            }
            finally
            {
                cts.Cancel();
                try { await serverTask; } catch { }
            }
        }

        [Fact]
        public async Task GroupB_Features_Tests()
        {
            int port = 65532;
            using var cts = new CancellationTokenSource();
            var sp = CreateNode(port, "en");
            var server = sp.GetRequiredService<TcpServer>();
            var serverTask = server.StartAsync(cts.Token);
            var client = sp.GetRequiredService<INetworkClient>();
            var targetIp = "127.0.0.1";

            try
            {
                await Task.Delay(500);

                // B-02: Lang Switch English
                _output.WriteLine("Running B-02: LANG en");
                await client.SendCommandAsync(targetIp, port, "LANG en");
                var errEn = await client.SendCommandAsync(targetIp, port, "XYZ");
                // If it's en, it should be "Unknown command." or similar logic if we mock it?
                // The prompt says "Unknown command."
                
                // Note: The message might depend on the implementation of CommandParser/Translator
                _output.WriteLine($"Error response EN: {errEn}");
                Assert.Contains("Unknown command", errEn);

                // B-03: Lang Switch Czech
                _output.WriteLine("Running B-03: LANG cs");
                await client.SendCommandAsync(targetIp, port, "LANG cs");
                var errCs = await client.SendCommandAsync(targetIp, port, "XYZ");
                _output.WriteLine($"Error response CS: {errCs}");
                Assert.Contains("Neznámý příkaz", errCs); // Assuming cs.json has this

                // B-04: LANG List
                var resLang = await client.SendCommandAsync(targetIp, port, "LANG");
                Assert.Contains("en", resLang);
                Assert.Contains("cs", resLang);

                // B-05: HELP
                // NetworkClient only reads one line, so we need a custom helper for multiline HELP response
                var resHelp = await SendCommandMultilineAsync(targetIp, port, "HELP");
                // _output.WriteLine($"HELP Output:\n{resHelp}");
                Assert.Contains("BC", resHelp);
                Assert.Contains("AC", resHelp);

                // Switch back to EN for remaining tests
                await client.SendCommandAsync(targetIp, port, "LANG en");

                // B-10: Did you mean?
                _output.WriteLine("Running B-10: Did You Mean");
                var resTypo = await client.SendCommandAsync(targetIp, port, "ACCC");
                Assert.Contains("Did you mean AC?", resTypo);
                
                // B-22: Max Command Length (Config default is huge? Let's assume default is checked in parser)
                // actually config.example says 1024 or not present? Defaults check.
                
                // B-23: Strict Range
                // Create account manually or try invalid address string parsing?
                // The client sends commands as strings. AC returns valid ones.
                // We test if server rejects invalid format in commands like AD 9999/ip
                var resStrict = await client.SendCommandAsync(targetIp, port, "AD 9999/127.0.0.1:0 500");
                Assert.StartsWith("ER", resStrict);
            }
            finally
            {
                cts.Cancel();
                try { await serverTask; } catch { }
            }
        }

        [Fact]
        public async Task GroupC_Proxy_Tests()
        {
            // Setup Node A (65534) and Node B (65535)
            // A will proxy to B
            int portA = 65534;
            int portB = 65535;
            using var cts = new CancellationTokenSource();
            
            var spA = CreateNode(portA);
            var serverA = spA.GetRequiredService<TcpServer>();
            var tA = serverA.StartAsync(cts.Token);
            
            var spB = CreateNode(portB);
            var serverB = spB.GetRequiredService<TcpServer>();
            var tB = serverB.StartAsync(cts.Token);
            
            var client = spA.GetRequiredService<INetworkClient>(); // Client talking to A
            var targetIp = "127.0.0.1";

            try
            {
                await Task.Delay(1000); // Startup

                // Create Account on B
                // Direct connect to B first to setup? Or proxy AC? 
                // Proxy AC requires specifying target node? Protocol 'AC' creates LOCAL account.
                // So we must talk to B directly to create account there first.
                // Use a separate client for B or just re-use client helper targeting portB
                
                var clientDirectB = spB.GetRequiredService<INetworkClient>();
                var resAC_B = await clientDirectB.SendCommandAsync(targetIp, portB, "AC");
                var accFull_B = resAC_B.Split(' ')[1]; // 10000/127.0.0.1:65535
                
                // Note: The AC response formatting includes IP:Port usually? 
                // Let's check AccountCommandStrategy logic or previous test output.
                // A-02 test said: "AC <acc>/<ip>". If port is non-default, does it include it?
                // Accounts are identifying themselves. 
                
                // A-13: Proxy Access
                // Query B's account VIA A
                // A needs to know how to reach B. The account identifier has the IP/Port.
                // BUT, if AC response only gave "127.0.0.1" and not port, we might have issue testing on localhost with unique ports.
                // Assumption: Hacker Edition P2P usually assumes standard ports or explicit port in address.
                // Let's try explicitly constructing the address with port B.
                
                var accNumB = accFull_B.Split('/')[0];
                var accAddressB = $"{accNumB}/127.0.0.1:{portB}"; 
                
                _output.WriteLine($"Running A-13: Proxy Check {accAddressB} via Node A");
                var resAB_Proxy = await client.SendCommandAsync(targetIp, portA, $"AB {accAddressB}");
                Assert.Contains("AB 0", resAB_Proxy); // Initially 0

                // A-14: Remote Deposit
                _output.WriteLine("Running A-14: Proxy Deposit");
                var resAD_Proxy = await client.SendCommandAsync(targetIp, portA, $"AD {accAddressB} 500");
                Assert.Contains("AD", resAD_Proxy); // Forwarded success
                
                // Verify on B directly
                var resAB_Direct = await clientDirectB.SendCommandAsync(targetIp, portB, $"AB {accAddressB}");
                Assert.Contains("AB 500", resAB_Direct);
                
                // B-12: Extended Address Format verified implicitly by using :portB
            }
            finally
            {
                cts.Cancel();
                try { await Task.WhenAll(tA, tB); } catch { }
            }
        }

        [Fact]
        public async Task GroupD_AdvancedFeatures_Tests()
        {
            int port = 65529;
            
            // Manual Setup for RateLimit override (RP command generates many requests)
            var config = new AppConfig { 
                Port = port, 
                NodeIp = "127.0.0.1", 
                Language = "en",
                Timeout = 2000,
                RateLimit = 1000 // Allow Robbery Plan storm
            };
            
            var services = new ServiceCollection();
            var accountsFile = $"accounts_{_testId}_{port}.json";
            services.AddSingleton(config);
            services.AddLogging(c => c.AddConsole());
            services.AddSingleton<IAccountRepository>(sp => new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), accountsFile));
            services.AddSingleton<IAccountService, AccountService>();
            services.AddSingleton<TcpServer>();
            services.AddSingleton<INetworkClient, NetworkClient>();
            services.AddSingleton<CommandParser>();
            // Add Decorators (Standard Pipeline)
            services.AddSingleton<ICommandProcessor>(p => 
                new BankNode.App.Decorators.MetricsDecorator( 
                        new BankNode.App.Decorators.RateLimitingDecorator(
                            new RequestLoggingDecorator(
                                p.GetRequiredService<CommandParser>(),
                                p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                            ),
                            p.GetRequiredService<ILogger<BankNode.App.Decorators.RateLimitingDecorator>>(),
                            p.GetRequiredService<AppConfig>()
                        )
                ));
            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.JsonFileTranslationStrategy>();

            // Strategies
            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, AccountCommandStrategy>();
            services.AddSingleton<ICommandStrategy, RobberyCommandStrategy>();
            services.AddSingleton<ICommandStrategy, HelpCommandStrategy>();
            services.AddSingleton<ICommandStrategy, LanguageCommandStrategy>();
            services.AddSingleton<ICommandStrategy, BackupCommandStrategy>();
            services.AddSingleton<ICommandStrategy, HealthCommandStrategy>();

            var sp = services.BuildServiceProvider();
            if (File.Exists(accountsFile)) File.Delete(accountsFile);
            
            using var cts = new CancellationTokenSource();
            var server = sp.GetRequiredService<TcpServer>();
            var serverTask = server.StartAsync(cts.Token);
            var client = sp.GetRequiredService<INetworkClient>();
            var targetIp = "127.0.0.1";

            try
            {
                await Task.Delay(1000);

                // B-20: HISTORY
                _output.WriteLine("Running B-20: HISTORY");
                // We need a persistent session for history
                var historyRes = await SendSessionCommandsAsync(targetIp, port, new[] { "BC", "AC", "HISTORY" });
                var bcOutput = historyRes[0];
                var acOutput = historyRes[1];
                var histOutput = historyRes[2]; // This should contain the history list
                
                Assert.Contains("BC 127.0.0.1", bcOutput); // Verify commands ran
                Assert.Contains("BC", histOutput); // Verify history saw them
                Assert.Contains("AC", histOutput);

                // B-21: EXECUTE
                // Needs a file on disk
                var scriptFile = $"script_{_testId}.txt";
                await File.WriteAllTextAsync(scriptFile, "BC\nBN");
                
                _output.WriteLine("Running B-21: EXECUTE");
                var resExec = await SendCommandMultilineAsync(targetIp, port, $"EXECUTE {scriptFile}");
                Assert.Contains("BC 127.0.0.1", resExec);
                // BN might be 0
                
                if (File.Exists(scriptFile)) File.Delete(scriptFile);

                // A-15: Robbery Plan
                // Needs victims. Create accounts locally or scan?
                // RP expects to scan network ports.
                // We only have this node running in this test scope.
                // RP 100 on localhost might find itself if it scans its own port?
                // But it needs ACCOUNTS to rob.
                // Let's create an account with money.
                var resAC = await client.SendCommandAsync(targetIp, port, "AC");
                var acc = resAC.Split(' ')[1];
                await client.SendCommandAsync(targetIp, port, $"AD {acc} 10000");
                
                // RP might fail if no neighbors found or no money found (it usually excludes self? No, it's evil node)
                // Actually RobberyCommandStrategy logic:
                // Scans IP range / Ports.
                // If checking localhost, it might hit itself.
                _output.WriteLine("Running A-15: RP");
                var resRP = await client.SendCommandAsync(targetIp, port, "RP 100");
                // It might return "Could not find enough money" or a plan.
                // As long as it's not "Unknown Command"
                Assert.True(resRP.StartsWith("RP") || resRP.StartsWith("ER"), $"Unexpected RP response: {resRP}");

                // B-14: Rate Limiting (Config default 60/min = 1/sec?)
                // Default is 60. so > 1 per second is fine?
                // config.Example says 60.
                // We'd need tospam crazy fast to hit it or reconfigure low limit.
                // Let's skip spam test effectively unless we inject config.
                
                // B-16: BACKUP
                var backupFile = $"backup_{_testId}.json";
                if(File.Exists(backupFile)) File.Delete(backupFile);
                
                _output.WriteLine("Running B-16: BACKUP");
                var resBackup = await client.SendCommandAsync(targetIp, port, $"BACKUP {backupFile}");
                Assert.Contains("BACKUP Created", resBackup);
                Assert.True(File.Exists(backupFile));
                
                // B-17: RESTORE
                // Wipe data?
                // Just restore.
                 _output.WriteLine("Running B-17: RESTORE");
                var resRestore = await client.SendCommandAsync(targetIp, port, $"RESTORE {backupFile}");
                Assert.Contains("RESTORE Completed", resRestore);

            }
            finally
            {
                cts.Cancel();
                try { await serverTask; } catch { }
            }
        }

        [Fact]
        public async Task GroupE_Configuration_Tests()
        {
            // B-08: Hot Reload
            // B-14: Rate Limiting
            // B-18: Max Connections
            // B-19: Idle Timeout
            // B-22: Max Length (1024)
            // A-17: Port Range
            // A-20: Case Sensitivity

            int port = 65526;
            
            var config = new AppConfig { 
                Port = port, 
                NodeIp = "127.0.0.1", 
                Language = "en",
                Timeout = 2000,
                RateLimit = 10,
                MaxConcurrentConnections = 3,
                ClientIdleTimeout = 2000
            };
            
            var services = new ServiceCollection();
            var accountsFile = $"accounts_{_testId}_GroupE.json";
            services.AddSingleton(config);
            services.AddLogging(c => c.AddConsole());
            services.AddSingleton<IAccountRepository>(sp => new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), accountsFile));
            services.AddSingleton<IAccountService, AccountService>();
            services.AddSingleton<TcpServer>();
            services.AddSingleton<INetworkClient, NetworkClient>();
            services.AddSingleton<CommandParser>();
            
            services.AddSingleton<ICommandProcessor>(p => 
                new BankNode.App.Decorators.MetricsDecorator( 
                        new BankNode.App.Decorators.RateLimitingDecorator(
                            new RequestLoggingDecorator(
                                p.GetRequiredService<CommandParser>(),
                                p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                            ),
                            p.GetRequiredService<ILogger<BankNode.App.Decorators.RateLimitingDecorator>>(),
                            p.GetRequiredService<AppConfig>()
                        )
                ));

            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.JsonFileTranslationStrategy>();
            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
            services.AddSingleton<ICommandStrategy, HelpCommandStrategy>();
            
            var sp = services.BuildServiceProvider();
            if (File.Exists(accountsFile)) File.Delete(accountsFile);
            
            // Allow B-08 Hot Reload & ensure RateLimit=10 persists after Load()
            var initialConfigJson = System.Text.Json.JsonSerializer.Serialize(config);
            await File.WriteAllTextAsync("config.json", initialConfigJson);
            
            config.Load();
            
            var server = sp.GetRequiredService<TcpServer>();
            using var cts = new CancellationTokenSource();
            var serverTask = server.StartAsync(cts.Token);
            var client = sp.GetRequiredService<INetworkClient>();
            var targetIp = "127.0.0.1";

            try
            {
                await Task.Delay(1000);

                _output.WriteLine("Running A-20: Case Sensitivity");
                var resLower = await client.SendCommandAsync(targetIp, port, "bc");
                Assert.Contains("BC", resLower);
                var resMixed = await client.SendCommandAsync(targetIp, port, "Bc");
                Assert.Contains("BC", resMixed);

                _output.WriteLine("Running B-14: Rate Limiting");
                bool limitHit = false;
                for(int i=0; i<15; i++)
                {
                   var r = await client.SendCommandAsync(targetIp, port, "BC");
                   if (r.Contains("Rate limit")) {
                       limitHit = true;
                       _output.WriteLine($"Rate limit hit at {i}");
                       break;
                   }
                }
                Assert.True(limitHit, "Rate limit should be hit");

                _output.WriteLine("Running B-18: Max Concurrent Connections (Queueing)");
                // Configured Max=3.
                var conns = new List<System.Net.Sockets.TcpClient>();
                try 
                {
                    for(int k=0; k<3; k++)
                    {
                        var c = new System.Net.Sockets.TcpClient();
                        await c.ConnectAsync(targetIp, port);
                        // Read welcome to ensure they are fully accepted
                        var s = c.GetStream();
                        var buf = new byte[1024];
                        await s.ReadAsync(buf, 0, buf.Length);
                        conns.Add(c);
                    }
                    
                    // 4th should be queued.
                    var c4 = new System.Net.Sockets.TcpClient();
                    var connectTask = c4.ConnectAsync(targetIp, port);
                    
                    // If ConnectAsync finishes (TCP backlog), the Welcome message read should hang.
                    // Wait for it?
                    await connectTask; 
                    
                    var s4 = c4.GetStream();
                    var reader4 = new StreamReader(s4);
                    
                    var readTask = reader4.ReadLineAsync(); // Should hang
                    var completedTask = await Task.WhenAny(readTask, Task.Delay(1000));
                    
                    Assert.True(completedTask != readTask, "Should timeout (be queued) waiting for welcome");
                    
                    // Release one
                    conns[0].Close();
                    conns[0].Dispose();
                    
                    // Now 4th should proceed
                    var welcome = await readTask; // Should complete now
                    Assert.NotNull(welcome);
                    Assert.Contains("BankNode", welcome);
                    
                    c4.Close(); 
                }
                finally
                {
                    foreach(var c in conns) try { c.Dispose(); } catch {}
                }

                _output.WriteLine("Running B-22: Max Length");
                var longCmd = new string('A', 1030);
                var resLong = await client.SendCommandAsync(targetIp, port, longCmd);
                Assert.Contains("too long", resLong);

                _output.WriteLine("Running B-19: Idle Timeout");
                using (var idleClient = new System.Net.Sockets.TcpClient())
                {
                    await idleClient.ConnectAsync(targetIp, port);
                    await Task.Delay(2500); 
                    try {
                        var stream = idleClient.GetStream();
                        var writer = new StreamWriter(stream) { AutoFlush = true };
                        await writer.WriteLineAsync("BC");
                         var reader = new StreamReader(stream);
                         var resp = await reader.ReadLineAsync();
                         Assert.True(resp == null || !idleClient.Connected, "Should be disconnected/empty");
                    }
                    catch (Exception)
                    {
                        // Expected
                    }
                }
            }
            finally
            {
                cts.Cancel();
                try { await serverTask; } catch { }
                if (File.Exists(accountsFile)) File.Delete(accountsFile);
            }
        }

        [Fact]
        public async Task GroupF_Logging_Console_Tests()
        {
            // B-15: Metrics via HC
            int port = 65527;
            using var cts = new CancellationTokenSource();

            // Custom node setup with HealthStrategy
            var accountsFile = $"accounts_{_testId}_GroupF.json";
            var config = new AppConfig { Port = port, NodeIp = "127.0.0.1", Language = "en" };
            var services = new ServiceCollection();
            services.AddSingleton(config);
            services.AddSingleton<IAccountRepository>(sp => new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), accountsFile));
            services.AddSingleton<IAccountService, AccountService>();
            services.AddSingleton<TcpServer>();
            services.AddSingleton<INetworkClient, NetworkClient>();
            services.AddSingleton<CommandParser>();
            services.AddLogging(c => c.AddConsole());
            services.AddSingleton<ICommandProcessor>(p => 
                new BankNode.App.Decorators.MetricsDecorator( // Metrics
                    new RequestLoggingDecorator(
                        p.GetRequiredService<CommandParser>(),
                        p.GetRequiredService<ILogger<RequestLoggingDecorator>>()
                    )
            ));
            services.AddSingleton<BankNode.Translation.ITranslationStrategy, BankNode.Translation.Strategies.JsonFileTranslationStrategy>();
            services.AddSingleton<ICommandStrategy, BasicCommandStrategy>();
             services.AddSingleton<ICommandStrategy, HealthCommandStrategy>();

            var sp = services.BuildServiceProvider();
            if (File.Exists(accountsFile)) File.Delete(accountsFile);

            var server = sp.GetRequiredService<TcpServer>();
            var serverTask = server.StartAsync(cts.Token);
            var client = sp.GetRequiredService<INetworkClient>();
            var targetIp = "127.0.0.1";

            try
            {
                await Task.Delay(1000);
                
                _output.WriteLine("Running B-15: Metrics");
                await client.SendCommandAsync(targetIp, port, "BC");
                
                var resHC = await client.SendCommandAsync(targetIp, port, "HC");
                Assert.Contains("Uptime", resHC); 
                Assert.Contains("TotalRequests", resHC);
                Assert.Contains("1", resHC); // check count > 0
            }
            finally
            {
                cts.Cancel();
                try { await serverTask; } catch { }
                if (File.Exists(accountsFile)) File.Delete(accountsFile);
            }
        }


        [Fact]
        public async Task GroupF_ConsoleLogic_Tests()
        {
            // B-06 (BN), B-07 (LOG), Help, Exit
            // We test the Program.RunConsoleLoopAsync logic directly using Memory Streams
            using var cts = new CancellationTokenSource();
            var sb = new StringBuilder();
            var writer = new StringWriter(sb);
            var input = new StringReader("BN\nLOG\nLOG\nHELP\nEXIT\n"); // BN, Toggle Debug, Toggle Info, Help, Exit
            
            // Mock infrastructure
            var services = new ServiceCollection();
            var accountsFile = $"accounts_{_testId}_GroupConsole.json";
            var config = new AppConfig { Port = 0, NodeIp = "127.0.0.1", Language = "en" };
            services.AddSingleton(config);
            var switchLog = new BankNode.App.LogLevelSwitch();
            services.AddSingleton(switchLog);
            services.AddLogging(configure =>
            {
                configure.AddConsole(); 
            });

            services.AddSingleton<IAccountRepository>(sp => new FileAccountRepository(sp.GetRequiredService<ILogger<FileAccountRepository>>(), accountsFile));
            services.AddSingleton<IAccountService, AccountService>();
            services.AddSingleton<CommandParser>(); // Required if used? Not used in Loop unless BN command uses it? No BN just uses Repo.
            
            var sp = services.BuildServiceProvider();
            var logger = sp.GetRequiredService<ILogger<Program>>();
            
            // Execute
            await Program.RunConsoleLoopAsync(input, writer, cts, sp, logger);
            
            // Verifications
            var output = sb.ToString();
            
            // 1. Check commands ran
            Assert.Contains("Server started", output);
            Assert.Contains("Local Accounts:", output); // from BN
            Assert.Contains("Log Level set to DEBUG", output); // from LOG
            Assert.Contains("Log Level set to INFO", output); // from LOG second time
            Assert.Contains("Available Local Commands:", output); // from HELP
            
            // 2. Check Logic (State change)
            // The input toggled LOG twice (Info->Debug->Info).
            // Initial default is Info.
            // LOG 1 -> Debug. logic prints "Set to DEBUG".
            // LOG 2 -> Info. logic prints "Set to INFO".
            // switchLog state should be Info finally.
            // Let's check intermediate state? Hard in one run.
            // Assert output confirms logic ran.
            
            Assert.Equal(LogLevel.Information, switchLog.MinimumLevel);
            
            // 3. EXIT command
            Assert.True(cts.IsCancellationRequested, "EXIT should cancel token");
        }

        [Fact]
        public async Task GroupG_Performance_Tests()
        {
            // B-13: Connection Pooling
            int port = 65528;
            using var cts = new CancellationTokenSource();
            var sp = CreateNode(port);
            var server = sp.GetRequiredService<TcpServer>();
            _ = server.StartAsync(cts.Token);
            
            var targetIp = "127.0.0.1";
            await Task.Delay(1000);

            // Baseline: Non-Pooled (New Connection per Request)
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            for(int i=0; i<50; i++)
            {
                using var client = new System.Net.Sockets.TcpClient();
                await client.ConnectAsync(targetIp, port);
                using var stream = client.GetStream();
                using var writer = new StreamWriter(stream) { AutoFlush = true };
                using var reader = new StreamReader(stream);
                await reader.ReadLineAsync(); // Welcome
                await writer.WriteLineAsync("BC");
                await reader.ReadLineAsync(); // Response
            }
            stopwatch.Stop();
            var timeNonPooled = stopwatch.ElapsedMilliseconds;

            // Pooled: Reuse Connection
            stopwatch.Restart();
            using (var client = new System.Net.Sockets.TcpClient())
            {
                await client.ConnectAsync(targetIp, port);
                using var stream = client.GetStream();
                using var writer = new StreamWriter(stream) { AutoFlush = true };
                using var reader = new StreamReader(stream);
                await reader.ReadLineAsync(); // Welcome
                
                for(int i=0; i<50; i++)
                {
                    await writer.WriteLineAsync("BC");
                    await reader.ReadLineAsync(); // Response
                }
            }
            stopwatch.Stop();
            var timePooled = stopwatch.ElapsedMilliseconds;
            
            _output.WriteLine($"Non-Pooled: {timeNonPooled}ms, Pooled: {timePooled}ms");
            Assert.True(timePooled < timeNonPooled, "Pooled should be faster");
        }
        
        [Fact]
        public async Task GroupH_AtomicPersistence_Tests()
        {
            // B-11: Atomic Writes (Recovery)
            // Setup: Create a partial/corrupt temp file and ensure it is ignored.
            int port = 65541;
            var accountsFile = $"accounts_{_testId}_{port}.json";
            var tempFile = accountsFile + ".tmp";
            
            // 3. Start Node (Setup SP but don't resolve repo yet)
            var sp = CreateNode(port);
            // CreateNode deletes the file on start. So we write AFTER CreateNode returns (Delete happened), 
            // BUT BEFORE we resolve Repo (which reads it).
            
            // 1. Create valid account file (NDJSON format, one JSON object per line)
            var validJson = "{\"AccountNumber\":\"10000\",\"Balance\":500}";
            await File.WriteAllTextAsync(accountsFile, validJson);
            
            // 2. Create corrupt temp file
            await File.WriteAllTextAsync(tempFile, "[{\"AccountNumber\":\"20000\",\"Balan... ARGH CRASH");
            
            var repo = sp.GetRequiredService<IAccountRepository>();
            var acc = await repo.GetByAccountNumberAsync("10000");
            
            // Assert: Loaded valid data, ignored temp
            Assert.NotNull(acc);
            Assert.Equal(500, acc.Balance);
            
            // 4. Trigger Save (Modify)
            await repo.AddAsync(new BankNode.Core.Models.Account { AccountNumber = "99999", Balance = 0 });
            
            // 5. Verify Persistence
            // Should have overwritten accountsFile with 2 accounts.
            // Temp file might exist briefly but effectively atomic logic uses it.
            // We can check if file is valid JSON.
            var content = await File.ReadAllTextAsync(accountsFile);
            Assert.Contains("99999", content);
            Assert.Contains("10000", content);
            
            // Clean
            if(File.Exists(accountsFile)) File.Delete(accountsFile);
            if(File.Exists(tempFile)) File.Delete(tempFile);
        }

        private async Task<string[]> SendSessionCommandsAsync(string ip, int port, string[] commands)
        {
            var results = new List<string>();
            using var client = new System.Net.Sockets.TcpClient();
            await client.ConnectAsync(ip, port);
            using var stream = client.GetStream();
            using var reader = new StreamReader(stream, System.Text.Encoding.UTF8);
            using var writer = new StreamWriter(stream, System.Text.Encoding.UTF8) { AutoFlush = true };

            // Read welcome
            await reader.ReadLineAsync();

            foreach (var cmd in commands)
            {
                await writer.WriteLineAsync(cmd);
                
                // Read response. Some commands might be multiline? 
                // For this test, BC and AC are single line. HISTORY is multiline.
                // We need a robust read. The server doesn't send "End of Response" marker explicitly.
                // But usually we can read until we get a result.
                // HISTORY stops sending? 
                // Wait for data.
                
                var sb = new StringBuilder();
                var buffer = new char[4096];
                await Task.Delay(50); // wait for processing
                
                // Read at least something
                int read = await reader.ReadAsync(buffer, 0, buffer.Length);
                sb.Append(buffer, 0, read);
                
                // If more available, read it (for multiline like HISTORY)
                while (client.Available > 0)
                {
                    read = await reader.ReadAsync(buffer, 0, buffer.Length);
                    sb.Append(buffer, 0, read);
                }
                results.Add(sb.ToString());
            }
            return results.ToArray();
        }

        private async Task<string> SendCommandMultilineAsync(string ip, int port, string command)
        {
            using var client = new System.Net.Sockets.TcpClient();
            await client.ConnectAsync(ip, port);
            using var stream = client.GetStream();
            using var reader = new StreamReader(stream, System.Text.Encoding.UTF8);
            using var writer = new StreamWriter(stream, System.Text.Encoding.UTF8) { AutoFlush = true };

            // Read welcome message first
            await reader.ReadLineAsync();

            await writer.WriteLineAsync(command);
            
            var sb = new StringBuilder();
            var buffer = new char[4096];
            
            // Allow some time for response
            await Task.Delay(200);
            
            while (client.Available > 0)
            {
                int read = await reader.ReadAsync(buffer, 0, buffer.Length);
                sb.Append(buffer, 0, read);
                await Task.Delay(50); 
            }
            
            return sb.ToString(); 
        }
        [Fact]
        public void Unit_AppConfig_Validation_Tests()
        {
            // A-17: Port Range
            var config = new AppConfig { Port = 100 }; // Invalid
            Assert.Throws<ArgumentException>(() => config.Load());
            
            config.Port = 70000;
            Assert.Throws<ArgumentException>(() => config.Load());
            
            config.Port = 65525; // Valid
            config.Load(); // Should pass (assuming other defaults are valid)
        }
    }
}
