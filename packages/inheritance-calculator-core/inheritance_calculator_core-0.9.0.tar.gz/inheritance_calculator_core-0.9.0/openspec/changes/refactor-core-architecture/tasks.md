# Implementation Tasks

実装タスクを段階的に実施し、各段階で100%テストカバレッジを維持します。

## Phase 1: 基盤整備（2週間）

### Task 1.1: PersonID値オブジェクトの導入
**所要時間**: 3日
**依存**: なし
**検証**: 型チェックとユニットテスト

- [ ] `src/inheritance_calculator_core/models/value_objects.py` を作成
- [ ] `PersonID` クラスを実装（frozen dataclass）
  - `generate()`, `from_string()`, `from_uuid()` メソッド
  - `__hash__()`, `__str__()` 実装
- [ ] `Person.id` の型を `Union[UUID, PersonID]` に変更（移行期間用）
- [ ] PersonID使用のユニットテストを追加（10+テストケース）
- [ ] mypy型チェックでエラーなしを確認

**検証基準**:
```bash
pytest tests/test_models/test_value_objects.py -v --cov
mypy src/inheritance_calculator_core/models/value_objects.py --strict
```

---

### Task 1.2: ShareCalculatorのPersonIDキー対応
**所要時間**: 2日
**依存**: Task 1.1
**検証**: 既存テスト全パス + 新規テスト

- [ ] `ShareCalculator.calculate_shares()` の戻り値を `Dict[PersonID, Fraction]` に変更
- [ ] 内部実装を `str(person.id)` から `person.id` に変更
- [ ] InheritanceCalculatorでの使用箇所を更新
- [ ] 既存の全テストが通ることを確認
- [ ] PersonIDキーの新規テストを追加

**検証基準**:
```bash
pytest tests/test_services/test_share_calculator.py -v --cov=src/inheritance_calculator_core/services/share_calculator.py
pytest tests/test_services/test_inheritance_calculator.py -v
```

---

### Task 1.3: 依存性注入の実装（InheritanceCalculator）
**所要時間**: 2日
**依存**: なし
**検証**: モックテスト + 既存テスト全パス

- [ ] `InheritanceCalculator.__init__()` にオプショナル引数追加
  - `validator: Optional[HeirValidator] = None`
  - `share_calculator: Optional[ShareCalculator] = None`
- [ ] デフォルト値で後方互換性を確保
- [ ] モックを使用したテストケースを追加（5+ケース）
- [ ] 既存の全テストが通ることを確認

**検証基準**:
```bash
pytest tests/test_services/test_inheritance_calculator.py::test_dependency_injection -v
pytest tests/test_services/ -v --cov
```

---

### Task 1.4: ServiceFactoryの実装
**所要時間**: 1日
**依存**: Task 1.3
**検証**: ファクトリテスト

- [ ] `src/inheritance_calculator_core/services/factory.py` を作成
- [ ] `ServiceFactory` クラスを実装
  - `create_inheritance_calculator()`
  - `create_heir_validator()`
  - `create_share_calculator()`
- [ ] ファクトリのテストを追加
- [ ] ドキュメントを更新

**検証基準**:
```bash
pytest tests/test_services/test_factory.py -v --cov=src/inheritance_calculator_core/services/factory.py
```

---

### Task 1.5: BaseRepositoryの実装
**所要時間**: 3日
**依存**: Task 1.1
**検証**: リポジトリテスト全パス

- [ ] `src/inheritance_calculator_core/database/base_repository.py` を作成
- [ ] `BaseRepository[T]` ジェネリッククラスを実装
  - `_node_to_model()` 抽象メソッド
  - `_convert_neo4j_date()` 共通メソッド
  - `_nodes_to_models()` ヘルパーメソッド
- [ ] PersonRepository, RelationshipRepositoryをBaseRepositoryから継承
- [ ] `_to_person` → `_node_to_model` にリネーム
- [ ] リポジトリ間の依存を削除（RelationshipRepository.person_repo削除）
- [ ] 既存のリポジトリテストが全パス

**検証基準**:
```bash
pytest tests/test_database/test_repositories.py -v --cov=src/inheritance_calculator_core/database
mypy src/inheritance_calculator_core/database/ --strict
```

---

## Phase 2: 内部リファクタリング（3週間）

### Task 2.1: データクラスの定義
**所要時間**: 2日
**依存**: Phase 1完了
**検証**: データクラステスト

- [ ] `src/inheritance_calculator_core/models/calculation.py` を作成
- [ ] `ValidatedHeirs` データクラスを実装
  - `spouses`, `children`, `parents`, `siblings` フィールド
  - `has_first_rank`, `has_second_rank`, `has_third_rank` プロパティ
- [ ] `NormalizedInput` データクラスを実装
- [ ] `RetransferInfo` データクラスを実装
- [ ] データクラスのテストを追加（20+ケース）

**検証基準**:
```bash
pytest tests/test_models/test_calculation.py -v --cov=src/inheritance_calculator_core/models/calculation.py
```

---

### Task 2.2: InheritanceCalculator._normalize_inputs()の抽出
**所要時間**: 1日
**依存**: Task 2.1
**検証**: ユニットテスト

- [ ] `_normalize_inputs()` メソッドを実装
- [ ] `calculate()` から入力正規化ロジックを移動
- [ ] テストケースを追加（10+ケース）
- [ ] 既存テストが全パス

**検証基準**:
```bash
pytest tests/test_services/test_inheritance_calculator.py::test_normalize_inputs -v
```

---

### Task 2.3: InheritanceCalculator._validate_and_filter_heirs()の抽出
**所要時間**: 2日
**依存**: Task 2.1
**検証**: ユニットテスト + 統合テスト

- [ ] `_validate_and_filter_heirs()` メソッドを実装
- [ ] `calculate()` から検証ロジックを移動
- [ ] `ValidatedHeirs` を戻り値とする
- [ ] テストケースを追加（15+ケース）
- [ ] 既存の統合テストが全パス

**検証基準**:
```bash
pytest tests/test_services/test_inheritance_calculator.py::test_validate_and_filter_heirs -v
pytest tests/test_services/test_inheritance_calculator.py -v
```

---

### Task 2.4: InheritanceCalculator._calculate_statutory_shares()の抽出
**所要時間**: 1日
**依存**: Task 2.3
**検証**: ユニットテスト

- [ ] `_calculate_statutory_shares()` メソッドを実装
- [ ] `calculate()` から相続割合計算ロジックを移動
- [ ] テストケースを追加
- [ ] 既存テストが全パス

**検証基準**:
```bash
pytest tests/test_services/test_inheritance_calculator.py::test_calculate_statutory_shares -v
```

---

### Task 2.5: InheritanceCalculator._build_result()の抽出
**所要時間**: 2日
**依存**: Task 2.4
**検証**: ユニットテスト

- [ ] `_build_result()` メソッドを実装
- [ ] `calculate()` から結果構築ロジックを移動
- [ ] テストケースを追加
- [ ] 既存テストが全パス

**検証基準**:
```bash
pytest tests/test_services/test_inheritance_calculator.py::test_build_result -v
```

---

### Task 2.6: 再転相続ロジックの統合
**所要時間**: 5日
**依存**: Task 2.1
**検証**: 再転相続テスト全パス

- [ ] 新しい `_process_retransfer_inheritance()` を実装
  - `RetransferInfo` を引数とする統一インターフェース
  - 情報源の違いをStrategyパターンで吸収
- [ ] 古いメソッドを非推奨化（deprecation warning）
  - `_process_retransfer_inheritance()` (old)
  - `_process_retransfer_inheritance_with_info()` (old)
  - `_find_retransfer_heirs()`
  - `_calculate_retransfer_shares()`
- [ ] 新しい実装で既存テストが全パス
- [ ] 新しい統合テストを追加

**検証基準**:
```bash
pytest tests/test_services/test_retransfer_inheritance.py -v --cov
pytest tests/test_services/test_retransfer_renunciation.py -v
```

---

### Task 2.7: calculate()メソッドの書き換え
**所要時間**: 3日
**依存**: Task 2.2-2.6完了
**検証**: 全テスト通過 + メソッド長確認

- [ ] `calculate()` メソッドを新しいメソッドを使用して書き換え
- [ ] メソッド長を200行以下に削減
- [ ] 古い実装をコメントアウト
- [ ] 全ての既存テストが通ることを確認
- [ ] コードレビュー実施
- [ ] 古い実装を完全削除

**検証基準**:
```bash
pytest tests/test_services/ -v --cov=src/inheritance_calculator_core/services
# メソッド長確認
wc -l src/inheritance_calculator_core/services/inheritance_calculator.py
grep -A 200 "def calculate(" src/inheritance_calculator_core/services/inheritance_calculator.py | wc -l
```

---

## Phase 3: 設定外部化（1週間）

### Task 3.1: CivilCodeConfigの実装
**所要時間**: 2日
**依存**: Phase 2完了
**検証**: 設定テスト

- [ ] `src/inheritance_calculator_core/config/civil_code.py` を作成
- [ ] `CivilCodeConfig` データクラスを実装
  - 民法第900条の定数フィールド
  - `__post_init__()` でバリデーション
  - `load()`, `from_dict()` クラスメソッド
- [ ] `ConfigValidationError` 例外クラスを追加
- [ ] テストケースを追加（20+ケース）

**検証基準**:
```bash
pytest tests/test_config/test_civil_code.py -v --cov=src/inheritance_calculator_core/config
```

---

### Task 3.2: ShareCalculatorの設定対応
**所要時間**: 2日
**依存**: Task 3.1
**検証**: 既存テスト + 設定テスト

- [ ] `ShareCalculator.__init__()` に `config` 引数追加
- [ ] ハードコードされた法定相続分を設定から取得
  - `_calculate_spouse_and_children()`
  - `_calculate_spouse_and_parents()`
  - `_calculate_spouse_and_siblings()`
- [ ] デフォルト設定で後方互換性確保
- [ ] カスタム設定のテストケースを追加
- [ ] 既存の全テストが通ることを確認

**検証基準**:
```bash
pytest tests/test_services/test_share_calculator.py -v
pytest tests/test_config/test_civil_code_integration.py -v
```

---

### Task 3.3: 設定ファイルとドキュメント
**所要時間**: 1日
**依存**: Task 3.2
**検証**: ドキュメントレビュー

- [ ] `config/civil_code.yaml` サンプルファイルを作成
- [ ] 設定ファイルの使用方法をREADMEに追加
- [ ] 法改正対応ガイドを作成
- [ ] APIドキュメントを更新

**検証基準**:
```bash
# YAMLが正しく読み込めることを確認
python -c "from inheritance_calculator_core.config import CivilCodeConfig; CivilCodeConfig.load('config/civil_code.yaml')"
```

---

### Task 3.4: 最終統合テストとベンチマーク
**所要時間**: 2日
**依存**: Task 3.3
**検証**: 全テスト + パフォーマンス

- [ ] 全テストスイートを実行（100%カバレッジ維持）
- [ ] パフォーマンスベンチマークを実施
  - リファクタリング前後のパフォーマンス比較
  - 劣化が5%以内であることを確認
- [ ] mypy --strict でエラーゼロを確認
- [ ] ruff, blackでコード品質確認
- [ ] ドキュメント最終レビュー
- [ ] リリースノート作成

**検証基準**:
```bash
# 全テスト
pytest tests/ -v --cov=src/inheritance_calculator_core --cov-report=html --cov-report=term-missing
coverage report | grep "TOTAL" | awk '{print $4}'  # 100%であることを確認

# 型チェック
mypy src/inheritance_calculator_core --strict

# コード品質
ruff check src/
black --check src/

# パフォーマンス
python scripts/benchmark.py --before --after
```

---

## Validation Gates

各フェーズ完了時に以下のゲートを通過する必要があります：

### Phase 1 Complete
- [ ] すべてのPhase 1タスク完了
- [ ] テストカバレッジ100%維持
- [ ] mypy --strict でエラーなし
- [ ] 既存のすべてのテストがパス
- [ ] コードレビュー承認

### Phase 2 Complete
- [ ] すべてのPhase 2タスク完了
- [ ] InheritanceCalculator.calculate()が200行以下
- [ ] 再転相続テストがすべてパス
- [ ] テストカバレッジ100%維持
- [ ] パフォーマンス劣化なし

### Phase 3 Complete
- [ ] すべてのPhase 3タスク完了
- [ ] 設定ファイルのサンプルとドキュメント完備
- [ ] 全テストスイートがパス
- [ ] mypy --strict でエラーゼロ
- [ ] リリースノート作成完了

---

## Rollback Plan

各フェーズで問題が発生した場合のロールバック手順：

### Phase 1 Rollback
1. 新規追加ファイルを削除
2. Person.idの型変更を元に戻す
3. 既存テストが全パスすることを確認

### Phase 2 Rollback
1. calculate()メソッドを元の実装に戻す
2. 新規メソッドを削除
3. 既存テストが全パスすることを確認

### Phase 3 Rollback
1. ShareCalculatorのconfig引数を削除
2. ハードコード値に戻す
3. 既存テストが全パスすることを確認

---

## Success Metrics

プロジェクト完了時の成功基準：

- ✅ テストカバレッジ: 100%（維持）
- ✅ InheritanceCalculator.calculate(): ≤ 200行
- ✅ 型変換 `str(id)` 使用箇所: 80%削減
- ✅ mypy --strict: エラー0件
- ✅ パフォーマンス劣化: < 5%
- ✅ 既存API互換性: 100%維持
- ✅ ドキュメント: 完全更新
