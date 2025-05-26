from pathlib import Path


def list_4_dashboard(in_path, out_path):
    in_path = Path(in_path)
    folders = list(in_path.rglob("*"))
    folders = [f for f in folders if f.is_file() and not f.name.startswith('.')]
    folders = sorted(folders)
    files = []
    for f in folders:
        parts = f.parts[-1], '/'.join(f.parts[9:-1])
        files.append(parts)

    out = '\n'.join(['\t'.join(f) for f in files])
    Path(out_path).write_text(out)

if __name__ == '__main__':
    in_path = '/run/user/1000/gvfs/dav:host=kytsodnangdsm.synology.me,port=5026,ssl=true/Archives/Audio Archives/Original Files/'
    out_path = 'output/file_list.tsv'
    list_4_dashboard(in_path, out_path)