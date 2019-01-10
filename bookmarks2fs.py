import configparser
from pathlib import Path
import base64
from urllib.parse import urlparse

import bookmarks_parser


def get_bookmark_with_path(bookmarks):
    def title2path(child, prev=None):
        for bookmark in child:
            if bookmark.get('children'):
                if prev:
                    bookmark['title'] = '{}/{}'.format(prev['title'], bookmark['title'])
                if bookmark['children']:
                    title2path(bookmark['children'], bookmark)
    title2path(bookmarks)
    return bookmarks


def get_flat(bookmark_with_path):
    flat = {}

    def path2flat(bookmark_with_path):
        for bookmark in bookmark_with_path:
            if bookmark.get('children'):
                flat[bookmark['title']] = bookmark['children']
                if bookmark['children']:
                    path2flat(bookmark['children'])
    path2flat(bookmark_with_path)
    return flat


bookmarks = bookmarks_parser.parse("example/chrome_bookmarks.html")
bookmark_with_path = get_bookmark_with_path(bookmarks)
flat = get_flat(bookmark_with_path)

config = configparser.RawConfigParser()
config.optionxform = str

p = Path('icons')
if not p.exists():
    p.mkdir()

for i in flat:
    bookmark_folder_path = Path(i)
    if not bookmark_folder_path.exists():
        bookmark_folder_path.mkdir()
    for b in flat[i]:
        if b['type'] == 'bookmark':
            title = b['title'].replace("/", "")
            if b.get('icon'):
                img_data = b['icon'].replace('data:image/png;base64,', '')
                domain_name = urlparse(b['url']).hostname.replace('www.', '').split('.')[0]
                relative_path = Path("icons/{}.png".format(domain_name))
                if not relative_path.exists():
                    with open(relative_path, "wb") as fh:
                        fh.write(base64.decodebytes(img_data.encode()))
                    path = Path.cwd() / relative_path
                else:
                    path = Path.cwd() / domain_name
                config['Desktop Entry'] = {'Version': '1.0', 'Type': 'Link', 'Name': title, 'URL': b['url'], 'Icon': path}
            else:
                config['Desktop Entry'] = {'Version': '1.0', 'Type': 'Link', 'Name': title, 'URL': b['url']}
            with open('{}/{}.desktop'.format(i, title), 'w') as configfile:
                config.write(configfile)
