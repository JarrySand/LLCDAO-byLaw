"""
LLCDAO定款規程レビューシステム 設定ファイル
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

class LLCDAOConfig:
    """LLCDAO専用設定管理"""
    
    # 基本設定
    PROJECT_ROOT = "C:/Users/zukas/LLCDAO-bylaw"
    
    # Notion設定
    # TODO: 以下を実際の値に更新してください
    DATABASE_IDS = {
        "review_materials": "24539d01e781800884eaca3a3a95e78e",  # 確定ID
        "modifications": "24539d01e781800884eaca3a3a95e78e",  # 同じDBを使用
        "issues": "24539d01e781800884eaca3a3a95e78e"  # 同じDBを使用
    }
    
    # 同期対象フォルダ
    REVIEW_FOLDERS = [
        "review/01-materials",      # 週次事前資料
        "review/02-minutes",        # 議事録
        "review/03-modifications",  # 修正・課題管理
        "review/templates"          # テンプレート
    ]
    
    # 週次フォルダマッピング
    WEEK_FOLDERS = {
        1: "review/01-materials/week1-kickoff-token",
        2: "review/01-materials/week2-dao-assembly", 
        3: "review/01-materials/week3-dao-operation",
        4: "review/01-materials/week4-treasury",
        5: "review/01-materials/week5-charter",
        6: "review/01-materials/week6-integration"
    }
    
    # 規程タイプマッピング
    REGULATION_TYPES = {
        "token": "トークン規程",
        "assembly": "DAO総会規程", 
        "operation": "DAO運営規程",
        "treasury": "トレジャリー管理規程",
        "charter": "DAO憲章"
    }
    
    # 資料タイプマッピング  
    MATERIAL_TYPES = {
        "readme": "事前資料",
        "diff": "diff比較",
        "checklist": "チェックリスト", 
        "minutes": "議事録",
        "proposal": "修正提案",
        "issue": "課題管理"
    }
    
    @classmethod
    def get_api_key(cls) -> str:
        """環境変数からAPIキーを取得"""
        api_key = os.getenv("NOTION_API_KEY")
        if not api_key:
            raise ValueError(
                "NOTION_API_KEY not found in environment variables. "
                "Please set it in .env file"
            )
        return api_key
    
    @classmethod
    def get_project_path(cls) -> Path:
        """プロジェクトルートパスを取得"""
        return Path(cls.PROJECT_ROOT)
    
    @classmethod
    def validate_setup(cls) -> dict:
        """設定の妥当性をチェック"""
        issues = []
        
        # プロジェクトパス確認
        if not cls.get_project_path().exists():
            issues.append(f"プロジェクトルートが見つかりません: {cls.PROJECT_ROOT}")
        
        # APIキー確認
        try:
            cls.get_api_key()
        except ValueError as e:
            issues.append(str(e))
        
        # データベースID確認
        for db_name, db_id in cls.DATABASE_IDS.items():
            if db_id == f"YOUR_{db_name.upper()}_DATABASE_ID_HERE":
                issues.append(f"{db_name}のデータベースIDが未設定です")
        
        # レビューフォルダ確認
        missing_folders = []
        for folder in cls.REVIEW_FOLDERS:
            folder_path = cls.get_project_path() / folder
            if not folder_path.exists():
                missing_folders.append(folder)
        
        if missing_folders:
            issues.append(f"レビューフォルダが見つかりません: {missing_folders}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

# 設定確認用のメイン関数
if __name__ == "__main__":
    print("🔧 LLCDAO設定確認")
    print("=" * 40)
    
    config_check = LLCDAOConfig.validate_setup()
    
    if config_check["valid"]:
        print("✅ 全ての設定が正常です")
        print(f"📁 プロジェクトルート: {LLCDAOConfig.PROJECT_ROOT}")
        print(f"📋 同期対象フォルダ: {len(LLCDAOConfig.REVIEW_FOLDERS)}個")
    else:
        print("⚠️  設定に問題があります:")
        for issue in config_check["issues"]:
            print(f"  - {issue}")
        
        print("\n🔧 修正が必要な項目:")
        print("1. .env ファイルでNOTION_API_KEYを設定")
        print("2. llcdao_config.py でデータベースIDを更新")
        print("3. 必要なフォルダが存在することを確認")