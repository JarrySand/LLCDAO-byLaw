## 公開コメント受付（最小構成）

本リポジトリは、公開コメント受付用の最小構成です。以下の「定款・規程（4点）」と「別紙（3点）」をご確認のうえ、Issue または Pull Request でご意見をお寄せください。

### 定款・規程（最新版・版番号付き）
1. [01_【社員権トークン＋ガバナンストークン】合同会社型DAO定款ひな形ver2.0.md](./01_【社員権トークン＋ガバナンストークン】合同会社型DAO定款ひな形ver2.0.md)
2. [02_DAO総会規程ver2.1.md](./02_DAO総会規程ver2.1.md)
3. [03_運営規程ver2.1.md](./03_運営規程ver2.1.md)
4. [04_トークン規程ver2.2.md](./04_トークン規程ver2.2.md)

### 別紙（appendices）
- [DAO総会別紙.md](./appendices/DAO総会別紙.md)
- [共通運用.md](./appendices/共通運用.md)
- [トークン別紙.md](./appendices/トークン別紙.md)

---

## 公開コメントの送り方

- **Issue で提案する（推奨）**: [新規Issueを作成](../../issues/new)
  - 件名: 対象文書名 + 要約（例: トークン規程ver2.2 - 付与上限の明確化提案）
  - 本文: 該当箇所URL、現行文、提案文、理由、影響範囲
- **Pull Request で提案する**: [差分を作成](../../compare)
  - 対象ファイルを直接編集し、変更点を明確に記載してください

- GitHub が不慣れな方: [変更提案フォーム（Google スプレッドシート）](https://docs.google.com/spreadsheets/d/1M_cnJ385RMKyuDKkMPdxGibrTTB_9WevOXxaNHaSzcs/edit?gid=0#gid=0)
  - 記入項目: 対象文書/箇所、提案文、理由等（詳細はスプシをご確認ください））
  - 提出後、内容を確認し変更可否を判断します

- 毎週水曜日を目途に内容を確認し、反映可否の判断と資料のアップデートをしていきます（2025年11月上旬までの集中改善期間））

受付範囲は上記7ファイルに加え、`docs/guide/` 配下のガイド文書（context / structure / operation）もレビュー対象に含めます。

---

## ディレクトリ構成（公開用）
```
LLCDAO-bylaw/
├── 01_【社員権トークン＋ガバナンストークン】合同会社型DAO定款ひな形ver2.0.md
├── 02_DAO総会規程ver2.1.md
├── 03_運営規程ver2.1.md
├── 04_トークン規程ver2.2.md
├── appendices/
│   ├── DAO総会別紙.md
│   ├── 共通運用.md
│   └── トークン別紙.md
├── docs/
│   ├── README.md
│   ├── guide/
│   │   └── README.md
├── assets/
├── release/
├── archive/
└── wip/
```

### 運用メモ
- **release/**: 確定時に「ルート＋appendices（＋必要ならassets）」を `release/vX.Y/` にスナップショット保存
- **archive/**: 作業用ディレクトリ一式は日付フォルダ配下に退避（例: `archive/20251018/`）
- **wip/**: まだ調整中の文書
  - [DAO憲章v1.0.md](./wip/DAO憲章v1.0.md)
  - [トレジャリー管理規程v1.0.md](./wip/トレジャリー管理規程v1.0.md)

---

## docs/ の補足
- `docs/` は周辺ドキュメントの置き場です。
- 運用ガイドや手順等は `docs/guide/` に配置してください。
- 参考: [docs/README.md](./docs/README.md), [docs/guide/README.md](./docs/guide/README.md)

---

## 免責
本資料は一般的な情報提供を目的としたものであり、法律上の助言を構成するものではありません。実装や運用にあたっては、専門家の助言を受けてください。

---
**最終更新**: 2025-10-09