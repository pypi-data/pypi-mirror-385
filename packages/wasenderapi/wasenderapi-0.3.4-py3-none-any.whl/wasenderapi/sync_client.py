import json
import time
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
import requests
from ._version import __version__ as SDK_VERSION
from .models import (
    BaseMessage,
    WasenderSuccessResponse,
    RateLimitInfo,
    WasenderSendResult,
    RetryConfig,
    WasenderOperationResult,
    UploadMediaFileResult,
    DecryptMediaResult,
    MessageInfoResult,
    CheckWhatsAppNumberResult
)
from .errors import WasenderAPIError
from .webhook import (
    WEBHOOK_SIGNATURE_HEADER,
    verify_wasender_webhook_signature,
    WasenderWebhookEvent
)
from .contacts import (
    GetAllContactsResult,
    GetContactInfoResult,
    GetContactProfilePictureResult,
    ContactActionResult
)
from .groups import (
    GetAllGroupsResult,
    GetGroupMetadataResult,
    GetGroupParticipantsResult,
    ModifyGroupParticipantsResult,
    ModifyGroupParticipantsPayload,
    UpdateGroupSettingsPayload,
    UpdateGroupSettingsResult,
    CreateGroupPayload,
    CreateGroupResult,
    UpdateGroupParticipantsPayload,
    UpdateGroupParticipantsResult,
    LeaveGroupResult,
    AcceptGroupInvitePayload,
    AcceptGroupInviteResult,
    GetGroupInviteInfoResult,
    GetGroupInviteLinkResult,
    GetGroupProfilePictureResult
)
from .sessions import (
    CreateWhatsAppSessionPayload,
    UpdateWhatsAppSessionPayload,
    GetAllWhatsAppSessionsResult,
    GetWhatsAppSessionDetailsResult,
    CreateWhatsAppSessionResult,
    UpdateWhatsAppSessionResult,
    DeleteWhatsAppSessionResult,
    ConnectSessionResult,
    GetQRCodeResult,
    DisconnectSessionResult,
    RegenerateApiKeyResult,
    GetSessionStatusResult
)
from pydantic import TypeAdapter

class WebhookRequestAdapter:
    def __init__(self, headers: Dict[str, str], body: str):
        self.headers = headers
        self.body = body

    def get_header(self, name: str) -> Optional[str]:
        return self.headers.get(name.lower())

    def get_raw_body(self) -> str:
        return self.body

class WasenderSyncClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.wasenderapi.com/api",
        retry_options: Optional[RetryConfig] = None,
        webhook_secret: Optional[str] = None,
        personal_access_token: Optional[str] = None
    ):
        if not api_key:
            raise ValueError("WASENDER_API_KEY is required to initialize the Wasender SDK.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.retry_config = retry_options if retry_options is not None else RetryConfig()
        self.webhook_secret = webhook_secret
        self.personal_access_token = personal_access_token

    def _parse_rate_limit_headers(self, headers: Dict[str, str]) -> RateLimitInfo:
        limit = headers.get("X-RateLimit-Limit")
        remaining = headers.get("X-RateLimit-Remaining")
        reset = headers.get("X-RateLimit-Reset")

        reset_timestamp = int(reset) if reset else None

        return RateLimitInfo(
            limit=int(limit) if limit else None,
            remaining=int(remaining) if remaining else None,
            reset_timestamp=reset_timestamp
        )

    def _request( 
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        use_personal_token: bool = False,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {
            "Accept": "application/json",
            "User-Agent": f"wasenderapi-python-sdk/{SDK_VERSION}"
        }

        if use_personal_token:
            if not self.personal_access_token:
                raise ValueError(
                    "This endpoint requires a personal access token. "
                    "Provide 'personal_access_token' when creating the client."
                )
            headers["Authorization"] = f"Bearer {self.personal_access_token}"
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"

        processed_body = body.copy() if body else None

        if processed_body and isinstance(processed_body, dict) and processed_body.get("messageType") == "location":
            location_payload = processed_body.get("location", {})
            if isinstance(location_payload.get("latitude"), str):
                location_payload["latitude"] = float(location_payload["latitude"])
            if isinstance(location_payload.get("longitude"), str):
                location_payload["longitude"] = float(location_payload["longitude"])

        request_options = {
            "method": method,
            "headers": headers,
            "url": url
        }

        if params:
            request_options["params"] = params

        if files:
            request_options["files"] = files

        if data is not None:
            request_options["data"] = data

        if method in ["POST", "PUT"] and not files and data is None:
            headers["Content-Type"] = "application/json"
            request_options["json"] = processed_body or {}
        elif processed_body and not files and data is None and method not in ["POST", "PUT"]:
            request_options["json"] = processed_body

        attempts = 0
        rate_limit_info: Optional[RateLimitInfo] = None

        while True:
            attempts += 1
            try:
                raw_response = requests.request(**request_options)
                
                if method == "POST" and path == "/send-message":
                    rate_limit_info = self._parse_rate_limit_headers(raw_response.headers)

                response_dict: Dict[str, Any] = {}

                if raw_response.status_code == 204:
                    response_content: Dict[str, Any]
                    if method == "DELETE" and path.startswith("/whatsapp-sessions/"):
                        response_content = {"success": True, "data": None}
                    elif (method == "POST" or method == "PUT") and ("block" in path or "unblock" in path or "participants" in path or "settings" in path):
                        action_message = "Action completed successfully."
                        if "block" in path: action_message = "Contact blocked/unblocked successfully."
                        if "participants" in path: action_message = "Participants modified successfully."
                        if "settings" in path: action_message = "Settings updated successfully."
                        response_content = {"success": True, "message": action_message, "data": { "message": action_message } }
                    else:
                        response_content = {"success": True, "message": "Operation successful, no content returned."}
                    
                    response_dict["response"] = response_content
                    if rate_limit_info:
                        response_dict["rate_limit"] = rate_limit_info
                    return response_dict

                response_body = raw_response.json()

                if not raw_response.ok:
                    error_response_data = response_body
                    
                    # Handle rate limiting with retry logic
                    if raw_response.status_code == 429:
                        if self.retry_config.enabled and attempts <= self.retry_config.max_retries:
                            # Get retry_after from response headers or body
                            retry_after = None
                            if 'Retry-After' in raw_response.headers:
                                try:
                                    retry_after = int(raw_response.headers['Retry-After'])
                                except ValueError:
                                    pass
                            elif error_response_data.get("retry_after"):
                                retry_after = error_response_data.get("retry_after")
                            
                            sleep_time = retry_after if retry_after is not None and retry_after > 0 else 1
                            time.sleep(sleep_time)
                            continue
                    
                    # If not rate limited or retries exhausted/disabled, raise the error
                    raise WasenderAPIError(
                        message=error_response_data.get("message", "API request failed"),
                        status_code=raw_response.status_code,
                        api_message=error_response_data.get("message"),
                        error_details=error_response_data.get("errors"),
                        rate_limit=rate_limit_info,                        retry_after=error_response_data.get("retry_after")
                    )
                
                response_dict["response"] = response_body
                if rate_limit_info:
                    response_dict["rate_limit"] = rate_limit_info
                return response_dict

            except WasenderAPIError as e:
                # If it's a rate limit error and we can retry, handle it
                if e.status_code == 429 and self.retry_config.enabled and attempts <= self.retry_config.max_retries:
                    sleep_time = e.retry_after if e.retry_after is not None and e.retry_after > 0 else 1
                    time.sleep(sleep_time)
                    continue
                else:
                    raise

            except requests.exceptions.RequestException as e:
                if attempts > self.retry_config.max_retries:
                    raise WasenderAPIError(message=f"Network error: {str(e)}", status_code=None) from e
                if not self.retry_config.enabled:
                    raise WasenderAPIError(message=f"Network error: {str(e)}", status_code=None) from e
                time.sleep(1)

            except json.JSONDecodeError as e:
                raise WasenderAPIError(
                    message="Failed to decode API response (not JSON).", 
                    status_code=raw_response.status_code,
                    api_message=raw_response.text
                ) from e

    def _post_internal(
        self,
        path: str,
        payload: Optional[Dict[str, Any]],
        use_personal_token: bool = False,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            path,
            body=payload,
            use_personal_token=use_personal_token,
            params=params,
            files=files,
            data=data
        )

    def _get_internal(
        self,
        path: str,
        use_personal_token: bool = False,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self._request("GET", path, use_personal_token=use_personal_token, params=params)

    def _put_internal(
        self,
        path: str,
        payload: Dict[str, Any],
        use_personal_token: bool = False,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self._request("PUT", path, body=payload, use_personal_token=use_personal_token, params=params)

    def _delete_internal(self, path: str, use_personal_token: bool = False) -> Dict[str, Any]:
        return self._request("DELETE", path, use_personal_token=use_personal_token)

    def send(self, payload: BaseMessage) -> WasenderSendResult:
        result = self._post_internal("/send-message", payload.model_dump(by_alias=True))
        return WasenderSendResult(**result)

    def send_text(self, to: str, text_body: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "text"
        payload["text"] = text_body
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_image(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "image"
        payload["imageUrl"] = url
        if caption:
            payload["text"] = caption
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_video(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "video"
        payload["videoUrl"] = url
        if caption:
            payload["text"] = caption
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_document(self, to: str, url: str, filename: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "document"
        payload["documentUrl"] = url
        payload["fileName"] = filename
        if caption:
            payload["text"] = caption
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_audio(self, to: str, url: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "audio"
        payload["audioUrl"] = url
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_sticker(self, to: str, url: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "sticker"
        payload["stickerUrl"] = url
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_contact(self, to: str, contact_name: str, contact_phone_number: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "contact"
        payload["contact"] = {"name": contact_name, "phone": contact_phone_number}
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_location(self, to: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "location"
        location_payload = {"latitude": latitude, "longitude": longitude}
        if name:
            location_payload["name"] = name
        if address:
            location_payload["address"] = address
        payload["location"] = location_payload
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)
    
    def send_poll(self,
        to: str,
        question: str,
        options: List[str],
        is_multiple_choice: bool = False,
    ) -> WasenderSendResult:
        payload: Dict[str, Any] = {
            "to": to,
            "messageType": "poll",
            "poll": {
                "question": question,
                "options": options,
                "multiSelect": is_multiple_choice
            }
        }
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_message_with_mentions(
        self,
        group_jid: str,
        text_body: str,
        mentions: List[str],
        **kwargs: Any
    ) -> WasenderSendResult:
        if not group_jid or not group_jid.endswith("@g.us"):
            raise ValueError("group_jid must be a valid WhatsApp group JID ending with '@g.us'.")
        if not text_body or not text_body.strip():
            raise ValueError("text_body must be a non-empty string.")
        if not mentions:
            raise ValueError("mentions must contain at least one participant JID.")
        if any(not isinstance(m, str) or not m.strip() for m in mentions):
            raise ValueError("mentions must contain only non-empty strings.")

        payload: Dict[str, Any] = {**kwargs}
        payload.update({
            "to": group_jid,
            "messageType": "text",
            "text": text_body,
            "mentions": mentions
        })
        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def send_quoted_message(
        self,
        to: str,
        reply_to: Optional[int] = None,
        *,
        text: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        **message_payload: Any
    ) -> WasenderSendResult:
        payload: Dict[str, Any] = {"to": to}

        if reply_to is not None:
            if not isinstance(reply_to, int) or reply_to <= 0:
                raise ValueError("reply_to must be a positive integer if provided.")
            payload["replyTo"] = reply_to

        if text is not None:
            if not text.strip():
                raise ValueError("text cannot be empty when provided.")
            payload["text"] = text

        if mentions is not None:
            if not mentions:
                raise ValueError("mentions must contain at least one entry when provided.")
            if any(not isinstance(m, str) or not m.strip() for m in mentions):
                raise ValueError("mentions must contain only non-empty strings.")
            payload["mentions"] = mentions

        payload.update(message_payload)

        inferred_type = payload.get("messageType")
        if not inferred_type:
            for field, message_type in [
                ("imageUrl", "image"),
                ("videoUrl", "video"),
                ("documentUrl", "document"),
                ("audioUrl", "audio"),
                ("stickerUrl", "sticker"),
                ("contact", "contact"),
                ("location", "location"),
            ]:
                if field in payload:
                    inferred_type = message_type
                    break

        if not inferred_type:
            inferred_type = "text"

        payload["messageType"] = inferred_type

        if inferred_type == "text" and "text" not in payload:
            raise ValueError("A text value must be provided for text reply messages.")

        result = self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    def edit_message(self, message_id: int, new_text: str) -> WasenderOperationResult:
        if message_id <= 0:
            raise ValueError("message_id must be a positive integer.")
        if not new_text or not new_text.strip():
            raise ValueError("new_text must be a non-empty string.")
        payload = {"text": new_text}
        result = self._put_internal(f"/messages/{message_id}", payload)
        return WasenderOperationResult(**result)

    def delete_message(self, message_id: int) -> WasenderOperationResult:
        if message_id <= 0:
            raise ValueError("message_id must be a positive integer.")
        result = self._delete_internal(f"/messages/{message_id}")
        return WasenderOperationResult(**result)

    def get_message_info(self, message_id: int) -> MessageInfoResult:
        if message_id <= 0:
            raise ValueError("message_id must be a positive integer.")
        result = self._get_internal(f"/messages/{message_id}/info")
        return MessageInfoResult(**result)

    def send_presence_update(
        self,
        jid: str,
        presence_type: str,
        delay_ms: Optional[int] = None
    ) -> WasenderOperationResult:
        allowed_types = {"composing", "recording", "available", "unavailable"}
        if presence_type not in allowed_types:
            raise ValueError(f"presence_type must be one of {sorted(allowed_types)}")
        payload: Dict[str, Any] = {"jid": jid, "type": presence_type}
        if delay_ms is not None:
            if delay_ms < 0:
                raise ValueError("delay_ms cannot be negative.")
            payload["delayMs"] = delay_ms
        result = self._post_internal("/send-presence-update", payload)
        return WasenderOperationResult(**result)

    def decrypt_media_file(self, message_payload: Dict[str, Any]) -> DecryptMediaResult:
        if not message_payload:
            raise ValueError("message_payload must not be empty.")
        result = self._post_internal("/decrypt-media", message_payload)
        return DecryptMediaResult(**result)

    def upload_media_file(
        self,
        *,
        file_path: Optional[Union[str, Path]] = None,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        base64_data: Optional[str] = None,
        mimetype_hint: Optional[str] = None
    ) -> UploadMediaFileResult:
        if base64_data:
            payload: Dict[str, Any] = {"base64": base64_data}
            if mimetype_hint:
                payload["mimetype"] = mimetype_hint
            result = self._post_internal("/upload", payload)
            return UploadMediaFileResult(**result)

        resolved_path: Optional[Path] = None
        if file_path:
            resolved_path = Path(file_path)
            if not resolved_path.is_file():
                raise FileNotFoundError(f"File not found: {resolved_path}")
            filename = filename or resolved_path.name
            mimetype = mimetype_hint or mimetypes.guess_type(resolved_path.name)[0] or "application/octet-stream"
            with resolved_path.open("rb") as file_handle:
                files = {"file": (filename, file_handle, mimetype)}
                result = self._request("POST", "/upload", use_personal_token=False, files=files)
                return UploadMediaFileResult(**result)

        if file_bytes is not None:
            if not filename:
                raise ValueError("filename is required when providing file_bytes.")
            mimetype = mimetype_hint or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            files = {"file": (filename, file_bytes, mimetype)}
            result = self._request("POST", "/upload", use_personal_token=False, files=files)
            return UploadMediaFileResult(**result)

        raise ValueError("Provide either base64_data, file_path, or file_bytes to upload media.")

    def check_if_on_whatsapp(self, phone_number: str) -> CheckWhatsAppNumberResult:
        if not phone_number or not phone_number.strip():
            raise ValueError("phone_number must be a non-empty string.")
        result = self._get_internal(f"/on-whatsapp/{phone_number}")
        return CheckWhatsAppNumberResult(**result)

    def get_contacts(self) -> GetAllContactsResult:
        result = self._get_internal("/contacts")
        return GetAllContactsResult(**result)

    def get_contact_info(self, contact_phone_number: str) -> GetContactInfoResult:
        result = self._get_internal(f"/contacts/{contact_phone_number}")
        return GetContactInfoResult(**result)

    def get_contact_profile_picture(self, contact_phone_number: str) -> GetContactProfilePictureResult:
        result = self._get_internal(f"/contacts/{contact_phone_number}/profile-picture")
        return GetContactProfilePictureResult(**result)

    def block_contact(self, contact_phone_number: str) -> ContactActionResult:
        result = self._post_internal(f"/contacts/{contact_phone_number}/block", None)
        return ContactActionResult(**result)

    def unblock_contact(self, contact_phone_number: str) -> ContactActionResult:
        result = self._post_internal(f"/contacts/{contact_phone_number}/unblock", None)
        return ContactActionResult(**result)

    def get_groups(self) -> GetAllGroupsResult:
        result = self._get_internal("/groups")
        return GetAllGroupsResult(**result)

    def get_group_metadata(self, group_jid: str) -> GetGroupMetadataResult:
        result = self._get_internal(f"/groups/{group_jid}/metadata")
        return GetGroupMetadataResult(**result)

    def get_group_participants(self, group_jid: str) -> GetGroupParticipantsResult:
        result = self._get_internal(f"/groups/{group_jid}/participants")
        return GetGroupParticipantsResult(**result)

    def add_group_participants(self, group_jid: str, participants: List[str]) -> ModifyGroupParticipantsResult:
        payload = ModifyGroupParticipantsPayload(participants=participants).model_dump(by_alias=True)
        result = self._post_internal(f"/groups/{group_jid}/participants/add", payload)
        return ModifyGroupParticipantsResult(**result)

    def remove_group_participants(self, group_jid: str, participants: List[str]) -> ModifyGroupParticipantsResult:
        payload = ModifyGroupParticipantsPayload(participants=participants).model_dump(by_alias=True)
        result = self._post_internal(f"/groups/{group_jid}/participants/remove", payload)
        return ModifyGroupParticipantsResult(**result)

    def update_group_participants(self, group_jid: str, action: str, participants: List[str]) -> UpdateGroupParticipantsResult:
        payload_model = UpdateGroupParticipantsPayload(action=action, participants=participants)
        payload = payload_model.model_dump(by_alias=True)
        result = self._put_internal(f"/groups/{group_jid}/participants/update", payload)
        return UpdateGroupParticipantsResult(**result)

    def update_group_settings(self, group_jid: str, settings: UpdateGroupSettingsPayload) -> UpdateGroupSettingsResult:
        payload_dict = settings.model_dump(by_alias=True, exclude_none=True)
        result = self._put_internal(f"/groups/{group_jid}/settings", payload_dict)
        return UpdateGroupSettingsResult(**result)

    def create_group(self, name: str, participants: Optional[List[str]] = None) -> CreateGroupResult:
        payload = CreateGroupPayload(name=name, participants=participants).model_dump(exclude_none=True, by_alias=True)
        result = self._post_internal("/groups", payload)
        return CreateGroupResult(**result)

    def leave_group(self, group_jid: str) -> LeaveGroupResult:
        result = self._post_internal(f"/groups/{group_jid}/leave", None)
        return LeaveGroupResult(**result)

    def accept_group_invite(self, invite_code: str) -> AcceptGroupInviteResult:
        payload = AcceptGroupInvitePayload(code=invite_code).model_dump(by_alias=True)
        result = self._post_internal("/groups/invite/accept", payload)
        return AcceptGroupInviteResult(**result)

    def get_group_invite_info(self, invite_code: str) -> GetGroupInviteInfoResult:
        result = self._get_internal(f"/groups/invite/{invite_code}")
        return GetGroupInviteInfoResult(**result)

    def get_group_invite_link(self, group_jid: str) -> GetGroupInviteLinkResult:
        result = self._get_internal(f"/groups/{group_jid}/invite-link")
        return GetGroupInviteLinkResult(**result)

    def get_group_profile_picture(self, group_jid: str) -> GetGroupProfilePictureResult:
        result = self._get_internal(f"/groups/{group_jid}/picture")
        return GetGroupProfilePictureResult(**result)

    def get_all_whatsapp_sessions(self) -> GetAllWhatsAppSessionsResult:
        self._ensure_personal_token()
        result = self._get_internal("/whatsapp-sessions", use_personal_token=True)
        return GetAllWhatsAppSessionsResult(**result)

    def create_whatsapp_session(self, payload: CreateWhatsAppSessionPayload) -> CreateWhatsAppSessionResult:
        self._ensure_personal_token()
        payload_dict = payload.model_dump(by_alias=True)
        result = self._post_internal("/whatsapp-sessions", payload_dict, use_personal_token=True)
        return CreateWhatsAppSessionResult(**result)

    def get_whatsapp_session_details(self, session_id: int) -> GetWhatsAppSessionDetailsResult:
        self._ensure_personal_token()
        result = self._get_internal(f"/whatsapp-sessions/{session_id}", use_personal_token=True)
        return GetWhatsAppSessionDetailsResult(**result)

    def update_whatsapp_session(self, session_id: int, payload: UpdateWhatsAppSessionPayload) -> UpdateWhatsAppSessionResult:
        self._ensure_personal_token()
        payload_dict = payload.model_dump(by_alias=True, exclude_none=True)
        result = self._put_internal(f"/whatsapp-sessions/{session_id}", payload_dict, use_personal_token=True)
        return UpdateWhatsAppSessionResult(**result)

    def delete_whatsapp_session(self, session_id: int) -> DeleteWhatsAppSessionResult:
        self._ensure_personal_token()
        result = self._delete_internal(f"/whatsapp-sessions/{session_id}", use_personal_token=True)
        return DeleteWhatsAppSessionResult(**result)

    def connect_whatsapp_session(self, session_id: int, qr_as_image: Optional[bool] = None) -> ConnectSessionResult:
        self._ensure_personal_token()
        params = {"qrAsImage": "true"} if qr_as_image else None
        result = self._post_internal(
            f"/whatsapp-sessions/{session_id}/connect",
            None,
            use_personal_token=True,
            params=params
        )
        return ConnectSessionResult(**result)

    def get_whatsapp_session_qr_code(self, session_id: int) -> GetQRCodeResult:
        self._ensure_personal_token()
        result = self._get_internal(f"/whatsapp-sessions/{session_id}/qr-code", use_personal_token=True)
        return GetQRCodeResult(**result)

    def disconnect_whatsapp_session(self, session_id: int) -> DisconnectSessionResult:
        self._ensure_personal_token()
        result = self._post_internal(f"/whatsapp-sessions/{session_id}/disconnect", None, use_personal_token=True)
        return DisconnectSessionResult(**result)

    def regenerate_api_key(self, session_id: int) -> RegenerateApiKeyResult:
        self._ensure_personal_token()
        result = self._post_internal(f"/whatsapp-sessions/{session_id}/regenerate-api-key", None, use_personal_token=True)
        return RegenerateApiKeyResult(**result)

    def get_session_status(self, session_id: str) -> GetSessionStatusResult:
        result = self._get_internal(f"/sessions/{session_id}/status", use_personal_token=False)
        return GetSessionStatusResult(**result)

    def get_session_user_info(self) -> WasenderOperationResult:
        result = self._get_internal("/user", use_personal_token=False)
        return WasenderOperationResult(**result)

    def handle_webhook_event(
        self,
        request_body_bytes: bytes,
        signature_header: Optional[str]
    ) -> WasenderWebhookEvent:
        if not self.webhook_secret:
            raise ValueError("Webhook secret is not configured in the client.")
        
        if not verify_wasender_webhook_signature(signature_header, self.webhook_secret):
            raise WasenderAPIError("Invalid webhook signature", status_code=400)

        try:
            request_body_str = request_body_bytes.decode('utf-8')
            data = json.loads(request_body_str)
            adapter = TypeAdapter(WasenderWebhookEvent)
            parsed_event = adapter.validate_python(data)
            return parsed_event
        except json.JSONDecodeError as e:
            raise WasenderAPIError("Invalid JSON in webhook body", status_code=400) from e
        except Exception as e:
            raise WasenderAPIError(f"Invalid webhook event data: {str(e)}", status_code=400) from e

    def _ensure_personal_token(self) -> None:
        if not self.personal_access_token:
            raise ValueError(
                "This endpoint requires a personal access token. "
                "Provide 'personal_access_token' when creating the client."
            )

def create_sync_wasender(
    api_key: str,
    base_url: Optional[str] = None,
    retry_options: Optional[RetryConfig] = None,
    webhook_secret: Optional[str] = None,
    personal_access_token: Optional[str] = None
) -> WasenderSyncClient:
    """Create a new instance of the WasenderSyncClient.

    Args:
        api_key: Your Wasender API key
        base_url: Optional custom base URL for the API
        retry_options: Optional retry configuration
        webhook_secret: Optional webhook secret for verifying webhook requests
        personal_access_token: Optional personal access token for authentication

    Returns:
        A new WasenderSyncClient instance
    """
    return WasenderSyncClient(
        api_key=api_key,
        base_url=base_url or "https://www.wasenderapi.com/api",
        retry_options=retry_options,
        webhook_secret=webhook_secret,
        personal_access_token=personal_access_token
    )