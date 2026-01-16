using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace BankNode.Network
{
    public class NetworkClient
    {
        private readonly int _defaultTimeout = 5000;

        public async Task<string> SendCommandAsync(string ip, int port, string command)
        {
            try
            {
                using var client = new TcpClient();
                var connectTask = client.ConnectAsync(ip, port);
                
                if (await Task.WhenAny(connectTask, Task.Delay(_defaultTimeout)) != connectTask)
                {
                     return "ER Connection timeout.";
                }
                await connectTask;

                using var stream = client.GetStream();
                stream.ReadTimeout = _defaultTimeout;
                stream.WriteTimeout = _defaultTimeout;

                using var writer = new StreamWriter(stream, Encoding.UTF8, leaveOpen: true) { AutoFlush = true };
                using var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true);

                await writer.WriteLineAsync(command);
                
                var readTask = reader.ReadLineAsync();
                if (await Task.WhenAny(readTask, Task.Delay(_defaultTimeout)) != readTask)
                {
                    return "ER Response timeout.";
                }
                
                var response = await readTask;
                return response ?? "ER No response.";
            }
            catch (Exception ex)
            {
                return $"ER Connection failed: {ex.Message}";
            }
        }
    }
}
