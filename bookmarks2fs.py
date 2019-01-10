import configparser
from pathlib import Path
import base64
from urllib.parse import urlparse

import bookmarks_parser

config = configparser.RawConfigParser()
config.optionxform = str


def create_bookmark(bookmark, folder_name):
    title = bookmark['title'].replace("/", "")
    if bookmark.get('icon'):
        img_data = bookmark['icon'].replace('data:image/png;base64,', '')
        domain_name = urlparse(bookmark['url']).hostname.replace('www.', '').split('.')[0]
        relative_path = Path("icons/{}.png".format(domain_name))
        if not relative_path.exists():
            with open(relative_path, "wb") as fh:
                fh.write(base64.decodebytes(img_data.encode()))
            path = Path.cwd() / relative_path
        else:
            path = Path.cwd() / domain_name
        config['Desktop Entry'] = {'Version': '1.0', 'Type': 'Link', 'Name': title, 'URL': bookmark['url'], 'Icon': path}
    else:
        config['Desktop Entry'] = {'Version': '1.0', 'Type': 'Link', 'Name': title, 'URL': bookmark['url']}
    with open('{}/{}.desktop'.format(folder_name, title), 'w') as configfile:
        config.write(configfile)


def title2path(child, prev=None):
    for bookmark in child:
        if bookmark.get('children'):
            if prev:
                bookmark['title'] = '{}/{}'.format(prev['title'], bookmark['title'])
            bookmark_folder_path = Path(bookmark['title'])
            if not bookmark_folder_path.exists():
                bookmark_folder_path.mkdir()
            if bookmark['children']:
                title2path(bookmark['children'], bookmark)
        elif bookmark['type'] == 'bookmark':
            create_bookmark(bookmark, prev['title'])


if __name__ == '__main__':
    bookmarks = bookmarks_parser.parse("example/chrome_bookmarks.html")
    p = Path('icons')
    if not p.exists():
        p.mkdir()
    title2path(bookmarks)
