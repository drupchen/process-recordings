import csv
from datetime import time
from collections import defaultdict

from pydub import AudioSegment


def parse_catalog(catalog):
    def to_milliseconds(tm):
        millis = int((tm.hour * 3600) + (tm.minute * 60) + tm.second) * 1000 + (tm.microsecond / 1000)
        return millis

    parsed = defaultdict(list)
    with open(catalog, newline='') as csvfile:
        rows = list(csv.reader(csvfile, delimiter='\t', quotechar='|'))
        legend, rows = rows[0], rows[1:]
        for in_file, start, _, duration, _, filename, _, _ in rows:
            start = to_milliseconds(time.fromisoformat(start))
            duration = to_milliseconds(time.fromisoformat(duration))
            entry = {'start': start, 'duration': duration, 'filename': filename}
            parsed[in_file].append(entry)
    return parsed


def export_sessions(catalog, audio_path, out_path, pass_missing=False):
    out_path.mkdir(exist_ok=True, parents=True)
    for audio_file, sessions in catalog.items():
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


def export_teachings(catalog, audio_path, out_path, pass_missing=False):
    catalog = parse_catalog(catalog)
    export_sessions(catalog, audio_path, out_path)
