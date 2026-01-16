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
                foreach (var ip in host.AddressList)
                {
                    if (ip.AddressFamily == AddressFamily.InterNetwork)
                    {
                        return ip.ToString();
                    }
                }
            }
            catch
            {
                // Fallback
            }
            return "127.0.0.1";
        }
    }
}
