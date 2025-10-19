# PyPI公開手順

## 前提条件

1. **PyPIアカウント**
   - 本番: https://pypi.org/account/register/
   - テスト: https://test.pypi.org/account/register/

2. **APIトークンの取得**
   - PyPIにログイン → Account settings → API tokens
   - "Add API token" をクリック
   - Scope: "Entire account" (初回) または "Project: inheritance-calculator-core"
   - トークンをコピー（一度しか表示されません）

## 手動公開手順

### 1. TestPyPIでテスト

```bash
cd /Users/k-kawahara/Dev-Work/inheritance-calculator-core

# ビルド
uv build

# TestPyPIに公開
uv publish --publish-url https://test.pypi.org/legacy/ --token <YOUR_TEST_PYPI_TOKEN>

# インストールテスト
pip install --index-url https://test.pypi.org/simple/ inheritance-calculator-core
```

### 2. 本番PyPIに公開

```bash
# ビルド（既にある場合はスキップ）
uv build

# 本番PyPIに公開
uv publish --token <YOUR_PYPI_TOKEN>

# インストール確認
pip install inheritance-calculator-core
```

## GitHub Actionsでの自動公開（推奨）

### 1. PyPI APIトークンをGitHub Secretsに登録

1. GitHubリポジトリ: https://github.com/kazumasakawahara/inheritance-calculator-core
2. Settings → Secrets and variables → Actions
3. "New repository secret" をクリック
4. Name: `PYPI_API_TOKEN`
5. Secret: PyPI APIトークンを貼り付け
6. "Add secret" をクリック

### 2. リリースを作成

```bash
# タグを作成
git tag v1.0.0
git push origin v1.0.0
```

または、GitHub Web UIから:

1. https://github.com/kazumasakawahara/inheritance-calculator-core/releases/new
2. "Choose a tag" → 新しいタグ `v1.0.0` を入力
3. Release title: `v1.0.0 - Initial Release`
4. Description: リリースノートを記載
5. "Publish release" をクリック

GitHub Actionsが自動的にPyPIに公開します。

### 3. 公開確認

- PyPI: https://pypi.org/project/inheritance-calculator-core/
- インストール: `pip install inheritance-calculator-core`

## バージョン管理

### バージョン番号の更新

`pyproject.toml` の `version` を更新:

```toml
[project]
name = "inheritance-calculator-core"
version = "1.0.1"  # ← ここを更新
```

### セマンティックバージョニング

- **MAJOR** (1.x.x): 破壊的変更（API変更、民法改正対応）
- **MINOR** (x.1.x): 後方互換な機能追加
- **PATCH** (x.x.1): バグ修正

### リリースフロー

```bash
# 1. バージョン更新
# pyproject.toml の version を更新

# 2. 変更をコミット
git add pyproject.toml
git commit -m "chore: bump version to 1.0.1"
git push origin main

# 3. タグ作成
git tag v1.0.1
git push origin v1.0.1

# 4. GitHubでリリース作成（自動的にPyPIに公開される）
```

## トラブルシューティング

### エラー: "Invalid or non-existent authentication information"

APIトークンが間違っているか、期限切れです。新しいトークンを取得してください。

### エラー: "File already exists"

同じバージョンは再公開できません。`pyproject.toml` のバージョンを上げてください。

### GitHub Actionsが失敗する

1. Secrets に `PYPI_API_TOKEN` が正しく登録されているか確認
2. Actions タブでログを確認
3. トークンのスコープが正しいか確認（プロジェクト or アカウント全体）

## 参考リンク

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- uv documentation: https://docs.astral.sh/uv/
- Packaging Python Projects: https://packaging.python.org/tutorials/packaging-projects/
