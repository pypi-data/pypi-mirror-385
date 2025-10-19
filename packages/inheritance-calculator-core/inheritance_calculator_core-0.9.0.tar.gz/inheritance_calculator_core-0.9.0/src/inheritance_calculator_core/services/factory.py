"""サービスファクトリ

サービスインスタンスを生成し、依存関係を自動的に注入する。
"""
from typing import Optional

from .heir_validator import HeirValidator
from .share_calculator import ShareCalculator
from .inheritance_calculator import InheritanceCalculator


class ServiceFactory:
    """
    サービスファクトリ

    サービスインスタンスの生成と依存性注入を管理する。
    シングルトンパターンでサービスインスタンスを再利用可能。
    """

    def __init__(self) -> None:
        """初期化"""
        self._heir_validator: Optional[HeirValidator] = None
        self._share_calculator: Optional[ShareCalculator] = None
        self._inheritance_calculator: Optional[InheritanceCalculator] = None

    def get_heir_validator(self) -> HeirValidator:
        """
        HeirValidatorインスタンスを取得

        Returns:
            HeirValidatorインスタンス（シングルトン）
        """
        if self._heir_validator is None:
            self._heir_validator = HeirValidator()
        return self._heir_validator

    def get_share_calculator(self) -> ShareCalculator:
        """
        ShareCalculatorインスタンスを取得

        Returns:
            ShareCalculatorインスタンス（シングルトン）
        """
        if self._share_calculator is None:
            self._share_calculator = ShareCalculator()
        return self._share_calculator

    def get_inheritance_calculator(self) -> InheritanceCalculator:
        """
        InheritanceCalculatorインスタンスを取得

        依存するHeirValidatorとShareCalculatorを自動的に注入する。

        Returns:
            InheritanceCalculatorインスタンス（シングルトン）
        """
        if self._inheritance_calculator is None:
            self._inheritance_calculator = InheritanceCalculator(
                validator=self.get_heir_validator(),
                calculator=self.get_share_calculator()
            )
        return self._inheritance_calculator

    def reset(self) -> None:
        """
        全てのキャッシュされたインスタンスをリセット

        主にテスト用途で使用。
        """
        self._heir_validator = None
        self._share_calculator = None
        self._inheritance_calculator = None
