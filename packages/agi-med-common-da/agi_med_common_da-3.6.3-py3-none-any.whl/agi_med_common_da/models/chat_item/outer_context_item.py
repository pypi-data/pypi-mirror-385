from pydantic import Field
from typing import Any

from .. import _Base
from ..enums import TrackIdEnum


class OuterContextItem(_Base):
    sex: bool = Field(False, alias="Sex", description="True = male, False = female", examples=[True])
    age: int = Field(0, alias="Age", examples=[20])
    user_id: str = Field("", alias="UserId", examples=["123456789"])
    session_id: str = Field("", alias="SessionId", examples=["987654321"])
    client_id: str = Field("", alias="ClientId", examples=["543216789"])
    track_id: TrackIdEnum = Field(TrackIdEnum.CONSULTATION, alias="TrackId")

    def create_id(self, short: bool = False, clean: bool = False) -> str:
        if short:
            return f"{self.user_id}_{self.session_id}_{self.client_id}"
        if not clean:
            return f"user_{self.user_id}_session_{self.session_id}_client_{self.client_id}"
        return f"user_{self.user_id}_session_{self.session_id}_client_{self.client_id}_clean"

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)
