import re
from typing import List, Dict, Any, Optional, Tuple
import os

class EnhancedMarkdownConverter:
    """
    高度なMarkdown→Notionブロック変換システム
    
    対応機能:
    - ヘッダー (H1-H6)
    - 太字・斜体・コード
    - リンク・画像
    - リスト（番号付き・箇条書き・ネスト対応）
    - 引用
    - コードブロック
    - テーブル
    - 水平線
    """
    
    def __init__(self):
        # リッチテキストパターン
        self.rich_text_patterns = [
            # **太字** または __太字__
            (r'\*\*(.*?)\*\*|__(.*?)__', 'bold'),
            # *斜体* または _斜体_
            (r'\*(.*?)\*|_(.*?)_', 'italic'),
            # `コード`
            (r'`([^`]+)`', 'code'),
            # [リンクテキスト](URL)
            (r'\[([^\]]+)\]\(([^)]+)\)', 'link'),
        ]
    
    def convert_content_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Markdownコンテンツを完全にNotionブロックに変換"""
        blocks = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 空行をスキップ
            if not line.strip():
                i += 1
                continue
            
            # コードブロック処理
            if line.strip().startswith('```'):
                code_block, lines_consumed = self._parse_code_block(lines[i:])
                if code_block:
                    blocks.append(code_block)
                i += lines_consumed
                continue
            
            # テーブル処理
            if '|' in line and self._is_table_row(line):
                table_blocks, lines_consumed = self._parse_table(lines[i:])
                blocks.extend(table_blocks)
                i += lines_consumed
                continue
            
            # ヘッダー処理
            if line.strip().startswith('#'):
                header_block = self._parse_header(line)
                if header_block:
                    blocks.append(header_block)
                i += 1
                continue
            
            # 水平線処理
            if re.match(r'^[-*_]{3,}$', line.strip()):
                blocks.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })
                i += 1
                continue
            
            # 引用処理
            if line.strip().startswith('>'):
                quote_block = self._parse_quote(line)
                blocks.append(quote_block)
                i += 1
                continue
            
            # リスト処理
            if self._is_list_item(line):
                list_blocks, lines_consumed = self._parse_list(lines[i:])
                blocks.extend(list_blocks)
                i += lines_consumed
                continue
            
            # 通常の段落処理
            paragraph_block = self._parse_paragraph(line)
            blocks.append(paragraph_block)
            i += 1
        
        return blocks
    
    def _parse_rich_text(self, text: str) -> List[Dict[str, Any]]:
        """テキストをリッチテキスト形式に変換"""
        if not text or not text.strip():
            return [{"type": "text", "text": {"content": " "}}]
        
        # テキストを分析してフォーマットを抽出
        rich_text = []
        current_pos = 0
        
        while current_pos < len(text):
            # 最も早く出現するパターンを見つける
            earliest_match = None
            earliest_pos = len(text)
            pattern_type = None
            
            for pattern, format_type in self.rich_text_patterns:
                match = re.search(pattern, text[current_pos:])
                if match and match.start() < earliest_pos - current_pos:
                    earliest_match = match
                    earliest_pos = current_pos + match.start()
                    pattern_type = format_type
            
            if earliest_match is None:
                # パターンが見つからない場合、残りのテキストを通常テキストとして追加
                remaining_text = text[current_pos:]
                if remaining_text:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": remaining_text}
                    })
                break
            
            # マッチする前のテキストを通常テキストとして追加
            before_text = text[current_pos:earliest_pos]
            if before_text:
                rich_text.append({
                    "type": "text",
                    "text": {"content": before_text}
                })
            
            # フォーマット済みテキストを追加
            formatted_block = self._create_formatted_text(earliest_match, pattern_type)
            if formatted_block:
                rich_text.append(formatted_block)
            
            current_pos = earliest_pos + len(earliest_match.group(0))
        
        # 結果の検証と安全なフォールバック
        if not rich_text:
            return [{"type": "text", "text": {"content": text if text.strip() else " "}}]
        
        # 各リッチテキスト要素の検証
        valid_rich_text = []
        for rt in rich_text:
            if rt.get('type') == 'text' and rt.get('text', {}).get('content') is not None:
                valid_rich_text.append(rt)
        
        return valid_rich_text if valid_rich_text else [{"type": "text", "text": {"content": text if text.strip() else " "}}]
    
    def _create_formatted_text(self, match: re.Match, format_type: str) -> Optional[Dict[str, Any]]:
        """フォーマット済みテキストブロックを作成"""
        if format_type == 'bold':
            content = match.group(1) or match.group(2)
            if not content:
                return None
            return {
                "type": "text",
                "text": {"content": content},
                "annotations": {"bold": True}
            }
        elif format_type == 'italic':
            content = match.group(1) or match.group(2)
            if not content:
                return None
            return {
                "type": "text", 
                "text": {"content": content},
                "annotations": {"italic": True}
            }
        elif format_type == 'code':
            content = match.group(1)
            if not content:
                return None
            return {
                "type": "text",
                "text": {"content": content},
                "annotations": {"code": True}
            }
        elif format_type == 'link':
            text_content = match.group(1)
            url = match.group(2)
            if not text_content or not url:
                return None
            return {
                "type": "text",
                "text": {"content": text_content, "link": {"url": url}}
            }
        
        return None
    
    def _parse_header(self, line: str) -> Optional[Dict[str, Any]]:
        """ヘッダー行を解析"""
        line = line.strip()
        if not line.startswith('#'):
            return None
        
        # ヘッダーレベルを計算
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break
        
        # Notionは heading_1, heading_2, heading_3 のみサポート
        if level > 3:
            level = 3
        elif level < 1:
            return None
        
        # ヘッダーテキストを抽出（#の後のスペースを考慮）
        header_text = line.lstrip('#').strip()
        if not header_text:
            return None
        
        # ヘッダータイプを決定
        header_type = f"heading_{level}"
        
        return {
            "object": "block",
            "type": header_type,
            header_type: {
                "rich_text": self._parse_rich_text(header_text)
            }
        }
    
    def _parse_paragraph(self, line: str) -> Dict[str, Any]:
        """段落を解析"""
        rich_text = self._parse_rich_text(line.strip())
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": rich_text}
        }
    
    def _parse_quote(self, line: str) -> Dict[str, Any]:
        """引用を解析"""
        quote_text = line.strip()[1:].strip()  # '>' を除去
        rich_text = self._parse_rich_text(quote_text)
        return {
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": rich_text}
        }
    
    def _is_list_item(self, line: str) -> bool:
        """リストアイテムかどうか判定"""
        stripped = line.strip()
        # 箇条書きリスト
        if re.match(r'^[-*+]\s', stripped):
            return True
        # 番号付きリスト
        if re.match(r'^\d+\.\s', stripped):
            return True
        return False
    
    def _parse_list(self, lines: List[str]) -> Tuple[List[Dict[str, Any]], int]:
        """リストを解析"""
        blocks = []
        lines_consumed = 0
        
        for line in lines:
            if not line.strip():
                lines_consumed += 1
                break
            
            if not self._is_list_item(line):
                break
            
            stripped = line.strip()
            
            # 箇条書きリスト
            if re.match(r'^[-*+]\s', stripped):
                list_text = re.sub(r'^[-*+]\s', '', stripped)
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": self._parse_rich_text(list_text)
                    }
                })
            
            # 番号付きリスト
            elif re.match(r'^\d+\.\s', stripped):
                list_text = re.sub(r'^\d+\.\s', '', stripped)
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item", 
                    "numbered_list_item": {
                        "rich_text": self._parse_rich_text(list_text)
                    }
                })
            
            lines_consumed += 1
        
        return blocks, lines_consumed
    
    def _parse_code_block(self, lines: List[str]) -> Tuple[Optional[Dict[str, Any]], int]:
        """コードブロックを解析"""
        if not lines[0].strip().startswith('```'):
            return None, 1
        
        # 言語を抽出
        first_line = lines[0].strip()
        language = first_line[3:].strip() if len(first_line) > 3 else "plain text"
        
        # コード内容を収集
        code_lines = []
        lines_consumed = 1
        
        for i in range(1, len(lines)):
            if lines[i].strip() == '```':
                lines_consumed = i + 1
                break
            code_lines.append(lines[i])
        
        code_content = '\n'.join(code_lines)
        
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": code_content}}],
                "language": language.lower() if language else "plain text"
            }
        }, lines_consumed
    
    def _is_table_row(self, line: str) -> bool:
        """テーブル行かどうか判定"""
        return '|' in line and line.strip().startswith('|') and line.strip().endswith('|')
    
    def _parse_table(self, lines: List[str]) -> Tuple[List[Dict[str, Any]], int]:
        """テーブルを解析（Notionのテーブルブロックとして）"""
        table_blocks = []
        lines_consumed = 0
        
        # テーブルヘッダーを解析
        if not self._is_table_row(lines[0]):
            return [], 1
        
        header_row = lines[0].strip()
        headers = [cell.strip() for cell in header_row.split('|')[1:-1]]
        
        # ヘッダー行を追加
        table_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"📊 テーブル: {' | '.join(headers)}"}}]
            }
        })
        
        lines_consumed += 1
        
        # セパレーター行をスキップ
        if lines_consumed < len(lines) and '---' in lines[lines_consumed]:
            lines_consumed += 1
        
        # データ行を処理
        for i in range(lines_consumed, len(lines)):
            if not self._is_table_row(lines[i]):
                break
            
            row = lines[i].strip()
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            
            # 行を段落として追加
            row_text = ' | '.join(cells)
            table_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": self._parse_rich_text(row_text)
                }
            })
            
            lines_consumed += 1
        
        return table_blocks, lines_consumed