using MCPForUnity.Editor.Settings;
using NUnit.Framework;
using UnityEngine;

namespace MCPForUnity.Tests.EditMode.Helpers
{
    public static class McpSettingsTests
    {
        [Test]
        public static void SettingsProviderReturnsDefaults()
        {
            var settings = McpSettingsProvider.Settings;
            Assert.IsNotNull(settings);
            Assert.Greater(settings.defaultUnityPort, 0);
            Assert.Greater(settings.responseTimeoutSeconds, 0f);
        }

        [Test]
        public static void SettingsHideFlagsPreventAssetCreation()
        {
            var settings = McpSettingsProvider.Settings;
            Assert.AreEqual(HideFlags.HideAndDontSave, settings.hideFlags);
        }
    }
}
