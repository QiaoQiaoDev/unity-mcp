using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Settings
{
    [CreateAssetMenu(fileName = "McpSettings", menuName = "MCP/Mcp Settings", order = 10)]
    internal sealed class McpSettings : ScriptableObject
    {
        [Header("Ports")]
        public int defaultUnityPort = 6400;
        public int serverPort = 6500;

        [Header("Timeouts (seconds)")]
        public float connectionTimeoutSeconds = 1.0f;
        public float responseTimeoutSeconds = 30.0f;

        [Header("Telemetry")]
        public bool telemetryEnabled = true;

        [Header("Permissions")]
        public bool allowDestructiveOperations = true;
    }
}
