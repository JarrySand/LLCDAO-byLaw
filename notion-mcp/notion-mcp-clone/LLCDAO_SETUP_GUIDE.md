# 🚀 LLCDAO定款規程レビューシステム セットアップガイド

## 📋 概要
このガイドに従って、LLCDAO定款規程レビュープロセスをNotion上で実行できるようにセットアップします。

## ✅ 前提条件チェックリスト

- [ ] Pythonがインストール済み（既存環境: Python 3.13.2 ✅）
- [ ] 仮想環境が作成済み（既存環境: venv ✅）
- [ ] 必要なライブラリがインストール済み（既存環境: ✅）
- [ ] LLCDAO-bylawプロジェクトが準備済み（既存環境: ✅）

## 🔧 Step 1: Notion環境準備

### 1.1 新しいIntegration作成
1. [Notion Developers](https://developers.notion.com/) にアクセス
2. **"+ New integration"** をクリック
3. 以下の設定で作成：
   - **名前**: `LLCDAO-Review-System`
   - **説明**: `DAO定款規程レビュープロセス管理`
   - **Workspace**: LLCDAOプロジェクト用ワークスペース
4. **APIトークンをコピー**（後で使用）

### 1.2 レビュー資料データベース作成

Notionで以下のデータベースを作成：

#### 📋 **DAO規程レビュー資料** データベース
```
プロパティ設定:
├── 名前 (Title) - ページタイトル
├── Week (Select) - Week1, Week2, Week3, Week4, Week5, Week6  
├── 規程種別 (Select) - トークン規程, DAO総会規程, DAO運営規程, トレジャリー管理規程, DAO憲章
├── 資料種別 (Multi-select) - 事前資料, diff比較, チェックリスト, 議事録
├── ステータス (Status) - 準備中, レビュー中, 完了
├── 担当者 (Person) - 専門家・参加者
├── 期日 (Date) - スケジュール管理
└── 優先度 (Select) - 高, 中, 低
```

#### 🔧 **修正提案管理** データベース（オプション）
```
プロパティ設定:
├── 提案ID (Title) - MP-001, MP-002...
├── 対象規程 (Select) - 対象文書
├── 条文 (Text) - 第3条第2項等
├── 提案者 (Person) - 提案者
├── 重要度 (Select) - 高, 中, 低
├── 専門分野 (Multi-select) - 法務, 税務, 技術, 実務
├── 承認状況 (Status) - 検討中, 承認, 保留, 却下
└── Week (Select) - Week1-6
```

### 1.3 データベースID取得
1. 作成したデータベースのURLから**データベースID**を抽出：
   ```
   URL例: https://www.notion.so/workspace/1234567890abcdef1234567890abcdef?v=...
   データベースID: 1234567890abcdef1234567890abcdef
   ```
2. IDをコピーして保存

### 1.4 Integration権限設定
1. 各データベースページで **"..."** → **"接続を追加"**
2. 作成したIntegration **"LLCDAO-Review-System"** を選択
3. **"招待"** をクリック

## 🔧 Step 2: 環境設定更新

### 2.1 APIキー設定
```bash
# .env ファイルを編集
NOTION_API_KEY=ntn_YOUR_NEW_API_KEY_HERE
```

### 2.2 設定ファイル更新
`llcdao_config.py` を編集して、データベースIDを設定：

```python
DATABASE_IDS = {
    "review_materials": "YOUR_ACTUAL_DATABASE_ID_HERE",
    "modifications": "YOUR_MODIFICATIONS_DATABASE_ID_HERE",  # オプション
    "issues": "YOUR_ISSUES_DATABASE_ID_HERE"  # オプション
}
```

## 🧪 Step 3: 設定確認テスト

### 3.1 基本設定確認
```bash
# 仮想環境をアクティベート
venv\Scripts\activate

# 設定確認実行
python llcdao_config.py
```

期待される出力：
```
🔧 LLCDAO設定確認
========================================
✅ 全ての設定が正常です
📁 プロジェクトルート: C:/Users/zukas/LLCDAO-bylaw
📋 同期対象フォルダ: 4個
```

### 3.2 API接続テスト
```bash
# API接続テスト（実際のデータベースIDを設定後）
python -c "import asyncio; from llcdao_review_sync import LLCDAOReviewSyncSystem; asyncio.run(LLCDAOReviewSyncSystem().test_connection())"
```

## 🚀 Step 4: 初回同期実行

### 4.1 テスト同期（少数ファイル）
```bash
# テスト用に1つのフォルダのみ同期
python llcdao_review_sync.py
```

### 4.2 全体同期（設定確認後）
設定が正常であることを確認後、全レビュー資料を同期：
```bash
# 全レビューフォルダ同期
python llcdao_review_sync.py
```

## 📊 Step 5: 結果確認

### 5.1 Notionデータベース確認
1. Notionで作成したデータベースを開く
2. 同期されたページが表示されることを確認
3. メタデータ（Week、規程種別等）が正しく設定されていることを確認

### 5.2 同期ログ確認
```bash
# 同期ログファイル確認
type C:\Users\zukas\LLCDAO-bylaw\.cursor\sync_log.json
```

## 🎯 Step 6: 運用開始

### 6.1 日常ワークフロー
1. **Cursorでファイル編集** → **保存**
2. **同期実行**: `python llcdao_review_sync.py`
3. **Notionで協働レビュー**: コメント・フィードバック収集
4. **フィードバック反映**: Cursorで修正 → 再同期

### 6.2 週次レビュー用
```bash
# 特定週のみ同期（例：Week1）
python -c "import asyncio; from llcdao_review_sync import LLCDAOReviewSyncSystem; asyncio.run(LLCDAOReviewSyncSystem().sync_specific_week(1))"
```

## 🔧 トラブルシューティング

### よくある問題

#### ❌ APIキーエラー
```
ValueError: NOTION_API_KEY not found
```
**解決策**: `.env` ファイルでAPIキーを設定

#### ❌ データベースアクセス拒否
```
Client error '400 Bad Request'
```
**解決策**: 
1. データベースIDが正しいか確認
2. Integration権限が設定されているか確認

#### ❌ フォルダが見つからない
```
フォルダが見つかりません: review/01-materials
```
**解決策**: プロジェクトルートパスが正しいか確認

## 📞 サポート

### 設定確認コマンド集
```bash
# 環境確認
python --version
venv\Scripts\activate

# 設定確認
python llcdao_config.py

# 同期テスト
python llcdao_review_sync.py
```

## 🎉 完了チェックリスト

- [ ] Notion Integration作成・APIキー取得
- [ ] レビュー資料データベース作成・ID取得
- [ ] Integration権限設定
- [ ] .env ファイル更新
- [ ] llcdao_config.py 更新
- [ ] 設定確認テスト実行
- [ ] API接続テスト実行
- [ ] 初回同期実行
- [ ] Notion結果確認

全て完了したら、**日本最先端のDAO規程レビューシステム**の運用開始です！🎊