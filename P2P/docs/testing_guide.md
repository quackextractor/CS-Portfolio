# P2P Testing Guide

This guide explains how to test the P2P Bank Node functionality using multiple devices or a single device.

## Option 1: Testing with Multiple Devices (Recommended)

This interacts with the P2P logic exactly as intended in a real network.

### Prerequisites
- Two computers (or VMs) on the same local network (e.g., connected to the same Wi-Fi).
- Both computers must have the .NET 8.0 SDK installed.
- Firewall on both computers must allow incoming connections on port `65525` (or the port you choose).

### Steps

1.  **Determine IP Addresses**
    -   On **Device A**, run `ipconfig` (Windows) or `ifconfig` (Linux/Mac) and note the IPv4 address (e.g., `192.168.1.5`).
    -   On **Device B**, do the same (e.g., `192.168.1.6`).

2.  **Start the Nodes**
    -   On **Device A**:
        ```bash
        cd src/BankNode.App
        dotnet run -- --port 65525
        ```
    -   On **Device B**:
        ```bash
        cd src/BankNode.App
        dotnet run -- --port 65525
        ```
    -   *Note: Both can use the same port since they are on different IPs.*

3.  **Verify Node IP**
    -   On both devices, type `BC` and press Enter. The node should reply with its IP. Ensure it matches the LAN IP you found in Step 1.

4.  **Execute P2P Transaction**
    -   **On Device A**: Create an account.
        ```
        AC
        ```
        > Response: `AC 10001/192.168.1.5` (Example)
    
    -   **On Device B**: Send money to Device A's account.
        ```
        AD 10001/192.168.1.5 500
        ```
        > If successful, Device B connects to Device A, sends the command, and Device A processes it.
        > Response: `AD`

5.  **Verify Balance**
    -   **On Device B** (or Device A): Check balance remotely.
        ```
        AB 10001/192.168.1.5
        ```
        > Response: `AB 500`

---

## Option 2: Testing on a Single Device

To test on a single device, you can run multiple instances of the node on different ports and have them communicate with each other.

### 1. Start Two Nodes
Open two separate terminal windows.

**Terminal 1 (Node A):**
```bash
cd src/BankNode.App
dotnet run -- --port 65525
```

**Terminal 2 (Node B):**
```bash
cd src/BankNode.App
dotnet run -- --port 65526
```

### 2. Connect and Execute Transactions
We will now send commands from **Node A** (65525) to **Node B** (65526).

1.  Open a Telnet session (or use a third terminal) to **Node A**:
    ```bash
    telnet localhost 65525
    ```

2.  **Create an Account**:
    ```
    AC
    ```
    > Response: `AC 10001/127.0.0.1` (or your LAN IP)

3.  **Send Money to Node B**:
    To send money to an account on Node B, you need to specify its port. Let's assume you want to deposit to account `20001` on Node B (which is running on 127.0.0.1:65526).

    ```
    AD 20001/127.0.0.1:65526 500
    ```
    *(Note the `:65526` at the end of the IP)*

    > Node A will recognize the different port and forward the request to Node B.
    > Response: `AD`

### 3. Verify
You can verify the balance on Node B by checking it from Node A (or by connecting directly to Node B).

**From Node A (Proxy check):**
```
AB 20001/127.0.0.1:65526
```
> Response: `AB 500`

This confirms that Node A successfully communicated with Node B running on a different port.

---

---

## Option 4: Automated Testing & CI/CD

To run the full suite of automated tests, use the standard dotnet test runner. This is recommended for verifying all functional requirements including thread safety and internationalization.

### Running Tests locally
```bash
dotnet test src/
```

### Example Test Script (PowerShell)
You can use a simple script to run tests and build the project, useful for pre-commit checks:
```powershell
Write-Host "Building Project..."
dotnet build src/BankNode.sln
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Running Tests..."
dotnet test src/BankNode.sln
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Success!"
```

---

## Appendix: Connecting via PuTTY or Telnet

To manually interact with a node (e.g., to send commands like `AC`, `BC`, `AD` manually), you need a raw TCP client.

### Using PuTTY (Windows)

1.  **Download PuTTY**: If you don't have it, download it from [putty.org](https://www.putty.org/).
2.  **Open PuTTY**.
3.  **Configure Session**:
    -   **Host Name (or IP address)**: Enter `localhost` (or the IP of the remote node).
    -   **Port**: Enter the port the node is listening on (e.g., `65525`).
    -   **Connection type**: Select **Raw**.
4.  **Connect**: Click **Open**.
5.  **Usage**: A black terminal window will open. You can now type commands like `BC` and press Enter.

### Using Telnet (Windows/Linux/Mac)

**Windows Note**: You may need to enable the Telnet Client feature in "Turn Windows features on or off".

1.  Open your terminal or command prompt.
2.  Run the telnet command:
    ```bash
    telnet <host> <port>
    ```
    Example:
    ```bash
    telnet localhost 65525
    ```
3.  **Usage**: Once connected, you can type commands like `BC` and press Enter.

---

## Option 3: Testing Localization

To test language switching:

1.  **Stop the Node** if running.
2.  **Edit `config.json`**: Change `"Language"` to `"cs"` (Czech) or back to `"en"` (English).
    ```json
    {
       ...
       "Language": "cs"
    }
    ```
3.  **Start the Node**: `dotnet run`
4.  **Connect and Verify**:
    -   Connect via Telnet/PuTTY.
    -   Type `HELP`.
    -   **Expected Result**:
        -   If `"en"`, you see "Available Commands".
        -   If `"cs"`, you see "Dostupné příkazy".
    -   Type an invalid command (e.g., `XYZ`).
        -   **Expected Result**:
            -   If `"en"`, "ER Unknown command."
            -   If `"cs"`, "ER Neznámý příkaz."
