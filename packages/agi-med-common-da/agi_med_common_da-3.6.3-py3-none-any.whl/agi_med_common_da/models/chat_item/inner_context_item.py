from pydantic import Field

from . import ReplicaItem
from .. import _Base


class InnerContextItem(_Base):
    replicas: list[ReplicaItem] = Field(alias="Replicas")

    def to_dict(self) -> dict[str, list]:
        return self.model_dump(by_alias=True)
