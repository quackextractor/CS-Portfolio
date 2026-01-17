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
        public int RobberyConcurrency { get; set; } = 20;
        public int RateLimit { get; set; } = 60;
        public int MaxConcurrentConnections { get; set; } = 100;
        public int ClientIdleTimeout { get; set; } = 300000; // 5 minutes default

        private FileSystemWatcher? _watcher;
        private DateTime _lastRead = DateTime.MinValue;

        public void Load()
        {
            LoadFromFile();

            // Setup Hot Reload
            SetupWatcher();

            // If NodeIp is still default loopback, try to auto-detect
            if (NodeIp == "127.0.0.1")
            {
                NodeIp = GetLocalIpAddress();
            }

            ValidateConfiguration();
        }

        private void ValidateConfiguration()
        {
            if (Port < 65525 || Port > 65535)
                throw new ArgumentException($"Port must be between 65525 and 65535, got {Port}");
            
            if (Timeout <= 0)
                throw new ArgumentException($"Timeout must be positive, got {Timeout}");
            
            if (RobberyConcurrency <= 0 || RobberyConcurrency > 100)
                throw new ArgumentException($"RobberyConcurrency must be between 1 and 100, got {RobberyConcurrency}");
            
            if (RateLimit <= 0)
                throw new ArgumentException($"RateLimit must be positive, got {RateLimit}");

            if (MaxConcurrentConnections <= 0)
                throw new ArgumentException($"MaxConcurrentConnections must be positive, got {MaxConcurrentConnections}");
            
            if (ClientIdleTimeout <= 0)
                throw new ArgumentException($"ClientIdleTimeout must be positive, got {ClientIdleTimeout}");
        }

        private void LoadFromFile()
        {
            if (File.Exists("config.json"))
            {
                try
                {
                    // Debounce
                    if (DateTime.Now - _lastRead < TimeSpan.FromSeconds(1)) return;

                    // Retry logic for file lock
                    for (int i = 0; i < 3; i++)
                    {
                        try
                        {
                            var json = File.ReadAllText("config.json");
                            var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                            var loadedConfig = JsonSerializer.Deserialize<AppConfig>(json, options);
                            
                            if (loadedConfig != null)
                            {
                                // Only update runtime-safe properties
                                Timeout = loadedConfig.Timeout;
                                Language = loadedConfig.Language ?? "en";
                                RobberyConcurrency = loadedConfig.RobberyConcurrency > 0 ? loadedConfig.RobberyConcurrency : 20;
                                RateLimit = loadedConfig.RateLimit > 0 ? loadedConfig.RateLimit : 60;
                                MaxConcurrentConnections = loadedConfig.MaxConcurrentConnections > 0 ? loadedConfig.MaxConcurrentConnections : 100;
                                ClientIdleTimeout = loadedConfig.ClientIdleTimeout > 0 ? loadedConfig.ClientIdleTimeout : 300000;

                                // Note: Port and NodeIp usually require restart, so we might skip them or log a warning if they changed
                                Console.WriteLine($"Config reloaded. Timeout: {Timeout}, Language: {Language}");
                            }
                            _lastRead = DateTime.Now;
                            break;
                        }
                        catch (IOException)
                        {
                            System.Threading.Thread.Sleep(100);
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading config.json: {ex.Message}");
                }
            }
        }

        private void SetupWatcher()
        {
            if (_watcher != null) return;

            var path = Directory.GetCurrentDirectory();
            _watcher = new FileSystemWatcher(path, "config.json");
            _watcher.NotifyFilter = NotifyFilters.LastWrite;
            _watcher.Changed += (s, e) => LoadFromFile();
            _watcher.EnableRaisingEvents = true;
        }

        public void Save()
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(this, options);
                
                // Disable watcher briefly to prevent self-trigger loop? 
                // Actually debounce handles it mostly, but good practice
                if (_watcher != null) _watcher.EnableRaisingEvents = false;
                
                File.WriteAllText("config.json", json);
                
                if (_watcher != null) _watcher.EnableRaisingEvents = true;
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

                Console.WriteLine("Warning: Node visible only to localhost (127.0.0.1).");
                return "127.0.0.1";
            }
            catch
            {
                Console.WriteLine("Warning: Node visible only to localhost (127.0.0.1).");
                return "127.0.0.1";
            }
        }
    }
}
