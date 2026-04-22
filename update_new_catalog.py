from collections import defaultdict
from pathlib import Path
from urllib.request import urlretrieve
import csv

from mutagen.mp3 import MP3

from tibetan_sort import TibetanSort

from process_recordings import parse_catalog, keep_sessions_with_export_name


def format_ms_to_HHMMSS(milliseconds):
    seconds = milliseconds / 1000
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if minutes < 10:
        minutes = "0{}".format(minutes)
    if seconds < 10:
        seconds = "0{}".format(seconds)
    return "{}:{}:{}".format(hours, minutes,seconds)


def create_sessions(catalog_sessions):
    sessions = {}
    for _, a in catalog_sessions.items():
        for _, b in a.items():
            for _, c in b:
                # file info
                status = c['session export status']
                prefix = status if status not in ['Synchronized', 'No Text', 'Others'] else ''
                if prefix:
                    folder = f"In Progress/{c['session export status']}/{c['export folder']}"
                else:
                    folder = f"{c['export folder']}"
                export_name = c['export filename']
                export_folder = c['export folder']
                # filter all empty entries
                if not export_name:
                    continue

                # meta info
                text_title = c['text title']
                author = c['author']

                if status not in ['Synchronized', 'Others', 'No Text']:
                    file_path = path_to_new_parsed_archives / 'In Progress' / status / export_folder / (export_name + '.mp3')
                else:
                    file_path = path_to_new_parsed_archives / export_folder / (export_name + '.mp3')
                audio = MP3(file_path)
                duration = audio.info.length * 1000
                duration = format_ms_to_HHMMSS(duration)
                location_in_text = c['starting from:']
                sound_notes = c['sound quality in the original']
                text_notes = c['text notes']
                original_notes = c['notes']
                cur_session = {
                    'status': status if status not in ['Synchronized'] else 'Done',
                    'folder': folder,
                    'duration': duration,
                    'export_name': export_name,
                    'text_title': text_title,
                    'author': author,
                    'location_in_text': location_in_text,
                    'sound_notes': sound_notes,
                    'text_notes': text_notes,
                    'original_notes': original_notes,
                }
                key = f'{export_folder}/{export_name}'
                if status not in sessions:
                    sessions[status] = {}
                if key not in sessions[status]:
                    sessions[status][key] = []
                sessions[status][key].append(cur_session)
    return sessions


def sort_n_format(sessions):
    sorted_sessions = defaultdict(list)
    for status, llist in sessions.items():
        keys = list(llist.keys())
        keys = TibetanSort().sort_list(keys)
        for k in keys:
            sorted_sessions[status].append(llist[k][0])

    # remove all folder names except first one
    for status, llist in sorted_sessions.items():
        for i, e in reversed(list(enumerate(llist))):
            if i - 1 >= 0 and e['folder'] == sorted_sessions[status][i - 1]['folder']:
                sorted_sessions[status][i]['folder'] = ''

    return sorted_sessions


def parse_new_archives(filename):
    existing_sessions = []
    with open(filename, newline='') as csvfile:
        cat = csv.DictReader(csvfile, delimiter='\t', quotechar='|')
        last_folder = ''
        for row in cat:
            folder = row['folder']
            if not last_folder:
                last_folder = folder
            if not folder and last_folder:
                folder = last_folder
            if folder and folder != last_folder:
                last_folder = folder

            name = row['export_name']
            cur = f'{folder}/{name}'
            existing_sessions.append(cur)
    return existing_sessions


def filter_existing_sessions(existing_sessions, new_sorted_sessions):
    only_new = defaultdict(list)
    for k in ['Synchronized', 'Need Help', 'Identified', 'Others']:
        for s in new_sorted_sessions[k]:
            cur_path = f"{s['folder']}/{s['export_name']}"
            #print()



# parse dashboard
catalog_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSGcAAMyJQYeR91n_9JF84BUpuMdHu4sxXBIrkLhEHCPe_F_rD_8YK9y6pzmCPK1adBPEQWzQ9Aynn4/pub?gid=2035952658&single=true&output=tsv'
filename = "input/audio $archives - sessions.tsv"
urlretrieve(catalog_url, filename)

path_to_new_parsed_archives = Path('/media/drupchen/Khyentse Önang/NAS/New Archives/MP3')

catalog, catalog_sessions = parse_catalog(filename, renamed_export=True)
catalog_sessions = keep_sessions_with_export_name(catalog_sessions)
sessions = create_sessions(catalog_sessions)
sorted_sessions = sort_n_format(sessions)

with open('new_archives.tsv', 'w', newline='') as csvfile:
    fieldnames = [
        'status',
        'folder',
        'export_name',
        'duration',
        'author',
        'location_in_text',
        'text_title',
        'text_notes',
        'original_notes',
        'sound_notes']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()
    for k in ['Synchronized', 'No Text', 'Others', 'Identified', 'Need Help', 'To Check']:
        for s in sorted_sessions[k]:
            writer.writerow(s)

# parse new archives
new_archives_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQKD99giqmFZFMMMsEGoXrGZSx6Z0GQfRAJKqNnBtGZ_-gm4Bo12ND4pg6hm2RhrVMpYPC4aFl6Gh2K/pub?gid=0&single=true&output=tsv'
filename_new = "input/new_archives.tsv"
urlretrieve(new_archives_url, filename_new)

new_parsed = parse_new_archives(filename_new)

#only_new = filter_existing_sessions(new_parsed, sorted_sessions)
print()


