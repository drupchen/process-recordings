from pathlib import Path
from urllib.request import urlretrieve

from process_recordings import export_teachings, export_final_files
from process_recordings.chunk_recordings import export_renamed_sessions

# modes:
# 1. Segmentation process: export individual sessions from the cassette sides + resegment sessions when needed
# 2. same as above, but for restored audio
# 3. export individual renamed sessions in corresponding folders
# 4. Alignment process: when everything is aligned, export final sessions + .srt files for hyperaudio with final filenames + tibetan session title
mode = 3

if mode == 1:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5UhciIy-L82-xPJJ5TmpNS-Hizae9ot_2fuvbl2cPQvuBwwRYfpYSSQkeSletINUeaq3UILKlP0gA/pub?gid=2043758745&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Original Files')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/Original Files in Sessions')
    cassette_side_to_resegment = 'AUDIO Khyentse Rinpoche WAV/176 A-Kyerim'  # folder required
    cassette_side_to_resegment = ''
    export_teachings(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

if mode == 2:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5UhciIy-L82-xPJJ5TmpNS-Hizae9ot_2fuvbl2cPQvuBwwRYfpYSSQkeSletINUeaq3UILKlP0gA/pub?gid=2043758745&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Cleaned by Thubten')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/Cleaned by Thubten in Sessions')
    cassette_side_to_resegment = '111 A-Dzogchen Lamrim Yigdrupa'
    cassette_side_to_resegment = ''
    export_teachings(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

if mode == 3:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5UhciIy-L82-xPJJ5TmpNS-Hizae9ot_2fuvbl2cPQvuBwwRYfpYSSQkeSletINUeaq3UILKlP0gA/pub?gid=2043758745&single=true&output=tsv'
    # test catalog
    #catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5UhciIy-L82-xPJJ5TmpNS-Hizae9ot_2fuvbl2cPQvuBwwRYfpYSSQkeSletINUeaq3UILKlP0gA/pub?gid=1920094530&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Test')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/New Archives')
    cassette_side_to_resegment = 'AUDIO Khyentse Rinpoche WAV/176 A-Kyerim'  # folder required
    cassette_side_to_resegment = ''
    export_renamed_sessions(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

elif mode == 4:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGZJWL9nTtAurpNBs3AVK7UHELhEW41I3t1u9NZHU8xDxPKHTz9Qml1W_jVJ4vpyQzZxDDLv6Q2pq2/pub?gid=708229619&single=true&output=tsv'
    filename = "input/tsiksum nedek catalog - final catalog.tsv"
    filename = ''
    urlretrieve(catalog_url, filename)

    mp3_path = 'output/tsiksum nedek/'
    srt_path = '/home/drupchen/Documents/Dilkhyen Transcriptions/TSIG SUM/Sessions/SRT'
    out_path = '/home/drupchen/Documents/Dilkhyen Transcriptions/TSIG SUM/Sessions/Final'
    export_final_files(Path(filename), mp3_path=mp3_path, srt_path=srt_path, out=out_path)
