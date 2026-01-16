using System;
using System.IO;
using Microsoft.Extensions.Logging;

namespace BankNode.Shared.Logging
{
    public class FileLogger : Microsoft.Extensions.Logging.ILogger
    {
        private readonly string _name;
        private readonly string _filePath;
        private static readonly object _lock = new object();

        public FileLogger(string name, string filePath)
        {
            _name = name;
            _filePath = filePath;
        }

        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => default;

        public bool IsEnabled(LogLevel logLevel) => logLevel != LogLevel.None;

        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
        {
            if (!IsEnabled(logLevel))
            {
                return;
            }

            var message = formatter(state, exception);
            var logRecord = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] [{logLevel}] [{_name}] {message}";

            if (exception != null)
            {
                logRecord += Environment.NewLine + exception.ToString();
            }

            lock (_lock)
            {
                try
                {
                    File.AppendAllText(_filePath, logRecord + Environment.NewLine);
                }
                catch
                {
                    // Fail silently or write to console fallback
                }
            }
        }
    }
}
