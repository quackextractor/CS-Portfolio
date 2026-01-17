# Scenarios Verification Output

**Date:** 2026-01-17
**Verified By:** FullScenariosTests.cs (Automated Integration Tests)

All scenarios have been verified using a comprehensive automated integration test suite (`src/BankNode.Tests.Integration/FullScenariosTests.cs`).

## Summary
- **Total Tests:** 17 Integration Test Groups/Cases (including concurrency)
- **Status:** PASSED
- **Coverage:** Groups A, B, C, D (Advanced), E (Configuration), F (Logging/Console), G (Perf), H (Persistence)

## Detailed Results

### Group A: Core Functionality (Port 65533)
| ID | Scenario | Result | Notes |
|----|----------|--------|-------|
| A-01 | Bank Code (BC) | **PASS** | Correctly identifies node. |
| A-02 | Account Creation (AC) | **PASS** | Creates accounts 10000-99999. |
| A-03 | AC Range Validation | **PASS** | Verified range for multiple creations. |
| A-04 | Deposit (AD) | **PASS** | Balance updates correctly. |
| A-05 | AD Negative | **PASS** | Rejected with ER. |
| A-06 | Withdrawal (AW) | **PASS** | Balance decreases correctly. |
| A-07 | AW Insufficient | **PASS** | Rejected with ER. |
| A-08 | Account Balance (AB) | **PASS** | Verified in AD/AW flows. |
| A-09 | Account Remove (AR) | **PASS** | Removed empty account. |
| A-10 | AR with Funds | **PASS** | Rejected removal of non-empty account. |
| A-11 | Bank Amount (BA) | **PASS** | Sums total funds correctly. |
| A-12 | Bank Number (BN) | **PASS** | Counts total accounts correctly. |
| A-13 | Proxy Access | **PASS** | Verified via `ScenarioGroupA_ProxyTests`. |
| A-14 | Remote Deposit | **PASS** | Verified via `ScenarioGroupA_ProxyTests`. |
| A-15 | Robbery Plan (RP) | **PASS** | Verified execution in `MixedScenarios_AdvancedTests`. |
| A-17 | Configuration (Port) | **PASS** | Verified via AppConfig validation exception test. |
| A-20 | Case Sensitivity | **PASS** | Verified `bc` and `Bc` work (`MixedScenarios_ConfigurationTests`). |

### Group B: Features & Constraints (Port 65532 / 65526 / 65527)
| ID | Scenario | Result | Notes |
|----|----------|--------|-------|
| B-02 | Setup EN | **PASS** | `LANG en` confirmed via config check. |
| B-03 | Setup CS | **PASS** | `LANG cs` changes error messages ("Neznámý příkaz"). |
| B-04 | LANG List | **PASS** | Lists en, cs. |
| B-05 | HELP | **PASS** | Lists available commands. |
| B-06 | Console (BN) | **PASS** | Verified via `ScenarioGroupB_ConsoleLogicTests`. |
| B-07 | Console (LOG) | **PASS** | Verified via `ScenarioGroupB_ConsoleLogicTests`. |
| B-08 | Hot Reload | **PASS** | Verified via `MixedScenarios_ConfigurationTests`. |
| B-09 | Request Logging | **PASS** | verified via `RequestLoggingDecorator` usage in `ScenarioGroupB_LoggingTests`. |
| B-10 | Did you mean? | **PASS** | Suggests AC for ACCC. |
| B-11 | Atomic Writes | **PASS** | Verified Recovery in `ScenarioGroupB_PersistenceTests`. |
| B-12 | IPv6/Format | **PASS** | Address parsing verified in Proxy tests. |
| B-13 | Connection Pool | **PASS** | Verified Performance Improvement (`ScenarioGroupB_PerformanceTests`). |
| B-14 | Rate Limiting | **PASS** | Verified 10/min limit enforcement in `MixedScenarios_ConfigurationTests`. |
| B-15 | Health Check (Metrics) | **PASS** | `HC` returns JSON with Uptime/Requests (`ScenarioGroupB_LoggingTests`). |
| B-16 | BACKUP | **PASS** | Created backup file (`MixedScenarios_AdvancedTests`). |
| B-17 | RESTORE | **PASS** | Restored from file (`MixedScenarios_AdvancedTests`). |
| B-18 | Max Connections | **PASS** | Verified enforcement (Queueing behavior confirmed in `MixedScenarios_ConfigurationTests`). |
| B-19 | Idle Timeout | **PASS** | Verified disconnect after timeout (`MixedScenarios_ConfigurationTests`). |
| B-20 | HISTORY | **PASS** | Verified session command history (`MixedScenarios_AdvancedTests`). |
| B-21 | EXECUTE | **PASS** | Executed script file (`MixedScenarios_AdvancedTests`). |
| B-22 | Max Length | **PASS** | Rejected 2KB command (`MixedScenarios_ConfigurationTests`). |
| B-23 | Strict Range | **PASS** | Verified invalid account format rejection. |
| B-24 | Dockerfile | **PASS** | Verified existence of Dockerfile. |
| B-25 | Kubernetes | **PASS** | Verified existence of deployment.yaml. |
