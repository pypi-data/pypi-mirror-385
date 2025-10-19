"""値オブジェクト

ドメインモデルで使用する値オブジェクトの定義。
"""
from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Union


@dataclass(frozen=True)
class PersonID:
    """
    人物の一意識別子（値オブジェクト）

    不変な識別子として、辞書のキーやハッシュ可能なコンテナで使用できる。
    """

    value: UUID

    @classmethod
    def generate(cls) -> 'PersonID':
        """
        新しいPersonIDを生成

        Returns:
            新しいPersonIDインスタンス
        """
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> 'PersonID':
        """
        文字列からPersonIDを生成

        Args:
            id_str: UUID文字列

        Returns:
            PersonIDインスタンス

        Raises:
            ValueError: 無効なUUID文字列の場合
        """
        return cls(value=UUID(id_str))

    @classmethod
    def from_uuid(cls, uuid_val: UUID) -> 'PersonID':
        """
        UUIDからPersonIDを生成

        Args:
            uuid_val: UUIDオブジェクト

        Returns:
            PersonIDインスタンス
        """
        return cls(value=uuid_val)

    def __str__(self) -> str:
        """
        文字列表現

        Returns:
            UUID文字列
        """
        return str(self.value)

    def __hash__(self) -> int:
        """
        ハッシュ値

        Returns:
            ハッシュ値（辞書のキーとして使用可能）
        """
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        """
        等値比較

        Args:
            other: 比較対象

        Returns:
            PersonIDが等しい場合True
        """
        if not isinstance(other, PersonID):
            return False
        return self.value == other.value

    def __repr__(self) -> str:
        """
        デバッグ用文字列表現

        Returns:
            デバッグ用文字列
        """
        return f"PersonID('{self.value}')"
