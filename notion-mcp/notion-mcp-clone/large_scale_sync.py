#!/usr/bin/env python3
"""
大規模DAO協働システム - 数百単位同期対応
Cursor + Notion MCP 完全自動化スクリプト
"""

import os
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
from notion_mcp.client import NotionClient
import yaml
import time

# 新しいMarkdown変換システムをインポート
from enhanced_markdown_converter import EnhancedMarkdownConverter

class LargeScaleSyncSystem:
    """数百単位の同期に対応した大規模同期システム"""
    
    def __init__(self, api_key: str, project_root: str = "C:/Users/zukas/mybrain"):
        self.client = NotionClient(api_key)
        self.project_root = Path(project_root)
        self.database_id = "24039d01-e781-8040-8205-d82e13a1e8f0"
        self.sync_log = self.project_root / ".cursor" / "sync_log.json"
        self.batch_size = 10  # API制限対応
        self.retry_count = 3
        
        # 新しいMarkdown変換システムを初期化
        self.markdown_converter = EnhancedMarkdownConverter()
        
    async def sync_markdown_files_to_notion(self, folder_path: str) -> Dict[str, Any]:
        """指定フォルダのMarkdownファイルを一括Notion同期"""
        print(f"🚀 大規模同期開始: {folder_path}")
        
        folder = Path(folder_path)
        markdown_files = list(folder.rglob("*.md"))
        
        results = {
            "total_files": len(markdown_files),
            "processed": 0,
            "created": 0,
            "updated": 0,
            "errors": [],
            "start_time": datetime.now().isoformat()
        }
        
        # バッチ処理で実行
        for i in range(0, len(markdown_files), self.batch_size):
            batch = markdown_files[i:i + self.batch_size]
            print(f"📦 バッチ {i//self.batch_size + 1}: {len(batch)}ファイル処理中...")
            
            batch_tasks = []
            for md_file in batch:
                batch_tasks.append(self._process_markdown_file(md_file, results))
            
            # 並列実行
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # API制限回避のための待機
            await asyncio.sleep(1)
            
        results["end_time"] = datetime.now().isoformat()
        await self._save_sync_log(results)
        
        print(f"✅ 同期完了: {results['created']}件作成, {results['updated']}件更新")
        return results
    
    async def _process_markdown_file(self, md_file: Path, results: Dict[str, Any]):
        """個別Markdownファイル処理（フル同期対応）"""
        try:
            # ファイル内容読み込み
            content = md_file.read_text(encoding='utf-8')
            
            # メタデータ抽出
            metadata = self._extract_metadata(content, md_file)
            
            # Notion形式に変換
            properties = self._convert_to_notion_properties(metadata)
            all_blocks = self._convert_content_to_blocks_full(content)
            
            # 既存ページチェック（全重複対応）
            existing_pages = await self._find_all_existing_pages(metadata["title"])
            
            if existing_pages:
                # 全重複ページを削除・再作成方式（確実な更新）
                print(f"🔄 {len(existing_pages)}個の重複ページ発見・削除中: {metadata['title']}")
                for page in existing_pages:
                    await self._delete_page_with_retry(page["id"])
                results["updated"] += 1
                
            # 新規ページ作成（最初の50ブロック - より安全なサイズ）
            initial_blocks = all_blocks[:50] if len(all_blocks) > 50 else all_blocks
            page = await self._create_page_with_retry(properties, initial_blocks)
            page_id = page.id
            
            if not existing_pages:
                results["created"] += 1
                print(f"✅ 作成: {metadata['title']} (初期{len(initial_blocks)}ブロック)")
            else:
                print(f"🆕 再作成: {metadata['title']} (初期{len(initial_blocks)}ブロック)")
            
            # 残りのブロックを段階的追加
            if len(all_blocks) > 50:
                await self._append_remaining_blocks(page_id, all_blocks[50:], metadata["title"])
            
            # processed カウンターを適切に処理
            if "processed" not in results:
                results["processed"] = 0
            results["processed"] += 1
            print(f"📚 フル同期完了: {metadata['title']} ({len(all_blocks)}ブロック)")
            
        except Exception as e:
            error_info = {
                "file": str(md_file),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            results["errors"].append(error_info)
            print(f"❌ エラー: {md_file.name} - {e}")
    
    async def _append_remaining_blocks(self, page_id: str, remaining_blocks: List[Dict[str, Any]], title: str):
        """残りのブロックを段階的に追加（適応的サイズ調整）"""
        max_blocks_per_batch = 50  # より小さなバッチサイズ
        total_remaining = len(remaining_blocks)
        batch_count = (total_remaining + max_blocks_per_batch - 1) // max_blocks_per_batch
        
        print(f"  🔄 段階的ブロック追加: {total_remaining}ブロック → {batch_count}回に分割")
        
        for batch_num in range(batch_count):
            start_idx = batch_num * max_blocks_per_batch
            end_idx = min(start_idx + max_blocks_per_batch, total_remaining)
            batch_blocks = remaining_blocks[start_idx:end_idx]
            
            # 適応的バッチサイズでリトライ
            success = await self._append_batch_with_adaptive_retry(page_id, batch_blocks, batch_num + 1, batch_count)
            
            if success:
                print(f"  ✅ バッチ {batch_num + 1}/{batch_count}: {len(batch_blocks)}ブロック追加")
            else:
                print(f"  ⚠️ バッチ {batch_num + 1}/{batch_count}: 一部ブロックをスキップ")
            
            # API制限対応の待機
            await asyncio.sleep(1.5)  # 少し長めの待機
    
    async def _append_batch_with_adaptive_retry(self, page_id: str, blocks: List[Dict[str, Any]], batch_num: int, total_batches: int) -> bool:
        """適応的バッチサイズでブロック追加リトライ"""
        if not blocks:
            return True
        
        # 最初は通常のリトライを試行
        try:
            await self._append_blocks_with_retry(page_id, blocks)
            return True
        except Exception as e:
            error_msg = str(e).lower()
            
            # サイズ関連エラーの場合は分割して再試行
            if any(keyword in error_msg for keyword in ['400', 'bad request', 'too large', 'size', 'limit']):
                print(f"    📦 バッチ{batch_num} サイズエラー検出 → 分割処理開始")
                return await self._split_and_retry_batch(page_id, blocks, batch_num)
            else:
                # その他のエラーは従来通りスキップ
                print(f"    ❌ バッチ{batch_num} 処理エラー（非サイズ関連）: {e}")
                return False
    
    async def _split_and_retry_batch(self, page_id: str, blocks: List[Dict[str, Any]], batch_num: int) -> bool:
        """バッチを分割して再帰的にリトライ"""
        total_blocks = len(blocks)
        
        # 1ブロックまで分割した場合の最終処理
        if total_blocks == 1:
            try:
                await self._append_blocks_with_retry(page_id, blocks)
                return True
            except Exception as e:
                print(f"      ❌ 単一ブロック処理失敗: {e}")
                return False
        
        # バッチを半分に分割
        mid = total_blocks // 2
        first_half = blocks[:mid]
        second_half = blocks[mid:]
        
        print(f"      🔄 バッチ{batch_num} 分割: {total_blocks} → {len(first_half)} + {len(second_half)}")
        
        # 前半・後半を順次処理
        success_count = 0
        
        for i, sub_batch in enumerate([first_half, second_half], 1):
            try:
                await self._append_blocks_with_retry(page_id, sub_batch)
                print(f"        ✅ 分割{i}: {len(sub_batch)}ブロック成功")
                success_count += 1
            except Exception as e:
                # さらに分割が必要な場合は再帰処理
                if len(sub_batch) > 1:
                    sub_success = await self._split_and_retry_batch(page_id, sub_batch, f"{batch_num}.{i}")
                    if sub_success:
                        success_count += 1
                else:
                    print(f"        ❌ 分割{i} 単一ブロック失敗: {e}")
            
            # 各分割の間に短い待機
            await asyncio.sleep(0.5)
        
        return success_count > 0  # 一部でも成功すればTrue
    
    async def _append_blocks_with_retry(self, page_id: str, blocks: List[Dict[str, Any]]):
        """リトライ機能付きブロック追加"""
        for attempt in range(self.retry_count):
            try:
                return await self.client.append_block_children(page_id, blocks)
            except Exception as e:
                if attempt == self.retry_count - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数バックオフ
    
    async def _create_page_with_retry(self, properties: Dict[str, Any], children: List[Dict[str, Any]]):
        """リトライ機能付きページ作成"""
        for attempt in range(self.retry_count):
            try:
                return await self.client.create_page(
                    parent_id=self.database_id,
                    properties=properties,
                    children=children
                )
            except Exception as e:
                if attempt == self.retry_count - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数バックオフ
    
    def _extract_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Markdownファイルからメタデータ抽出"""
        lines = content.split('\n')
        
        # YAMLフロントマター検出
        if lines[0].strip() == '---':
            yaml_end = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    yaml_end = i
                    break
            
            if yaml_end:
                try:
                    yaml_content = '\n'.join(lines[1:yaml_end])
                    metadata = yaml.safe_load(yaml_content)
                    if isinstance(metadata, dict):
                        return self._normalize_metadata(metadata, file_path)
                except:
                    pass
        
        # フロントマターがない場合のデフォルト
        title = lines[0].replace('#', '').strip() if lines else file_path.stem
        
        return {
            "title": title,
            "category": self._infer_category(file_path),
            "status": "未着手",
            "priority": "中",
            "file_path": str(file_path),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    
    def _normalize_metadata(self, metadata: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """メタデータ正規化"""
        return {
            "title": metadata.get("title", file_path.stem),
            "category": metadata.get("category", self._infer_category(file_path)),
            "status": metadata.get("status", "未着手"),
            "priority": metadata.get("priority", "中"),
            "due_date": metadata.get("due_date"),
            "tags": metadata.get("tags", []),
            "file_path": str(file_path),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    
    def _infer_category(self, file_path: Path) -> str:
        """ファイルパスからカテゴリ推定（LLCDAO専用）"""
        path_str = str(file_path).lower()
        
        if "token" in path_str or "トークン" in path_str or "week1" in path_str:
            return "トークン規程"
        elif "assembly" in path_str or "総会" in path_str or "week2" in path_str:
            return "総会規程"
        elif "operation" in path_str or "運営規程" in path_str or "week3" in path_str:
            return "運営規程"
        elif "treasury" in path_str or "トレジャリー" in path_str or "week4" in path_str:
            return "トレジャリー規程"
        elif "charter" in path_str or "憲章" in path_str or "week5" in path_str:
            return "DAO憲章"
        elif "integration" in path_str or "統合" in path_str or "week6" in path_str:
            return "統合"
        else:
            return "その他"  # デフォルト
    
    def _convert_to_notion_properties(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Notionプロパティ形式に変換"""
        properties = {
            "名前": {"title": [{"text": {"content": metadata["title"]}}]},
            "Category": {"select": {"name": metadata["category"]}},
            "Status": {"status": {"name": metadata["status"]}},
            "Priority": {"select": {"name": metadata["priority"]}}
        }
        
        if metadata.get("due_date"):
            properties["Due Date"] = {"date": {"start": metadata["due_date"]}}
            
        if metadata.get("tags"):
            # Tagsプロパティに追加（複数選択）
            tag_options = [{"name": tag} for tag in metadata["tags"]]
            properties["Tags"] = {"multi_select": tag_options}
            
        return properties
    
    def _convert_content_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Markdownコンテンツをnotionブロック形式に変換（100ブロック制限対応）"""
        print("🔄 高度なMarkdown変換システムを使用中（制限版）...")
        
        # 新しいコンバーターを使用
        all_blocks = self.markdown_converter.convert_content_to_blocks(content)
        
        # ブロック制限対応
        max_blocks = 50  # より安全なサイズ
        
        if len(all_blocks) <= max_blocks:
            print(f"✅ 変換完了: {len(all_blocks)}ブロック生成（制限内）")
            return all_blocks
        else:
            # 制限を超える場合は切り詰めてメッセージを追加
            limited_blocks = all_blocks[:max_blocks-2]
            limited_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "..."}}]}
            })
            limited_blocks.append({
                "object": "block",
                "type": "paragraph", 
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "📄 完全な内容はローカルファイルを参照してください。"}}]}
            })
            
            print(f"⚠️ ブロック制限対応: {len(all_blocks)} → {len(limited_blocks)}ブロック")
            print(f"📊 対応フォーマット: 太字・斜体・コード・リンク・テーブル・コードブロック等")
            
            return limited_blocks
    
    def _convert_content_to_blocks_full(self, content: str) -> List[Dict[str, Any]]:
        """Markdownコンテンツを完全変換（制限なし）- 新しい高度な変換システム使用"""
        print("🔄 高度なMarkdown変換システムを使用中...")
        
        # 新しいコンバーターを使用
        blocks = self.markdown_converter.convert_content_to_blocks(content)
        
        print(f"✅ 変換完了: {len(blocks)}ブロック生成")
        print(f"📊 対応フォーマット: 太字・斜体・コード・リンク・テーブル・コードブロック等")
        
        return blocks
    
    async def _find_all_existing_pages(self, title: str) -> List[Dict[str, Any]]:
        """同名の全既存ページを検索（重複対応）"""
        try:
            # データベース内の同名ページをすべて取得
            results = await self.client.query_database(
                database_id=self.database_id,
                filter={
                    "property": "名前",
                    "title": {
                        "equals": title
                    }
                }
            )
            
            if hasattr(results, 'results') and results.results:
                return results.results
            elif isinstance(results, dict) and results.get('results'):
                return results['results']
                
        except Exception as e:
            print(f"  ⚠️ 既存ページ検索エラー: {e}")
            
        return []
    
    async def _update_page_with_retry(self, page_id: str, properties: Dict[str, Any]):
        """リトライ機能付きページ更新"""
        for attempt in range(self.retry_count):
            try:
                return await self.client.update_page(page_id, properties)
            except Exception as e:
                if attempt == self.retry_count - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
    
    async def _delete_page_with_retry(self, page_id: str):
        """リトライ機能付きページ削除（アーカイブ）"""
        for attempt in range(self.retry_count):
            try:
                # Notionではページを削除する代わりにアーカイブする
                await self.client.update_page(page_id, properties={}, archived=True)
                print(f"    🗄️ アーカイブ完了: {page_id}")
                return True
            except Exception as e:
                print(f"    ⚠️ アーカイブ試行 {attempt + 1}/{self.retry_count}: {e}")
                if attempt == self.retry_count - 1:
                    print(f"    ❌ アーカイブ失敗: {page_id}")
                    return False
                await asyncio.sleep(2 ** attempt)
    
    async def _save_sync_log(self, results: Dict[str, Any]):
        """同期ログ保存"""
        self.sync_log.parent.mkdir(exist_ok=True)
        
        # 既存ログ読み込み
        if self.sync_log.exists():
            with open(self.sync_log, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # 新しいログ追加
        logs.append(results)
        
        # 最新100件のみ保持
        logs = logs[-100:]
        
        # 保存
        with open(self.sync_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

# コマンドライン実行
async def main():
    """メイン実行関数"""
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        print("❌ NOTION_API_KEY環境変数が設定されていません")
        return
    
    sync_system = LargeScaleSyncSystem(api_key)
    
    # DAOプロジェクトフォルダを同期
    dao_folder = "C:/Users/zukas/mybrain/02_Projects/ProjectE_合同会社型DAO_アクセラレーション/Documents"
    
    if Path(dao_folder).exists():
        results = await sync_system.sync_markdown_files_to_notion(dao_folder)
        print(f"\n📊 同期結果:")
        print(f"  📁 対象ファイル: {results['total_files']}")
        print(f"  ✅ 作成: {results['created']}")
        print(f"  🔄 更新: {results['updated']}")
        print(f"  ❌ エラー: {len(results['errors'])}")
    else:
        print(f"❌ フォルダが見つかりません: {dao_folder}")

if __name__ == "__main__":
    asyncio.run(main())