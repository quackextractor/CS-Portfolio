using System.Net;
using System.Net.Sockets;

namespace BankNode.Shared
{
    public class AppConfig
    {
        public int Port { get; set; } = 65525;
        public int Timeout { get; set; } = 5000;
        public string NodeIp { get; set; } = "127.0.0.1";

        public void Load()
        {
            // Simple logic to detect IP if not set, or loading from args could go here.
            // For now, we default to loopback or try to find a real IP.
            NodeIp = GetLocalIpAddress();
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
