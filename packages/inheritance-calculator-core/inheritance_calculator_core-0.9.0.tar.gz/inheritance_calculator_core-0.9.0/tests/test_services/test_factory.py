"""ServiceFactoryのテスト"""
import pytest

from inheritance_calculator_core.services.factory import ServiceFactory
from inheritance_calculator_core.services.heir_validator import HeirValidator
from inheritance_calculator_core.services.share_calculator import ShareCalculator
from inheritance_calculator_core.services.inheritance_calculator import InheritanceCalculator


class TestServiceFactory:
    """ServiceFactoryのテスト"""

    def test_get_heir_validator(self):
        """HeirValidatorインスタンスを取得できる"""
        factory = ServiceFactory()
        validator = factory.get_heir_validator()

        assert isinstance(validator, HeirValidator)

    def test_heir_validator_singleton(self):
        """HeirValidatorはシングルトンとして動作する"""
        factory = ServiceFactory()
        validator1 = factory.get_heir_validator()
        validator2 = factory.get_heir_validator()

        assert validator1 is validator2

    def test_get_share_calculator(self):
        """ShareCalculatorインスタンスを取得できる"""
        factory = ServiceFactory()
        calculator = factory.get_share_calculator()

        assert isinstance(calculator, ShareCalculator)

    def test_share_calculator_singleton(self):
        """ShareCalculatorはシングルトンとして動作する"""
        factory = ServiceFactory()
        calculator1 = factory.get_share_calculator()
        calculator2 = factory.get_share_calculator()

        assert calculator1 is calculator2

    def test_get_inheritance_calculator(self):
        """InheritanceCalculatorインスタンスを取得できる"""
        factory = ServiceFactory()
        calculator = factory.get_inheritance_calculator()

        assert isinstance(calculator, InheritanceCalculator)

    def test_inheritance_calculator_singleton(self):
        """InheritanceCalculatorはシングルトンとして動作する"""
        factory = ServiceFactory()
        calculator1 = factory.get_inheritance_calculator()
        calculator2 = factory.get_inheritance_calculator()

        assert calculator1 is calculator2

    def test_inheritance_calculator_dependency_injection(self):
        """InheritanceCalculatorに依存が正しく注入される"""
        factory = ServiceFactory()
        calculator = factory.get_inheritance_calculator()

        # 注入された依存がファクトリから取得したインスタンスと同一であることを確認
        assert calculator.validator is factory.get_heir_validator()
        assert calculator.calculator is factory.get_share_calculator()

    def test_reset(self):
        """reset()で全てのインスタンスがクリアされる"""
        factory = ServiceFactory()

        # インスタンスを取得
        validator1 = factory.get_heir_validator()
        calculator1 = factory.get_share_calculator()
        inheritance_calc1 = factory.get_inheritance_calculator()

        # リセット
        factory.reset()

        # 再度取得すると別のインスタンスになる
        validator2 = factory.get_heir_validator()
        calculator2 = factory.get_share_calculator()
        inheritance_calc2 = factory.get_inheritance_calculator()

        assert validator1 is not validator2
        assert calculator1 is not calculator2
        assert inheritance_calc1 is not inheritance_calc2

    def test_multiple_factories_independent(self):
        """複数のファクトリインスタンスは独立している"""
        factory1 = ServiceFactory()
        factory2 = ServiceFactory()

        calculator1 = factory1.get_inheritance_calculator()
        calculator2 = factory2.get_inheritance_calculator()

        # 異なるファクトリから取得したインスタンスは異なる
        assert calculator1 is not calculator2
        assert calculator1.validator is not calculator2.validator
        assert calculator1.calculator is not calculator2.calculator
