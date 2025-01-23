from pathlib import Path

from process_recordings import export_teachings

catalog = Path('input/lama yangtik catalog - final catalog.tsv')
audio_path = Path('input/mp3/')
out_path = Path('output/lama yangtik')
export_teachings(catalog, audio_path, out_path, pass_missing=True)
