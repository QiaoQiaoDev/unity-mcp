using System.IO;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Settings
{
    internal static class McpSettingsProvider
    {
        private const string AssetPath = "Assets/Settings/McpSettings.asset";
        private static McpSettings _cached;

        public static McpSettings Settings
        {
            get
            {
                if (_cached == null)
                {
                    _cached = LoadOrCreate();
                }

                return _cached;
            }
        }

        private static McpSettings LoadOrCreate()
        {
            var settings = AssetDatabase.LoadAssetAtPath<McpSettings>(AssetPath);
            if (settings != null)
            {
                return settings;
            }

            // Ensure the parent folder exists so users can create the asset easily later.
            string directory = Path.GetDirectoryName(AssetPath);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            settings = ScriptableObject.CreateInstance<McpSettings>();
            settings.hideFlags = HideFlags.HideAndDontSave;
            return settings;
        }
    }
}
