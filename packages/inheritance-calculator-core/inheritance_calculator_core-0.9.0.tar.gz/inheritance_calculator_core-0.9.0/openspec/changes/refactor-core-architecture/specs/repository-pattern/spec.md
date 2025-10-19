# Repository Pattern Enhancement

リポジトリパターンの完全実装により、カプセル化を強化し、データアクセス層の品質を向上させます。

## MODIFIED Requirements

#### Requirement: リポジトリ内部メソッドのカプセル化
**変更内容**: 内部メソッドのアクセス制御を強化

リポジトリの内部変換メソッドは、外部から直接アクセスできないようにしなければならない。

#### Scenario: 内部メソッドの保護
```python
from inheritance_calculator_core.database import PersonRepository, RelationshipRepository

person_repo = PersonRepository(client)
relationship_repo = RelationshipRepository(client)

# ❌ 以前は可能だった（カプセル化違反）
# person = relationship_repo.person_repo._to_person(node)

# ✅ 適切なパブリックAPIを使用
children = relationship_repo.find_children("親の名前")
assert all(isinstance(child, Person) for child in children)
```

#### Requirement: 共通変換ロジックの基底クラス化
**変更内容**: 重複した変換メソッドを基底クラスに抽出

Neo4jノードとPydanticモデル間の変換ロジックは、基底リポジトリクラスで提供されなければならない。

#### Scenario: 基底クラスの変換メソッド使用
```python
from inheritance_calculator_core.database.base import BaseRepository

class PersonRepository(BaseRepository[Person]):
    """人物リポジトリ"""

    def find_by_name(self, name: str) -> Optional[Person]:
        result = self.client.execute(PersonQueries.FIND_BY_NAME, {"name": name})
        if not result:
            return None

        # 基底クラスの変換メソッドを使用
        return self._node_to_model(result[0]["p"])

    def _node_to_model(self, node: Dict[str, Any]) -> Person:
        """Neo4jノードをPersonモデルに変換"""
        # Person固有の変換ロジック
        birth_date = self._convert_neo4j_date(node.get("birth_date"))
        death_date = self._convert_neo4j_date(node.get("death_date"))
        gender = Gender(node["gender"]) if node.get("gender") else Gender.UNKNOWN

        return Person(
            id=PersonID.from_string(node["id"]),
            name=node["name"],
            is_alive=node["is_alive"],
            is_decedent=node["is_decedent"],
            birth_date=birth_date,
            death_date=death_date,
            gender=gender,
            address=node.get("address"),
            phone=node.get("phone"),
            email=node.get("email")
        )
```

## ADDED Requirements

#### Requirement: BaseRepositoryの型安全な実装
**民法根拠**: なし（技術的改善）

すべてのリポジトリは、型パラメータを持つBaseRepositoryを継承しなければならない。

#### Scenario: ジェネリクスを使用した型安全なリポジトリ
```python
from typing import TypeVar, Generic, Optional, List, Dict, Any
from abc import ABC, abstractmethod

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """リポジトリの基底クラス"""

    def __init__(self, client: Neo4jClient) -> None:
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _node_to_model(self, node: Dict[str, Any]) -> T:
        """
        Neo4jノードをモデルに変換（サブクラスで実装）

        Args:
            node: Neo4jノード

        Returns:
            モデルインスタンス
        """
        pass

    def _convert_neo4j_date(self, neo4j_date: Any) -> Optional[date]:
        """Neo4jのdateオブジェクトをPythonのdateに変換"""
        if neo4j_date is None:
            return None

        if hasattr(neo4j_date, "year"):
            return date(neo4j_date.year, neo4j_date.month, neo4j_date.day)

        return None

    def _nodes_to_models(self, nodes: List[Dict[str, Any]]) -> List[T]:
        """複数のノードを変換"""
        return [self._node_to_model(node) for node in nodes]
```

#### Scenario: 型安全なリポジトリの使用
```python
# PersonRepositoryは BaseRepository[Person] を継承
person_repo: PersonRepository = PersonRepository(client)

# 戻り値の型が保証される
person: Optional[Person] = person_repo.find_by_name("山田太郎")
persons: List[Person] = person_repo.find_all()

# mypyで型チェック可能
if person is not None:
    assert isinstance(person.name, str)  # 型安全
```

#### Requirement: リポジトリ間の依存性削除
**民法根拠**: なし（技術的改善）

リポジトリは他のリポジトリのインスタンスを直接保持してはならない。

#### Scenario: リポジトリの独立性
```python
# ❌ 以前の実装（リポジトリ間の依存）
class RelationshipRepository:
    def __init__(self, client: Neo4jClient) -> None:
        self.client = client
        self.person_repo = PersonRepository(client)  # 依存

    def find_children(self, parent_name: str) -> List[Person]:
        result = self.client.execute(...)
        return [self.person_repo._to_person(r["child"]) for r in result]

# ✅ 新しい実装（独立したリポジトリ）
class RelationshipRepository(BaseRepository[Relationship]):
    def __init__(self, client: Neo4jClient) -> None:
        super().__init__(client)
        # 他のリポジトリへの依存なし

    def find_children(self, parent_name: str) -> List[Person]:
        result = self.client.execute(...)
        # 自身の_node_to_modelで変換
        return [self._node_to_model(r["child"]) for r in result]

    def _node_to_model(self, node: Dict[str, Any]) -> Person:
        """Personノードの変換（必要に応じて）"""
        # 共通の変換ロジックを使用
        return self._convert_person_node(node)
```

## Implementation Notes

### BaseRepository Implementation
```python
# src/inheritance_calculator_core/database/base_repository.py
from typing import TypeVar, Generic, Optional, List, Dict, Any
from abc import ABC, abstractmethod
from datetime import date
import logging

from .neo4j_client import Neo4jClient

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    リポジトリの基底クラス

    Neo4jとPydanticモデル間の変換を抽象化する。
    """

    def __init__(self, client: Neo4jClient) -> None:
        """
        初期化

        Args:
            client: Neo4jクライアント
        """
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _node_to_model(self, node: Dict[str, Any]) -> T:
        """
        Neo4jノードをモデルに変換

        Args:
            node: Neo4jノード

        Returns:
            モデルインスタンス
        """
        pass

    def _convert_neo4j_date(self, neo4j_date: Any) -> Optional[date]:
        """
        Neo4jのdateオブジェクトをPythonのdateに変換

        Args:
            neo4j_date: Neo4jのdate型オブジェクト

        Returns:
            Pythonのdate、またはNone
        """
        if neo4j_date is None:
            return None

        if hasattr(neo4j_date, "year"):
            return date(neo4j_date.year, neo4j_date.month, neo4j_date.day)

        return None

    def _nodes_to_models(self, nodes: List[Dict[str, Any]]) -> List[T]:
        """
        複数のノードをモデルに変換

        Args:
            nodes: Neo4jノードのリスト

        Returns:
            モデルインスタンスのリスト
        """
        return [self._node_to_model(node) for node in nodes]
```

### Migration Path
1. BaseRepositoryジェネリッククラスを作成
2. PersonRepository, RelationshipRepositoryをBaseRepositoryから継承
3. _to_person → _node_to_model にリネーム
4. リポジトリ間の依存を削除
5. すべてのテストがパスすることを確認
6. 古いbase.pyの内容を統合

### Benefits
- **カプセル化**: 内部実装の隠蔽
- **型安全性**: ジェネリクスによる型保証
- **再利用性**: 共通ロジックの基底クラス化
- **保守性**: 変換ロジックの一元管理
