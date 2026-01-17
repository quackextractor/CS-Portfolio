# Testing Scenarios for P2P Bank Node (Hacker Edition)

## Group A: Core Functionality Tests

### A-01: Bank Code Command (BC)
**Test ID:** A-001  
**Description:** Verify BC command returns correct IP address  
**Preconditions:** Node running on port 65525  
**Steps:**
1. Connect to node via telnet/PuTTY
2. Send command: `BC`
3. Observe response  
**Expected Result:** `BC <node_ip>` (e.g., `BC 192.168.1.5`)

### A-02: Account Creation (AC)
**Test ID:** A-002  
**Description:** Verify AC creates account with valid number  
**Preconditions:** Node running, no account with same number  
**Steps:**
1. Connect to node
2. Send command: `AC`
3. Observe response  
**Expected Result:** `AC <account>/<ip>` where account is 10000-99999

### A-03: Account Creation - Range Validation
**Test ID:** A-003  
**Description:** Verify account numbers are within specified range  
**Preconditions:** Node running  
**Steps:**
1. Create multiple accounts (20+)
2. Verify all account numbers are 10000-99999  
**Expected Result:** All account numbers within 10000-99999 inclusive

### A-04: Account Deposit (AD) - Valid
**Test ID:** A-004  
**Description:** Verify deposit increases account balance  
**Preconditions:** Account created, balance = 0  
**Steps:**
1. Connect to node
2. Send: `AD <account>/<ip> 1000`
3. Send: `AB <account>/<ip>`
4. Observe balance  
**Expected Result:** First response: `AD`, Second response: `AB 1000`

### A-05: Account Deposit (AD) - Invalid Amount
**Test ID:** A-005  
**Description:** Verify error on negative deposit  
**Preconditions:** Account exists  
**Steps:**
1. Send: `AD <account>/<ip> -100`
2. Observe response  
**Expected Result:** `ER <error_message>`

### A-06: Account Withdrawal (AW) - Valid
**Test ID:** A-006  
**Description:** Verify withdrawal decreases balance  
**Preconditions:** Account with balance 1000  
**Steps:**
1. Send: `AW <account>/<ip> 500`
2. Send: `AB <account>/<ip>`
3. Observe balance  
**Expected Result:** First: `AW`, Second: `AB 500`

### A-07: Account Withdrawal (AW) - Insufficient Funds
**Test ID:** A-007  
**Description:** Verify error when insufficient balance  
**Preconditions:** Account with balance 100  
**Steps:**
1. Send: `AW <account>/<ip> 200`
2. Observe response  
**Expected Result:** `ER Není dostatek finančních prostředků.` (or English equivalent)

### A-08: Account Balance (AB)
**Test ID:** A-008  
**Description:** Verify balance query returns correct amount  
**Preconditions:** Account with known balance  
**Steps:**
1. Deposit specific amount
2. Query balance
3. Verify matches deposited amount  
**Expected Result:** `AB <correct_amount>`

### A-09: Account Remove (AR) - Zero Balance
**Test ID:** A-009  
**Description:** Verify account deletion with zero balance  
**Preconditions:** Account with balance 0  
**Steps:**
1. Send: `AR <account>/<ip>`
2. Try to query same account  
**Expected Result:** First: `AR`, Second: `ER Account not found.`

### A-10: Account Remove (AR) - Non-Zero Balance
**Test ID:** A-010  
**Description:** Verify error when deleting account with funds  
**Preconditions:** Account with balance > 0  
**Steps:**
1. Send: `AR <account>/<ip>`
2. Observe response  
**Expected Result:** `ER Cannot remove account with non-zero balance.`

### A-11: Bank Amount (BA)
**Test ID:** A-011  
**Description:** Verify total bank amount calculation  
**Preconditions:** Multiple accounts with known balances  
**Steps:**
1. Create 3 accounts
2. Deposit: A1=500, A2=300, A3=200
3. Send: `BA`
4. Observe response  
**Expected Result:** `BA 1000`

### A-12: Bank Number (BN)
**Test ID:** A-012  
**Description:** Verify client count  
**Preconditions:** Multiple accounts created  
**Steps:**
1. Create N accounts
2. Send: `BN`
3. Observe response  
**Expected Result:** `BN <N>`

### A-13: Proxy Functionality - Remote Account Access
**Test ID:** A-013  
**Description:** Verify proxy works for remote accounts  
**Preconditions:** Two nodes running (NodeA:65525, NodeB:65526), account on NodeB  
**Steps:**
1. From NodeA, send: `AB <account>/127.0.0.1:65526`
2. Observe response from NodeB  
**Expected Result:** Correct balance from NodeB's account

### A-14: Proxy Functionality - Remote Deposit
**Test ID:** A-014  
**Description:** Verify deposit to remote account  
**Preconditions:** Two nodes, account on NodeB  
**Steps:**
1. From NodeA, send: `AD <account>/127.0.0.1:65526 500`
2. Verify on NodeB: `AB <account>/127.0.0.1`
3. Observe balance  
**Expected Result:** Balance increased by 500 on NodeB

### A-15: Robbery Plan (RP) - Basic Functionality
**Test ID:** A-015  
**Description:** Verify RP command returns plan  
**Preconditions:** Multiple nodes with accounts and balances  
**Steps:**
1. Scan network (or mock scan results)
2. Send: `RP 1000000`
3. Observe response  
**Expected Result:** `RP <plan_message>` with bank list and victim count

### A-16: Error Response Format
**Test ID:** A-016  
**Description:** Verify error responses follow ER format  
**Preconditions:** Node running  
**Steps:**
1. Send invalid command: `XYZ`
2. Observe response format  
**Expected Result:** `ER <message>` (starts with ER, space, message)

### A-17: Configuration - Port Range
**Test ID:** A-017  
**Description:** Verify port must be 65525-65535  
**Preconditions:** None  
**Steps:**
1. Start node with port 65524
2. Observe startup result  
**Expected Result:** Error/refusal to start or validation error

### A-18: Configuration - Timeout
**Test ID:** A-018  
**Description:** Verify timeout configuration works  
**Preconditions:** Node with timeout=1000ms  
**Steps:**
1. From another node, start connection but don't respond
2. Measure time until timeout  
**Expected Result:** Connection times out within ~1000-1500ms

### A-19: Persistence - Account Survival
**Test ID:** A-019  
**Description:** Verify accounts survive restart  
**Preconditions:** Account with balance created  
**Steps:**
1. Create account with deposit
2. Restart node
3. Query account balance  
**Expected Result:** Same balance after restart

### A-20: Protocol Compliance - Command Case
**Test ID:** A-020  
**Description:** Verify uppercase commands work (case sensitivity)  
**Preconditions:** Node running  
**Steps:**
1. Send: `bc` (lowercase)
2. Send: `Bc` (mixed)
3. Send: `BC` (uppercase)  
**Expected Result:** All should work OR only uppercase works (documented behavior)

---

## Group B: Additional Functionality Tests

### B-01: Health Check (HC) Command
**Test ID:** B-001  
**Description:** Verify HC returns comprehensive metrics  
**Preconditions:** Node running for some time  
**Steps:**
1. Send: `HC`
2. Parse JSON response  
**Expected Result:** JSON with uptime, memory usage, account count, total balance, request metrics

### B-02: Language Switching (LANG) - English
**Test ID:** B-002  
**Description:** Verify language switch to English  
**Preconditions:** Node running, default language may be different  
**Steps:**
1. Send: `LANG en`
2. Send invalid command: `XYZ`
3. Observe error message  
**Expected Result:** English error message: `ER Unknown command.`

### B-03: Language Switching (LANG) - Czech
**Test ID:** B-003  
**Description:** Verify language switch to Czech  
**Preconditions:** Node running  
**Steps:**
1. Send: `LANG cs`
2. Send invalid command: `XYZ`
3. Observe error message  
**Expected Result:** Czech error message: `ER Neznámý příkaz.`

### B-04: Language Switching (LANG) - List Available
**Test ID:** B-004  
**Description:** Verify LANG lists available languages  
**Preconditions:** Node with multiple language files  
**Steps:**
1. Send: `LANG`
2. Observe response  
**Expected Result:** List of available languages (e.g., "Available languages: en, cs")

### B-05: HELP Command
**Test ID:** B-005  
**Description:** Verify HELP returns command list  
**Preconditions:** Node running  
**Steps:**
1. Send: `HELP`
2. Observe response  
**Expected Result:** List of commands with descriptions (in current language)

### B-06: Interactive Server Console - BN Local Command
**Test ID:** B-006  
**Description:** Verify BN works in server console  
**Preconditions:** Node running with accounts  
**Steps:**
1. In server terminal (not telnet), type: `BN`
2. Observe output  
**Expected Result:** Shows local bank statistics

### B-07: Interactive Server Console - LOG Level Toggle
**Test ID:** B-007  
**Description:** Verify LOG toggles verbosity  
**Preconditions:** Node running  
**Steps:**
1. In server terminal, type: `LOG`
2. Check log output level changes
3. Type `LOG` again
4. Check level returns  
**Expected Result:** Logging level toggles between INFO and DEBUG

### B-08: Hot Configuration Reload
**Test ID:** B-008  
**Description:** Verify config changes without restart  
**Preconditions:** Node running with config.json  
**Steps:**
1. Modify config.json (change Timeout from 5000 to 1000)
2. Wait for file watcher detection
3. Test timeout behavior  
**Expected Result:** New timeout value takes effect without restart

### B-09: Request Logging
**Test ID:** B-009  
**Description:** Verify requests are logged  
**Preconditions:** Node running  
**Steps:**
1. Send multiple commands via telnet
2. Check node.log file  
**Expected Result:** Each command logged with timestamp, IP, command, response, execution time

### B-10: "Did You Mean?" Suggestions
**Test ID:** B-010  
**Description:** Verify command suggestions on typo  
**Preconditions:** Node running  
**Steps:**
1. Send: `ABBB 10001/127.0.0.1` (typo of AB)
2. Observe response  
**Expected Result:** `ER Unknown command. Did you mean AB?`

### B-11: Atomic File Writes
**Test ID:** B-011  
**Description:** Verify data integrity during crashes  
**Preconditions:** Node with accounts  
**Steps:**
1. Simulate crash during write (kill process mid-transaction)
2. Restart node
3. Check account data integrity  
**Expected Result:** No corrupted data, either old or new complete state

### B-12: Extended Address Format with Port
**Test ID:** B-012  
**Description:** Verify address with custom port works  
**Preconditions:** NodeA on 65525, NodeB on 65526  
**Steps:**
1. From any client, send: `AB <account>/127.0.0.1:65526`
2. Observe response  
**Expected Result:** Successfully proxies to NodeB on port 65526

### B-13: Connection Pooling Performance
**Test ID:** B-013  
**Description:** Verify connection reuse improves performance  
**Preconditions:** Two nodes, connection pooling enabled  
**Steps:**
1. Time 100 sequential RP commands (scanning)
2. Compare with connection pooling disabled  
**Expected Result:** Faster execution with pooling (reduced connection overhead)

### B-14: Rate Limiting
**Test ID:** B-014  
**Description:** Verify rate limit enforcement  
**Preconditions:** Node with RateLimit=10 per minute  
**Steps:**
1. Send 12 commands rapidly from same IP
2. Observe responses for 11th and 12th  
**Expected Result:** Commands 11+ get: `ER Rate limit exceeded.`

### B-15: Metrics Collection
**Test ID:** B-015  
**Description:** Verify metrics track command usage  
**Preconditions:** Node running, HC command working  
**Steps:**
1. Send various commands (AC, AD, AB, etc.)
2. Send: `HC`
3. Check command distribution in metrics  
**Expected Result:** Metrics show counts for each command type

### B-16: BACKUP Command
**Test ID:** B-016  
**Description:** Verify backup creates restorable file  
**Preconditions:** Node with accounts  
**Steps:**
1. Send: `BACKUP test_backup.json`
2. Check file exists
3. Verify JSON format  
**Expected Result:** File created with all accounts in JSON format

### B-17: RESTORE Command
**Test ID:** B-017  
**Description:** Verify restore from backup  
**Preconditions:** Backup file exists  
**Steps:**
1. Delete all accounts (simulate loss)
2. Send: `RESTORE test_backup.json`
3. Verify accounts restored  
**Expected Result:** Accounts and balances match backup

### B-18: MaxConcurrentConnections Limit
**Test ID:** B-018  
**Description:** Verify connection limit enforcement  
**Preconditions:** Node with MaxConcurrentConnections=5  
**Steps:**
1. Open 6 simultaneous telnet connections
2. Try to send commands on all  
**Expected Result:** 5 connections work, 6th rejected or queued

### B-19: ClientIdleTimeout
**Test ID:** B-019  
**Description:** Verify idle clients disconnected  
**Preconditions:** Node with ClientIdleTimeout=30000 (30s)  
**Steps:**
1. Connect via telnet
2. Wait 35 seconds without sending command
3. Try to send command  
**Expected Result:** Connection closed or timeout error

### B-20: HISTORY Command
**Test ID:** B-020  
**Description:** Verify command history tracking  
**Preconditions:** Node running, HISTORY command implemented  
**Steps:**
1. Send 5 different commands
2. Send: `HISTORY`
3. Observe output  
**Expected Result:** List of last 5 commands (or up to 10)

### B-21: EXECUTE Script Command
**Test ID:** B-021  
**Description:** Verify script execution from file  
**Preconditions:** Script file with commands  
**Steps:**
1. Create test_script.txt with: `BC`, `AC`, `BA`
2. Send: `EXECUTE test_script.txt`
3. Observe outputs  
**Expected Result:** Each command executed and responses returned

### B-22: MaxCommandLength Enforcement
**Test ID:** B-022  
**Description:** Verify command length limit  
**Preconditions:** Node with MaxCommandLength=1024  
**Steps:**
1. Send command with 1025 characters
2. Observe response  
**Expected Result:** `ER Invalid format (Command too long)`

### B-23: Account Number Validation (Strict Range)
**Test ID:** B-023  
**Description:** Verify strict 10000-99999 range (Breaking Change v1.6.0)  
**Preconditions:** Node version 1.6.0+  
**Steps:**
1. Try to parse account 9999
2. Try to parse account 100000  
**Expected Result:** Both rejected as invalid format

### B-24: Docker Containerization
**Test ID:** B-024  
**Description:** Verify Docker image runs correctly  
**Preconditions:** Docker installed  
**Steps:**
1. Build image: `docker build -t banknode .`
2. Run container: `docker run -p 65525:65525 banknode`
3. Connect via telnet  
**Expected Result:** Node runs and accepts commands in container

### B-25: Kubernetes Deployment
**Test ID:** B-025  
**Description:** Verify K8s manifest deploys correctly  
**Preconditions:** Kubernetes cluster, kubectl  
**Steps:**
1. Apply deployment.yaml
2. Check pod status
3. Expose via NodePort
4. Connect to service  
**Expected Result:** Bank node accessible via K8s service