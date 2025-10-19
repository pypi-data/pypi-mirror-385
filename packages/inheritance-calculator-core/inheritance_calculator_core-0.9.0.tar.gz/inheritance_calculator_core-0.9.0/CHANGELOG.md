# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2025-10-19

### Added
- **PersonID値オブジェクト**: 型安全なID管理のための`PersonID`クラスを導入
  - UUIDをラップしたfrozenデータクラス
  - ハッシュ可能で辞書のキーとして使用可能
  - `generate()`, `from_uuid()`, `from_string()`メソッドを提供
- **ServiceFactory**: サービスインスタンスの一元管理のためのファクトリパターンを実装
  - シングルトンパターンによる効率的なインスタンス管理
  - 依存性注入のサポート
  - テスト用の`reset()`メソッド
- **BaseRepository抽象クラス**: 同期版リポジトリの基底クラスを追加
  - CRUD操作の統一インターフェース
  - PersonIDベースの型安全なデータアクセス
  - 使用ガイドドキュメント(`docs/base_repository_usage.md`)を追加
- **GitHub Actions統合**: CI/CD自動化の実装
  - テスト自動実行ワークフロー
  - PyPI自動公開ワークフロー

### Changed
- **型安全性の向上**: 文字列ベースのIDからPersonIDへ全面移行
  - `ShareCalculator`の全メソッドが`Dict[PersonID, Fraction]`を返却
  - `InheritanceCalculator`がPersonIDキーの辞書を受け入れ
  - `BaseEntity.id`フィールドをPersonID型に変更
- **依存性注入のサポート**: `InheritanceCalculator`にオプション引数を追加
  - `validator`パラメータでHeirValidatorを注入可能
  - `calculator`パラメータでShareCalculatorを注入可能
  - 後方互換性を維持（引数省略時はデフォルトインスタンス使用）
- **Neo4jService改善**: PersonIDを使用した兄弟姉妹の血族関係管理

### Fixed
- 型チェックエラーの解消: mypy --strictモードでの全チェックをパス
- テストコードの型安全性向上: 全テストファイルでPersonID使用に統一
- インポートパスの修正: テストモックでの正しいモジュールパス使用

### Development
- テストカバレッジ: 59% (206/216 tests passing)
- Python 3.12+対応
- 開発ツール: pytest, mypy, ruff, black統合

## [Unreleased]

### Planned
- Phase 2: 新継承パターン対応（遺言、遺産分割協議）
- Phase 3: パフォーマンス最適化
- 非同期リポジトリ対応（AsyncDatabaseClient）

---

[0.9.0]: https://github.com/kazumasakawahara/inheritance-calculator-core/releases/tag/v0.9.0
