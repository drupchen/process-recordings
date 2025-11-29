import csv
from datetime import time
from collections import defaultdict
from pathlib import Path
from shutil import copy
import concurrent.futures
from functools import partial

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

errors = []


def parse_catalog(catalog, renamed_export=False):
    def to_milliseconds(tm):
        millis = int((tm.hour * 3600) + (tm.minute * 60) + tm.second) * 1000 + (tm.microsecond / 1000)
        return millis

    parsed = defaultdict(list)
    # initial parse + reformat timecodes to ms
    with open(catalog, newline='') as csvfile:
        cat = csv.DictReader(csvfile, delimiter='\t', quotechar='|')
        for row in cat:
            file = row['filename'][:row['filename'].rfind('.')]
            file = f"{row['Folder']}/{file}"
            if row['start']:
                row['start'] = to_milliseconds(time.fromisoformat(row['start']))
            else:
                row['start'] = None
            if row['end']:
                row['end'] = to_milliseconds(time.fromisoformat(row['end']))
            else:
                row['end'] = None
            if row['duration']:
                row['duration'] = to_milliseconds(time.fromisoformat(row['duration']))
            else:
                row['duration'] = None
            parsed[file].append(row)

    # group in teaching sessions
    def is_processed(parts):
        for p in parts:
            if p[S]:
                return True
            if p[S_T]:
                return True
        return False

    processed_in_sessions = {}
    S, S_T = 'session number', 'translation session number'
    for filename, parts in parsed.items():
        # filter out all unprocessed files
        if not is_processed(parts):
            continue

        sessions = {}
        for p in parts:
            # 1. parse main teaching
            session, part = None, None
            if ',' in p[S]:
                session, part = p[S].split(',')
            else:
                session, part = p[S], '1'

            # filter all sessions that don't have session numbers
            if session:
                # create scaffolding
                if session not in sessions:
                    sessions[session] = []

                sessions[session].append((part, p))

            # 2. parse translation
            session_trans, part_trans = None, None
            if ',' in p[S_T]:
                session_trans, part_trans = p[S_T].split(',')
            else:
                session_trans, part_trans = p[S_T], '1'

            # filter all sessions that don't have translation number
            if session_trans:
                session_trans += '_trans'
                if session_trans not in sessions:
                    sessions[session_trans] = []

                sessions[session_trans].append((part_trans, p))

            # add sessions that have renamed export names even if they have no numbers
            if renamed_export and not p[S] and not p[S_T] and p['export filename']:
                # create scaffolding
                session = '1'
                if session not in sessions:
                    sessions[session] = []
                sessions[session].append((session, p))
        processed_in_sessions[filename] = sessions

    return parsed, processed_in_sessions


def gen_outpaths(audio_file, s_name, s, out_path, final_filename):
    ext = s[0][1]['filename'][s[0][1]['filename'].rfind('.') + 1:]
    if final_filename:
        filename = f"{s[0][1]['export filename']}.{ext}"
        status = s[0][1]['session export status']
        status = status if status != 'Synchronized' else None
        if status:
            out_file = out_path / Path('In Progress') / Path(status) / Path(s[0][1]['export folder']) / filename
            out_file_compressed = out_file.parent.parent.parent.parent / Path('mp3') / Path('In Progress') / Path(status) / out_file.parts[-2] / (out_file.stem + '.mp3')
        else:

            out_file = out_path / Path(s[0][1]['export folder']) / filename
            out_file_compressed = out_file.parent.parent / Path('mp3') / out_file.parts[-2] / (out_file.stem + '.mp3')
    else:
        filename = f'{audio_file}_{s_name}.{ext}'
        out_file = out_path / filename
        out_file = out_file.parent / audio_file[audio_file.rfind('/') + 1:] / (out_file.stem + ".wav")
        out_file_compressed = out_file.with_suffix('.m4a')

    return out_file, out_file_compressed


def check_session_needs_export(audio_file, s_name, s, out_path, final_filename):
    """Check if a session needs to be exported without loading audio"""
    # Prepare output paths
    out_file, out_file_m4a = gen_outpaths(audio_file, s_name, s, out_path, final_filename)

    # Return True if either file is missing
    return not (out_file.is_file() and out_file_m4a.is_file())


def load_audio_file(audio_path, folder, filename, pass_missing):
    """Load audio file with error handling"""
    af = audio_path / folder / filename

    if not af.is_file():
        if pass_missing:
            return None, f'File missing: {af}'
        else:
            raise FileExistsError(af)

    try:
        audio = AudioSegment.from_file(af)
        return audio, None
    except CouldntDecodeError:
        # Handle MS_ADPCM files
        new_af = af.parent / (af.stem + '_pcm16' + af.suffix)
        if not new_af.is_file():
            import soundfile as sf
            data, samplerate = sf.read(af)
            sf.write(new_af, data, samplerate, format='wav', subtype='PCM_16')
        audio = AudioSegment.from_file(new_af)
        return audio, None


def export_single_session(task, audio_cache):
    """Export a single session"""
    audio_file, s_name, s, out_path, final_filename = task

    if audio_file not in audio_cache:
        return f"Skipped {audio_file} - audio not loaded"

    audio = audio_cache[audio_file]

    # Prepare output paths
    out_file, out_file_compressed = gen_outpaths(audio_file, s_name, s, out_path, final_filename)

    # Build session audio
    session_audio = AudioSegment.empty()
    for part_num, part in s:
        start, duration = part['start'], part['duration']
        if not duration:
            errors.append(f"Error: Missing timecodes for {out_file.name}")
            return f"Error: Missing timecodes for {out_file.name}"
        audio_part = audio[start:start + duration]
        session_audio += audio_part

    # Export both formats
    try:
        if not out_file.is_file():
            out_file.parent.mkdir(parents=True, exist_ok=True)
            session_audio.export(out_file, format="wav")
        if not out_file_compressed.is_file():
            out_file_compressed.parent.mkdir(parents=True, exist_ok=True)
            if 'm4a' in out_file_compressed.suffix:
                session_audio.export(out_file_compressed, format="ipod",
                                     bitrate="256k",
                                     parameters=["-q:a", "2"])
            elif 'mp3' in out_file_compressed.suffix:
                session_audio.export(out_file_compressed, format="mp3")
        return f"Exported: {out_file.stem}"
    except Exception as e:
        errors.append(f"Error exporting {out_file.name}: {str(e)}")
        return f"Error exporting {out_file.name}: {str(e)}"


def process_batch(batch_info, audio_path, out_path, pass_missing, final_filename, max_workers):
    """Process a batch of audio files"""
    batch_catalog, batch_num, total_batches = batch_info

    print(f"\n{'=' * 60}")
    print(f"Processing batch {batch_num}/{total_batches} ({len(batch_catalog)} audio files)")
    print(f"{'=' * 60}")

    # Step 1: Check which files actually need processing
    print("\nChecking which sessions need export...")
    audio_files_needed = set()
    pending_tasks = []
    skipped_count = 0

    for audio_file, sessions in batch_catalog.items():
        needs_export = False

        for s_name, s in sessions.items():
            if check_session_needs_export(audio_file, s_name, s, out_path, final_filename):
                needs_export = True
                pending_tasks.append((audio_file, s_name, s, out_path, final_filename))

        if needs_export:
            audio_files_needed.add(audio_file)
        else:
            skipped_count += 1

    print(f"  - Files that need processing: {len(audio_files_needed)}")
    print(f"  - Files already complete: {skipped_count}")
    print(f"  - Sessions to export: {len(pending_tasks)}")

    if not audio_files_needed:
        print("\nAll files in this batch are already exported!")
        return 0

    # Step 2: Get audio file info only for files that need processing
    audio_info = {}
    for audio_file in audio_files_needed:
        sessions = batch_catalog[audio_file]
        if '0' in sessions:
            folder = sessions['0'][0][1]['Folder']
            filename = sessions['0'][0][1]['filename']
        elif '1' in sessions:
            folder = sessions['1'][0][1]['Folder']
            filename = sessions['1'][0][1]['filename']
        else:
            continue
        audio_info[audio_file] = (folder, filename)

    # Step 3: Load only the audio files we need
    audio_cache = {}
    print(f"\nLoading {len(audio_info)} audio files that need processing...")

    for audio_file, (folder, filename) in audio_info.items():
        audio, error = load_audio_file(audio_path, folder, filename, pass_missing)
        if audio is not None:
            audio_cache[audio_file] = audio
            print(f"  ✓ Loaded: {folder}/{filename}")
        elif error:
            print(f"  ✗ {error}")
            errors.append(f"  ✗ {error}")

    # Step 4: Process exports in parallel
    if pending_tasks:
        # Filter tasks to only include those with loaded audio
        valid_tasks = [task for task in pending_tasks if task[0] in audio_cache]

        print(f"\nExporting {len(valid_tasks)} sessions using {max_workers} workers...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            export_func = partial(export_single_session, audio_cache=audio_cache)

            # Submit all tasks
            future_to_task = {executor.submit(export_func, task): task for task in valid_tasks}

            completed = 0
            successful = 0
            for future in concurrent.futures.as_completed(future_to_task):
                completed += 1
                result = future.result()
                if result and not result.startswith("Skipped"):
                    print(f"  [{completed}/{len(valid_tasks)}] {result}")
                    if result.startswith("Exported"):
                        successful += 1

        print(f"\nBatch complete: {successful} files exported")

    # Clear memory
    audio_cache.clear()
    return len(valid_tasks) if 'valid_tasks' in locals() else 0


def export_sessions(catalog, audio_path, out_path, pass_missing=False, single_file='',
                    final_filename=False, batch_size=10, max_workers=4):
    """Export sessions processing files in batches with pre-checking"""
    out_path.mkdir(exist_ok=True, parents=True)

    # Filter catalog if single_file is specified
    if single_file:
        catalog = {k: v for k, v in catalog.items() if k == single_file}

    # Quick scan to see how many files need processing
    print("Performing initial scan to check which files need export...")
    total_needs_export = 0
    total_already_complete = 0

    for audio_file, sessions in catalog.items():
        needs_export = False
        for s_name, s in sessions.items():
            if check_session_needs_export(audio_file, s_name, s, out_path, final_filename):
                needs_export = True
                break

        if needs_export:
            total_needs_export += 1
        else:
            total_already_complete += 1

    print(f"\nInitial scan complete:")
    print(f"  - Total audio files: {len(catalog)}")
    print(f"  - Files needing export: {total_needs_export}")
    print(f"  - Files already complete: {total_already_complete}")

    if total_needs_export == 0:
        print("\nAll files are already exported! Nothing to do.")
        return

    # Split catalog into batches
    catalog_items = list(catalog.items())
    batches = []

    for i in range(0, len(catalog_items), batch_size):
        batch = dict(catalog_items[i:i + batch_size])
        batches.append(batch)

    print(f"\nProcessing configuration:")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Number of batches: {len(batches)}")
    print(f"  - Parallel workers per batch: {max_workers}")

    # Process each batch
    total_exported = 0
    for batch_num, batch in enumerate(batches, 1):
        batch_info = (batch, batch_num, len(batches))
        exported = process_batch(batch_info, audio_path, out_path,
                                 pass_missing, final_filename, max_workers)
        total_exported += exported

    print(f"\n{'=' * 60}")
    print(f"All batches complete! Total sessions exported: {total_exported}")
    print(f"{'=' * 60}")

def export_final_sessions(catalog, audio_path, out_path, pass_missing=False, single_file='',
                    final_filename=False, batch_size=10, max_workers=4):
    """Export sessions processing files in batches with pre-checking"""
    out_path.mkdir(exist_ok=True, parents=True)

    # Filter catalog if single_file is specified
    if single_file:
        catalog = {k: v for k, v in catalog.items() if k == single_file}

    # Quick scan to see how many files need processing
    print("Performing initial scan to check which files need export...")
    total_needs_export = 0
    total_already_complete = 0

    for audio_file, sessions in catalog.items():
        needs_export = False
        for s_name, s in sessions.items():
            if check_session_needs_export(audio_file, s_name, s, out_path, final_filename):
                needs_export = True
                break

        if needs_export:
            total_needs_export += 1
        else:
            total_already_complete += 1

    print(f"\nInitial scan complete:")
    print(f"  - Total audio files: {len(catalog)}")
    print(f"  - Files needing export: {total_needs_export}")
    print(f"  - Files already complete: {total_already_complete}")

    if total_needs_export == 0:
        print("\nAll files are already exported! Nothing to do.")
        return

    # Split catalog into batches
    catalog_items = list(catalog.items())
    batches = []

    for i in range(0, len(catalog_items), batch_size):
        batch = dict(catalog_items[i:i + batch_size])
        batches.append(batch)

    print(f"\nProcessing configuration:")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Number of batches: {len(batches)}")
    print(f"  - Parallel workers per batch: {max_workers}")

    # Process each batch
    total_exported = 0
    for batch_num, batch in enumerate(batches, 1):
        batch_info = (batch, batch_num, len(batches))
        exported = process_batch(batch_info, audio_path, out_path,
                                 pass_missing, final_filename, max_workers)
        total_exported += exported

    print(f"\n{'=' * 60}")
    print(f"All batches complete! Total sessions exported: {total_exported}")
    print(f"{'=' * 60}")


def export_teachings(catalog, audio_path, out_path, pass_missing=False,
                     single_file='', batch_size=10, max_workers=10):
    """Main export function with pre-checking and configurable batch size"""
    catalog, catalog_sessions = parse_catalog(catalog)
    export_sessions(catalog_sessions, audio_path, out_path,
                    pass_missing=pass_missing,
                    single_file=single_file,
                    final_filename=False,
                    batch_size=batch_size,
                    max_workers=max_workers)
    print('-'*80)
    print('Errors:')
    for e in errors:
        print(e)
    print('-'*80)

def export_renamed_sessions(catalog, audio_path, out_path, pass_missing=False,
                     single_file='', batch_size=10, max_workers=10):
    """export final sessions processing files in batches with pre-checking"""
    catalog, catalog_sessions = parse_catalog(catalog, renamed_export=True)
    export_final_sessions(catalog_sessions, audio_path, out_path,
                    pass_missing=pass_missing,
                    single_file=single_file,
                    final_filename=True,
                    batch_size=batch_size,
                    max_workers=max_workers)
    print('-'*80)
    print('Errors:')
    for e in errors:
        print(e)
    print('-'*80)

def export_final_files(catalog_path, mp3_path, srt_path, out):
    catalog = parse_catalog(catalog_path)
    mp3, srt, out = Path(mp3_path), Path(srt_path), Path(out)
    for sessions in catalog.values():
        for s in sessions:
            new = s['filename_session']
            if new:
                orig = s['filename']
                mp3_orig = mp3 / (orig + '.mp3')
                mp3_new = out / (new + '.mp3')
                copy(mp3_orig, mp3_new)

                srt_orig = srt / (orig + '.srt')
                srt_new = out / (new + '.srt')
                copy(srt_orig, srt_new)

                title = out / (new + '.txt')
                title.write_text(s['session_title'])
