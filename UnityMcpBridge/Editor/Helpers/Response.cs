using System.Collections.Generic;
using MCPForUnity.Editor;

namespace MCPForUnity.Editor.Helpers
{
    /// <summary>
    /// Provides static methods for creating standardized success and error response objects.
    /// Ensures consistent JSON structure for communication back to the Python server.
    /// </summary>
    public static class Response
    {
        /// <summary>
        /// Creates a standardized success response object.
        /// </summary>
        /// <param name="message">A message describing the successful operation.</param>
        /// <param name="data">Optional additional data to include in the response.</param>
        /// <returns>An object representing the success response.</returns>
        public static object Success(string message, object data = null)
        {
            var payload = new Dictionary<string, object>
            {
                ["success"] = true,
                ["message"] = message,
            };

            if (data != null)
            {
                payload["data"] = data;
            }

            AttachRequestId(payload);
            return payload;
        }

        /// <summary>
        /// Creates a standardized error response object.
        /// </summary>
        /// <param name="errorCodeOrMessage">A message describing the error.</param>
        /// <param name="data">Optional additional data (e.g., error details) to include.</param>
        /// <returns>An object representing the error response.</returns>
        public static object Error(string errorCodeOrMessage, object data = null)
        {
            var payload = new Dictionary<string, object>
            {
                ["success"] = false,
                ["code"] = errorCodeOrMessage,
                ["error"] = errorCodeOrMessage,
            };

            if (data != null)
            {
                payload["data"] = data;
            }

            AttachRequestId(payload);
            return payload;
        }

        private static void AttachRequestId(IDictionary<string, object> payload)
        {
            string requestId = RequestContext.CurrentRequestId;
            if (!string.IsNullOrEmpty(requestId))
            {
                payload["requestId"] = requestId;
                payload["request_id"] = requestId;
            }
            payload["protocolVersion"] = MCPForUnityBridge.ProtocolVersion;
            payload["protocol_version"] = MCPForUnityBridge.ProtocolVersion;
        }
    }
}
