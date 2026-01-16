using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
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

        private string GetLocalIpAddress()
        {
            try
            {
                var host = Dns.GetHostEntry(Dns.GetHostName());
                string? bestIp = null;
                int bestScore = 0;

                foreach (var ip in host.AddressList)
                {
                    if (ip.AddressFamily == AddressFamily.InterNetwork)
                    {
                        var ipStr = ip.ToString();
                        int score = 0;

                        if (ipStr.StartsWith("192.168.")) score = 3;
                        else if (ipStr.StartsWith("10.")) score = 2;
                        else if (ipStr.StartsWith("172.")) score = 1; // Simplification for 172.16-31 range
                        
                        // Ignore link-local
                        if (ipStr.StartsWith("169.254.")) continue;

                        if (score >= bestScore)
                        {
                            bestScore = score;
                            bestIp = ipStr;
                        }
                    }
                }

                return bestIp ?? "127.0.0.1";
            }
            catch
            {
                return "127.0.0.1";
            }
        }
    }
}
