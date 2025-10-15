// Navigation config for the site. Group documents by section.
// path is relative to the site root (repository root when Pages source is root).
window.DOCS = [
  {
    key: 'bylaws',
    title: '定款・規程（最新版）',
    items: [
      { id: 'bylaw-articles-v2-0', title: '01 定款ひな形 ver2.0', path: '01_【社員権トークン＋ガバナンストークン】合同会社型DAO定款ひな形ver2.0.md' },
      { id: 'assembly-rules-v2-1', title: '02 DAO総会規程 ver2.1', path: '02_DAO総会規程ver2.1.md' },
      { id: 'operation-rules-v2-1', title: '03 運営規程 ver2.1', path: '03_運営規程ver2.1.md' },
      { id: 'token-rules-v2-2', title: '04 トークン規程 ver2.2', path: '04_トークン規程ver2.2.md' },
    ],
  },
  {
    key: 'appendices',
    title: '別紙（appendices）',
    items: [
      { id: 'appendix-assembly', title: 'DAO総会別紙', path: 'appendices/DAO総会別紙.md' },
      { id: 'appendix-shared-ops', title: '共通運用', path: 'appendices/共通運用.md' },
      { id: 'appendix-token', title: 'トークン別紙', path: 'appendices/トークン別紙.md' },
    ],
  },
  {
    key: 'guides',
    title: 'ガイド（docs/guide/）',
    items: [
      { id: 'guide-readme', title: 'ガイド概要（README）', path: 'docs/guide/README.md' },
      { id: 'guide-context', title: '設計思想（context）', path: 'docs/guide/context.md' },
      { id: 'guide-structure', title: '構成/参照/版管理（structure）', path: 'docs/guide/structure.md' },
      { id: 'guide-operation', title: '実運用（operation）', path: 'docs/guide/operation.md' },
    ],
    subsections: [
      {
        key: 'runbook',
        title: 'ランブック（dao-runbook）',
        items: [
          { id: 'dao-runbook-readme', title: 'ランブック 概要', path: 'docs/guide/dao-runbook/README.md' },
          { id: 'dao-runbook-01', title: 'ランブック 01 役割と責任', path: 'docs/guide/dao-runbook/01_roles_and_responsibilities.md' },
          { id: 'dao-runbook-02', title: 'ランブック 02 年間カレンダー', path: 'docs/guide/dao-runbook/02_annual_calendar.md' },
          { id: 'dao-runbook-03', title: 'ランブック 03 総会運営', path: 'docs/guide/dao-runbook/03_assembly_operations.md' },
          { id: 'dao-runbook-04', title: 'ランブック 04 提案ライフサイクル', path: 'docs/guide/dao-runbook/04_proposal_lifecycle.md' },
          { id: 'dao-runbook-05', title: 'ランブック 05 トークンと権限', path: 'docs/guide/dao-runbook/05_token_and_permissions.md' },
          { id: 'dao-runbook-06', title: 'ランブック 06 トレジャリー運用', path: 'docs/guide/dao-runbook/06_treasury_operations.md' },
          { id: 'dao-runbook-07', title: 'ランブック 07 コンプライアンス・インシデント', path: 'docs/guide/dao-runbook/07_compliance_and_incidents.md' },
          { id: 'dao-runbook-08', title: 'ランブック 08 監査と改善', path: 'docs/guide/dao-runbook/08_audit_and_improvement.md' },
        ],
      },
      {
        key: 'setup',
        title: '立上げガイド（dao-setup）',
        items: [
          { id: 'dao-setup-readme', title: '立上げガイド 概要', path: 'docs/guide/dao-setup/README.md' },
          { id: 'dao-setup-01', title: '立上げ 01 目的/範囲/法域', path: 'docs/guide/dao-setup/01_purpose_scope_jurisdiction.md' },
          { id: 'dao-setup-02', title: '立上げ 02 採用/版管理/発効', path: 'docs/guide/dao-setup/02_adopt_bylaws_versioning_effective.md' },
          { id: 'dao-setup-03', title: '立上げ 03 トークンと権限モデル', path: 'docs/guide/dao-setup/03_tokens_and_authority_model.md' },
          { id: 'dao-setup-04', title: '立上げ 04 投票・基準・定足数', path: 'docs/guide/dao-setup/04_voting_methods_thresholds_quorum.md' },
          { id: 'dao-setup-05', title: '立上げ 05 トレジャリーデザイン', path: 'docs/guide/dao-setup/05_treasury_design.md' },
          { id: 'dao-setup-06', title: '立上げ 06 役割/RACI/チャネル', path: 'docs/guide/dao-setup/06_roles_raci_channels.md' },
          { id: 'dao-setup-07', title: '立上げ 07 ツールスタック', path: 'docs/guide/dao-setup/07_tools_stack.md' },
          { id: 'dao-setup-08', title: '立上げ 08 セキュリティ/コンプライアンス', path: 'docs/guide/dao-setup/08_security_compliance.md' },
          { id: 'dao-setup-09', title: '立上げ 09 ローンチ手順', path: 'docs/guide/dao-setup/09_launch_procedure.md' },
        ],
      },
    ],
  },
];


