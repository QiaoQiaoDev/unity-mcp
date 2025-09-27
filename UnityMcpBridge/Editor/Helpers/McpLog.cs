using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Helpers
{
    internal static class McpLog
    {
        private const string Prefix = "<b><color=#2EA3FF>MCP-FOR-UNITY</color></b>:";
        private const string JsonPrefix = "[MCP] ";
        private static readonly bool JsonLogsEnabled;

        private static bool IsDebugEnabled()
        {
            try { return EditorPrefs.GetBool("MCPForUnity.DebugLogs", false); } catch { return false; }
        }

        static McpLog()
        {
            JsonLogsEnabled = DetermineJsonLogging();
        }

        private static bool DetermineJsonLogging()
        {
            bool plainText = ReadEnvFlag("LOG_PLAIN_TEXT", false);
            bool jsonEnabled = ReadEnvFlag("MCP_JSON_LOGS", false);
            return !plainText && jsonEnabled;
        }

        private static bool ReadEnvFlag(string name, bool defaultValue)
        {
            try
            {
                string value = Environment.GetEnvironmentVariable(name);
                if (string.IsNullOrWhiteSpace(value))
                {
                    return defaultValue;
                }

                switch (value.Trim().ToLowerInvariant())
                {
                    case "1":
                    case "true":
                    case "yes":
                    case "on":
                        return true;
                    case "0":
                    case "false":
                    case "no":
                    case "off":
                        return false;
                    default:
                        return defaultValue;
                }
            }
            catch
            {
                return defaultValue;
            }
        }

        private static string FormatMessage(string level, string message, Exception exception = null)
        {
            if (!JsonLogsEnabled)
            {
                return $"{Prefix} {message}";
            }

            var payload = new Dictionary<string, object>
            {
                ["timestamp"] = DateTime.UtcNow.ToString("O"),
                ["level"] = level,
                ["message"] = message,
                ["logger"] = "UnityMCP",
            };

            string requestId = RequestContext.CurrentRequestId;
            if (!string.IsNullOrEmpty(requestId))
            {
                payload["request_id"] = requestId;
            }

            if (exception != null)
            {
                payload["exception"] = exception.Message;
                payload["stackTrace"] = exception.StackTrace;
            }

            return JsonPrefix + JsonConvert.SerializeObject(payload);
        }

        public static void Info(string message, bool always = true)
        {
            if (!always && !IsDebugEnabled()) return;
            Debug.Log(FormatMessage("INFO", message));
        }

        public static void Warn(string message)
        {
            if (!JsonLogsEnabled)
            {
                Debug.LogWarning($"<color=#cc7a00>{Prefix} {message}</color>");
                return;
            }

            Debug.LogWarning(FormatMessage("WARNING", message));
        }

        public static void Error(string message)
        {
            if (!JsonLogsEnabled)
            {
                Debug.LogError($"<color=#cc3333>{Prefix} {message}</color>");
                return;
            }

            Debug.LogError(FormatMessage("ERROR", message));
        }
    }
}

