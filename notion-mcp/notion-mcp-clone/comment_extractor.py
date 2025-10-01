#!/usr/bin/env python3
"""
LLCDAO Notion コメント抽出システム
Notionデータベース内のページからコメントを抽出して表示
"""

import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# MCPクライアントをインポート
from src.notion_mcp.client import NotionClient

# .envファイルを読み込み
load_dotenv()

class LLCDAOCommentExtractor:
    """LLCDAO用コメント抽出システム"""
    
    def __init__(self, api_key: str = None):
        # APIキーを環境変数から取得
        if not api_key:
            api_key = os.getenv("NOTION_API_KEY")
            if not api_key:
                raise ValueError("NOTION_API_KEY not found in environment variables")
        
        # NotionClient初期化
        self.client = NotionClient(api_key)
        
        # LLCDAO データベースID（確定）
        self.database_id = "24539d01e781800884eaca3a3a95e78e"
        
    async def extract_all_comments(self) -> dict:
        """データベース内の全ページのコメントを抽出"""
        print("🔍 LLCDAO データベースからコメント抽出開始")
        print(f"📊 データベースID: {self.database_id}")
        
        results = {
            "extraction_time": datetime.now().isoformat(),
            "database_id": self.database_id,
            "total_pages": 0,
            "total_comments": 0,
            "pages_with_comments": 0,
            "comment_details": []
        }
        
        try:
            # データベース内の全ページを取得
            print("\n📋 データベースページ一覧取得中...")
            pages_response = await self.client.query_database(
                database_id=self.database_id,
                page_size=100
            )
            
            pages = pages_response.results
            results["total_pages"] = len(pages)
            print(f"✅ {len(pages)}個のページを発見")
            
            # 各ページのコメントを確認
            for i, page in enumerate(pages, 1):
                page_title = self.get_page_title(page)
                print(f"\n🔍 [{i}/{len(pages)}] {page_title} をチェック中...")
                
                try:
                    # ページのコメントを取得（コンテキスト付き）
                    comments = await self.client.get_comments(
                        block_id=page.id,
                        page_size=100
                    )
                    
                    if comments.results:
                        results["pages_with_comments"] += 1
                        results["total_comments"] += len(comments.results)
                        
                        print(f"💬 {len(comments.results)}個のコメントを発見!")
                        
                        # 各コメントの詳細を収集
                        page_comments = []
                        for comment in comments.results:
                            try:
                                # コンテキスト情報を取得
                                context = await self.client.get_comment_context(comment)
                                
                                comment_data = {
                                    "id": comment.id,
                                    "content": "".join([
                                        rt.plain_text if hasattr(rt, 'plain_text') 
                                        else rt.get('plain_text', '') 
                                        for rt in comment.rich_text
                                    ]),
                                    "created_time": comment.created_time,
                                    "created_by": {
                                        "id": comment.created_by.id if hasattr(comment.created_by, 'id') else None,
                                        "type": comment.created_by.type if hasattr(comment.created_by, 'type') else None
                                    },
                                    "discussion_id": comment.discussion_id,
                                    "context": context
                                }
                                page_comments.append(comment_data)
                                
                                # コンソール出力
                                print(f"  📝 コメント: {comment_data['content'][:100]}...")
                                print(f"     作成者: {comment_data['created_by']['id']}")
                                print(f"     作成日時: {comment_data['created_time']}")
                                
                            except Exception as e:
                                print(f"    ⚠️ コメント詳細取得エラー: {str(e)}")
                        
                        results["comment_details"].append({
                            "page_id": page.id,
                            "page_title": page_title,
                            "comment_count": len(page_comments),
                            "comments": page_comments
                        })
                    else:
                        print("   📭 コメントなし")
                        
                except Exception as e:
                    print(f"   ❌ ページコメント取得エラー: {str(e)}")
                    
        except Exception as e:
            print(f"❌ データベース取得エラー: {str(e)}")
            results["error"] = str(e)
            
        return results
    
    def get_page_title(self, page) -> str:
        """ページタイトルを取得"""
        try:
            # Notionページのタイトルプロパティを取得
            if hasattr(page, 'properties') and page.properties:
                # 通常のタイトルプロパティ
                for prop_name, prop_value in page.properties.items():
                    if hasattr(prop_value, 'title') and prop_value.title:
                        return "".join([rt.plain_text for rt in prop_value.title])
                    elif hasattr(prop_value, 'rich_text') and prop_value.rich_text:
                        return "".join([rt.plain_text for rt in prop_value.rich_text])
            
            # フォールバック: page IDを返す
            return f"Page {page.id}"
            
        except Exception as e:
            return f"Unknown Page ({page.id})"
    
    async def save_results_to_file(self, results: dict) -> str:
        """結果をJSONファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"llcdao_comments_extracted_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)
    
    def print_summary(self, results: dict):
        """結果サマリーを表示"""
        print("\n" + "="*60)
        print("📊 LLCDAO コメント抽出結果サマリー")
        print("="*60)
        print(f"🗃️  総ページ数: {results['total_pages']}")
        print(f"💬 総コメント数: {results['total_comments']}")
        print(f"📝 コメント付きページ数: {results['pages_with_comments']}")
        print(f"⏰ 抽出実行時刻: {results['extraction_time']}")
        
        if results['total_comments'] > 0:
            print(f"\n🎯 コメント詳細:")
            for page_info in results['comment_details']:
                print(f"\n📄 {page_info['page_title']}")
                print(f"   💬 {page_info['comment_count']}個のコメント")
                
                for comment in page_info['comments']:
                    print(f"   📝 「{comment['content'][:80]}...」")
                    print(f"      👤 {comment['created_by']['id']} ({comment['created_time']})")
        else:
            print("\n📭 コメントは見つかりませんでした")

async def main():
    """メイン関数"""
    print("🚀 LLCDAO Notion コメント抽出システム")
    print("="*50)
    
    try:
        # コメント抽出システム初期化
        extractor = LLCDAOCommentExtractor()
        
        # コメント抽出実行
        results = await extractor.extract_all_comments()
        
        # 結果をファイルに保存
        saved_file = await extractor.save_results_to_file(results)
        print(f"\n💾 結果をファイルに保存: {saved_file}")
        
        # サマリー表示
        extractor.print_summary(results)
        
        print("\n🎉 コメント抽出完了!")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        print("設定を確認して再実行してください")

if __name__ == "__main__":
    asyncio.run(main())