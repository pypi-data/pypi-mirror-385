# Refactor Core Architecture for Maintainability and Type Safety

## Summary

包括的なアーキテクチャリファクタリングにより、コアライブラリの保守性、型安全性、テスタビリティを大幅に改善します。

## Why

現在のコードベースは100%のテストカバレッジを達成していますが、以下の構造的な問題により長期的な保守性に課題があります：

1. **大規模メソッドによる保守性の低下**: InheritanceCalculator.calculate()が605行と巨大で、変更リスクが高い
2. **型安全性の欠如によるバグリスク**: ID変換が散在し、ランタイムエラーの可能性がある
3. **依存性注入の不完全実装**: サービス層がハードコードされ、テストが困難
4. **コードの重複**: 再転相続ロジックが2箇所で重複実装され、保守コストが増大
5. **将来の拡張性の課題**: 民法定数がハードコードされ、法改正時の変更コストが高い

これらの問題は、今後の機能追加や法改正対応において、開発速度の低下と品質リスクの増大を招きます。

## What Changes

本提案では、以下の5つの capability を追加/変更します：

### 1. **type-safety** (新規追加)
- PersonID値オブジェクトの導入
- SharesディクショナリのPersonIDキー化
- Personモデルのid属性型変更

### 2. **service-layer** (変更)
- InheritanceCalculatorへの依存性注入実装
- ServiceFactoryの追加
- 型ヒントの明示化

### 3. **calculator-refactor** (変更)
- calculate()メソッドの責任分離
- ValidatedHeirsデータクラスの追加
- 再転相続ロジックの統合
- 重複メソッドの削除

### 4. **repository-pattern** (変更)
- リポジトリ内部メソッドのカプセル化
- BaseRepositoryジェネリッククラスの追加
- リポジトリ間依存性の削除

### 5. **configuration** (新規追加)
- CivilCodeConfig設定クラスの追加
- 民法定数の外部ファイル化
- ShareCalculatorの設定注入対応

すべての変更は既存APIの後方互換性を維持し、段階的に実装されます。

## Motivation

現在のコードベースは100%のテストカバレッジを達成していますが、以下の構造的な問題により長期的な保守性に課題があります：

### Critical Issues
1. **責任過多の計算ロジック**: `InheritanceCalculator.calculate()`が605行の単一メソッドで複数の責任を持つ
2. **型安全性の欠如**: ID変換(`str(person.id)`)が至る所にあり、型安全性が低い
3. **依存性注入の不完全実装**: サービス層の依存関係がハードコードされ、テスタビリティが低い
4. **コードの重複**: 再転相続ロジックが2つのメソッドで重複実装
5. **カプセル化違反**: リポジトリの内部メソッドが外部からアクセス可能

### Impact on Business
- **保守コスト増**: 大規模メソッドの変更リスクが高い
- **バグリスク**: 型安全性の欠如によるランタイムエラーの可能性
- **開発速度低下**: テストが困難なコード構造
- **技術的負債**: 将来の機能追加が困難

## Proposed Changes

### 1. InheritanceCalculatorの責任分離
- `calculate()`メソッドを論理的な単位に分割
- 検証フェーズ、計算フェーズ、結果構築フェーズを明確に分離

### 2. 型安全性の向上
- PersonIDを新しい値オブジェクトとして導入
- 型ヒントを強化し、mypy strictモードに対応

### 3. 依存性注入の完全実装
- サービス層のコンストラクタで依存性を注入
- テスト時のモック可能性を確保

### 4. 再転相続ロジックの統合
- 重複した実装を単一の実装に統合
- Strategy パターンで情報源の違いを吸収

### 5. リポジトリパターンの完全実装
- 内部メソッドのprivate化（命名規約の強化）
- 共通変換ロジックを基底クラスに抽出

### 6. 民法定数の設定管理
- ハードコードされた法定相続分を設定ファイルに抽出
- 将来の法改正に容易に対応可能な構造

## Benefits

### Immediate
- ✅ コードの可読性向上（メソッドサイズ削減）
- ✅ 型安全性向上（ランタイムエラー減少）
- ✅ テスタビリティ向上（依存性注入）

### Long-term
- 📈 保守コスト削減（変更箇所の局所化）
- 🔒 品質向上（型チェックによるバグ防止）
- 🚀 開発速度向上（明確な責任分離）
- 🔧 拡張性向上（新機能追加の容易化）

## Migration Strategy

### Phase 1: 基盤整備（Breaking Changes なし）
- PersonID値オブジェクトの導入
- 依存性注入の実装
- 既存のインターフェースは維持

### Phase 2: 内部リファクタリング（API互換性維持）
- InheritanceCalculatorの分割
- 再転相続ロジックの統合
- 既存のテストはすべてパス

### Phase 3: 設定外部化（後方互換性確保）
- 民法定数の設定ファイル化
- デフォルト値で既存の振る舞いを保証

## Risks and Mitigations

### Risk: テストの網羅性低下
**Mitigation**: 100%カバレッジを維持する CI チェック

### Risk: パフォーマンスへの影響
**Mitigation**: ベンチマークテストで性能劣化を監視

### Risk: 互換性の破損
**Mitigation**: 既存のすべてのテストが変更なしでパスすることを確認

## Success Criteria

1. ✅ すべての既存テストがパス（100%カバレッジ維持）
2. ✅ mypy --strict モードでエラーゼロ
3. ✅ InheritanceCalculator.calculate()のメソッド長が200行以下
4. ✅ 型変換(`str(id)`)の使用箇所が80%削減
5. ✅ サービス層のコンストラクタで依存性注入が実装されている

## Timeline

- **Phase 1**: 2週間（基盤整備）
- **Phase 2**: 3週間（内部リファクタリング）
- **Phase 3**: 1週間（設定外部化）

**Total**: 6週間

## Related Changes

このプロポーザルは以下の改善を統合したものです：
- refactor-inheritance-calculator
- improve-type-safety
- enhance-dependency-injection
- consolidate-retransfer-logic
- fix-repository-encapsulation
- extract-civil-code-constants
