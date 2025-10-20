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
import os
import sqlite3


# see https://www.sqlite.org/lang.html
SCHEMA_VERSIONS = (
    # version 1
    '''
create table if not exists obj (
    hashid text primary key not null,
    discriminator text not null,
    new boolean not null default true,  -- NOTE this is dropped in v2
    added time not null,
    updated time default null,
    slug text not null,
    title text not null,
    description text not null,
    copyright text default null
);
create table if not exists feed (
    hashid text primary key references obj (hashid) on delete cascade,
    dormant boolean not null,
    build_date time default null,
    xml_url text not null,
    html_url text not null
);
create table if not exists episode (
    hashid text primary key references obj (hashid) on delete cascade,
    feedid text references feed (hashid) on delete cascade,
    listened boolean not null default false,  -- NOTE unused, could be dropped
    pub_date time,
    enclosure text not null,
    html_url text not null
);
PRAGMA user_version=1;
''',
    # version 2
    # column obj.new is considered obsolete, superseded by table new
    # this is quite tricky, though: sometimes we want to do natural joins, sometimes we want to do outer joins
    # outer joins can lead to ambiguous columns EXCEPT with the USING syntax, so we should be USING that :)
    '''
create table if not exists new (
    hashid text primary key references obj (hashid) on delete cascade
);
create table if not exists fav (
    hashid text primary key references obj (hashid) on delete cascade
);
insert or ignore into new (hashid)
select hashid from obj where obj.new;
-- the following is not idempotent because there is no "if exists" variant :(
alter table obj drop column new;
PRAGMA user_version=2;
''',
)


_SELECTION = f'selection_{os.getpid()}'
SQL_CREATE_SELECTION_TABLE = f'''
drop table if exists {_SELECTION};
create temp table {_SELECTION} (hashid text primary key);'''
SQL_INSERT_SELECTION = f'''
insert or ignore into {_SELECTION} values (?);'''
SQL_INSERT_NEW = f'''
insert or ignore into new values (?);'''
SQL_INSERT_FAV = f'''
insert or ignore into fav values (?);'''
SQL_UPDATE_FEED_OBJ = '''
insert into obj (hashid, discriminator, added, slug, title, description, copyright)
values (:hashid, 'feed', datetime('now'), :slug, :title, :description, :copyright)
on conflict (hashid) do
update set (updated, slug, title, description, copyright) = (datetime('now'), excluded.slug, excluded.title, excluded.description, excluded.copyright)
returning updated;'''
SQL_UPDATE_FEED = '''
insert into feed (hashid, dormant, build_date, html_url, xml_url) values (:hashid, :dormant, :build_date, :html_url, :xml_url)
on conflict (hashid) do
update set (dormant, build_date, html_url) = (excluded.dormant, excluded.build_date, excluded.html_url);'''
SQL_INSERT_OR_UPDATE_EPISODE_OBJ = '''
insert into obj (hashid, discriminator, added, slug, title, description, copyright)
values (:hashid, 'episode', datetime('now'), :slug, :title, :description, :copyright)
on conflict (hashid) do
update set (updated, slug, title, description, copyright) = (datetime('now'), excluded.slug, excluded.title, excluded.description, excluded.copyright)
returning updated;'''
SQL_INSERT_OR_UPDATE_EPISODE = '''
insert or replace into episode (hashid, feedid, pub_date, enclosure, html_url)
values (:hashid, :feedid, :pub_date, :enclosure, :html_url);'''
SQLT_QUERY_EPISODES = '''
select eo.hashid, slug, enclosure from obj eo natural join episode {join} {where};'''
SQL_QUERY_NEW = '''
select hashid, discriminator, title from obj natural join new order by slug;'''
SQLT_CLEAR_NEW = '''
delete from new {where};'''
SQLT_SET_DORMANT = '''
update feed set dormant = ? {where};'''
SQLT_QUERY_LATEST_FEEDS = '''
select feed.hashid, slug, title, dormant, added, updated, build_date, xml_url, html_url, new.hashid is not null, description
from feed natural join obj
left outer join new using (hashid)
{join}
{where}
{order};'''
SQLT_QUERY_LATEST = '''
select eo.hashid, eo.slug, eo.title, pub_date, feedid, fo.slug, fo.title, eo.description, episode.html_url, feed.build_date
from obj eo
natural join episode
join obj fo on fo.hashid = episode.feedid
  JOIN feed ON fo.hashid = feed.hashid
{join}
{where}
order by pub_date desc limit ?;'''
SQLT_JOIN_SELECTION = f'natural join {_SELECTION}'
SQLT_JOIN_SELECTION_FEEDID = f'join {_SELECTION} selection on feedid = selection.hashid'
SQLT_JOIN_EP_NEW = 'join new on new.hashid = eo.hashid'
SQLT_JOIN_FEED_NEW = 'JOIN new ON new.hashid = fo.hashid'
SQLT_WHERE_SELECTION = f'where hashid in (SELECT hashid FROM {_SELECTION})'
SQLT_WHERE_ACTIVE = 'where not dormant'
SQLT_WHERE_HASHID = 'where hashid = ?'
SQLT_ORDER_DATE = 'order by build_date desc'
SQLT_ORDER_SLUG = 'order by slug'

# I got the idea for this query from StackOverflow. It's quite weird, but I think I understand it:
# - the JOIN e2, GROUP BY, HAVING business mainly computes for each episode
#   the number of episodes that are not older, and restricts this to (placeholder);
# - this is in each case the episode itself, plus any that is newer
# - so we get the (placeholder) latest episodes!
# Quite ingenious! What I don't understand is how this query is so much faster than any alternative
# that I would come up with...
# Just for fun, here's the query plan
#
# QUERY PLAN
# |--SCAN e USING INDEX sqlite_autoindex_episode_1
# |--SEARCH fo USING INDEX sqlite_autoindex_obj_1 (hashid=?)
# |--SEARCH eo USING INDEX sqlite_autoindex_obj_1 (hashid=?)
# |--SEARCH feed USING INDEX sqlite_autoindex_feed_1 (hashid=?)
# |--SEARCH e2 USING AUTOMATIC COVERING INDEX (feedid=?)
# `--USE TEMP B-TREE FOR ORDER BY
SQLT_QUERY_LATEST_PER_FEED = '''
SELECT eo.hashid, eo.slug, eo.title, episode.pub_date, episode.feedid, fo.slug, fo.title, eo.description, episode.html_url, feed.build_date
  FROM episode
  JOIN obj eo ON episode.hashid = eo.hashid
  JOIN obj fo ON episode.feedid = fo.hashid
{join}
  JOIN feed ON fo.hashid = feed.hashid
  JOIN episode e2
    ON episode.feedid = e2.feedid AND episode.pub_date <= e2.pub_date
{where}
GROUP BY episode.hashid
HAVING COUNT(*) <= ?
ORDER BY feed.build_date desc, episode.pub_date desc;'''


EP_SELECTION = SQLT_JOIN_SELECTION
FEED_SELECTION = SQLT_JOIN_SELECTION_FEEDID
EP_NEW = SQLT_JOIN_EP_NEW
FEED_NEW = SQLT_JOIN_FEED_NEW


def connect(path):
    con = sqlite3.connect(path, autocommit=False)
    cur = con.cursor()
    with con:
        cur.executescript('''pragma foreign_keys=on;''')
    version = cur.execute("pragma user_version").fetchone()[0]
    while version < len(SCHEMA_VERSIONS):
        with con:
            cur.executescript(SCHEMA_VERSIONS[version])
        version += 1
    return con


def select_items(con, *hashids):
    con.executescript(SQL_CREATE_SELECTION_TABLE)
    con.executemany(SQL_INSERT_SELECTION, [(hashid, ) for hashid in hashids])


def query_new_items(con):
    rows = con.execute(SQL_QUERY_NEW).fetchall()
    return [{
        'hashid': row[0],
        'discriminator': row[1],
        'title': row[2],
    } for row in rows]


def query_episodes(con, filter_=None):
    rows = con.execute(SQLT_QUERY_EPISODES.format(
        join=filter_ or '', where='',
    )).fetchall()
    return [{
        'hashid': row[0],
        'slug': row[1],
        'enclosure': row[2],
    } for row in rows]


def _rows_to_feed_items(rows):
    return [{
        'hashid': row[0],
        'new': row[9],
        'slug': row[1],
        'title': row[2],
        'description': row[10],
        'dormant': row[3],
        'added': row[4],
        'updated': row[5],
        'date': row[6] or '',
        'xml_url': row[7],
        'html_url': row[8],
    } for row in rows]


def query_feeds(con, restricted=False, active=False, by_date=False):
    rows = con.execute(SQLT_QUERY_LATEST_FEEDS.format(
        join=SQLT_JOIN_SELECTION if restricted else '',
        where=SQLT_WHERE_ACTIVE if active else '',
        order=SQLT_ORDER_DATE if by_date else SQLT_ORDER_SLUG,
    )).fetchall()
    return _rows_to_feed_items(rows)


def query_feed(con, hashid):
    row = con.execute(SQLT_QUERY_LATEST_FEEDS.format(
        join='', where=SQLT_WHERE_HASHID, order='',
    ), (hashid, )).fetchone()
    if not row:
        return {}
    return _rows_to_feed_items((row, ))[0]


def update_feed(con, feed_item, episode_items, old_hashid=None):
    cur = con.cursor()
    with con:
        if old_hashid is not None and old_hashid != feed_item['hashid']:
            cur.execute(SQLT_CLEAR_NEW.format(where=SQLT_WHERE_HASHID), (old_hashid, ))
            cur.execute(SQLT_SET_DORMANT.format(where=SQLT_WHERE_HASHID), (True, old_hashid, ))
        cur.execute(SQL_UPDATE_FEED_OBJ, feed_item)
        # add new feed to inbox
        new_feed = cur.fetchone()[0] is None or feed_item.get('new', False)
        if new_feed:
            cur.execute(SQL_INSERT_NEW, (feed_item['hashid'], ))
        cur.execute(SQL_UPDATE_FEED, feed_item)
        for episode_item in episode_items:
            cur.execute(SQL_INSERT_OR_UPDATE_EPISODE_OBJ, episode_item)
            new_ep = cur.fetchone()[0] is None
            # add new items to inbox, except when the feed itself is new
            if new_ep and not new_feed:
                cur.execute(SQL_INSERT_NEW, (episode_item['hashid'], ))
            cur.execute(SQL_INSERT_OR_UPDATE_EPISODE, episode_item)


def clear_new_items(con, restricted=False):
    with con:
        con.execute(SQLT_CLEAR_NEW.format(
            where=SQLT_WHERE_SELECTION if restricted else '',
        ))


def _rows_to_ep_items(rows):
    return [{
        'hashid': row[0],
        'slug': row[1],
        'title': row[2],
        'description': row[7],
        'pub_date': row[3],
        'html_url': row[8],
        'feed': {
            'hashid': row[4],
            'slug': row[5],
            'title': row[6],
            'build_date': row[9],
        },
    } for row in rows]


def query_latest_episodes(con, filter_=None, limit=25):
    rows = con.execute(SQLT_QUERY_LATEST.format(
        join=filter_ or '', where='',
    ), (limit, )).fetchall()
    return _rows_to_ep_items(rows)


def query_latest_per_feed(con, active=False, filter_=None, limit=3):
    rows = con.execute(SQLT_QUERY_LATEST_PER_FEED.format(
        join=filter_ or '',
        where=SQLT_WHERE_ACTIVE if active else '',
    ), (limit, )).fetchall()
    return _rows_to_ep_items(rows)
