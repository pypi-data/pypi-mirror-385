# InheritanceCalculator Refactoring

InheritanceCalculatorの巨大なcalculate()メソッドを論理的な単位に分割し、保守性を向上させます。

## MODIFIED Requirements

#### Requirement: calculate()メソッドの責任分離
**変更内容**: 単一の巨大メソッド（605行）を複数の小さなメソッドに分割

InheritanceCalculator.calculate()メソッドは、検証フェーズ、計算フェーズ、結果構築フェーズを明確に分離しなければならない。

#### Scenario: 段階的な相続計算プロセス
```python
from inheritance_calculator_core.services import InheritanceCalculator
from inheritance_calculator_core.models import Person, InheritanceResult

calculator = InheritanceCalculator()
decedent = Person(name="被相続人", is_decedent=True, is_alive=False)
spouse = Person(name="配偶者", is_alive=True)
child = Person(name="子", is_alive=True)

# 公開APIは変更なし
result = calculator.calculate(
    decedent=decedent,
    spouses=[spouse],
    children=[child],
    parents=[],
    siblings=[]
)

# 内部的には以下のフェーズで実行される:
# 1. _validate_and_filter_heirs() - 相続人の検証とフィルタリング
# 2. _calculate_statutory_shares() - 法定相続分の計算
# 3. _build_result() - 結果オブジェクトの構築
# 4. _process_special_cases() - 特殊ケース（再転相続等）の処理
```

#### Scenario: 各フェーズの明確な入出力
```python
# フェーズ1: 検証済み相続人の取得
validated = calculator._validate_and_filter_heirs(
    decedent=decedent,
    spouses=[spouse],
    children=[child],
    parents=[],
    siblings=[],
    renounced=[],
    disqualified=[],
    disinherited=[]
)
assert validated.spouses == [spouse]
assert validated.children == [child]

# フェーズ2: 相続割合の計算
shares = calculator._calculate_statutory_shares(validated)
assert shares[spouse.id] == Fraction(1, 2)
assert shares[child.id] == Fraction(1, 2)

# フェーズ3: 結果の構築
result = calculator._build_result(decedent, validated, shares)
assert result.total_heirs == 2
```

## ADDED Requirements

#### Requirement: ValidatedHeirsデータクラスの導入
**民法根拠**: なし（技術的改善）

システムは検証済み相続人を保持するValidatedHeirsデータクラスを提供しなければならない。

#### Scenario: 検証結果の型安全な受け渡し
```python
from dataclasses import dataclass
from typing import List
from inheritance_calculator_core.models import Person

@dataclass
class ValidatedHeirs:
    """検証済み相続人のコンテナ"""
    spouses: List[Person]
    children: List[Person]
    parents: List[Person]
    siblings: List[Person]

    @property
    def has_first_rank(self) -> bool:
        return len(self.children) > 0

    @property
    def has_second_rank(self) -> bool:
        return len(self.parents) > 0

    @property
    def has_third_rank(self) -> bool:
        return len(self.siblings) > 0

# 使用例
validated = ValidatedHeirs(
    spouses=[spouse],
    children=[child],
    parents=[],
    siblings=[]
)
assert validated.has_first_rank is True
```

#### Requirement: 再転相続ロジックの統合
**民法根拠**: 民法第896条（相続人の相続）

再転相続処理は、情報源の違いに関わらず単一のメソッドで処理されなければならない。

#### Scenario: 統一された再転相続処理
```python
# 従来の2つのメソッドを統合
# - _process_retransfer_inheritance()
# - _process_retransfer_inheritance_with_info()

# 新しい統一インターフェース
result = calculator._process_retransfer_inheritance(
    result=current_result,
    retransfer_info=RetransferInfo(
        deceased_heirs=deceased_heirs,
        targets=targets,
        relationships=relationships,
        second_inheritance_renounced=renounced
    )
)

# RetransferInfoは情報源の違いを吸収
# - 明示的な情報提供パターン
# - 推論による情報構築パターン
```

## REMOVED Requirements

#### Requirement: 重複した再転相続メソッドの削除
**削除理由**: 機能が重複し、保守コストが高い

以下のメソッドは削除され、統合された実装に置き換えられる:
- `_process_retransfer_inheritance()`
- `_find_retransfer_heirs()`
- `_calculate_retransfer_shares()`

新しい統合メソッドで同等の機能を提供する。

## Implementation Notes

### Refactored calculate() Method Structure
```python
def calculate(
    self,
    decedent: Person,
    spouses: List[Person],
    children: List[Person],
    parents: List[Person],
    siblings: List[Person],
    renounced: Optional[List[Person]] = None,
    disqualified: Optional[List[Person]] = None,
    disinherited: Optional[List[Person]] = None,
    sibling_blood_types: Optional[Dict[PersonID, BloodType]] = None,
    retransfer_heirs_info: Optional[Dict[PersonID, List[Person]]] = None,
    retransfer_relationships: Optional[Dict[PersonID, Dict[PersonID, str]]] = None,
    second_inheritance_renounced: Optional[Dict[PersonID, List[Person]]] = None,
) -> InheritanceResult:
    """
    相続計算を実行（リファクタリング版）

    約50-80行に削減（コメント含む）
    """
    # フェーズ1: 入力の正規化（10-15行）
    normalized_input = self._normalize_inputs(
        renounced, disqualified, disinherited,
        sibling_blood_types, retransfer_heirs_info,
        retransfer_relationships, second_inheritance_renounced
    )

    # フェーズ2: バリデータの初期化（5-10行）
    self._initialize_validator(decedent, normalized_input)

    # フェーズ3: 相続人の検証（10-15行）
    validated = self._validate_and_filter_heirs(
        spouses, children, parents, siblings
    )

    # フェーズ4: 相続割合の計算（5-10行）
    shares = self._calculate_statutory_shares(
        validated, normalized_input.sibling_blood_types
    )

    # フェーズ5: 結果の構築（10-15行）
    result = self._build_result(decedent, validated, shares)

    # フェーズ6: 特殊ケースの処理（10-15行）
    if normalized_input.has_retransfer_info:
        result = self._process_retransfer_inheritance(
            result, normalized_input.retransfer_info
        )

    self.log_operation(
        "Inheritance calculation completed",
        total_heirs=result.total_heirs
    )

    return result
```

### Extracted Methods
```python
def _normalize_inputs(self, ...) -> NormalizedInput:
    """入力パラメータの正規化（約20-30行）"""

def _initialize_validator(self, decedent: Person, input: NormalizedInput) -> None:
    """バリデータの初期化（約10-15行）"""

def _validate_and_filter_heirs(self, ...) -> ValidatedHeirs:
    """相続人の検証とフィルタリング（約30-40行）"""

def _calculate_statutory_shares(self, ...) -> Dict[PersonID, Fraction]:
    """法定相続分の計算（約15-20行）"""

def _build_result(self, ...) -> InheritanceResult:
    """結果オブジェクトの構築（約40-50行）"""

def _process_retransfer_inheritance(self, ...) -> InheritanceResult:
    """再転相続の統合処理（約80-100行）"""
```

### Method Size Goals
- **calculate()**: ~80行以下（コメント含む）
- **各抽出メソッド**: ~50行以下
- **総行数**: 変更なし（分割により可読性向上）

### Migration Path
1. ValidatedHeirs, NormalizedInput, RetransferInfoデータクラスを追加
2. 新しいプライベートメソッドを実装
3. calculate()を新しいメソッドを使用するように書き換え
4. 古い実装をコメントアウト
5. すべてのテストがパスすることを確認
6. 古い実装を削除
