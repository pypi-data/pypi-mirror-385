"""ベースモデルクラス"""
from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator

from .value_objects import PersonID


class BaseEntity(BaseModel):
    """全エンティティの基底クラス"""

    model_config = ConfigDict(
        # JSON互換性
        json_encoders={datetime: lambda v: v.isoformat()},
        # バリデーション設定
        validate_assignment=True,
        # 追加フィールドを許可しない
        extra='forbid',
    )

    id: PersonID = Field(default_factory=lambda: PersonID.generate(), description="エンティティID")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: Optional[datetime] = Field(default=None, description="更新日時")

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_person_id(cls, v: Union[UUID, PersonID, str]) -> PersonID:
        """
        UUIDをPersonIDに変換（後方互換性のため）

        Args:
            v: UUID、PersonID、または文字列

        Returns:
            PersonID
        """
        if isinstance(v, PersonID):
            return v
        elif isinstance(v, UUID):
            return PersonID.from_uuid(v)
        elif isinstance(v, str):
            return PersonID.from_string(v)
        else:
            raise ValueError(f"Invalid type for id: {type(v)}")

    def mark_updated(self) -> None:
        """更新日時を記録"""
        self.updated_at = datetime.now()


class Neo4jNode(BaseEntity):
    """Neo4jノードの基底クラス"""

    @property
    def neo4j_labels(self) -> list[str]:
        """Neo4jラベルのリスト"""
        return [self.__class__.__name__]

    @property
    def neo4j_properties(self) -> Dict[str, Any]:
        """Neo4jプロパティの辞書"""
        return self.model_dump(exclude={'id'})


class Neo4jRelationship(BaseModel):
    """Neo4jリレーションシップの基底クラス"""

    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid',
    )

    @property
    def neo4j_type(self) -> str:
        """Neo4jリレーションシップタイプ"""
        return self.__class__.__name__.upper()

    @property
    def neo4j_properties(self) -> Dict[str, Any]:
        """Neo4jプロパティの辞書"""
        return self.model_dump()
