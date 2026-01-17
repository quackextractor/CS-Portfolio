using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;
using BankNode.Network;
using BankNode.Shared;
using Microsoft.Extensions.Logging;

namespace BankNode.App.Decorators
{
    public class RateLimitingDecorator : ICommandProcessor
    {
        private readonly ICommandProcessor _inner;
        private readonly ILogger<RateLimitingDecorator> _logger;
        private readonly AppConfig _config;
        private readonly ConcurrentDictionary<string, Queue<DateTime>> _requestHistory = new();
        
        public RateLimitingDecorator(ICommandProcessor inner, ILogger<RateLimitingDecorator> logger, AppConfig config)
        {
            _inner = inner;
            _logger = logger;
            _config = config;
        }

        public async Task<string> ProcessCommandAsync(string rawCommand, string clientIp)
        {
            if (!IsAllowed(clientIp))
            {
                _logger.LogWarning($"Rate limit exceeded for {clientIp}");
                return "ER Rate limit exceeded. Please wait before sending more commands.";
            }

            return await _inner.ProcessCommandAsync(rawCommand, clientIp);
        }

        private bool IsAllowed(string clientIp)
        {
            // Allow localhost or trusted IPs unlimited? Ideally no, rate limit everyone to prevent accidents.
            // But maybe higher limit for localhost? keeping simple for now.

            var now = DateTime.UtcNow;
            var windowStart = now.AddMinutes(-1);
            
            var history = _requestHistory.GetOrAdd(clientIp, _ => new Queue<DateTime>());
            
            lock (history)
            {
                // Clean old entries
                while (history.Count > 0 && history.Peek() < windowStart)
                {
                    history.Dequeue();
                }
                
                if (history.Count >= _config.RateLimit)
                {
                    return false;
                }
                
                history.Enqueue(now);
                return true;
            }
        }
    }
}
