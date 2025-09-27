using UnityEngine;
using Unity.Cinemachine;

namespace GiantFight
{
    /// <summary>
    /// Bootstraps a lightweight third-person training ring showing right-stick driven attacks and camera focus.
    /// The setup deliberately uses runtime instantiation so the sample scene remains editor-neutral.
    /// </summary>
    public sealed class GiantFightRuntimeBootstrap : MonoBehaviour
    {
        private const float MoveSpeed = 6.5f;
        private const float CameraDistance = 18f;
        private const float CameraHeight = 8f;
        private const float FightFocusHeight = 4.5f;
        private const float MinPitch = 12f;
        private const float MaxPitch = 65f;

        private GiantFightInputActions _input;
        private Transform _fighterRoot;
        private CinemachineVirtualCamera _virtualCamera;
        private float _yaw = 135f;
        private float _pitch = 28f;
        private Vector3 _lastFightVector = new Vector3(0f, 0f, 1f);

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void RuntimeInit()
        {
            var go = new GameObject("GiantFightRuntimeBootstrap");
            DontDestroyOnLoad(go);
            go.AddComponent<GiantFightRuntimeBootstrap>();
        }

        private void Awake()
        {
            _input = new GiantFightInputActions();
            _input.Enable();

            _fighterRoot = BuildFighterAvatar();
            SetupCinemachine();

            _input.GuardPerformed += OnGuard;
            _input.DashPerformed += OnDash;
            _input.SpecialPerformed += OnSpecial;
        }

        private void OnDestroy()
        {
            if (_input != null)
            {
                _input.GuardPerformed -= OnGuard;
                _input.DashPerformed -= OnDash;
                _input.SpecialPerformed -= OnSpecial;
                _input.Dispose();
                _input = null;
            }
        }

        private Transform BuildFighterAvatar()
        {
            var root = new GameObject("GiantFighter").transform;
            root.position = new Vector3(0f, 0f, 0f);

            var body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            body.name = "Body";
            body.transform.SetParent(root, false);
            body.transform.localScale = new Vector3(2.6f, 4.2f, 2.4f);
            body.GetComponent<Renderer>().material.color = new Color(0.12f, 0.32f, 0.58f, 1f);
            Destroy(body.GetComponent<Collider>());

            var glove = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            glove.name = "RightGlove";
            glove.transform.SetParent(root, false);
            glove.transform.localScale = new Vector3(1.2f, 1.2f, 1.2f);
            glove.transform.localPosition = new Vector3(1.8f, 3.5f, 0.8f);
            glove.GetComponent<Renderer>().material.color = new Color(0.8f, 0.14f, 0.18f, 1f);
            Destroy(glove.GetComponent<Collider>());

            var marker = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            marker.name = "ArenaMarker";
            marker.transform.SetParent(root, false);
            marker.transform.localScale = new Vector3(7f, 0.05f, 7f);
            marker.transform.localPosition = Vector3.zero;
            marker.GetComponent<Renderer>().material.color = new Color(0.25f, 0.27f, 0.32f, 0.35f);
            Destroy(marker.GetComponent<Collider>());

            return root;
        }

        private void SetupCinemachine()
        {
            var mainCamera = Camera.main;
            if (mainCamera == null)
            {
                mainCamera = new GameObject("Main Camera").AddComponent<Camera>();
                mainCamera.tag = "MainCamera";
                mainCamera.clearFlags = CameraClearFlags.Skybox;
            }

            if (!mainCamera.TryGetComponent(out CinemachineBrain brain))
            {
                brain = mainCamera.gameObject.AddComponent<CinemachineBrain>();
            }

            var rigRoot = new GameObject("GiantFight VCam");
            rigRoot.transform.SetParent(transform, false);
            _virtualCamera = rigRoot.AddComponent<CinemachineVirtualCamera>();
            _virtualCamera.Priority = 100;
            _virtualCamera.Follow = _fighterRoot;
            _virtualCamera.LookAt = _fighterRoot;
            _virtualCamera.m_Lens.FieldOfView = 52f;

            UpdateCameraTransform();
        }

        private void Update()
        {
            if (_input == null)
            {
                return;
            }

            var move = _input.Move;
            if (move.sqrMagnitude > 0.0001f)
            {
                // Move relative to the current camera heading so inputs feel natural.
                var cameraForward = Quaternion.Euler(0f, _yaw, 0f) * new Vector3(move.x, 0f, move.y).normalized;
                _fighterRoot.position += cameraForward * (MoveSpeed * Time.deltaTime);
            }

            var fight = _input.FightDirection;
            var fightSqr = fight.sqrMagnitude;
            if (fightSqr > 0.02f)
            {
                _lastFightVector = new Vector3(fight.x, 0f, fight.y).normalized;
                var desiredRotation = Quaternion.LookRotation(_lastFightVector, Vector3.up);
                _fighterRoot.rotation = Quaternion.Slerp(_fighterRoot.rotation, desiredRotation, Time.deltaTime * 9f);

                // Right stick also biases the camera heading so the player always sees the fists.
                _yaw = Mathf.Atan2(_lastFightVector.x, _lastFightVector.z) * Mathf.Rad2Deg;
            }

            // Small damping so the camera keeps some inertia.
            _yaw = Mathf.Repeat(_yaw, 360f);
            _pitch = Mathf.Clamp(_pitch + Time.deltaTime * -fight.y * 25f, MinPitch, MaxPitch);

            UpdateCameraTransform();
        }

        private void UpdateCameraTransform()
        {
            if (_virtualCamera == null)
            {
                return;
            }

            var heading = Quaternion.Euler(_pitch, _yaw, 0f);
            var offset = heading * new Vector3(0f, 0f, -CameraDistance);
            var focus = _fighterRoot.position + Vector3.up * FightFocusHeight;
            _virtualCamera.transform.position = focus + offset + Vector3.up * (CameraHeight - FightFocusHeight);
            _virtualCamera.transform.LookAt(focus);
        }

        private void OnGuard()
        {
            Debug.Log("[GiantFight] Guard raised — block incoming hits.");
        }

        private void OnDash()
        {
            Debug.Log("[GiantFight] Dash triggered — short burst movement.");
        }

        private void OnSpecial()
        {
            Debug.Log("[GiantFight] Special attack primed — charge the reactor punch!");
        }
    }
}
