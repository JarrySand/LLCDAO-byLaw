#!/usr/bin/env python3
"""
LLCDAO 定款規程レビューシステム専用同期スクリプト
review/ フォルダのMarkdownファイルをNotion DBに同期
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import yaml
from dotenv import load_dotenv
from large_scale_sync import LargeScaleSyncSystem

# .envファイルを読み込み
load_dotenv()

class LLCDAOReviewSyncSystem(LargeScaleSyncSystem):
    """LLCDAO定款規程レビュー専用同期システム"""
    
    def __init__(self, api_key: str = None):
        # LLCDAO専用設定
        project_root = "C:/Users/zukas/LLCDAO-bylaw"
        
        # 環境変数または.envからAPIキーを取得
        if not api_key:
            api_key = os.getenv("NOTION_API_KEY")
            if not api_key:
                raise ValueError("NOTION_API_KEY not found. Please set it in .env file")
        
        # 親クラス初期化（プロジェクトルート変更）
        super().__init__(api_key, project_root)
        
        # LLCDAO専用データベースID（URLから抽出）
        # LLCDAO専用データベースID（確定）
        self.database_id = "24539d01e781800884eaca3a3a95e78e"
        
        # レビュー専用フォルダ設定
        self.review_folders = [
            "review/01-materials",
            "review/02-minutes", 
            "review/03-modifications",
            "review/templates"
        ]
    
    async def sync_all_review_materials(self) -> Dict[str, Any]:
        """全レビュー資料をNotionに同期"""
        print("🚀 LLCDAO定款規程レビュー資料同期開始")
        
        total_results = {
            "folders_processed": 0,
            "total_files": 0,
            "total_success": 0,
            "total_errors": 0,
            "folder_results": {},
            "start_time": datetime.now().isoformat()
        }
        
        for folder in self.review_folders:
            folder_path = self.project_root / folder
            if folder_path.exists():
                print(f"\n📁 処理中: {folder}")
                
                # フォルダ単位で同期実行
                result = await self.sync_markdown_files_to_notion(str(folder_path))
                
                total_results["folder_results"][folder] = result
                total_results["folders_processed"] += 1
                total_results["total_files"] += result.get("total_files", 0)
                total_results["total_success"] += result.get("created", 0) + result.get("updated", 0)
                total_results["total_errors"] += len(result.get("errors", []))
                
                print(f"✅ {folder} 完了: {result.get('created', 0) + result.get('updated', 0)}/{result.get('total_files', 0)} ファイル")
            else:
                print(f"⚠️  フォルダが見つかりません: {folder}")
        
        total_results["end_time"] = datetime.now().isoformat()
        total_results["duration"] = "計算中"
        
        return total_results
    
    async def sync_specific_week(self, week_number: int) -> Dict[str, Any]:
        """特定の週のレビュー資料のみ同期"""
        week_folder = f"review/01-materials/week{week_number}-*"
        week_path = list(self.project_root.glob(week_folder))
        
        if not week_path:
            return {"error": f"Week {week_number} のフォルダが見つかりません"}
        
        print(f"🗓️  Week {week_number} 資料同期開始")
        return await self.sync_markdown_files_to_notion(str(week_path[0]))
    
    def add_review_metadata(self, content: str, file_path: Path) -> str:
        """レビュー専用のYAMLフロントマターを追加"""
        
        # 既存のYAMLフロントマターをチェック
        if content.startswith('---'):
            return content
        
        # パスからメタデータを推定
        metadata = {}
        path_parts = file_path.parts
        
        # Week情報の抽出
        for part in path_parts:
            if 'week' in part.lower():
                if 'week1' in part.lower(): metadata['week'] = 'Week1'
                elif 'week2' in part.lower(): metadata['week'] = 'Week2'
                elif 'week3' in part.lower(): metadata['week'] = 'Week3'
                elif 'week4' in part.lower(): metadata['week'] = 'Week4'
                elif 'week5' in part.lower(): metadata['week'] = 'Week5'
                elif 'week6' in part.lower(): metadata['week'] = 'Week6'
        
        # 規程種別の推定
        filename = file_path.name.lower()
        if 'token' in filename or 'トークン' in filename:
            metadata['regulation_type'] = 'トークン規程'
        elif 'assembly' in filename or '総会' in filename:
            metadata['regulation_type'] = 'DAO総会規程'
        elif 'operation' in filename or '運営' in filename:
            metadata['regulation_type'] = 'DAO運営規程'
        elif 'treasury' in filename or 'トレジャリー' in filename:
            metadata['regulation_type'] = 'トレジャリー管理規程'
        elif 'charter' in filename or '憲章' in filename:
            metadata['regulation_type'] = 'DAO憲章'
        
        # 資料種別の推定
        material_types = []
        if 'diff' in filename: material_types.append('diff比較')
        if 'checklist' in filename or 'チェックリスト' in filename: material_types.append('チェックリスト')
        if 'readme' in filename: material_types.append('事前資料')
        if '議事録' in filename: material_types.append('議事録')
        
        # YAMLフロントマター生成
        yaml_front = "---\n"
        yaml_front += f"title: \"{file_path.stem}\"\n"
        
        if metadata.get('week'):
            yaml_front += f"week: \"{metadata['week']}\"\n"
        if metadata.get('regulation_type'):
            yaml_front += f"regulation_type: \"{metadata['regulation_type']}\"\n"
        if material_types:
            yaml_front += f"material_type: {material_types}\n"
        
        yaml_front += "status: \"準備中\"\n"
        yaml_front += "priority: \"中\"\n"
        yaml_front += f"tags: [\"レビュー資料\"]\n"
        yaml_front += "---\n\n"
        
        return yaml_front + content
    
    async def test_connection(self) -> bool:
        """API接続テスト"""
        try:
            # データベース情報を取得してAPI接続を確認
            database = await self.client.get_database(self.database_id)
            # データベースオブジェクトの属性に直接アクセス
            db_title = "LLCDAO Review Database" if hasattr(database, 'title') else "Connected Database"
            print(f"✅ データベース接続成功: {db_title}")
            print(f"   データベース情報: {type(database).__name__} オブジェクト")
            return True
        except Exception as e:
            print(f"❌ API接続エラー: {str(e)}")
            print("  確認事項:")
            print("  1. APIキーが正しく設定されているか")
            print("  2. データベースIDが正しいか") 
            print("  3. Integrationがデータベースに招待されているか")
            return False

async def main():
    """メイン実行関数"""
    
    print("🎯 LLCDAO定款規程レビューシステム")
    print("=" * 50)
    
    try:
        # 同期システム初期化
        sync_system = LLCDAOReviewSyncSystem()
        
        print("✅ システム初期化完了")
        print(f"📁 プロジェクトルート: {sync_system.project_root}")
        print(f"🗄️  データベースID: {sync_system.database_id}")
        
        if sync_system.database_id == "YOUR_REVIEW_DATABASE_ID_HERE":
            print("\n⚠️  データベースIDが設定されていません")
            print("1. Notionでレビュー資料データベースを作成")
            print("2. llcdao_review_sync.py の database_id を更新")
            print("3. 再実行してください")
            return
        
        # API接続テスト
        print("\n🔗 API接続テスト中...")
        connection_ok = await sync_system.test_connection()
        
        if not connection_ok:
            print("❌ API接続に失敗しました")
            return
        
        print("✅ API接続成功")
        
        # 全レビュー資料同期実行
        print("\n📋 全レビュー資料同期開始...")
        results = await sync_system.sync_all_review_materials()
        
        # 結果サマリー表示
        print("\n" + "=" * 50)
        print("📊 同期結果サマリー")
        print("=" * 50)
        print(f"処理フォルダ数: {results['folders_processed']}")
        print(f"総ファイル数: {results['total_files']}")
        print(f"成功: {results['total_success']}")
        print(f"エラー: {results['total_errors']}")
        
        if results['total_errors'] > 0:
            print("\n❌ エラーが発生したファイル:")
            for folder, result in results['folder_results'].items():
                for error in result.get('errors', []):
                    print(f"  - {folder}: {error}")
        
        print("\n🎉 同期完了！Notionデータベースを確認してください。")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        print("設定を確認して再実行してください。")

if __name__ == "__main__":
    asyncio.run(main())