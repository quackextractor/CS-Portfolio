namespace BankNode.App.Config
{
    public class AppConfig
    {
        public int Port { get; set; } = 65525;
        public int TimeoutMs { get; set; } = 5000;
        public string NodeIp { get; set; }
    }
}
