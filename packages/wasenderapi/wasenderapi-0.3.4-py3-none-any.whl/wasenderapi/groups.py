from typing import List, Optional, Any
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from .models import RateLimitInfo, WasenderSuccessResponse

class GroupParticipant(BaseModel):
    id: str
    admin: Optional[str] = None

class BasicGroupInfo(BaseModel):
    id: str
    name: Optional[str] = None
    img_url: Optional[str] = Field(None, alias="imgUrl")

class GroupMetadata(BasicGroupInfo):
    creation: int
    owner: Optional[str] = None
    subject: Optional[str] = None
    subject_owner: Optional[str] = Field(None, alias="subjectOwner")
    subject_time: Optional[int] = Field(None, alias="subjectTime")
    desc: Optional[str] = None
    desc_owner: Optional[str] = Field(None, alias="descOwner")
    desc_id: Optional[str] = Field(None, alias="descId")
    restrict: Optional[bool] = None
    announce: Optional[bool] = None
    is_community: Optional[bool] = Field(None, alias="isCommunity")
    is_community_announce: Optional[bool] = Field(None, alias="isCommunityAnnounce")
    join_approval_mode: Optional[bool] = Field(None, alias="joinApprovalMode")
    member_add_mode: Optional[bool] = Field(None, alias="memberAddMode")
    author: Optional[str] = None
    size: Optional[int] = None
    participants: List[GroupParticipant]
    ephemeral_duration: Optional[int] = Field(None, alias="ephemeralDuration")
    invite_code: Optional[str] = Field(None, alias="inviteCode")

class ModifyGroupParticipantsPayload(BaseModel):
    participants: List[str]

    @model_validator(mode="after")
    def validate_participants(self) -> "ModifyGroupParticipantsPayload":
        if not self.participants:
            raise ValueError("participants must contain at least one entry")
        if any(not isinstance(p, str) or not p.strip() for p in self.participants):
            raise ValueError("participants must contain only non-empty strings")
        return self


class UpdateGroupParticipantsPayload(BaseModel):
    action: Literal["promote", "demote"]
    participants: List[str]

    @model_validator(mode="after")
    def validate_payload(self) -> "UpdateGroupParticipantsPayload":
        if not self.participants:
            raise ValueError("participants must contain at least one entry")
        if any(not isinstance(p, str) or not p.strip() for p in self.participants):
            raise ValueError("participants must contain only non-empty strings")
        return self


class CreateGroupPayload(BaseModel):
    name: str
    participants: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_payload(self) -> "CreateGroupPayload":
        if not self.name or not self.name.strip():
            raise ValueError("Group name must be a non-empty string")
        if self.participants is not None:
            if not isinstance(self.participants, list):
                raise ValueError("participants must be a list of strings")
            if any(not isinstance(p, str) or not p.strip() for p in self.participants):
                raise ValueError("participants must contain only non-empty strings")
        return self


class AcceptGroupInvitePayload(BaseModel):
    code: str

    @model_validator(mode="after")
    def validate_code(self) -> "AcceptGroupInvitePayload":
        if not self.code or not self.code.strip():
            raise ValueError("Invite code must be a non-empty string")
        return self

class UpdateGroupSettingsPayload(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    announce: Optional[bool] = None
    restrict: Optional[bool] = None

class ParticipantActionStatus(BaseModel):
    status: int
    jid: str
    message: str

class UpdateGroupSettingsResponseData(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None

class GetAllGroupsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[BasicGroupInfo]

class GetGroupMetadataResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: GroupMetadata

class GetGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[GroupParticipant]

class ModifyGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[ParticipantActionStatus]


class UpdateGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[ParticipantActionStatus]

class UpdateGroupSettingsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: UpdateGroupSettingsResponseData

# Result types including rate limiting
class GetAllGroupsResult(BaseModel):
    response: GetAllGroupsResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetGroupMetadataResult(BaseModel):
    response: GetGroupMetadataResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetGroupParticipantsResult(BaseModel):
    response: GetGroupParticipantsResponse
    rate_limit: Optional[RateLimitInfo] = None

class ModifyGroupParticipantsResult(BaseModel):
    response: ModifyGroupParticipantsResponse
    rate_limit: Optional[RateLimitInfo] = None

class UpdateGroupSettingsResult(BaseModel):
    response: UpdateGroupSettingsResponse
    rate_limit: Optional[RateLimitInfo] = None 


class CreateGroupResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class UpdateGroupParticipantsResult(BaseModel):
    response: UpdateGroupParticipantsResponse
    rate_limit: Optional[RateLimitInfo] = None


class LeaveGroupResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class LeaveGroupResult(BaseModel):
    response: LeaveGroupResponse
    rate_limit: Optional[RateLimitInfo] = None


class AcceptGroupInviteResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class GetGroupInviteInfoData(BaseModel):
    subject: Optional[str] = None
    size: Optional[int] = None
    owner: Optional[str] = None
    invite_code: Optional[str] = Field(None, alias="inviteCode")
    group_jid: Optional[str] = Field(None, alias="groupJid")


class GetGroupInviteInfoResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[GetGroupInviteInfoData] = None


class GetGroupInviteInfoResult(BaseModel):
    response: GetGroupInviteInfoResponse
    rate_limit: Optional[RateLimitInfo] = None


class GetGroupInviteLinkData(BaseModel):
    link: Optional[str] = None


class GetGroupInviteLinkResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[GetGroupInviteLinkData] = None


class GetGroupInviteLinkResult(BaseModel):
    response: GetGroupInviteLinkResponse
    rate_limit: Optional[RateLimitInfo] = None


class GetGroupProfilePictureData(BaseModel):
    url: Optional[str] = None


class GetGroupProfilePictureResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[GetGroupProfilePictureData] = None


class GetGroupProfilePictureResult(BaseModel):
    response: GetGroupProfilePictureResponse
    rate_limit: Optional[RateLimitInfo] = None