#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
#if UNITY_RENDER_PIPELINE_UNIVERSAL
using UnityEngine.Rendering.Universal;
#endif

namespace GiantFight.Editor
{
    /// <summary>
    /// Keeps project-level settings aligned with the giant fighter sample (Input System + URP + mac-first focus).
    /// Execution happens in the editor so the runtime build stays lean.
    /// </summary>
    [InitializeOnLoad]
    public static class GiantFightProjectSetup
    {
        private const string MenuRoot = "Tools/Giant Fight/";
        private const string SettingsFolder = "Assets/Settings";
        private const string UrpAssetPath = SettingsFolder + "/GiantFightURP.asset";

        static GiantFightProjectSetup()
        {
            EnsureInputPipelineSettings();
        }

        private static void EnsureInputPipelineSettings()
        {
#if UNITY_2021_3_OR_NEWER
            if (PlayerSettings.activeInputHandler != PlayerSettingsActiveInputHandler.Both)
            {
                PlayerSettings.activeInputHandler = PlayerSettingsActiveInputHandler.Both;
                Debug.Log("[GiantFight] Active Input Handler set to Both so the new Input System runs alongside the legacy manager.");
            }
#endif
            if (PlayerSettings.colorSpace != ColorSpace.Linear)
            {
                PlayerSettings.colorSpace = ColorSpace.Linear;
            }
        }

        [MenuItem(MenuRoot + "Ensure URP Pipeline Asset", priority = 0)]
        private static void EnsureUrpPipeline()
        {
#if UNITY_RENDER_PIPELINE_UNIVERSAL
            if (!AssetDatabase.IsValidFolder(SettingsFolder))
            {
                AssetDatabase.CreateFolder("Assets", "Settings");
            }

            var pipelineAsset = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(UrpAssetPath);
            if (pipelineAsset == null)
            {
                pipelineAsset = ScriptableObject.CreateInstance<UniversalRenderPipelineAsset>();
                AssetDatabase.CreateAsset(pipelineAsset, UrpAssetPath);
                AssetDatabase.SaveAssets();
                Debug.Log($"[GiantFight] Created URP asset at {UrpAssetPath}. Use the URP inspector to fine-tune quality tiers.");
            }

            if (GraphicsSettings.defaultRenderPipeline != pipelineAsset)
            {
                GraphicsSettings.defaultRenderPipeline = pipelineAsset;
                Debug.Log("[GiantFight] Assigned URP asset as the active render pipeline.");
            }
#else
            Debug.LogWarning("Install the Universal Render Pipeline package (com.unity.render-pipelines.universal) before running this command.");
#endif
        }

        [MenuItem(MenuRoot + "Open Control Scheme Docs", priority = 50)]
        private static void OpenDocs()
        {
            Application.OpenURL("https://docs.unity3d.com/Packages/com.unity.inputsystem@1.14/manual/Actions.html");
        }
    }
}
#endif
