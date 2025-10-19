# Service Layer Dependency Injection

サービス層に適切な依存性注入を実装し、テスタビリティを向上させます。

## MODIFIED Requirements

#### Requirement: InheritanceCalculatorのコンストラクタ依存性注入
**変更内容**: 依存サービスをコンストラクタで注入可能に

InheritanceCalculatorは、HeirValidatorとShareCalculatorをコンストラクタで受け取ることができなければならない。

#### Scenario: 依存性注入によるインスタンス化
```python
from inheritance_calculator_core.services import (
    InheritanceCalculator,
    HeirValidator,
    ShareCalculator
)

# デフォルトインスタンス（後方互換性）
calculator = InheritanceCalculator()
assert isinstance(calculator.validator, HeirValidator)
assert isinstance(calculator.calculator, ShareCalculator)

# 依存性注入（推奨）
custom_validator = HeirValidator()
custom_calculator = ShareCalculator()

calculator = InheritanceCalculator(
    validator=custom_validator,
    share_calculator=custom_calculator
)
assert calculator.validator is custom_validator
assert calculator.calculator is custom_calculator
```

#### Scenario: テスト時のモック注入
```python
from unittest.mock import Mock
from inheritance_calculator_core.services import InheritanceCalculator

# モックオブジェクトの注入
mock_validator = Mock(spec=HeirValidator)
mock_calculator = Mock(spec=ShareCalculator)

calculator = InheritanceCalculator(
    validator=mock_validator,
    share_calculator=mock_calculator
)

# テスト時の振る舞い制御
mock_calculator.calculate_shares.return_value = {...}
result = calculator.calculate(...)

# モックの呼び出し検証
mock_validator.validate_spouse.assert_called_once()
```

## ADDED Requirements

#### Requirement: サービスファクトリの提供
**民法根拠**: なし（技術的改善）

システムは、標準的な依存関係でサービスインスタンスを生成するファクトリを提供しなければならない。

#### Scenario: ファクトリを使った標準インスタンス生成
```python
from inheritance_calculator_core.services.factory import ServiceFactory

# 標準構成でのサービス生成
calculator = ServiceFactory.create_inheritance_calculator()
assert isinstance(calculator, InheritanceCalculator)

# カスタム構成での生成
custom_config = {...}
calculator = ServiceFactory.create_inheritance_calculator(
    config=custom_config
)
```

#### Requirement: 依存性の型ヒント明示
**民法根拠**: なし（技術的改善）

すべてのサービスクラスのコンストラクタは、依存性の型ヒントを明示しなければならない。

#### Scenario: 型安全なコンストラクタ
```python
from typing import Optional

class InheritanceCalculator(BaseService[InheritanceResult]):
    def __init__(
        self,
        validator: Optional[HeirValidator] = None,
        share_calculator: Optional[ShareCalculator] = None
    ) -> None:
        super().__init__()
        self.validator = validator or HeirValidator()
        self.calculator = share_calculator or ShareCalculator()
```

## Implementation Notes

### Constructor Signature
```python
class InheritanceCalculator(BaseService[InheritanceResult]):
    """相続計算サービス"""

    def __init__(
        self,
        validator: Optional[HeirValidator] = None,
        share_calculator: Optional[ShareCalculator] = None
    ) -> None:
        """
        初期化

        Args:
            validator: 相続人検証サービス（省略時はデフォルトインスタンス）
            share_calculator: 相続割合計算サービス（省略時はデフォルトインスタンス）
        """
        super().__init__()
        self.validator = validator if validator is not None else HeirValidator()
        self.calculator = share_calculator if share_calculator is not None else ShareCalculator()
```

### Service Factory Implementation
```python
# src/inheritance_calculator_core/services/factory.py
from typing import Optional, Dict, Any

class ServiceFactory:
    """サービスインスタンス生成のファクトリ"""

    @staticmethod
    def create_inheritance_calculator(
        config: Optional[Dict[str, Any]] = None
    ) -> InheritanceCalculator:
        """
        InheritanceCalculatorインスタンスを生成

        Args:
            config: 設定（オプション）

        Returns:
            InheritanceCalculatorインスタンス
        """
        validator = HeirValidator()
        share_calculator = ShareCalculator()

        return InheritanceCalculator(
            validator=validator,
            share_calculator=share_calculator
        )

    @staticmethod
    def create_heir_validator() -> HeirValidator:
        """HeirValidatorインスタンスを生成"""
        return HeirValidator()

    @staticmethod
    def create_share_calculator() -> ShareCalculator:
        """ShareCalculatorインスタンスを生成"""
        return ShareCalculator()
```

### Migration Path
1. コンストラクタにオプショナル引数を追加
2. デフォルト値で後方互換性を確保
3. ServiceFactoryを追加
4. 既存のテストを修正せずにパス
5. 新しいテストで依存性注入パターンを推奨

### Testing Benefits
```python
# テストが簡潔に
def test_calculate_with_mock():
    # Arrange
    mock_validator = Mock(spec=HeirValidator)
    mock_validator.validate_spouse.return_value = True

    mock_calculator = Mock(spec=ShareCalculator)
    mock_calculator.calculate_shares.return_value = {
        person_id: Fraction(1, 2)
    }

    calculator = InheritanceCalculator(
        validator=mock_validator,
        share_calculator=mock_calculator
    )

    # Act
    result = calculator.calculate(...)

    # Assert
    assert len(result.heirs) == 1
    mock_validator.validate_spouse.assert_called()
```
