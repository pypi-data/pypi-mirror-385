# Wasender Python SDK: Group Management Examples

This document provides examples for managing WhatsApp groups using the Wasender Python SDK. It covers retrieving group lists, fetching metadata and participant details, modifying participants, updating group settings, and sending messages to groups.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Prerequisites

1.  **Install Python:** Ensure Python (3.8+) is installed on your system.
2.  **Obtain a Wasender API Key:** You'll need an API key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
3.  **SDK Installation:** Install the Wasender Python SDK using pip:
    ```bash
    pip install wasenderapi
    ```

## Initializing the SDK

All examples assume you have initialized the SDK. The examples in this document primarily use an asynchronous client.

```python
# group_examples_setup.py
import asyncio
import os
import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

# Corrected imports for client and RetryConfig
from wasenderapi import create_async_wasender, WasenderAsyncClient # For type hinting
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    RetryConfig, # RetryConfig is now from models
    # General
    RateLimitInfo,
    # WasenderSuccessResponse, # Renamed/updated from SimpleStatusResponse if applicable
    # Message Payloads & Results
    TextOnlyMessage, # Assuming this is used for sending text to groups
    WasenderSendResult,
    # Group Specific Models from wasenderapi.groups
    BasicGroupInfo, # Used in GetAllGroupsResult
    GroupMetadata,
    GroupParticipant,
    ModifyGroupParticipantsPayload, # For request payloads
    UpdateGroupSettingsPayload,   # For request payloads
    # Group Specific Result Models from wasenderapi.groups
    GetAllGroupsResult,
    GetGroupMetadataResult,
    GetGroupParticipantsResult,
    ModifyGroupParticipantsResult, # Wraps list of ParticipantActionStatus
    UpdateGroupSettingsResult,
    # ParticipantActionStatus # Sub-model in ModifyGroupParticipantsResult
)

# Configure basic logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SDK Initialization ---
api_key = os.getenv("WASENDER_API_KEY")
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN") # Often needed for listing all sessions, etc.

if not api_key:
    logger.error("Error: WASENDER_API_KEY environment variable not set.")
    # For document generation, use a placeholder if not set, but real operations will fail.
    api_key = "YOUR_API_KEY_PLACEHOLDER" 

# Initialize async client using the factory function
# Most group operations are on a specific session, identified by api_key.
# If PAT is needed for specific group-related endpoints (e.g. listing groups across all accounts - unlikely), pass it.
async_client = create_async_wasender(api_key=api_key, personal_access_token=personal_access_token)

logger.info(f"WasenderAsyncClient initialized for Group Management examples (API Key: {api_key[:4]}...)")

# Example of initializing with retry options (if desired)
# retry_config_groups = RetryConfig(enabled=True, max_retries=2)
# async_client_with_retries_groups = create_async_wasender(
#     api_key=api_key,
#     personal_access_token=personal_access_token,
#     retry_options=retry_config_groups
# )

# --- Placeholders for Testing ---
# Replace with a valid group JID (e.g., "1234567890-1234567890@g.us")
EXAMPLE_GROUP_JID = "1234567890-1234567890@g.us" # DO NOT COMMIT REAL JIDs
# Replace with valid participant JIDs (e.g., "PHONE_NUMBER@s.whatsapp.net")
# The client methods for groups (add/remove participants) expect a list of JIDs.
PARTICIPANT_JIDS_TO_ADD = ["19876543210@s.whatsapp.net", "19876543211@s.whatsapp.net"]
PARTICIPANT_JID_TO_REMOVE = "19876543210@s.whatsapp.net"
PARTICIPANT_JID_TO_PROMOTE = "19876543211@s.whatsapp.net"
PARTICIPANT_JID_TO_DEMOTE = "19876543210@s.whatsapp.net"

# --- Generic Error Handler for Group Examples ---
def handle_group_api_error(error: Exception, operation: str):
    if isinstance(error, WasenderAPIError):
        logger.error(f"API Error during {operation}:")
        logger.error(f"  Message: {error.message}")
        logger.error(f"  Status Code: {error.status_code or 'N/A'}")
        if error.api_message:
            logger.error(f"  API Message: {error.api_message}")
        if error.error_details:
            logger.error(f"  Error Details: {error.error_details}")
        if error.rate_limit:
            reset_time_str = datetime.fromtimestamp(error.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if error.rate_limit.reset_timestamp else "N/A"
            logger.error(
                f"  Rate Limit at Error: Remaining = {error.rate_limit.remaining}, Limit = {error.rate_limit.limit}, Resets at = {reset_time_str}"
            )
    else:
        logger.error(f"An unexpected error occurred during {operation}: {error}")

# --- Helper to log rate limits ---
def log_rate_limit_info(rate_limit: Optional[RateLimitInfo]):
    if rate_limit:
        reset_time_str = datetime.fromtimestamp(rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if rate_limit.reset_timestamp else "N/A"
        logger.info(
            f"Rate Limit Info: Remaining = {rate_limit.remaining}, Limit = {rate_limit.limit}, Resets at = {reset_time_str}"
        )
    else:
        logger.info("Rate limit information not available for this request.")

async def main():
    logger.info("Starting Group Management examples...")
    # Uncomment the examples you want to run. Be cautious with modifying operations.

    # await get_all_groups_example()
    # await send_message_to_group_example(EXAMPLE_GROUP_JID, "Hello from Python SDK!")
    # await get_group_metadata_example(EXAMPLE_GROUP_JID)
    # await get_group_participants_example(EXAMPLE_GROUP_JID)
    
    # Modifying operations - use with caution and valid JIDs
    # await add_participants_to_group_example(EXAMPLE_GROUP_JID, PARTICIPANT_JIDS_TO_ADD)
    # await remove_participants_from_group_example(EXAMPLE_GROUP_JID, [PARTICIPANT_JID_TO_REMOVE]) # Pass as list
    # await promote_participants_to_admin_example(EXAMPLE_GROUP_JID, [PARTICIPANT_JID_TO_PROMOTE]) # Pass as list
    # await demote_admins_to_participant_example(EXAMPLE_GROUP_JID, [PARTICIPANT_JID_TO_DEMOTE]) # Pass as list
    
    # new_settings = UpdateGroupSettingsPayload(
    #     subject="New Group Subject from Python SDK",
    #     description="Updated via Python SDK examples!",
    #     announce=False, # True for admin-only messages, False for all participants
    #     restrict=False  # True for admin-only group info edit, False for all participants
    # )
    # await update_group_settings_example(EXAMPLE_GROUP_JID, new_settings)
    
    # await leave_group_example(EXAMPLE_GROUP_JID) # CAUTION: Account will leave the group

    logger.info("Group Management examples finished.")

if __name__ == "__main__":
    # Ensure EXAMPLE_GROUP_JID and other JIDs are set to valid test values
    # if EXAMPLE_GROUP_JID == "1234567890-1234567890@g.us" or \
    #    PARTICIPANT_JIDS_TO_ADD[0] == "19876543210":
    #     logger.warning("Please update placeholder JIDs in the script before running examples.")
    # else:
    #    asyncio.run(main())
    logger.info("To run examples, uncomment calls in main() and ensure JIDs are correctly set.")
    logger.info("Then, you can run: asyncio.run(main()) after adjusting placeholder checks if needed.")

## Group Management Operations

Below are examples of common group management tasks. These functions assume `async_client`, `logger`, `handle_group_api_error`, `log_rate_limit_info`, `EXAMPLE_GROUP_JID`, and relevant Pydantic models are available from a setup similar to the one shown above.

### 1. Get All Groups

Retrieves a list of all WhatsApp groups the connected account is part of.

```python
# Example: Get All Groups
async def get_all_groups_example(client: WasenderAsyncClient):
    logger.info("\n--- Fetching All Groups ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning("Skipping API call for get_all_groups: API key is a placeholder.")
        return
    try:
        # result is now directly GetAllGroupsResult, not nested WasenderResponse
        result: GetAllGroupsResult = await client.get_groups()
        groups: List[BasicGroupInfo] = result.response.data
        
        logger.info(f"Successfully retrieved {len(groups)} groups.")
        if groups:
            logger.info("First group (details):")
            # .model_dump_json is good for full JSON, .model_dump for a dict
            logger.info(groups[0].model_dump_json(indent=2)) 
        
        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_group_api_error(e, "fetching all groups")

# In main(): await get_all_groups_example()
```

### 2. Send Message to a Group

Uses the standard `client.send()` method. The `to` field in the message payload should be the Group JID.

```python
# Example: Send Text Message to a Group
async def send_message_to_group_example(client: WasenderAsyncClient, group_jid: str, message_text: str):
    logger.info(f"\n--- Sending Message to Group: {group_jid} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for send_message_to_group {group_jid}: API key is a placeholder.")
        return
    if not group_jid:
        logger.error("Group JID is required.")
        return

    text_payload = TextOnlyMessage(
        to=group_jid,
        text_body=message_text,
    ) # message_type defaults to "text" if not set in TextPayload

    try:
        # Assuming client.send() returns WasenderResponse[WasenderSendResult]
        response: WasenderSendResult = await client.send_text(
            to=group_jid, 
            text_body=message_text
        )
        send_result: WasenderSendResult = response.response.data
        
        logger.info(f"Group message sent. Message ID: {send_result.message_id}, Status: {send_result.status}")
        if send_result.detail:
             logger.info(f"Detail: {send_result.detail}")
        
        log_rate_limit_info(response.rate_limit)
            
    except Exception as e:
        handle_group_api_error(e, f"sending message to group {group_jid}")

# In main(): await send_message_to_group_example(EXAMPLE_GROUP_JID, "Hello from Python SDK!")
```

### 3. Get Group Metadata

Retrieves detailed metadata for a specific group, including subject, description, and participants.

```python
# Example: Get Group Metadata
async def get_group_metadata_example(client: WasenderAsyncClient, group_jid: str):
    logger.info(f"\n--- Fetching Metadata for Group: {group_jid} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for get_group_metadata {group_jid}: API key is a placeholder.")
        return
    if not group_jid:
        logger.error("Group JID is required.")
        return

    try:
        # result is now directly GetGroupMetadataResult
        result: GetGroupMetadataResult = await client.get_group_metadata(group_jid=group_jid)
        metadata: GroupMetadata = result.response.data
        
        logger.info(f"Group metadata for {group_jid}:")
        logger.info(metadata.model_dump_json(indent=2))
        # You can access specific fields like metadata.subject, metadata.description
        # logger.info(f"Subject: {metadata.subject}")
        # if metadata.participants:
        #    logger.info(f"Found {len(metadata.participants)} participants.")

        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"fetching metadata for group {group_jid}")

# In main(): await get_group_metadata_example(EXAMPLE_GROUP_JID)
```

### 4. Get Group Participants (Alternative)

While `get_group_metadata` includes participants, if there's a dedicated endpoint in your SDK (like `client.get_group_participants`), it might be used for just fetching participants. Assuming `get_group_metadata` is comprehensive. If your SDK has `client.get_group_participants()` returning `WasenderResponse[List[GroupParticipant]]`, the example would be:

```python
# Example: Get Group Participants (if a dedicated endpoint exists)
async def get_group_participants_example(client: WasenderAsyncClient, group_jid: str):
    logger.info(f"\n--- Fetching Participants for Group: {group_jid} (using dedicated endpoint) ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for get_group_participants {group_jid}: API key is a placeholder.")
        return
    if not group_jid:
        logger.error("Group JID is required.")
        return
    
    try:
        # This assumes your client has such a method. Adjust if not.
        # result = await client.get_group_participants(group_jid=group_jid) 
        # participants: List[GroupParticipant] = result.response.data
        
        # For demonstration, we'll use get_group_metadata as it usually contains participants
        metadata_result: GetGroupMetadataResult = await client.get_group_metadata(group_jid=group_jid)
        participants: List[GroupParticipant] = metadata_result.response.data.participants or []

        logger.info(f"Retrieved {len(participants)} participants for group {group_jid}.")
        if participants:
            logger.info("First participant (details):")
            logger.info(participants[0].model_dump_json(indent=2))
            # Example: logger.info(f"Participant JID: {participants[0].id}, Admin: {participants[0].is_admin}")

        log_rate_limit_info(metadata_result.rate_limit) # Using rate_limit from the actual call made

    except Exception as e:
        handle_group_api_error(e, f"fetching participants for group {group_jid}")

# In main(): await get_group_participants_example(EXAMPLE_GROUP_JID)
```

### 5. Add Participants to Group

Adds one or more participants to a group. Requires admin privileges in the group.

```python
# Example: Add Participants to Group
async def add_participants_to_group_example(client: WasenderAsyncClient, group_jid: str, participant_jids: List[str]):
    logger.info(f"\n--- Adding Participants to Group: {group_jid} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for add_participants_to_group {group_jid}: API key is a placeholder.")
        return
    if not group_jid or not participant_jids:
        logger.error("Group JID and a list of participant JIDs are required.")
        return
    
    logger.info(f"Attempting to add: {participant_jids}")
    try:
        # result is now directly ModifyGroupParticipantsResult
        result: ModifyGroupParticipantsResult = await client.add_group_participants(
            group_jid=group_jid, 
            participants=participant_jids
        )
        logger.info(f"Add participants call completed for group {group_jid}.")

        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"adding participants to group {group_jid}")

# In main(): await add_participants_to_group_example(EXAMPLE_GROUP_JID, PARTICIPANT_JIDS_TO_ADD)
```

### 6. Remove Participants from Group

Removes one or more participants from a group. Requires admin privileges.

```python
# Example: Remove Participants from Group
async def remove_participants_from_group_example(group_jid: str, participant_jids: List[str]):
    logger.info(f"\n--- Removing Participants from Group: {group_jid} ---")
    if not group_jid or not participant_jids:
        logger.error("Group JID and a list of participant JIDs are required.")
        return

    logger.info(f"Attempting to remove: {participant_jids}")
    try:
        # Assumes client.remove_group_participants returns WasenderResponse[ModifyParticipantsResult]
        result = await client.remove_group_participants(group_jid=group_jid, participant_jids=participant_jids)
        mod_result: ModifyParticipantsResult = result.response.data

        logger.info("Remove participants operation result:")
        if mod_result.message:
            logger.info(f"  Message: {mod_result.message}")
        if mod_result.statuses:
            for status in mod_result.statuses:
                logger.info(f"  JID: {status.jid}, Status: {status.status}, Message: {status.message or 'N/A'}")
        else:
             logger.info(f"  Raw data: {mod_result.model_dump_json(indent=2)}")

        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"removing participants from group {group_jid}")

# In main(): await remove_participants_from_group_example(EXAMPLE_GROUP_JID, [PARTICIPANT_JID_TO_REMOVE])
```

### 7. Promote Participants to Admin

Promotes one or more group participants to admin status. Requires existing admin privileges.

```python
# Example: Promote Participants to Admin
async def promote_participants_to_admin_example(group_jid: str, participant_jids: List[str]):
    logger.info(f"\n--- Promoting Participants to Admin in Group: {group_jid} ---")
    if not group_jid or not participant_jids:
        logger.error("Group JID and a list of participant JIDs are required.")
        return

    logger.info(f"Attempting to promote: {participant_jids}")
    try:
        # Assumes client.promote_group_participants returns WasenderResponse[ModifyParticipantsResult]
        result = await client.promote_group_participants(group_jid=group_jid, participant_jids=participant_jids)
        mod_result: ModifyParticipantsResult = result.response.data
        
        logger.info("Promote participants operation result:")
        if mod_result.message:
            logger.info(f"  Message: {mod_result.message}")
        if mod_result.statuses:
            for status in mod_result.statuses:
                logger.info(f"  JID: {status.jid}, Status: {status.status}, Message: {status.message or 'N/A'}")
        else:
             logger.info(f"  Raw data: {mod_result.model_dump_json(indent=2)}")

        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"promoting participants in group {group_jid}")

# In main(): await promote_participants_to_admin_example(EXAMPLE_GROUP_JID, [PARTICIPANT_JID_TO_PROMOTE])
```

### 8. Demote Admins to Participant

Demotes one or more group admins to regular participant status. Requires existing admin privileges.

```python
# Example: Demote Admins to Participant
async def demote_admins_to_participant_example(group_jid: str, admin_jids: List[str]):
    logger.info(f"\n--- Demoting Admins to Participant in Group: {group_jid} ---")
    if not group_jid or not admin_jids:
        logger.error("Group JID and a list of admin JIDs are required.")
        return

    logger.info(f"Attempting to demote: {admin_jids}")
    try:
        # Assumes client.demote_group_participants returns WasenderResponse[ModifyParticipantsResult]
        result = await client.demote_group_participants(group_jid=group_jid, participant_jids=admin_jids) # participant_jids is the parameter name
        mod_result: ModifyParticipantsResult = result.response.data
        
        logger.info("Demote admins operation result:")
        if mod_result.message:
            logger.info(f"  Message: {mod_result.message}")
        if mod_result.statuses:
            for status in mod_result.statuses:
                logger.info(f"  JID: {status.jid}, Status: {status.status}, Message: {status.message or 'N/A'}")
        else:
             logger.info(f"  Raw data: {mod_result.model_dump_json(indent=2)}")
             
        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"demoting admins in group {group_jid}")

# In main(): await demote_admins_to_participant_example(EXAMPLE_GROUP_JID, [PARTICIPANT_JID_TO_DEMOTE])
```

### 9. Update Group Settings

Updates group settings like subject, description, and who can send messages or edit group info. Requires admin privileges.

```python
# Example: Update Group Settings
async def update_group_settings_example(group_jid: str, settings: UpdateGroupSettingsPayload):
    logger.info(f"\n--- Updating Settings for Group: {group_jid} ---")
    if not group_jid:
        logger.error("Group JID is required.")
        return
    
    logger.info(f"Attempting to update settings with: {settings.model_dump_json(indent=2)}")
    try:
        # Assumes client.update_group_settings returns WasenderResponse[GroupSettingsUpdateResult]
        result = await client.update_group_settings(group_jid=group_jid, payload=settings)
        update_result: GroupSettingsUpdateResult = result.response.data
        
        logger.info("Update group settings result:")
        # Assuming GroupSettingsUpdateResult has a 'message' or similar fields. Adjust as per your model.
        logger.info(f"  Message: {update_result.message or 'Success'}") 
        # You might have more specific fields in GroupSettingsUpdateResult like changed_fields
        # logger.info(f"  Details: {update_result.model_dump_json(indent=2)}")


        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"updating settings for group {group_jid}")

# In main(), after defining new_settings:
# new_settings = UpdateGroupSettingsPayload(subject="New Subject", description="New Desc", announce=False, restrict=False)
# await update_group_settings_example(EXAMPLE_GROUP_JID, new_settings)
```

### 10. Leave Group

Makes the connected WhatsApp account leave a specified group.

```python
# Example: Leave Group
async def leave_group_example(group_jid: str):
    logger.info(f"\n--- Attempting to Leave Group: {group_jid} ---")
    if not group_jid:
        logger.error("Group JID is required.")
        return
    
    try:
        # Assumes client.leave_group returns WasenderResponse[GroupLeaveResult or SimpleStatusResponse]
        result = await client.leave_group(group_jid=group_jid)
        # Assuming GroupLeaveResult or similar with a 'message' or 'status' field
        leave_data = result.response.data
        
        logger.info(f"Leave group operation for {group_jid} successful.")
        if hasattr(leave_data, 'message') and leave_data.message:
             logger.info(f"  Message: {leave_data.message}")
        elif hasattr(leave_data, 'status') and leave_data.status:
            logger.info(f"  Status: {leave_data.status}")
        else:
            logger.info(f"  Details: {leave_data.model_dump_json(indent=2)}")

        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_group_api_error(e, f"leaving group {group_jid}")

# In main(): await leave_group_example(EXAMPLE_GROUP_JID) # CAUTION!
```

## Important Notes

-   **Group JIDs:** Ensure you use the correct Group JID format (e.g., `1234567890-1234567890@g.us`). These are typically obtained from group metadata or events.
-   **Admin Privileges:** Operations like adding/removing/promoting/demoting participants or updating group settings require the WhatsApp account associated with the API Key to have admin privileges in the target group.
-   **Participant JIDs:** When adding, removing, promoting, or demoting participants, provide their JIDs in E.164 phone number format (e.g., `12345678901` without `+` or `@s.whatsapp.net`). Some APIs might accept the full JID with suffix for participants, but E.164 is common for input. Refer to specific SDK/API documentation if unsure.
-   **Testing:** Always test group modification operations carefully, preferably in test groups, to avoid unintended changes to important groups.
-   **Error Handling:** The examples use a generic `handle_group_api_error`. Robust applications should implement more detailed error checking and recovery.
-   **Rate Limiting:** Be mindful of API rate limits. The `RateLimitInfo` object (if returned by the SDK with responses) provides details on current limits.

This guide covers key group management functionalities of the Wasender Python SDK. Remember to replace placeholder JIDs, handle API keys securely, and consult the SDK's specific model definitions for exact request and response structures.
