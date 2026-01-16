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

To test on a single device, you must simulate the "other node" because the current implementation limits a single node to one listening port and assumes outgoing connections use that same port config.

### A. Testing Server Logic (Using Telnet)
You can test how your node handles requests from "others" by using Telnet to act as the second node.

1.  **Start your Node**
    ```bash
    dotnet run -- --port 65525
    ```

2.  **Connect with Telnet**
    Open a new terminal and run:
    ```bash
    telnet localhost 65525
    ```

3.  **Send Remote Commands**
    You are now the "client". You can send commands as if you were another node.
    ```
    AC
    AD 10001/127.0.0.1 500
    ```
    *(Note: Since you are connecting to localhost, your node treats `127.0.0.1` as "Local" so it processes it directly. To test Proxy logic, you'd need the node to believe the IP is remote, but that requires code changes).*

### B. Testing Two Nodes locally (Requires Code Change)
**Limitation**: The current code uses `_config.Port` (e.g., 65525) for *outgoing* connections. If you run Node B on 65526, Node A will still try to contact it on 65525 (Node A's port) unless you modify `NetworkClient.cs`.

**Workaround**:
If you need to test full P2P interaction on one machine:
1.  Run Node A on 65525.
2.  Run Node B on 65526.
3.  **Code Change Required**: You would need to update `ParseAccount` (in `AccountCommandStrategy.cs`) to allow `IP:Port` syntax (e.g. `127.0.0.1:65526`) and update `NetworkClient` to respect it.

For unmodifed code, use **Option 1**.
