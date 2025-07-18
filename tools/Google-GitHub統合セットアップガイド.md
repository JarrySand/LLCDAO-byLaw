# Google-GitHub統合セットアップガイド

## 🚀 即座に実装できる手順

### Step 1: Google Drive セットアップ（10分）

#### 1.1 フォルダ構成作成
```bash
# Google Drive で以下のフォルダ構成を作成
LLCDAO規程レビュー_v2.0/
├── 01_レビュー用文書/
├── 02_参考資料/
├── 03_フィードバック集約/
└── 04_質問・議論/
```

#### 1.2 Markdownファイルの Word変換
```bash
# 変換コマンド例（pandoc使用）
pandoc new/定款v2.0.md -o "01_レビュー用文書/定款v2.0_レビュー用.docx"
pandoc new/トークン規程_v2.1_統合版.md -o "01_レビュー用文書/トークン規程v2.1_レビュー用.docx"
pandoc new/DAO総会規程ver2.0.md -o "01_レビュー用文書/DAO総会規程v2.0_レビュー用.docx"
pandoc new/DAO運営規程ver2.0.md -o "01_レビュー用文書/運営規程v2.0_レビュー用.docx"
pandoc new/トレジャリー管理規程v1.0.md -o "01_レビュー用文書/トレジャリー管理規程v1.0_レビュー用.docx"
pandoc new/DAO憲章v1.0.md -o "01_レビュー用文書/DAO憲章v1.0_レビュー用.docx"
```

#### 1.3 権限設定
```
フォルダ権限: 「リンクを知っている全員が閲覧可能」
文書権限: 「リンクを知っている全員がコメント可能」
ダウンロード: 「無効」（機密保持）
```

### Step 2: フィードバック統合シート作成（15分）

#### 2.1 Google Sheets テンプレート
```
ファイル名: フィードバック統合シート.xlsx
場所: 03_フィードバック集約/

列構成:
A列: 規程名 (プルダウン: 定款v2.0, トークン規程v2.1, DAO総会規程v2.0, 運営規程v2.0, トレジャリー管理規程v1.0, DAO憲章v1.0)
B列: 条文番号 (例: 第1条第2項)
C列: レビュアー名
D列: 専門分野 (プルダウン: 法務, 税務, 技術, 運用, 国際, その他)
E列: 指摘事項
F列: 改善提案
G列: 重要度 (プルダウン: 1-5)
H列: ステータス (プルダウン: 未対応, 検討中, 対応済み, 却下)
I列: 対応予定日 (日付形式)
J列: 対応内容
K列: GitHub Issue番号
L列: 最終更新日 (自動)
```

#### 2.2 データ検証ルール設定
```javascript
// Google Apps Script でデータ検証
function setupDataValidation() {
  const sheet = SpreadsheetApp.getActiveSheet();
  
  // 規程名のプルダウン
  const regulationRange = sheet.getRange('A:A');
  const regulationValidation = SpreadsheetApp.newDataValidation()
    .requireValueInList(['定款v2.0', 'トークン規程v2.1', 'DAO総会規程v2.0', '運営規程v2.0', 'トレジャリー管理規程v1.0', 'DAO憲章v1.0'])
    .setAllowInvalid(false)
    .build();
  regulationRange.setDataValidation(regulationValidation);
  
  // 専門分野のプルダウン
  const expertiseRange = sheet.getRange('D:D');
  const expertiseValidation = SpreadsheetApp.newDataValidation()
    .requireValueInList(['法務', '税務', '技術', '運用', '国際', 'その他'])
    .setAllowInvalid(false)
    .build();
  expertiseRange.setDataValidation(expertiseValidation);
  
  // 重要度のプルダウン
  const priorityRange = sheet.getRange('G:G');
  const priorityValidation = SpreadsheetApp.newDataValidation()
    .requireValueInList(['1', '2', '3', '4', '5'])
    .setAllowInvalid(false)
    .build();
  priorityRange.setDataValidation(priorityValidation);
  
  // ステータスのプルダウン
  const statusRange = sheet.getRange('H:H');
  const statusValidation = SpreadsheetApp.newDataValidation()
    .requireValueInList(['未対応', '検討中', '対応済み', '却下'])
    .setAllowInvalid(false)
    .build();
  statusRange.setDataValidation(statusValidation);
}
```

### Step 3: GitHub連携スクリプト作成（20分）

#### 3.1 Google Apps Script プロジェクト作成
```javascript
// GitHub API設定
const GITHUB_TOKEN = 'your_github_token_here';
const REPO_OWNER = 'your_username';
const REPO_NAME = 'LLCDAO-bylaw';
const GITHUB_API_BASE = 'https://api.github.com';

// GitHub Issue作成関数
function createGitHubIssue(title, body, labels = [], assignees = []) {
  const url = `${GITHUB_API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/issues`;
  
  const payload = {
    title: title,
    body: body,
    labels: labels,
    assignees: assignees
  };
  
  const options = {
    method: 'POST',
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    const result = JSON.parse(response.getContentText());
    return result.number; // Issue番号を返す
  } catch (error) {
    console.error('GitHub Issue作成エラー:', error);
    return null;
  }
}

// フィードバック同期メイン関数
function syncFeedbackToGitHub() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  
  // ヘッダー行を除く
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    
    // 未対応で GitHub Issue番号が空の場合のみ処理
    if (row[7] === '未対応' && !row[10]) {
      const title = `[${row[0]}] ${row[4]}`; // 規程名 + 指摘事項
      const body = formatIssueBody(row);
      const labels = [row[3].toLowerCase(), `priority-${row[6]}`];
      
      const issueNumber = createGitHubIssue(title, body, labels);
      
      if (issueNumber) {
        // GitHub Issue番号をシートに記録
        sheet.getRange(i + 1, 11).setValue(issueNumber);
        // 最終更新日を記録
        sheet.getRange(i + 1, 12).setValue(new Date());
        
        console.log(`Issue #${issueNumber} created for row ${i + 1}`);
      }
    }
  }
}

// Issue本文フォーマット関数
function formatIssueBody(row) {
  return `## 📋 フィードバック詳細

### 指摘事項
${row[4]}

### 改善提案
${row[5]}

### 詳細情報
- **規程**: ${row[0]}
- **条文**: ${row[1]}
- **レビュアー**: ${row[2]}
- **専門分野**: ${row[3]}
- **重要度**: ${row[6]}/5
- **記録日**: ${row[11] || new Date().toLocaleDateString()}

### 元データ
- Google Sheets: [フィードバック統合シート](https://docs.google.com/spreadsheets/d/[SHEET_ID])

---
**自動生成**: Google Apps Script により自動作成されました。
**更新**: 元のGoogle Sheetsを更新してください。`;
}

// 定期実行設定（1日1回）
function setupTrigger() {
  ScriptApp.newTrigger('syncFeedbackToGitHub')
    .timeBased()
    .everyDays(1)
    .atHour(9) // 毎日9時に実行
    .create();
}
```

### Step 4: GitHub リポジトリ設定（10分）

#### 4.1 GitHub Discussions有効化
```bash
# リポジトリ設定 > Features > Discussions を有効化
```

#### 4.2 Discussion Categories作成
```yaml
# .github/DISCUSSION_TEMPLATE/categories.yml
categories:
  - name: "🏛️ 法務・コンプライアンス"
    description: "法的観点からのレビュー・議論"
    emoji: "🏛️"
  - name: "💰 税務・会計"
    description: "税務処理・会計処理に関する議論"
    emoji: "💰"
  - name: "🔧 技術・実装"
    description: "技術的実装・システム要件の議論"
    emoji: "🔧"
  - name: "📊 運用・プロセス"
    description: "運用プロセス・手続きに関する議論"
    emoji: "📊"
  - name: "🌐 国際・規制"
    description: "国際展開・規制対応の議論"
    emoji: "🌐"
  - name: "💡 一般・その他"
    description: "その他の議論・提案"
    emoji: "💡"
```

#### 4.3 Issue Template作成
```yaml
# .github/ISSUE_TEMPLATE/feedback.yml
name: 📝 フィードバック・改善提案
description: 規程に対するフィードバックや改善提案
title: "[規程名] 改善提案: "
labels: ["feedback", "improvement"]
body:
  - type: dropdown
    id: regulation
    attributes:
      label: 対象規程
      options:
        - 定款v2.0
        - トークン規程v2.1
        - DAO総会規程v2.0
        - 運営規程v2.0
        - トレジャリー管理規程v1.0
        - DAO憲章v1.0
    validations:
      required: true
  
  - type: input
    id: section
    attributes:
      label: 該当条文
      placeholder: "例: 第1条第2項"
    validations:
      required: false
  
  - type: dropdown
    id: expertise
    attributes:
      label: 専門分野
      options:
        - 法務
        - 税務
        - 技術
        - 運用
        - 国際
        - その他
    validations:
      required: true
  
  - type: textarea
    id: issue
    attributes:
      label: 指摘事項
      description: 具体的な指摘内容を記載してください
    validations:
      required: true
  
  - type: textarea
    id: proposal
    attributes:
      label: 改善提案
      description: 具体的な改善案を提示してください
    validations:
      required: true
  
  - type: dropdown
    id: priority
    attributes:
      label: 重要度
      options:
        - "1 (低)"
        - "2 (やや低)"
        - "3 (中)"
        - "4 (やや高)"
        - "5 (高)"
    validations:
      required: true
```

### Step 5: レビュアー招待システム（15分）

#### 5.1 招待メールテンプレート
```html
<!-- 招待メールテンプレート -->
<h2>📋 LLCDAO規程レビューへのご招待</h2>

<p>この度は、合同会社型DAO規程改善プロジェクトへのご協力をお願いいたします。</p>

<h3>🎯 プロジェクト概要</h3>
<ul>
  <li>日本初の合同会社型DAO規程体制の構築</li>
  <li>6規程統合による包括的ガバナンス設計</li>
  <li>ブロックチェーン技術と既存法制度の完全融合</li>
</ul>

<h3>📚 レビュー対象文書</h3>
<p><strong>Google Drive共有フォルダ</strong>: <a href="[DRIVE_LINK]">LLCDAO規程レビュー_v2.0</a></p>

<h3>🔧 フィードバック方法</h3>
<ol>
  <li><strong>簡単な方法</strong>: Google Docsに直接コメント</li>
  <li><strong>構造化方法</strong>: <a href="[SHEETS_LINK]">フィードバック統合シート</a>に記入</li>
  <li><strong>詳細議論</strong>: <a href="[GITHUB_DISCUSSIONS_LINK]">GitHub Discussions</a>で議論</li>
</ol>

<h3>📞 サポート</h3>
<p>GitHubが初めての方でも安心してご参加いただけます。</p>
<ul>
  <li>個別オンボーディング（30分）</li>
  <li>操作ガイド動画</li>
  <li>リアルタイムサポート</li>
</ul>

<p>ご参加いただける場合は、以下のフォームからご連絡ください。</p>
<p><strong>参加登録フォーム</strong>: <a href="[FORM_LINK]">こちら</a></p>
```

#### 5.2 参加登録Google Form
```yaml
# 参加登録フォーム項目
基本情報:
  - 氏名
  - 所属・役職
  - 専門分野（複数選択可）
  - 連絡先メールアドレス

参加レベル:
  - Google Docsコメントのみ
  - 構造化フィードバック
  - GitHub Discussions参加
  - 全て参加

サポート希望:
  - 個別オンボーディング希望
  - 操作ガイド動画希望
  - リアルタイムサポート希望
  - サポート不要

スケジュール:
  - 希望開始時期
  - 想定参加期間
  - 優先レビュー規程
```

### Step 6: 運用開始チェックリスト

#### 6.1 システム確認
```
□ Google Drive フォルダ構成完了
□ 全規程のWord変換完了
□ 権限設定完了（コメント可能、ダウンロード不可）
□ フィードバック統合シート作成完了
□ Google Apps Script設定完了
□ GitHub連携テスト完了
□ Discussion Categories設定完了
□ Issue Templates設定完了
```

#### 6.2 運用準備
```
□ レビュアーリスト作成完了
□ 招待メール送信完了
□ 参加登録フォーム設置完了
□ サポート体制整備完了
□ 操作ガイド動画作成完了
□ FAQ文書作成完了
□ 進捗管理システム設置完了
```

### Step 7: 継続運用スクリプト

#### 7.1 週次レポート自動生成
```javascript
function generateWeeklyReport() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // 週次統計算出
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  
  let newFeedback = 0;
  let resolvedIssues = 0;
  let activeReviewers = new Set();
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const updateDate = new Date(row[11]);
    
    if (updateDate >= weekAgo) {
      newFeedback++;
      activeReviewers.add(row[2]);
      
      if (row[7] === '対応済み') {
        resolvedIssues++;
      }
    }
  }
  
  // 週次レポートメール送信
  const report = `
週次レビュー進捗レポート
================

📊 今週の実績
- 新規フィードバック: ${newFeedback}件
- 解決済み課題: ${resolvedIssues}件  
- アクティブレビュアー: ${activeReviewers.size}名

📋 詳細統計
- 全フィードバック: ${data.length - 1}件
- 未対応: ${data.filter(row => row[7] === '未対応').length}件
- 検討中: ${data.filter(row => row[7] === '検討中').length}件
- 対応済み: ${data.filter(row => row[7] === '対応済み').length}件

🔗 リンク
- フィードバック統合シート: [URL]
- GitHub Issues: [URL]
- GitHub Discussions: [URL]
  `;
  
  // メール送信処理
  MailApp.sendEmail({
    to: 'admin@example.com',
    subject: `【LLCDAO規程レビュー】週次進捗レポート - ${new Date().toLocaleDateString()}`,
    body: report
  });
}
```

#### 7.2 自動リマインダー
```javascript
function sendWeeklyReminder() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // 7日以上未対応の課題を抽出
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  
  const overdueIssues = [];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const updateDate = new Date(row[11]);
    
    if (row[7] === '未対応' && updateDate < weekAgo) {
      overdueIssues.push({
        regulation: row[0],
        issue: row[4],
        reviewer: row[2],
        days: Math.floor((new Date() - updateDate) / (1000 * 60 * 60 * 24))
      });
    }
  }
  
  if (overdueIssues.length > 0) {
    let reminderBody = '以下の課題が7日以上未対応です：\n\n';
    
    overdueIssues.forEach(issue => {
      reminderBody += `• ${issue.regulation}: ${issue.issue} (${issue.reviewer}様, ${issue.days}日経過)\n`;
    });
    
    MailApp.sendEmail({
      to: 'admin@example.com',
      subject: '【要対応】LLCDAO規程レビュー - 未対応課題リマインダー',
      body: reminderBody
    });
  }
}
```

---

## 🎯 導入効果予測

### 参加促進効果
- **技術的ハードル**: 90%削減（Google Docs使用）
- **参加率**: 従来の3倍以上
- **フィードバック質**: 構造化により向上

### 運用効率化
- **手動作業**: 70%削減（自動化）
- **対応時間**: 50%短縮（統合管理）
- **追跡性**: 100%確保（完全記録）

---

このシステムにより、**GitHubに馴染みのない専門家でもGoogle Docsレベルの気軽さで参加**しながら、**GitHub上での高度なプロジェクト管理の恩恵**を受けることができます。 