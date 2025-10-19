"""データベース層の基底クラスとインターフェース"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from uuid import UUID


T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """リポジトリパターンの基底クラス"""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        エンティティを作成

        Args:
            entity: 作成するエンティティ

        Returns:
            作成されたエンティティ

        Raises:
            DatabaseConnectionError: データベース接続エラー
            ValidationError: バリデーションエラー
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        IDでエンティティを取得

        Args:
            entity_id: エンティティID

        Returns:
            エンティティ（存在しない場合はNone）

        Raises:
            DatabaseConnectionError: データベース接続エラー
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        エンティティを更新

        Args:
            entity: 更新するエンティティ

        Returns:
            更新されたエンティティ

        Raises:
            DatabaseConnectionError: データベース接続エラー
            ValidationError: バリデーションエラー
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """
        エンティティを削除

        Args:
            entity_id: エンティティID

        Returns:
            削除成功の場合True

        Raises:
            DatabaseConnectionError: データベース接続エラー
        """
        pass

    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        全エンティティを取得

        Args:
            limit: 取得件数制限
            offset: 取得開始位置

        Returns:
            エンティティのリスト

        Raises:
            DatabaseConnectionError: データベース接続エラー
        """
        pass


class DatabaseClient(ABC):
    """データベースクライアントの基底クラス（同期版）

    Note:
        現在の実装ではNeo4jの同期ドライバーを使用しているため、
        すべてのメソッドは同期版として定義されています。
        将来的に非同期対応が必要になった場合は、
        AsyncDatabaseClientクラスを別途定義することを推奨します。
    """

    @abstractmethod
    def connect(self) -> None:
        """
        データベースに接続

        Raises:
            DatabaseConnectionError: 接続エラー
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        データベース接続を切断

        Raises:
            DatabaseConnectionError: 切断エラー
        """
        pass

    @abstractmethod
    def execute_query(
        self,
        query: str,
        parameters: Optional[dict[str, Any]] = None
    ) -> Any:
        """
        クエリを実行

        Args:
            query: 実行するクエリ
            parameters: クエリパラメータ

        Returns:
            クエリ実行結果

        Raises:
            DatabaseConnectionError: 実行エラー
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        ヘルスチェック

        Returns:
            正常な場合True

        Raises:
            DatabaseConnectionError: 接続エラー
        """
        pass

    @abstractmethod
    def begin_transaction(self) -> Any:
        """
        トランザクションを開始

        Returns:
            トランザクションオブジェクト

        Raises:
            DatabaseConnectionError: トランザクション開始エラー
        """
        pass

    @abstractmethod
    def commit_transaction(self, transaction: Any) -> None:
        """
        トランザクションをコミット

        Args:
            transaction: トランザクションオブジェクト

        Raises:
            DatabaseConnectionError: コミットエラー
        """
        pass

    @abstractmethod
    def rollback_transaction(self, transaction: Any) -> None:
        """
        トランザクションをロールバック

        Args:
            transaction: トランザクションオブジェクト

        Raises:
            DatabaseConnectionError: ロールバックエラー
        """
        pass

    def __enter__(self) -> "DatabaseClient":
        """コンテキストマネージャーの開始"""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """コンテキストマネージャーの終了"""
        self.disconnect()
