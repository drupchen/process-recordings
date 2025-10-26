#!/usr/bin/env python3
"""
Script to calculate total duration of media files in a folder and subfolders.
Supports video files (mp4, avi, mkv, mov, etc.) and audio files (mp3, wav, flac, etc.)
"""

import sys
from pathlib import Path

try:
    from mutagen import File as MutagenFile

    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("Warning: mutagen not installed. Audio files will be skipped.")
    print("Install with: pip install mutagen")


def get_audio_duration(file_path):
    """Get duration of audio file in seconds using mutagen."""
    if not MUTAGEN_AVAILABLE:
        return 0

    try:
        audio_file = MutagenFile(str(file_path))
        if audio_file is not None and hasattr(audio_file, 'info'):
            return audio_file.info.length or 0
    except Exception as e:
        print(f"Error reading audio {file_path}: {e}")
    return 0


def format_duration(seconds):
    """Convert seconds to human-readable format (HH:MM:SS)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def calculate_total_duration(folder_path, excluded_files, excluded_folders):
    """Calculate total duration of all media files in folder and subfolders."""

    # Define supported file extensions
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'}

    total_duration = 0
    file_count = 0
    skipped_files = []
    file_sizes = []

    folder_path = Path(folder_path)

    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    print(f"Scanning folder: {folder_path}")
    print("=" * 50)

    # Walk through all files in folder and subfolders
    for file_path in folder_path.rglob('*'):
        to_exclude = False

        if file_path.is_file():
            for e in excluded_folders:
                if e in file_path.parts:
                    to_exclude = True
                    break

            for ending in excluded_files:
                if str(file_path).endswith(ending):
                    to_exclude = True
                    break

        if not to_exclude and file_path.is_file():
            file_ext = file_path.suffix.lower()
            duration = 0

            # Check if it's an audio file
            if file_ext in audio_extensions:
                duration = get_audio_duration(file_path)

            # Add duration to total if we got a valid duration
            if duration > 0:
                total_duration += duration
                print(file_path.name, format_duration(duration))
                file_count += 1
            elif file_ext in audio_extensions:
                skipped_files.append(str(file_path))

    # Display results
    if skipped_files:
        print(f"\nSkipped files ({len(skipped_files)}):")
        for skipped in skipped_files:
            print(f"  - {skipped}")

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {file_count}")
    print(f"Total duration: {format_duration(total_duration)}")
    print(f"Total duration (seconds): {total_duration:.2f}")


def main():
    """Main function to run the script."""

    folder_path = '/media/drupchen/Khyentse Önang/NAS/Original Files in Sessions'
    folders = [
        'Desheg Kundu Ngondro',
        'Gyalsey Lhaglen-France',
        'Kyabje Dorjechang 3',
        'Lojong Don Dunma',
        'Semdon Rabsel Dronme',
        'Tsasum Drildrup',
        'Tsasum Osel Nyingthig-France',
        'Khyentse Rinpoche-France-3'
    ]
    exclude_files = ['_orig.wav', '_trans.wav', '.wma', '.mp3']
    exclude_folders = ['AUDIO Khyentse Rinpoche WAV']
    exclude_folders = []

    if not MUTAGEN_AVAILABLE:
        print("Error: Neither moviepy nor mutagen is installed.")
        print("Install required packages with:")
        print("  pip install moviepy mutagen")
        sys.exit(1)
    calculate_total_duration(folder_path, exclude_files, exclude_folders)
    #for f in folders:
    #    calculate_total_duration(folder_path+f, exclude_files, exclude_folders)


if __name__ == "__main__":
    main()