#!/usr/bin/env python3
"""
Script to replace SRT subtitle content with lines from a text file.
Preserves empty lines for 1:1 mapping between TXT lines and SRT slots.
"""
from multiprocessing.queues import JoinableQueue

import srt
from pathlib import Path


def replace_srt_content(srt_file_path, txt_file_path, output_file_path):
    """Replace SRT subtitle content with lines from a text file."""

    # Read the SRT file
    with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
        subtitles = list(srt.parse(srt_file.read()))

    # Read the TXT file and split by lines
    with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
        txt_lines = txt_file.read().split('\n')

    # Handle text editor adding extra empty line at end
    if len(txt_lines) == len(subtitles) + 1 and txt_lines[-1].strip() == "":
        txt_lines = txt_lines[:-1]  # Remove the last empty line
        print("Removed trailing empty line added by text editor")

    print(srt_file_path)
    print(f"SRT slots: {len(subtitles)}, TXT lines: {len(txt_lines)}")

    # Check if line amounts match
    if len(subtitles) != len(txt_lines):
        print(f"ERROR: Line count mismatch!")
        print(f"SRT file has {len(subtitles)} subtitle slots")
        print(f"TXT file has {len(txt_lines)} lines")
        print("Both files must have the same number of lines/slots.")
        exit(1)

    # Replace subtitle content with text lines (1:1 mapping)
    for i, subtitle in enumerate(subtitles):
        content = txt_lines[i].strip()
        subtitle.content = content if content else "---"  # Use space for empty lines

    # Write the new SRT file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(srt.compose(subtitles))

    print(f"Created: {output_file_path}")


def main():
    mode = 1
    if mode == 1:
        # File paths - modify these according to your file locations
        in_path = Path('/media/drupchen/Khyentse Önang/K-Ö Archives/Pure Appearance')
        for f in in_path.rglob('*.srt'):
            print(f.name)
            txt = f.parent / (f.stem + '.txt')
            output_file_path = f
            replace_srt_content(f, txt, output_file_path)
            print()
    if mode == 2:
        in_path = Path('/media/drupchen/Khyentse Önang/K-Ö Archives/Initial Dilkhyen Transcriptions/Thokthabarsum')
        srt_file_path = in_path / "113 A-Dzogchen Lamrin Yeshey Drupa_improved.srt"
        txt_file_path = in_path / "113 A-Dzogchen Lamrin Yeshey Drupa.txt"
        output_file_path = srt_file_path

        replace_srt_content(srt_file_path, txt_file_path, output_file_path)


if __name__ == "__main__":
    main()
