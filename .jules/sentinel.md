## 2024-06-01 - [Leakage of API key in API payload]
**Vulnerability:** The API key was being leaked as a URL parameter in the `url` field of the payload returned by the `/v1/models/catalog` and `/v1/models` endpoints, and in stdout when starting a tunnel or displaying graphics.
**Learning:** Returning constructed URLs that contain authentication credentials in standard API responses or displaying them via CLI output can lead to credential leakage if the response is logged, cached, or displayed.
**Prevention:** Do not embed API keys directly in URLs meant for sharing or display. If necessary, use alternative methods (like short-lived tokens, passing via headers, or relying on the user to provide the key separately) to authorize the intended user interface or application.
