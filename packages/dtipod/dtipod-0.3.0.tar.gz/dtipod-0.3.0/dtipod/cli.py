#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2025 Matthias Büchse.
#
# This file is part of dtipod.
#
# dtipod is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# dtipod is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with dtipod.
# If not, see <https://www.gnu.org/licenses/>.
from email.utils import formatdate, parsedate_to_datetime
import hashlib
from html import unescape
import logging
import os
import os.path
import pytz
import re
import shutil
import subprocess
from textwrap import TextWrapper

from bs4 import BeautifulSoup
import click
from lxml import etree

from . import sql


# TODO make _html_to_text faster!
# TODO find feed on the interwebs (try to steal this from AntennaPod)
# TODO find feed from ARD Audiothek
# TODO mark episode as favorite, manage favorites
# TODO activate/deactivate/delete feed
# TODO search (for starters, maybe in slug)
# TODO export favorites!!

logger = logging.getLogger(__name__)
wrapper = TextWrapper(width=97, initial_indent='', subsequent_indent='    | ')
NODEFAULT = object()

# locations inspired by castero (MIT license)
HOME = os.path.expanduser("~")
XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))
XDG_DATA_HOME = os.getenv("XDG_DATA_HOME", os.path.join(HOME, ".local", "share"))
CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "dti")
DATA_DIR = os.path.join(XDG_DATA_HOME, "dti")
# additional locations
RSS_FETCH_DIR = os.path.join(DATA_DIR, 'rss')
RSS_ARCHIVE_DIR = os.path.join(DATA_DIR, 'rss0')
PODCASTS_DIR = os.path.join(HOME, 'Podcasts')
EPISODES_DIR = os.path.join(PODCASTS_DIR, 'Episodes')
ARCHIVE_DIR = os.path.join(PODCASTS_DIR, 'Archive')
STATE_DIR = PODCASTS_DIR

FMT_EP_SHORT = "{hashid} | {pub_date:<10.10} | {feed[title]:<16.16} | {title:<56.56}"
FMT_EP_LONG = "{no:3} | {hashid} | {pub_date:<10.10}\n    | {feed[title]:<97.97}\n    | {title:<97.97}\n    | {description}\n    | => {html_url}"
FMT_FEED_SHORT = "{hashid} | {date:<10.10} | {dormant:<7.7} | {title:<56.56}"
FMT_FEED_SHORT_ACTIVE = "{hashid} | {date:<10.10} | {title:<56.56}"
FMT_FEED_LONG = "{no:3} | {hashid} | {date:<10.10} | {dormant:<7.7}\n{title}\n{description}"
FMT_FEED_LONG_ACTIVE = "{no:3} | {hashid} | {date:<10.10}\n    | {title}\n    | {description}\n    | => {html_url}"


NON_BREAKING_ELEMENTS = {
    'a', 'abbr', 'acronym', 'audio', 'b', 'bdi', 'bdo', 'big', 'button',
    'canvas', 'cite', 'code', 'data', 'datalist', 'del', 'dfn', 'em', 'embed', 'i', 'iframe',
    'img', 'input', 'ins', 'kbd', 'label', 'map', 'mark', 'meter', 'noscript', 'object', 'output',
    'picture', 'progress', 'q', 'ruby', 's', 'samp', 'script', 'select', 'slot', 'small', 'span',
    'strong', 'sub', 'sup', 'svg', 'template', 'textarea', 'time', 'u', 'tt', 'var', 'video', 'wbr',
}


def _html_to_text(markup, preserve_new_lines=True, strip_tags={'style', 'script', 'code'}):
    soup = BeautifulSoup(unescape(markup[:2048]), "html.parser")
    for element in soup.find_all():
        if element.name in strip_tags:
            element.extract()
            continue
        if not preserve_new_lines or element.name in NON_BREAKING_ELEMENTS:
            continue
        if element.name == 'br':
            element.append('\n')
            continue
        element.append('\n\n')
    return soup.get_text()


def _shorten_desc(d):
    if not d:
        return ''
    return _html_to_text(d)[:1024].strip()


def _connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, 'dtipod.db')
    return sql.connect(path)


def _plural(obj):
    if not isinstance(obj, int):
        obj = len(obj)
    return '' if obj == 1 else 's'


def _hashid(s):
    return hashlib.sha256(s.encode('utf-8')).digest().hex()[:8]


def _slugify(s, maxlen=55):
    s1 = s.lower().replace('&amp;', 'and').replace('-', ' ').replace(':', ' ').replace('.', ' ').replace('+', ' ')
    s2 = ''.join(c for c in s1 if c.isalnum() or c.isspace())
    words = s2.split()
    slug = '-'.join(words)
    while len(slug) > maxlen and len(words) > 1:
        slug = slug[:-len(words[-1]) - 1]
        del words[-1:]
    return slug


def _report_new_items(con, outputter=logger.info):
    new_items = sql.query_new_items(con)
    if not new_items:
        outputter("Inbox empty.")
        return
    outputter("Your inbox:")
    for item in new_items:
        outputter(f"- {item['hashid']}: [{item['discriminator']}] {item['title']}")
    outputter("Use command 'clear' to remove items from inbox. New feeds will be removed when updated; new episodes will be removed after download.")


def _my_wrap(
    text,
    max_lines=8,
    max_width=80,
    wrapp3r=TextWrapper(width=80, initial_indent='', subsequent_indent='')
):
    lines = wrapp3r.wrap(text)
    if len(lines) > max_lines:
        del lines[max_lines:]
        lines[-1] = lines[-1][:max_width - 4].rsplit(' ', 1)[0].rstrip() + " ..."
    return lines


def _report_new_items_long(con, fileobj=None):
    # this function is going to be obsolete soon, because we will have the 'Inbox' state file
    _output_markdown(_query_new_items(con), fileobj=fileobj)


def _query_new_items(con):
    # We used to do the following with a single query, but that didn't work too well.
    # For the new episodes, the limit has to be quite high, and we don't want that for
    # new feeds. Besides, setting the new flag is way more simple this way.
    episode_items_1 = sql.query_latest_per_feed(con, filter_=sql.FEED_NEW, limit=5)
    episode_items_2 = sql.query_latest_per_feed(con, filter_=sql.EP_NEW, limit=100)
    for episode_item in episode_items_1:
        episode_item['feed']['new'] = True
    for episode_item in episode_items_2:
        episode_item['new'] = True
    return episode_items_1 + episode_items_2


def _output_markdown(episode_items, feed_item=None, fileobj=None):
    # NOTE this is actually more like gmi than md
    # also, it will generate a first-level heading per feed, so potentially multiple
    # which is a bit unusual, to have multiple first-level headings
    current_feed = None
    for item in episode_items:
        feeditem = item.get('feed', feed_item)
        if feeditem['hashid'] != current_feed:
            if current_feed:
                print('\n', file=fileobj)
            current_feed = feeditem['hashid']
            new_str = "NEW: " if feeditem.get('new') else ""
            print(f"# {new_str}({feeditem['hashid']}) {feeditem['title']}", file=fileobj)
            if feeditem.get('description'):
                print("", file=fileobj)
                print('\n'.join(_my_wrap(feeditem['description'])), file=fileobj)
            if feeditem.get('html_url'):
                print(f"\n=> {feeditem['html_url']}", file=fileobj)
        print("", file=fileobj)
        new_str = "NEW: " if item.get('new') else ""
        print(f"## {new_str}({item['hashid']}) {item['title']}\n", file=fileobj)
        print('\n'.join(_my_wrap(item['description'])), file=fileobj)
        if item['html_url']:
            print(f"\n=> {item['html_url']}", file=fileobj)


def _write_state_file(name, episode_items, feed_item=None):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, name), 'w') as fileobj:
        _output_markdown(episode_items, feed_item=feed_item, fileobj=fileobj)


def _query_latest_grouped(con):
    episode_items = sql.query_latest_episodes(con, limit=33)
    return sorted(episode_items, key=lambda it: (it['feed']['build_date'], it['pub_date']), reverse=True)
    # return sql.query_latest_per_feed(con, limit=5)


def _write_inbox_file(con):
    # capitalize Inbox/Latest so they are sorted in front of all the other state files,
    # and completion is unambiguous, too!
    _write_state_file('Inbox', _query_new_items(con))
    # this is not sorted by feed, so will look a bit strange, but I'll take it for the time being
    _write_state_file('Latest', _query_latest_grouped(con))


def _parse_opml(opml_path):
    # https://opml.org/spec2.opml
    tree = etree.parse(opml_path)
    body = tree.find('body')
    feed_items = []
    dormant = False
    for outline in body.iter('outline'):
        if 'dormant' in outline.attrib:
            dormant = outline.attrib['dormant'].lower() == 'true'
            continue
        type_ = outline.attrib.get('type', '').lower()
        if type_ == "link":
            logger.info(f"Skipping link: {outline.attrib.get('xmlUrl', '(?)')}")
            continue
        if type_ != "rss":
            logger.warning(f"Skipping unknown type: {type_}")
            continue
        xml_url = outline.attrib['xmlUrl']
        feed_items.append({
            'hashid': _hashid(xml_url),
            'slug': _slugify(outline.attrib['text']),
            'title': outline.attrib.get('title', outline.attrib['text']),
            'description': outline.attrib.get('description', ''),
            'dormant': dormant,
            'xml_url': xml_url,
            'html_url': outline.attrib.get('htmlUrl', ''),
        })
    return feed_items


def _write_opml(feed_items, opml_path):
    builder = etree.TreeBuilder()
    builder.start("opml", {"version": "2.0"})
    builder.start("head", {})
    builder.start("title", {})
    builder.data("dtipod feeds")
    builder.end("title")
    builder.start("dateCreated", {})
    builder.data(formatdate())
    builder.end("dateCreated")
    builder.end("head")
    builder.start("body", {})
    for dormant_value in (False, True):
        builder.start("outline", {
            "text": ["active", "dormant"][dormant_value],
            "dormant": str(dormant_value).lower(),
        })
        for feed_item in feed_items:
            if bool(feed_item.get("dormant")) != dormant_value:
                continue
            builder.start("outline", {
                "type": "rss",
                "text": feed_item['title'],
                "xmlUrl": feed_item['xml_url'],
                "htmlUrl": feed_item['html_url'],
            })
            builder.end("outline")
        builder.end("outline")
    builder.end("body")
    builder.end("opml")
    tree = etree.ElementTree(builder.close())
    etree.indent(tree)
    tree.write(opml_path, encoding='utf-8', xml_declaration=True)


def _download(episode_items, basedir=EPISODES_DIR):
    if not episode_items:
        logger.info("No episodes match.")
        return []
    logger.info(f"Downloading {len(episode_items)} episode{_plural(episode_items)}...")
    download_items = []
    for episode_item in episode_items:
        url = episode_item['enclosure']
        parts = url.split('?', 1)[0].rsplit('.', 1)
        ext = '' if len(parts) < 2 else parts[1]
        fn = f"{episode_item['slug']}-{episode_item['hashid']}.{ext}"
        episode_item['enclosure_path'] = os.path.join(basedir, fn)
        download_items.append((fn, url))
    _download_files(download_items, basedir=basedir, progress_meter=True)


def _download_rss(feed_items, basedir=RSS_FETCH_DIR):
    if not feed_items:
        logger.info("No feeds match.")
        return
    logger.info(f"Downloading {len(feed_items)} feed{_plural(feed_items)}...")
    download_items = []
    for feed_item in feed_items:
        fn = f"{feed_item['slug']}-{feed_item['hashid']}.rss"
        feed_item['rss_path'] = os.path.join(basedir, fn)
        download_items.append((fn, feed_item['xml_url']))
    _download_files(download_items, basedir=basedir)


def _download_files(download_items, basedir=None, progress_meter=False):
    if basedir is not None:
        os.makedirs(basedir, exist_ok=True)
    cmd = [shutil.which('curl'), '--parallel', '-L']
    if not progress_meter:
        cmd.append('--no-progress-meter')
    for fn, url in download_items:
        cmd.extend(['-o', fn, url])
    logger.debug(f"running {' '.join(cmd)}")
    subprocess.run(cmd, cwd=basedir)


def _split(episode_items, basedir=EPISODES_DIR, archive_dir=ARCHIVE_DIR):
    paths = [item['enclosure_path'] for item in episode_items]
    _split_files(paths, basedir, archive_dir)


def _split_downloads(basedir=EPISODES_DIR, archive_dir=ARCHIVE_DIR, partre=re.compile(r"p[0-9]{2,4}")):
    paths = []
    for fn in os.listdir(basedir):
        parts = fn.rsplit('.', 1)
        if len(parts) > 1 and parts[1] not in ('mp3', 'flac', 'ogg'):
            continue  # file not eligible for splitting
        partno = parts[0].rsplit('-', 1)[-1]
        if partre.match(partno):
            continue  # this is already split
        paths.append(fn)
    _split_files(paths, basedir=basedir)


def _split_files(paths, basedir='.', archive_dir=None):
    mp3splt = shutil.which('mp3splt')
    if not mp3splt:
        logger.error("Not splitting files: mp3splt not found.")
        return
    os.makedirs(archive_dir, exist_ok=True)
    for path in paths:
        cmd = [mp3splt, '-t', '15.00>10.00', '-a', '-o', '@f-p@n2', path]
        subprocess.run(cmd, cwd=basedir)
        if archive_dir is not None:
            os.rename(os.path.join(basedir, path), os.path.join(archive_dir, os.path.basename(path)))


# the following function adapted from castero, MIT License
# https://github.com/xgi/castero
# return value now is ISO format string
def _isodate_from_rfc822(date):
    """Convert a date string in RFC822 format into ISO format."""
    if date is None:
        return None
    try:
        return parsedate_to_datetime(date).replace(tzinfo=pytz.UTC).isoformat()
    except (TypeError, ValueError) as exc:
        logger.warning(f"couldn't convert 'date' to datetime: {exc!r}")
        return date  # hope that database can handle it


def _first_nonempty(el, tag, default=NODEFAULT):
    texts = [t for t in [
        subel.text.strip()
        for subel in el.findall(tag)
    ] if t]
    if texts:
        return texts[0]
    if default is NODEFAULT:
        raise ValueError(f'{el.tag} missing non-empty {tag}')
    return default


def _parse_rss(rss_path):
    root = etree.parse(rss_path).getroot()
    if root.tag != 'rss' or root.attrib.get('version') != '2.0':
        raise ValueError("feed is not RSS 2.0")
    channel = root.find('channel')
    if channel is None:
        raise ValueError("feed is missing channel")
    feed_title = _first_nonempty(channel, 'title')
    xml_url = None
    for link_el in channel.findall('{http://www.w3.org/2005/Atom}link'):
        if link_el.attrib.get('rel') == 'self':
            xml_url = link_el.attrib['href']
            break
    feed_item = {
        'hashid': None if xml_url is None else _hashid(xml_url),
        'xml_url': xml_url,
        'title': feed_title,
        'slug': _slugify(feed_title),
        'html_url': _first_nonempty(channel, 'link'),
        'description': _shorten_desc(_first_nonempty(channel, "description")),
        'build_date': _isodate_from_rfc822(_first_nonempty(channel, 'lastBuildDate', default=None)),
        'copyright': _first_nonempty(channel, 'copyright', default=None),
    }
    episode_items = []
    for item_el in channel.findall('item'):
        title = _first_nonempty(item_el, 'title', default=None)
        if title is None:
            logger.debug(f"skipping episode without title in feed {feed_title!r}")
            continue
        enclosure_el = item_el.find('enclosure')
        enclosure = None if enclosure_el is None else enclosure_el.attrib.get('url')
        if enclosure is None:
            logger.debug(f"skipping episode {title!r} without enclosure in feed {feed_title!r}")
            continue
        guid = _first_nonempty(item_el, 'guid', default=None)
        episode_items.append({
            'hashid': _hashid(guid or enclosure),
            'title': title,
            'slug': _slugify(title, maxlen=32),
            'pub_date': _isodate_from_rfc822(_first_nonempty(item_el, 'pubDate')),
            'html_url': _first_nonempty(item_el, 'link', default=''),
            'enclosure': enclosure,
            'description': _shorten_desc(_first_nonempty(item_el, 'description', default='')),
            'copyright': _first_nonempty(item_el, 'copyright', default=None),
        })
    # NOTE For many feeds, the build_date field is not beneficial, because it's just always today.
    # Therefore, put the date of the most recent episode instead!
    # Of course, that date could always be determined from the db with some clever SQL.
    # However, (a) I'm not clever, and (b) why waste cycles with overblown queries?
    pub_dates = [i['pub_date'] for i in episode_items if i['pub_date']]
    feed_item['build_date'] = max(pub_dates, default=feed_item['build_date'])
    return feed_item, episode_items


def _import_inner(con, fn, old_feed_item, feed_item, episode_items):
    old_hashid = old_feed_item.get('hashid')
    old_xml_url = old_feed_item.get('xml_url')
    if old_xml_url is None and feed_item['xml_url'] is None:
        raise RuntimeError("could not determine xml_url.")
    feed_item['dormant'] = old_feed_item.get('dormant', False)
    feed_item['new'] = old_feed_item.get('new', False)
    if feed_item['xml_url'] is None:
        logger.debug(f"feed RSS {fn} not providing xml_url")
        feed_item['xml_url'] = old_xml_url
        feed_item['hashid'] = old_hashid or _hashid(old_xml_url)
    if feed_item['hashid'] != old_hashid:
        old_id = f'{old_hashid} {old_xml_url}' if old_xml_url else f'({fn})'
        new_id = f"{feed_item['hashid']} {feed_item['xml_url']}"
        logger.info(f"Feed identity crisis; relocating:\n  old {old_id}\n  new {new_id}")
    for episode_item in episode_items:
        episode_item['feedid'] = feed_item['hashid']
    sql.update_feed(con, feed_item, episode_items, old_hashid=old_hashid)
    _write_state_file(f"{feed_item['slug']}_{feed_item['hashid']}.gmi", episode_items, feed_item=feed_item)


def _import_multiple(con, feed_items):
    logger.info(f"Importing {len(feed_items)} feed{_plural(feed_items)}...")
    imported = 0
    os.makedirs(RSS_ARCHIVE_DIR, exist_ok=True)
    for feed_item in feed_items:
        rss_path = feed_item['rss_path']
        fn = os.path.basename(rss_path)
        try:
            new_feed_item, episode_items = _parse_rss(rss_path)
            _import_inner(con, fn, feed_item, new_feed_item, episode_items)
        except Exception as e:
            logger.error(f"Failed to import {fn}: {e!r}")
            # os.rename(rss_path, os.path.join(RSS_ARCHIVE_DIR, fn + '.fail'))
        else:
            # move to archive so that it won't imported again (most relevant when hashid changed)
            os.rename(rss_path, os.path.join(RSS_ARCHIVE_DIR, fn))
            del feed_item['rss_path']
            imported += 1
    logger.info(f"Imported {imported} RSS file{_plural(imported)}.")


def _augment_from_db(con, feed_item):
    # fill in the blanks from the database, if possible
    extracted = feed_item['rss_path'].removesuffix('.rss').rsplit('-', 1)[-1]
    if len(extracted) != 8 or not extracted.isalnum():
        logger.info(f"importing external RSS: {feed_item['rss_path']}")
    else:
        feed_item.update(sql.query_feed(con, extracted))
    return feed_item  # argument is changed in-place; return for chaining


def _import_feeds(con):
    _import_multiple(con, [
        _augment_from_db(con, {'rss_path': os.path.join(RSS_FETCH_DIR, fn)})
        for fn in os.listdir(RSS_FETCH_DIR)
        if fn.endswith('.rss')
    ])


def _import_subscriptions(con, opml_path):
    """new-style OMPL import that validates data by fetching and parsing RSS files"""
    feed_items = _parse_opml(opml_path)
    # skip those that are already in the database
    sql.select_items(con, *[feed_item['hashid'] for feed_item in feed_items])
    extant = {
        fi['hashid']
        for fi in sql.query_feeds(con, restricted=True, active=False)
    }
    if extant:
        logger.info(f"Skipping {len(extant)} known feed{_plural(extant)}")
        feed_items[:] = [fi for fi in feed_items if fi['hashid'] not in extant]
    _download_rss(feed_items)
    _import_multiple(con, feed_items)


def _on_inbox_change(con):
    _report_new_items(con)
    _write_inbox_file(con)


# see https://click.palletsprojects.com/en/stable/#general-reference
@click.group()
def cli():
    pass


@cli.command
@click.argument('path', type=click.Path(exists=False, dir_okay=False))
def export(path):
    """export subscriptions; create OPML file at PATH"""
    con = _connect()
    feed_items = sql.query_latest_feeds(con, by_date=False)
    _write_opml(feed_items, path)


@cli.command(name='import')
@click.argument('path', type=click.Path(exists=True, dir_okay=False))
def import_subscriptions(path):
    """import RSS file or OPML file at PATH"""
    con = _connect()
    if path.endswith('.rss'):
        _import_multiple(con, [_augment_from_db(con, {'rss_path': path})])
    else:
        _import_subscriptions(con, path)
    _on_inbox_change(con)


@cli.command()
@click.argument('url', type=str, nargs=-1)
def import_url(url):
    """import RSS file from URL"""
    con = _connect()
    feed_items = []
    for i, s in enumerate(url):
        if not s.startswith('http://') and not s.startswith('https://'):
            logger.error(f"Not an URL: {s}")
            continue
        feed_items.append({
            'hashid': _hashid(s),
            'slug': str(i),
            'xml_url': s,
        })
    if not feed_items:
        logger.info("Nothing to be done.")
        return
    _download_rss(feed_items)
    _import_multiple(con, feed_items)
    _on_inbox_change(con)


@cli.command()
@click.argument('hashid', type=str, nargs=-1)
def fetch(hashid):
    """fetch RSS, either for all active feeds OR for those given via HASHID"""
    con = _connect()
    sql.select_items(con, *hashid)
    feed_items = sql.query_feeds(con, restricted=bool(hashid), active=not hashid)
    _download_rss(feed_items)


@cli.command()
def parse():
    """parse and import previously fetched feeds"""
    con = _connect()
    _import_feeds(con)
    _on_inbox_change(con)


@cli.command()
@click.argument('hashid', type=str, nargs=-1)
def update(hashid):
    """fetch and import RSS, either for all active feeds OR for those given via HASHID"""
    con = _connect()
    sql.select_items(con, *hashid)
    feed_items = sql.query_feeds(con, restricted=bool(hashid), active=not hashid)
    _download_rss(feed_items)
    _import_multiple(con, feed_items)
    _on_inbox_change(con)


@cli.command()
def inbox():
    """show new items (inbox)"""
    con = _connect()
    _report_new_items_long(con)


@cli.command()
@click.option('--active/--dormant', help="only show active feeds", is_flag=True, default=True)
def list(active):
    """list (latest) episodes, either for all feeds OR for those given via HASHID"""
    con = _connect()
    current_feed, num_feeds = None, 0
    episode_items = sql.query_latest_per_feed(con, active=active)
    for item in episode_items:
        if item['feed']['hashid'] != current_feed:
            current_feed = item['feed']['hashid']
            num_feeds += 1
            print(f"{num_feeds:3} | {item['feed']['hashid']} | {item['feed']['title']}")
        print(f"    | {item['hashid']} | {item['pub_date'][:10]} | {item['title']}")


@cli.command()
@click.argument('hashid', type=str, nargs=-1)
@click.option('--long', help="show descriptions", is_flag=True)
def episodes(long, hashid):
    """list (latest) episodes, either for all feeds OR for those given via HASHID"""
    fmt_str = FMT_EP_LONG if long else FMT_EP_SHORT
    con = _connect()
    sql.select_items(con, *hashid)
    episode_items = sql.query_latest_episodes(con, filter_=sql.FEED_SELECTION if hashid else None)
    for no, item in enumerate(episode_items):
        item['no'] = no + 1
        item['description'] = '\n'.join(wrapper.wrap(item['description'])[:3])
        print(fmt_str.format(**item))


@cli.command
@click.option('--active/--dormant', help="only show active feeds", is_flag=True, default=True)
@click.option('--long', help="show descriptions", is_flag=True)
def feeds(active, long):
    """list (most recently updated) feeds"""
    DOR = {True: "dormant", False: "active"}
    fmt_str = [
        [FMT_FEED_SHORT, FMT_FEED_SHORT_ACTIVE], [FMT_FEED_LONG, FMT_FEED_LONG_ACTIVE],
    ][min(long, 1)][min(active, 1)]
    con = _connect()
    feed_items = sql.query_feeds(con, active=active, by_date=True)
    for no, item in enumerate(feed_items):
        item['no'] = no + 1
        item['dormant'] = DOR[item['dormant']]
        item['description'] = '\n'.join(wrapper.wrap(item['description'])[:3])
        print(fmt_str.format(**item))


@cli.command()
@click.option('--split/--no-split', help="split downloaded episodes", is_flag=True, default=True)
@click.argument('hashid', type=str, nargs=-1)
def download(split, hashid):
    """download either all new episodes OR those given via HASHID"""
    con = _connect()
    sql.select_items(con, *hashid)
    episode_items = sql.query_episodes(con, filter_=sql.EP_SELECTION if hashid else sql.EP_NEW)
    _download(episode_items)
    if split:
        _split(episode_items)
    sql.clear_new_items(con, restricted=bool(hashid))
    _on_inbox_change(con)


@cli.command()
def split():
    """split downloaded episodes"""
    _split_downloads()


@cli.command()
@click.argument('hashid', type=str, nargs=-1)
def clear(hashid):
    """remove items from inbox (remove 'new flag'), either all or those given via HASHID"""
    con = _connect()
    sql.select_items(con, *hashid)
    sql.clear_new_items(con, restricted=bool(hashid))
    _on_inbox_change(con)


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    cli()


if __name__ == "__main__":
    main()
