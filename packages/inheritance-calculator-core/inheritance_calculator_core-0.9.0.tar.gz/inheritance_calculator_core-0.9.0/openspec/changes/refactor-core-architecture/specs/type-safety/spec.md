# Type Safety Enhancement

型安全性を向上させ、ランタイムエラーのリスクを削減します。

## ADDED Requirements

#### Requirement: PersonID値オブジェクトの導入
**民法根拠**: なし（技術的改善）

システムは人物の一意識別子として型安全なPersonID値オブジェクトを提供しなければならない。

#### Scenario: PersonIDの生成と比較
```python
from inheritance_calculator_core.models.value_objects import PersonID

# PersonIDの生成
person_id = PersonID.generate()
assert isinstance(person_id, PersonID)
assert person_id.value is not None

# 文字列からの変換
person_id2 = PersonID.from_string("550e8400-e29b-41d4-a716-446655440000")
assert person_id2.value == UUID("550e8400-e29b-41d4-a716-446655440000")

# 等値比較
person_id3 = PersonID.generate()
assert person_id == person_id2  # False
assert person_id == person_id   # True
```

#### Scenario: PersonモデルでのPersonID使用
```python
from inheritance_calculator_core.models import Person, PersonID

person = Person(
    id=PersonID.generate(),
    name="山田太郎",
    is_alive=True
)

# 型安全なアクセス
person_id: PersonID = person.id
assert isinstance(person_id, PersonID)
```

#### Requirement: SharesディクショナリのPersonIDキー化
**民法根拠**: なし（技術的改善）

相続割合計算の結果は、文字列キーではなくPersonIDオブジェクトをキーとするディクショナリを返さなければならない。

#### Scenario: ShareCalculatorの型安全な戻り値
```python
from inheritance_calculator_core.services import ShareCalculator
from inheritance_calculator_core.models import Person, PersonID
from fractions import Fraction

calculator = ShareCalculator()
spouse = Person(id=PersonID.generate(), name="配偶者", is_alive=True)
child = Person(id=PersonID.generate(), name="子", is_alive=True)

shares = calculator.calculate_shares(
    spouses=[spouse],
    first_rank=[child],
    second_rank=[],
    third_rank=[]
)

# 型安全なアクセス
assert isinstance(shares, dict)
spouse_share = shares[spouse.id]  # PersonIDをキーとして使用
assert spouse_share == Fraction(1, 2)
```

## MODIFIED Requirements

#### Requirement: Personモデルのid属性を型安全に
**変更内容**: `id: UUID`から`id: PersonID`に変更

PersonモデルのID属性は、UUID型ではなくPersonID値オブジェクト型でなければならない。

#### Scenario: 既存コードの後方互換性
```python
from inheritance_calculator_core.models import Person, PersonID

# 新しい方法（推奨）
person = Person(
    id=PersonID.generate(),
    name="山田太郎"
)

# 後方互換性（deprecation warning）
import uuid
person_old = Person(
    id=uuid.uuid4(),  # UUIDも受け入れるが警告
    name="山田花子"
)
# 内部的にPersonIDに変換される
assert isinstance(person_old.id, PersonID)
```

## Implementation Notes

### PersonID Value Object Design
```python
from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Union

@dataclass(frozen=True)
class PersonID:
    """人物の一意識別子（値オブジェクト）"""
    value: UUID

    @classmethod
    def generate(cls) -> 'PersonID':
        """新しいPersonIDを生成"""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> 'PersonID':
        """文字列からPersonIDを生成"""
        return cls(value=UUID(id_str))

    @classmethod
    def from_uuid(cls, uuid_val: UUID) -> 'PersonID':
        """UUIDからPersonIDを生成"""
        return cls(value=uuid_val)

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
```

### Migration Path
1. PersonID値オブジェクトを追加（新規ファイル）
2. Personモデルのidをオプショナルで両方サポート
3. ShareCalculatorの戻り値をPersonIDキーに変更
4. 全テストが通ることを確認
5. deprecation warningを追加
6. 次のメジャーバージョンでUUID直接指定を削除

### Type Checking
```bash
# mypy strict モードでエラーなし
mypy --strict src/inheritance_calculator_core
```
