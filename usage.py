from pathlib import Path
from urllib.request import urlretrieve

from process_recordings import export_teachings, export_final_files
from process_recordings.chunk_recordings import export_renamed_sessions

# modes:
# 1. Segmentation process: export individual sessions from the cassette sides + resegment sessions when needed
# 2. same as above, but for restored audio
# 3. export individual renamed sessions in New Archives
# 4. same as above, but for restored audio
mode = 4

if mode == 1:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=2035952658&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Original Files')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/Original Files in Sessions')
    cassette_side_to_resegment = 'AUDIO Khyentse Rinpoche WAV/176 A-Kyerim'  # folder required
    cassette_side_to_resegment = ''
    export_teachings(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

if mode == 2:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=2035952658&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Cleaned by Thubten')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/Cleaned by Thubten in Sessions')
    cassette_side_to_resegment = '111 A-Dzogchen Lamrim Yigdrupa'
    cassette_side_to_resegment = ''
    export_teachings(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

if mode == 3:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=2035952658&single=true&output=tsv'
    # test catalog
    #catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=1444985196&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Original Files')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/New Archives')
    cassette_side_to_resegment = 'AUDIO Khyentse Rinpoche WAV/176 A-Kyerim'  # folder required
    cassette_side_to_resegment = ''
    export_renamed_sessions(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

if mode == 4:
    # download from Google Drive
    catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=2035952658&single=true&output=tsv'
    # test catalog
    #catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=1444985196&single=true&output=tsv'
    filename = "input/audio $archives - sessions.tsv"
    urlretrieve(catalog_url, filename)

    audio_path = Path('/media/drupchen/Khyentse Önang/NAS/Cleaned by Thubten')
    out_path = Path('/media/drupchen/Khyentse Önang/NAS/New Archives_Restored')
    cassette_side_to_resegment = 'AUDIO Khyentse Rinpoche WAV/176 A-Kyerim'  # folder required
    cassette_side_to_resegment = ''
    export_renamed_sessions(Path(filename), audio_path, out_path, pass_missing=True, single_file=cassette_side_to_resegment)

