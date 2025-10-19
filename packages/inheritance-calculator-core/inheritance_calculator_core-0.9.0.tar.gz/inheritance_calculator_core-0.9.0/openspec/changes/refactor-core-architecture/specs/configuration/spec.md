# Civil Code Constants Configuration

民法の定数を設定ファイルに外部化し、将来の法改正に柔軟に対応できるようにします。

## ADDED Requirements

#### Requirement: 法定相続分定数の設定ファイル化
**民法根拠**: 民法第900条（法定相続分）

法定相続分の割合は、設定ファイルで管理され、コードから分離されなければならない。

#### Scenario: 設定ファイルからの法定相続分読み込み
```python
# config/civil_code.yaml
civil_code:
  article_900:
    # 民法第900条1号: 配偶者と子
    spouse_and_children:
      spouse_share: "1/2"
      children_share: "1/2"

    # 民法第900条2号: 配偶者と直系尊属
    spouse_and_parents:
      spouse_share: "2/3"
      parents_share: "1/3"

    # 民法第900条3号: 配偶者と兄弟姉妹
    spouse_and_siblings:
      spouse_share: "3/4"
      siblings_share: "1/4"

    # 民法第900条4号: 半血兄弟姉妹の相続分
    half_blood_sibling_ratio: "1/2"
```

```python
from inheritance_calculator_core.config import CivilCodeConfig

config = CivilCodeConfig.load()

# 法定相続分の取得
spouse_share = config.get_spouse_share_with_children()
assert spouse_share == Fraction(1, 2)

children_share = config.get_children_share_with_spouse()
assert children_share == Fraction(1, 2)
```

#### Scenario: ShareCalculatorでの設定使用
```python
from inheritance_calculator_core.services import ShareCalculator
from inheritance_calculator_core.config import CivilCodeConfig

# 設定を注入
config = CivilCodeConfig.load()
calculator = ShareCalculator(config=config)

# 設定に基づいた計算
shares = calculator.calculate_shares(
    spouses=[spouse],
    first_rank=[child],
    second_rank=[],
    third_rank=[]
)

# 設定ファイルの値が使用される
assert shares[spouse.id] == config.get_spouse_share_with_children()
```

#### Requirement: デフォルト設定による後方互換性
**民法根拠**: なし（技術的改善）

設定ファイルが提供されない場合、システムは現行の民法に基づくデフォルト値を使用しなければならない。

#### Scenario: デフォルト設定での動作
```python
from inheritance_calculator_core.services import ShareCalculator

# 設定なしでインスタンス化（デフォルト値使用）
calculator = ShareCalculator()

# 現行民法のデフォルト値で計算
shares = calculator.calculate_shares(
    spouses=[spouse],
    first_rank=[child],
    second_rank=[],
    third_rank=[]
)

# 民法第900条1号のデフォルト値
assert shares[spouse.id] == Fraction(1, 2)
assert shares[child.id] == Fraction(1, 2)
```

#### Requirement: 設定値のバリデーション
**民法根拠**: なし（技術的改善）

設定ファイルの法定相続分は、合計が1（100%）になることが検証されなければならない。

#### Scenario: 不正な設定の検出
```python
from inheritance_calculator_core.config import CivilCodeConfig, ConfigValidationError

# 不正な設定ファイル
invalid_config = """
civil_code:
  article_900:
    spouse_and_children:
      spouse_share: "2/3"  # 不正: 配偶者2/3 + 子2/3 = 4/3 > 1
      children_share: "2/3"
"""

# バリデーションエラー
try:
    config = CivilCodeConfig.from_yaml(invalid_config)
    assert False, "Should raise ConfigValidationError"
except ConfigValidationError as e:
    assert "合計が1を超えています" in str(e)
```

## MODIFIED Requirements

#### Requirement: ShareCalculatorの設定注入対応
**変更内容**: コンストラクタでCivilCodeConfigを受け入れる

ShareCalculatorは、法定相続分の設定をコンストラクタで受け取ることができなければならない。

#### Scenario: カスタム設定での計算
```python
from inheritance_calculator_core.services import ShareCalculator
from inheritance_calculator_core.config import CivilCodeConfig

# カスタム設定（将来の法改正を想定）
custom_config = CivilCodeConfig(
    spouse_share_with_children=Fraction(3, 5),  # 改正後: 3/5
    children_share_with_spouse=Fraction(2, 5)   # 改正後: 2/5
)

calculator = ShareCalculator(config=custom_config)

shares = calculator.calculate_shares(
    spouses=[spouse],
    first_rank=[child],
    second_rank=[],
    third_rank=[]
)

# カスタム設定が適用される
assert shares[spouse.id] == Fraction(3, 5)
assert shares[child.id] == Fraction(2, 5)
```

## Implementation Notes

### CivilCodeConfig Implementation
```python
# src/inheritance_calculator_core/config/civil_code.py
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional
import yaml
from pathlib import Path

@dataclass
class CivilCodeConfig:
    """民法の定数設定"""

    # 民法第900条1号: 配偶者と子
    spouse_share_with_children: Fraction = Fraction(1, 2)
    children_share_with_spouse: Fraction = Fraction(1, 2)

    # 民法第900条2号: 配偶者と直系尊属
    spouse_share_with_parents: Fraction = Fraction(2, 3)
    parents_share_with_spouse: Fraction = Fraction(1, 3)

    # 民法第900条3号: 配偶者と兄弟姉妹
    spouse_share_with_siblings: Fraction = Fraction(3, 4)
    siblings_share_with_spouse: Fraction = Fraction(1, 4)

    # 民法第900条4号: 半血兄弟姉妹の相続分
    half_blood_sibling_ratio: Fraction = Fraction(1, 2)

    def __post_init__(self) -> None:
        """設定値のバリデーション"""
        self._validate()

    def _validate(self) -> None:
        """設定値が正しいか検証"""
        validations = [
            (
                self.spouse_share_with_children + self.children_share_with_spouse,
                "配偶者と子の相続分"
            ),
            (
                self.spouse_share_with_parents + self.parents_share_with_spouse,
                "配偶者と直系尊属の相続分"
            ),
            (
                self.spouse_share_with_siblings + self.siblings_share_with_spouse,
                "配偶者と兄弟姉妹の相続分"
            ),
        ]

        for total, name in validations:
            if total != Fraction(1, 1):
                raise ConfigValidationError(
                    f"{name}の合計が1ではありません: {total} ({float(total)})"
                )

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'CivilCodeConfig':
        """
        設定ファイルから読み込み

        Args:
            config_path: 設定ファイルパス（省略時はデフォルト値使用）

        Returns:
            CivilCodeConfig インスタンス
        """
        if config_path is None:
            # デフォルト設定を使用
            return cls()

        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data['civil_code']['article_900'])

    @classmethod
    def from_dict(cls, data: dict) -> 'CivilCodeConfig':
        """辞書からインスタンスを生成"""
        def parse_fraction(s: str) -> Fraction:
            """文字列を分数に変換"""
            return Fraction(s)

        return cls(
            spouse_share_with_children=parse_fraction(
                data['spouse_and_children']['spouse_share']
            ),
            children_share_with_spouse=parse_fraction(
                data['spouse_and_children']['children_share']
            ),
            spouse_share_with_parents=parse_fraction(
                data['spouse_and_parents']['spouse_share']
            ),
            parents_share_with_spouse=parse_fraction(
                data['spouse_and_parents']['parents_share']
            ),
            spouse_share_with_siblings=parse_fraction(
                data['spouse_and_siblings']['spouse_share']
            ),
            siblings_share_with_spouse=parse_fraction(
                data['spouse_and_siblings']['siblings_share']
            ),
            half_blood_sibling_ratio=parse_fraction(
                data['half_blood_sibling_ratio']
            ),
        )

    def get_spouse_share_with_children(self) -> Fraction:
        """配偶者と子がいる場合の配偶者相続分を取得"""
        return self.spouse_share_with_children

    def get_children_share_with_spouse(self) -> Fraction:
        """配偶者と子がいる場合の子相続分を取得"""
        return self.children_share_with_spouse

    # 他のゲッターメソッド...
```

### ShareCalculator Modification
```python
class ShareCalculator(BaseService[Person]):
    """相続割合計算サービス"""

    def __init__(self, config: Optional[CivilCodeConfig] = None) -> None:
        """
        初期化

        Args:
            config: 民法定数設定（省略時はデフォルト値）
        """
        super().__init__()
        self.config = config if config is not None else CivilCodeConfig()

    def _calculate_spouse_and_children(
        self, spouses: List[Person], children: List[Person]
    ) -> Dict[PersonID, Fraction]:
        """配偶者と子の場合"""
        shares = {}

        # 設定から法定相続分を取得
        spouse_total = self.config.get_spouse_share_with_children()
        children_total = self.config.get_children_share_with_spouse()

        # 配偶者の相続分
        share_per_spouse = spouse_total / len(spouses)
        for spouse in spouses:
            shares[spouse.id] = share_per_spouse

        # 子の相続分
        share_per_child = children_total / len(children)
        for child in children:
            shares[child.id] = share_per_child

        return shares
```

### Migration Path
1. CivilCodeConfig クラスを作成
2. デフォルト値で現行民法の値を設定
3. ShareCalculatorにオプショナルで設定を注入
4. ハードコードされた値を設定から取得するように変更
5. すべてのテストがパスすることを確認
6. config/civil_code.yamlのサンプルファイルを提供

### Benefits
- **法改正対応**: 設定ファイル変更のみで対応可能
- **テスタビリティ**: カスタム設定でエッジケーステスト可能
- **保守性**: 定数が一箇所に集約
- **透明性**: 民法の条文と設定の対応が明確
