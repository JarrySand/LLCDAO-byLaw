// Navigation config for the site. Group documents by section.
// path is relative to the site root (repository root when Pages source is root).
window.DOCS = [
  // 1) 定款規程（ver2.0系 - 公開中）
  {
    key: 'bylaws',
    title: '📜 定款・規程（最新版）',
    items: [
      { id: 'bylaw-articles-v2-0', title: '01 定款ひな形 ver2.0', path: '01_【社員権トークン＋ガバナンストークン】合同会社型DAO定款ひな形ver2.0.md' },
      { id: 'assembly-rules-v2-1', title: '02 DAO総会規程 ver2.1', path: '02_DAO総会規程ver2.1.md' },
      { id: 'operation-rules-v2-1', title: '03 運営規程 ver2.1', path: '03_運営規程ver2.1.md' },
      { id: 'token-rules-v2-2', title: '04 トークン規程 ver2.2', path: '04_トークン規程ver2.2.md' },
      { id: 'glossary', title: '05 用語集', path: '05_用語集.md' },
    ],
  },
  // 2) 開発中（v3.x）
  {
    key: 'dev',
    title: '🔬 開発中（v3.x）',
    items: [
      { id: 'teikan-v3-3', title: '定款 ver3.3（ドラフト）', path: 'docs/teikan-revision/drafts/定款ver3.3.md' },
      { id: 'teikan-revision-readme', title: '改定プロジェクト概要', path: 'docs/teikan-revision/README.md' },
    ],
  },
  // 3) 別紙
  {
    key: 'appendices',
    title: '📎 別紙（appendices）',
    items: [
      { id: 'appendix-assembly', title: 'DAO総会別紙', path: 'appendices/DAO総会別紙.md' },
      { id: 'appendix-shared-ops', title: '共通運用', path: 'appendices/共通運用.md' },
      { id: 'appendix-token', title: 'トークン別紙', path: 'appendices/トークン別紙.md' },
    ],
  },
  // 4) 全体説明（ガイド）
  {
    key: 'guides',
    title: '📖 全体説明',
    items: [
      { id: 'guide-readme', title: 'ガイド概要（README）', path: 'docs/guide/README.md' },
      { id: 'guide-context', title: '設計思想（context）', path: 'docs/guide/context.md' },
      { id: 'guide-structure', title: '構成/参照/版管理（structure）', path: 'docs/guide/structure.md' },
    ],
  },
  // 5) 立上げガイド（Setup）
  {
    key: 'setup',
    title: '🚀 立上げガイド（Setup）',
    items: [
      { id: 'setup-readme', title: 'はじめに: 立上げの全体像', path: 'docs/guide/setup/README.md' },
      { id: 'setup-01', title: '1. 目的・範囲・法域', path: 'docs/guide/setup/01_concept.md' },
      { id: 'setup-02', title: '2. パラメータ設計', path: 'docs/guide/setup/02_parameters.md' },
      { id: 'setup-03', title: '3. 法人設立・規程採択', path: 'docs/guide/setup/03_legal.md' },
      { id: 'setup-04', title: '4. ツール導入・ローンチ', path: 'docs/guide/setup/04_launch.md' },
    ],
  },
  // 6) 運用ガイド（Operation）
  {
    key: 'operation',
    title: '⚙️ 運用ガイド（Operation）',
    items: [
      { id: 'operation-readme', title: 'はじめに: 運用ガイド概要', path: 'docs/guide/operation/README.md' },
      { id: 'operation-calendar', title: '1. 定常業務カレンダー', path: 'docs/guide/operation/02_calendar.md' },
      { id: 'operation-proposal', title: '2. 提案・投票の進め方', path: 'docs/guide/operation/03_proposal.md' },
      { id: 'operation-membership', title: '3. メンバー管理とトークン', path: 'docs/guide/operation/04_membership.md' },
      { id: 'operation-treasury', title: '4. トレジャリー運用', path: 'docs/guide/operation/05_treasury.md' },
      { id: 'operation-incident', title: '5. インシデント対応', path: 'docs/guide/operation/06_incident.md' },
    ],
  },
];
