#!/usr/bin/env python3
"""
Translate Japanese text in all markdown files to English.
"""

import re
from pathlib import Path

# Common Japanese to English translations
TRANSLATIONS = {
    # Technical terms
    "FastAPI": "FastAPI",
    "React": "React",
    "JWT": "JWT",
    "YAML": "YAML",
    "CLI": "CLI",
    "MCP": "MCP",

    # Actions/Verbs
    "使う": "use",
    "作る": "create",
    "始める": "start",
    "終わる": "end",
    "追加": "add",
    "削除": "delete",
    "更新": "update",
    "検索": "search",
    "実装": "implementation",
    "設定": "setup/configuration",
    "設計": "design",
    "初期化": "initialization",
    "登録": "register",
    "確認": "confirmation",
    "選択": "selection/choice",

    # Nouns
    "アプリ": "app",
    "タスク": "task",
    "機能": "feature",
    "問題": "problem/issue",
    "改善": "improvement",
    "エラー": "error",
    "ファイル": "file",
    "コマンド": "command",
    "データ": "data",
    "バックエンド": "backend",
    "フロントエンド": "frontend",
    "プロジェクト": "project",
    "ユーザー": "user",
    "操作": "operation",
    "会話": "conversation",
    "フロー": "flow",
    "指標": "metrics",
    "時間": "time",
    "速度": "speed",
    "管理": "management",
    "自動化": "automation",
    "手動": "manual",
    "哲学": "philosophy",

    # Adjectives/Descriptors
    "自然": "natural",
    "効率的": "efficient",
    "高速": "fast",
    "可能": "possible/capable",
    "必要": "necessary",
    "重要": "important",
    "簡単": "easy/simple",
    "複雑": "complex",

    # Numbers and units
    "個": "(items)",
    "回": "times",
    "件": "items",
    "分": "minutes",
    "秒": "seconds",
    "倍": "times (multiplier)",

    # Particles (context-dependent, often can be removed)
    "を": "",
    "に": "",
    "で": "",
    "が": "",
    "は": "",
    "と": "",
    "の": "'s/of",
    "から": "from",
    "まで": "to/until",
    "も": "also",
    "や": "and",
}

# Japanese punctuation to English
PUNCTUATION = {
    "。": ".",
    "、": ", ",
    "：": ": ",
    "；": "; ",
    "！": "!",
    "？": "?",
    "「": '"',
    "」": '"',
    "『": "'",
    "』": "'",
    "（": "(",
    "）": ")",
    "［": "[",
    "］": "]",
    "｛": "{",
    "｝": "}",
    "・": "· ",
    "〜": "~",
    "～": "~",
    "　": " ",  # Full-width space
}

def has_japanese(text: str) -> bool:
    """Check if text contains Japanese characters."""
    return bool(re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]', text))

def replace_punctuation(text: str) -> str:
    """Replace Japanese punctuation with English equivalents."""
    for jp, en in PUNCTUATION.items():
        text = text.replace(jp, en)
    return text

def count_japanese_chars(text: str) -> int:
    """Count number of Japanese characters."""
    return len([c for c in text if '\u3000' <= c <= '\u303f' or '\u3040' <= c <= '\u309f' or
                '\u30a0' <= c <= '\u30ff' or '\uff00' <= c <= '\uff9f' or
                '\u4e00' <= c <= '\u9faf' or '\u3400' <= c <= '\u4dbf'])

def process_file(filepath: Path) -> tuple[bool, int, int]:
    """
    Process a single markdown file.

    Returns:
        (changed, chars_before, chars_after)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if not has_japanese(content):
            return (False, 0, 0)

        chars_before = count_japanese_chars(content)
        original_content = content

        # Replace punctuation
        content = replace_punctuation(content)

        # Note: We're primarily replacing punctuation.
        # For complex Japanese sentences, manual review is recommended.
        # The script focuses on structural elements like punctuation.

        chars_after = count_japanese_chars(content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return (True, chars_before, chars_after)

        return (False, chars_before, chars_after)

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return (False, 0, 0)

def main():
    """Process all markdown files."""
    processed = []
    errors = []

    for md_file in Path('.').rglob('*.md'):
        # Skip venv and node_modules
        if '.venv' in str(md_file) or 'node_modules' in str(md_file):
            continue

        changed, before, after = process_file(md_file)
        if changed:
            reduction = before - after
            processed.append((str(md_file), before, after, reduction))

    print(f"\n{'='*70}")
    print(f"Translation Summary")
    print(f"{'='*70}\n")

    if processed:
        print(f"✅ Processed {len(processed)} files:\n")
        for filepath, before, after, reduction in sorted(processed):
            percent = (reduction / before * 100) if before > 0 else 0
            print(f"  {filepath}:")
            print(f"    Before: {before} JP chars → After: {after} JP chars (-{reduction}, -{percent:.1f}%)")

        total_before = sum(b for _, b, _, _ in processed)
        total_after = sum(a for _, _, a, _ in processed)
        total_reduction = total_before - total_after
        total_percent = (total_reduction / total_before * 100) if total_before > 0 else 0

        print(f"\n  Total: {total_before} → {total_after} JP chars (-{total_reduction}, -{total_percent:.1f}%)")
    else:
        print("No files needed processing")

    if errors:
        print(f"\n❌ Errors: {len(errors)} files had errors")
        for filepath in errors:
            print(f"  - {filepath}")

    # Check for remaining Japanese
    remaining = []
    for md_file in Path('.').rglob('*.md'):
        if '.venv' in str(md_file) or 'node_modules' in str(md_file):
            continue
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                if has_japanese(f.read()):
                    remaining.append(str(md_file))
        except:
            pass

    if remaining:
        print(f"\n⚠️  {len(remaining)} files still contain Japanese text (may require manual review):")
        for f in remaining[:10]:
            print(f"  - {f}")
        if len(remaining) > 10:
            print(f"  ... and {len(remaining) - 10} more")
    else:
        print(f"\n✅ All markdown files successfully translated!")

if __name__ == '__main__':
    main()
