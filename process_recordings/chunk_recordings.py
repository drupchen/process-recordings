import csv
from datetime import time
from collections import defaultdict
from pathlib import Path
from shutil import copy

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


def parse_catalog(catalog):
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

                if session_trans:
                    session_trans += '_trans'
                    if session_trans not in sessions:
                        sessions[session_trans] = []

                    sessions[session_trans].append((part_trans, p))
        processed_in_sessions[filename] = sessions

    return parsed, processed_in_sessions


def export_sessions(catalog, audio_path, out_path, pass_missing=False, single_file='', final_filename=False):
    out_path.mkdir(exist_ok=True, parents=True)
    for audio_file, sessions in catalog.items():
        if single_file and single_file != audio_file:
            continue

        if '0' in sessions:
            folder = sessions['0'][0][1]['Folder']
            filename = sessions['0'][0][1]['filename']
            af = audio_path / folder / filename
        elif '1' in sessions:
            folder = sessions['1'][0][1]['Folder']
            filename = sessions['1'][0][1]['filename']
            af = audio_path / folder / filename
        else:
            print('This should not happen. each session should either start with 0 or 1. Exiting')
            print(sessions)
            exit(0)
        if not af.is_file():
            if pass_missing:
                print('not parsing. file missing in input folder:', af)
                continue
            else:
                raise FileExistsError(af)

        print(f'"{folder}/{filename}"')

        audio = None
        for s_name, s in sessions.items():
            if final_filename:
                filename = s[0][1]['export filename']
            else:
                ext = s[0][1]['filename'][s[0][1]['filename'].rfind('.')+1:]
                filename = f'{audio_file}_{s_name}.{ext}'

            # out_folder = out_path / s[0][1]['Folder'] / audio_file
            # out_folder.mkdir(parents=True, exist_ok=True)
            out_file = out_path / filename
            # change extension to "wav" as export format is wav, even when input is mp3
            out_file = out_file.parent / audio_file[audio_file.rfind('/')+1:] / (out_file.stem + ".wav")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            if out_file.is_file():
               continue
            print('\t', out_file.name)

            if not audio:
                try:
                    audio = AudioSegment.from_file(af)
                except CouldntDecodeError:
                    # if WAV subtype is MS_ADPCM (from Windows 3.1), save it as PCM_16
                    # from https://stackoverflow.com/a/44813025
                    new_af = af.parent / (af.stem + '_pcm16' + af.suffix)
                    if not new_af.is_file():
                        import soundfile as sf
                        data, samplerate = sf.read(af)
                        new_af = af.parent / (af.stem + '_pcm16' + af.suffix)
                        sf.write(new_af, data, samplerate, format='wav', subtype='PCM_16')

                    audio = AudioSegment.from_file(new_af)
            session_audio = AudioSegment.empty()
            for part_num, part in s:
                start, duration = part['start'], part['duration']
                if not duration:
                    print("This file doesn't have timecodes. please retrieve them.")
                    print(part)
                    exit(1)
                audio_part = audio[start:start+duration]
                session_audio += audio_part
            session_audio.export(out_file, format="wav")

def export_teachings(catalog, audio_path, out_path, pass_missing=False, single_file=''):
    catalog, catalog_sessions = parse_catalog(catalog)
    export_sessions(catalog_sessions, audio_path, out_path, pass_missing=pass_missing, single_file=single_file)


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
