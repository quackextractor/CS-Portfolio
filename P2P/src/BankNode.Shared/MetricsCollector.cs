using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Linq;
using System.Threading;

namespace BankNode.Shared
{
    public class MetricsCollector
    {
        private static readonly Lazy<MetricsCollector> _instance = new(() => new MetricsCollector());
        public static MetricsCollector Instance => _instance.Value;
        
        private readonly ConcurrentDictionary<string, int> _commandCounts = new();
        private long _totalRequests;
        private long _failedRequests;
        
        public void RecordCommand(string commandCode, bool success)
        {
            Interlocked.Increment(ref _totalRequests);
            if (!success) Interlocked.Increment(ref _failedRequests);
            
            _commandCounts.AddOrUpdate(
                commandCode, 
                1, 
                (_, current) => current + 1);
        }
        
        public object GetMetrics()
        {
            return new
            {
                Uptime = DateTime.UtcNow - Process.GetCurrentProcess().StartTime,
                TotalRequests = Interlocked.Read(ref _totalRequests),
                FailedRequests = Interlocked.Read(ref _failedRequests),
                SuccessRate = _totalRequests > 0 ? (1 - (double)_failedRequests / _totalRequests) * 100 : 100,
                CommandDistribution = _commandCounts.ToDictionary(k => k.Key, v => v.Value),
                MemoryMB = Process.GetCurrentProcess().WorkingSet64 / 1024 / 1024,
                Threads = Process.GetCurrentProcess().Threads.Count
            };
        }
    }
}
