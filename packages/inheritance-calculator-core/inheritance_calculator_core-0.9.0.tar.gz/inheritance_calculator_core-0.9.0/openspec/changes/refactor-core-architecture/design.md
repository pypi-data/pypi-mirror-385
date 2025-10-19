# Design Document

## Architecture Overview

このリファクタリングは、以下のアーキテクチャ原則に基づいています：

### 1. 責任分離の原則（Separation of Concerns）
- 各メソッドは単一の責任を持つ
- 検証、計算、結果構築を明確に分離
- 最大メソッド長: 200行

### 2. 型安全性の強化（Type Safety First）
- PersonID値オブジェクトによるドメインモデリング
- mypy --strict モードでの型チェック
- ランタイムエラーの事前防止

### 3. 依存性注入（Dependency Injection)
- コンストラクタインジェクション
- テスタビリティの確保
- モック可能な設計

### 4. 設定外部化（Configuration as Data）
- 民法定数の設定ファイル管理
- 将来の法改正への柔軟な対応
- バリデーション機能の組み込み

## Technical Decisions

### Decision 1: PersonIDを値オブジェクトとして実装
**Context**: 現状、UUIDを直接使用しているが、型安全性が低い

**Options**:
1. UUID型のままにする（現状維持）
2. NewType で型エイリアスを作成
3. frozen dataclassで値オブジェクトを作成

**Decision**: frozen dataclass（Option 3）

**Rationale**:
- 完全な型安全性
- ハッシュ可能（辞書キーとして使用可能）
- カスタムメソッドの追加が容易
- immutabilityの保証

### Decision 2: BaseRepositoryをジェネリクスで実装
**Context**: リポジトリ間で変換ロジックが重複している

**Options**:
1. 共通関数をユーティリティモジュールに配置
2. ミックスインクラスで機能を提供
3. ジェネリックな基底クラスを作成

**Decision**: ジェネリック基底クラス（Option 3）

**Rationale**:
- 型安全性の確保
- 継承による自然な構造
- mypyでの型チェック対応

### Decision 3: 設定ファイルフォーマット
**Context**: 民法定数を外部化する必要がある

**Options**:
1. YAML形式
2. JSON形式
3. Python dictとして定義

**Decision**: YAML形式（Option 1）

**Rationale**:
- 人間が読みやすい
- コメントの記述が可能
- 分数表現が直感的

## Implementation Strategy

### Phase 1: 基盤整備
```
PersonID → ShareCalculator → DI → BaseRepository
```
既存機能に影響を与えず、基盤を整備

### Phase 2: 内部リファクタリング
```
データクラス → メソッド抽出 → calculate()書き換え
```
APIを変更せず、内部実装を改善

### Phase 3: 設定外部化
```
CivilCodeConfig → ShareCalculator統合 → ドキュメント
```
将来の拡張性を確保

## Migration Compatibility

### 後方互換性の保証
- 既存の公開APIは変更しない
- デフォルト値で現行の振る舞いを維持
- deprecation warningで移行を促進

### テスト戦略
- 既存テストはすべて変更なしでパス
- 新機能のテストを追加
- 100%カバレッジを維持

## Risk Mitigation

### リスク1: パフォーマンス劣化
**軽減策**: ベンチマークテストで監視、5%以内の劣化を許容

### リスク2: 予期しない副作用
**軽減策**: 段階的な実装、各フェーズでの完全なテスト実行

### リスク3: チーム学習コスト
**軽減策**: 詳細なドキュメント、移行ガイドの提供
