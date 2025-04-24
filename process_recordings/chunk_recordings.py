import csv
from datetime import time
from collections import defaultdict
from pathlib import Path
from shutil import copy

from pydub import AudioSegment


def parse_catalog(catalog):
    def to_milliseconds(tm):
        millis = int((tm.hour * 3600) + (tm.minute * 60) + tm.second) * 1000 + (tm.microsecond / 1000)
        return millis

    parsed = defaultdict(list)
    with open(catalog, newline='') as csvfile:
        rows = list(csv.reader(csvfile, delimiter='\t', quotechar='|'))
        legend, rows = rows[0], rows[1:]
        table = {l: n for n, l in enumerate(legend)}
        for r in rows:
            start = to_milliseconds(time.fromisoformat(r[table['start']]))
            duration = to_milliseconds(time.fromisoformat(r[table['duration']]))
            entry = {'start': start,
                     'duration': duration,
                     'filename': r[table['export filename']],
                     'filename_session': r[table['session filename']],
                     'session_title': r[table['session title']]
                     }
            parsed[r[table['recording filename']]].append(entry)
    return parsed


def export_sessions(catalog, audio_path, out_path, pass_missing=False, single_file=''):
    out_path.mkdir(exist_ok=True, parents=True)
    for audio_file, sessions in catalog.items():
        if single_file and audio_file != single_file:
            continue
        print(audio_file)
        af = audio_path / f'{audio_file}.mp3'
        if not af.is_file():
            if pass_missing:
                print('not parsing', af)
                continue
            else:
                raise FileExistsError(af)

        audio = AudioSegment.from_file(af)
        for s in sessions:
            print('\t', s['filename'])
            out_file = out_path / f'{s["filename"]}.mp3'
            session = audio[s['start']:s['start']+s['duration']]
            session.export(out_file, format="mp3")


def export_teachings(catalog, audio_path, out_path, pass_missing=False, single_file=''):
    catalog = parse_catalog(catalog)
    export_sessions(catalog, audio_path, out_path, pass_missing=pass_missing, single_file=single_file)


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
