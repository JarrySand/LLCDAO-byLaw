#!/usr/bin/env python3
"""
MCP機能を使用してNotionコメントを抽出
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートを追加
sys.path.append('.')
from src.notion_mcp.client import NotionClient

# .envファイルを読み込み
load_dotenv()

async def extract_comments_via_mcp():
    """MCP機能を使用してコメントを抽出"""
    
    # NotionClientを初期化
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        print("❌ NOTION_API_KEY が見つかりません")
        return
    
    client = NotionClient(api_key)
    database_id = "24539d01e781800884eaca3a3a95e78e"
    
    print("🚀 MCP機能を使用してNotionコメントを抽出中...")
    print(f"📊 データベースID: {database_id}")
    
    try:
        # データベース内のページを取得
        print("\n📋 データベースページを取得中...")
        pages = await client.query_database(database_id=database_id, page_size=100)
        print(f"✅ {len(pages.results)}個のページを発見")
        
        total_comments = 0
        pages_with_comments = 0
        
        # 各ページのコメントを取得
        for i, page in enumerate(pages.results, 1):
            # ページタイトルを取得
            page_title = "Unknown"
            if hasattr(page, 'properties') and page.properties:
                for prop_name, prop_value in page.properties.items():
                    if hasattr(prop_value, 'title') and prop_value.title:
                        page_title = "".join([rt.plain_text for rt in prop_value.title])
                        break
                    elif hasattr(prop_value, 'rich_text') and prop_value.rich_text:
                        page_title = "".join([rt.plain_text for rt in prop_value.rich_text])
                        break
            
            print(f"\n🔍 [{i}/{len(pages.results)}] {page_title}")
            print(f"   📄 Page ID: {page.id}")
            
            try:
                # コメントを取得
                comments = await client.get_comments(block_id=page.id, page_size=100)
                
                if comments.results:
                    pages_with_comments += 1
                    page_comment_count = len(comments.results)
                    total_comments += page_comment_count
                    
                    print(f"   💬 {page_comment_count}個のコメントを発見!")
                    
                    for j, comment in enumerate(comments.results, 1):
                        content = "".join([rt.plain_text for rt in comment.rich_text])
                        created_by = "Unknown"
                        if hasattr(comment.created_by, 'id'):
                            created_by = comment.created_by.id
                        
                        print(f"   [{j}] 📝 「{content[:80]}...」")
                        print(f"       👤 作成者: {created_by}")
                        print(f"       ⏰ 作成日時: {comment.created_time}")
                        print(f"       🔗 Discussion ID: {comment.discussion_id}")
                        print()
                else:
                    print("   📭 コメントなし")
                    
            except Exception as e:
                print(f"   ❌ コメント取得エラー: {str(e)}")
        
        # サマリーを表示
        print("\n" + "="*60)
        print("📊 コメント抽出結果サマリー")
        print("="*60)
        print(f"🗃️  総ページ数: {len(pages.results)}")
        print(f"💬 総コメント数: {total_comments}")
        print(f"📝 コメント付きページ数: {pages_with_comments}")
        print("🎉 MCP機能によるコメント抽出完了!")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    asyncio.run(extract_comments_via_mcp())