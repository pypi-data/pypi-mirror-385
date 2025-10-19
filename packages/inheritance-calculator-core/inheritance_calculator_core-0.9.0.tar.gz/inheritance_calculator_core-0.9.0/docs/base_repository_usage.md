# BaseRepository使用ガイド

## 概要

`BaseRepository`は、エンティティのCRUD操作を抽象化した基底クラスです。
PersonIDを使用した型安全なリポジトリパターンを提供します。

## 基本的な使い方

### 1. BaseRepositoryを継承したリポジトリクラスの作成

```python
from inheritance_calculator_core.database.base import BaseRepository
from inheritance_calculator_core.models.person import Person
from inheritance_calculator_core.models.value_objects import PersonID
from typing import Optional, List

class PersonRepository(BaseRepository[Person]):
    """人物リポジトリの実装例"""

    def __init__(self, client: DatabaseClient):
        self.client = client

    def create(self, entity: Person) -> Person:
        """人物を作成"""
        # データベースへの保存ロジック
        query = "CREATE (p:Person {id: $id, name: $name}) RETURN p"
        params = {
            "id": str(entity.id),
            "name": entity.name
        }
        self.client.execute_query(query, params)
        return entity

    def find_by_id(self, entity_id: PersonID) -> Optional[Person]:
        """IDで人物を検索"""
        query = "MATCH (p:Person {id: $id}) RETURN p"
        result = self.client.execute_query(query, {"id": str(entity_id)})

        if not result:
            return None

        return Person(**result[0]['p'])

    def update(self, entity: Person) -> Person:
        """人物情報を更新"""
        query = """
            MATCH (p:Person {id: $id})
            SET p.name = $name, p.updated_at = datetime()
            RETURN p
        """
        params = {
            "id": str(entity.id),
            "name": entity.name
        }
        self.client.execute_query(query, params)
        return entity

    def delete(self, entity_id: PersonID) -> bool:
        """人物を削除"""
        query = "MATCH (p:Person {id: $id}) DELETE p"
        self.client.execute_query(query, {"id": str(entity_id)})
        return True

    def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Person]:
        """全ての人物を取得"""
        query = "MATCH (p:Person) RETURN p SKIP $offset"
        if limit:
            query += " LIMIT $limit"

        params = {"offset": offset}
        if limit:
            params["limit"] = limit

        results = self.client.execute_query(query, params)
        return [Person(**r['p']) for r in results]
```

### 2. リポジトリの使用例

```python
from inheritance_calculator_core.database.neo4j_client import Neo4jClient
from inheritance_calculator_core.models.person import Person

# クライアントとリポジトリの初期化
client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password")
person_repo = PersonRepository(client)

# 作成
person = Person(name="田中太郎", is_alive=True)
created_person = person_repo.create(person)

# 検索
found_person = person_repo.find_by_id(created_person.id)
if found_person:
    print(f"Found: {found_person.name}")

# 更新
found_person.name = "田中次郎"
updated_person = person_repo.update(found_person)

# 削除
person_repo.delete(updated_person.id)

# 全件取得
all_persons = person_repo.find_all(limit=10, offset=0)
```

## PersonIDの利点

### 型安全性

```python
# ✅ 正しい使い方（PersonIDを使用）
person_id = PersonID.generate()
person = person_repo.find_by_id(person_id)

# ❌ コンパイルエラー（文字列は使えない）
person = person_repo.find_by_id("some-uuid-string")  # Type error!
```

### 辞書のキーとして使用

```python
# PersonIDはハッシュ可能なので辞書のキーに使える
person_map: Dict[PersonID, Person] = {}
person_map[person.id] = person

# 検索も型安全
found = person_map.get(person.id)
```

## ベストプラクティス

### 1. エラーハンドリング

```python
from inheritance_calculator_core.utils.exceptions import DatabaseException

def find_by_id(self, entity_id: PersonID) -> Optional[Person]:
    try:
        query = "MATCH (p:Person {id: $id}) RETURN p"
        result = self.client.execute_query(query, {"id": str(entity_id)})

        if not result:
            return None

        return Person(**result[0]['p'])
    except Exception as e:
        raise DatabaseException(f"Failed to find person: {e}")
```

### 2. トランザクション管理

```python
def create_with_relationships(self, person: Person, children: List[Person]) -> Person:
    """人物とその子供を一括作成（トランザクション）"""
    tx = self.client.begin_transaction()
    try:
        # 親を作成
        self.create(person)

        # 子供を作成し、関係を構築
        for child in children:
            self.create(child)
            self._create_child_relationship(person.id, child.id)

        self.client.commit_transaction(tx)
        return person
    except Exception as e:
        self.client.rollback_transaction(tx)
        raise DatabaseException(f"Transaction failed: {e}")
```

### 3. カスタムクエリメソッドの追加

```python
class PersonRepository(BaseRepository[Person]):
    # ... 基本メソッド実装 ...

    def find_by_name(self, name: str) -> Optional[Person]:
        """名前で人物を検索（カスタムメソッド）"""
        query = "MATCH (p:Person {name: $name}) RETURN p"
        result = self.client.execute_query(query, {"name": name})

        if not result:
            return None

        return Person(**result[0]['p'])

    def find_alive_persons(self) -> List[Person]:
        """生存している人物のみを取得"""
        query = "MATCH (p:Person {is_alive: true}) RETURN p"
        results = self.client.execute_query(query)
        return [Person(**r['p']) for r in results]
```

## テスト例

```python
import pytest
from unittest.mock import Mock
from inheritance_calculator_core.models.person import Person

class TestPersonRepository:
    def test_create_person(self):
        # モッククライアント
        mock_client = Mock()
        repo = PersonRepository(mock_client)

        # テストデータ
        person = Person(name="テスト太郎", is_alive=True)

        # 実行
        created = repo.create(person)

        # 検証
        assert created.name == "テスト太郎"
        mock_client.execute_query.assert_called_once()

    def test_find_by_id_not_found(self):
        mock_client = Mock()
        mock_client.execute_query.return_value = []
        repo = PersonRepository(mock_client)

        person_id = PersonID.generate()
        result = repo.find_by_id(person_id)

        assert result is None
```

## まとめ

`BaseRepository`を使用することで：

1. **型安全性**: PersonIDにより、IDの型エラーを防止
2. **一貫性**: 統一されたCRUDインターフェース
3. **拡張性**: カスタムメソッドを簡単に追加可能
4. **テスタビリティ**: モックを使った単体テストが容易
5. **保守性**: 変更の影響範囲を最小化

リポジトリパターンにより、データアクセス層とビジネスロジック層を明確に分離できます。
