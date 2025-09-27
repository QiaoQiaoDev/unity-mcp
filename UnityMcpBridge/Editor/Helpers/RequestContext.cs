using System;
using System.Threading;

namespace MCPForUnity.Editor.Helpers
{
    /// <summary>
    /// Maintains request-scoped data (currently just the MCP request id) using AsyncLocal.
    /// </summary>
    internal static class RequestContext
    {
        private static readonly AsyncLocal<string> CurrentId = new();

        public static string CurrentRequestId => CurrentId.Value;

        public static IDisposable Push(string requestId)
        {
            string previous = CurrentId.Value;
            CurrentId.Value = string.IsNullOrWhiteSpace(requestId) ? null : requestId;
            return new Popper(previous);
        }

        private sealed class Popper : IDisposable
        {
            private readonly string _previous;
            private bool _disposed;

            public Popper(string previous)
            {
                _previous = previous;
            }

            public void Dispose()
            {
                if (_disposed)
                {
                    return;
                }

                CurrentId.Value = _previous;
                _disposed = true;
            }
        }
    }
}
