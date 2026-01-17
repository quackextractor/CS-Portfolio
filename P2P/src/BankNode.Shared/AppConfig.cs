using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Net.NetworkInformation;
using System.Text.Json;

namespace BankNode.Shared
{
    public class AppConfig
    {
        public int Port { get; set; } = 65525;
        public int Timeout { get; set; } = 5000;
        public string NodeIp { get; set; } = "127.0.0.1";
        public string Language { get; set; } = "en";

        public void Load()
        {
            if (File.Exists("config.json"))
            {
                try
                {
                    var json = File.ReadAllText("config.json");
                    var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                    var loadedConfig = JsonSerializer.Deserialize<AppConfig>(json, options);
                    
                    if (loadedConfig != null)
                    {
                        Port = loadedConfig.Port;
                        Timeout = loadedConfig.Timeout;
                        // Only override NodeIp if it's explicitly set in the config file
                        if (!string.IsNullOrEmpty(loadedConfig.NodeIp) && loadedConfig.NodeIp != "127.0.0.1")
                        {
                            NodeIp = loadedConfig.NodeIp;
                        }
                        Language = loadedConfig.Language ?? "en";
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading config.json: {ex.Message}");
                }
            }

            // If NodeIp is still default loopback, try to auto-detect
            if (NodeIp == "127.0.0.1")
            {
                NodeIp = GetLocalIpAddress();
            }
        }

        public void Save()
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(this, options);
                File.WriteAllText("config.json", json);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error saving config.json: {ex.Message}");
            }
        }

        private string GetLocalIpAddress()
        {
            try
            {
                // First try to use NetworkInterfaces to find an active connection
                var interfaces = NetworkInterface.GetAllNetworkInterfaces()
                    .Where(ni => ni.OperationalStatus == OperationalStatus.Up && 
                                 ni.NetworkInterfaceType != NetworkInterfaceType.Loopback)
                    .OrderByDescending(ni => ni.NetworkInterfaceType == NetworkInterfaceType.Ethernet)
                    .ThenByDescending(ni => ni.NetworkInterfaceType == NetworkInterfaceType.Wireless80211)
                    .ToList();

                foreach (var ni in interfaces)
                {
                    var props = ni.GetIPProperties();
                    foreach (var ip in props.UnicastAddresses)
                    {
                        if (ip.Address.AddressFamily == AddressFamily.InterNetwork)
                        {
                            var ipStr = ip.Address.ToString();
                            
                            // Ignore link-local (169.254.x.x)
                            if (ipStr.StartsWith("169.254.")) continue;

                            return ipStr;
                        }
                    }
                }

                // Fallback to simpler DNS method if NetworkInterface fails
                var host = Dns.GetHostEntry(Dns.GetHostName());
                foreach (var ip in host.AddressList)
                {
                    if (ip.AddressFamily == AddressFamily.InterNetwork)
                    {
                        var ipStr = ip.ToString();
                        if (!ipStr.StartsWith("169.254.") && ipStr != "127.0.0.1") return ipStr;
                    }
                }

                return "127.0.0.1";
            }
            catch
            {
                return "127.0.0.1";
            }
        }
    }
}
