#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Sayan Chowdhury <sayan.chowdhury2012@gmail.com>

 Distributed under License GPLv3 or later
 You can find a copy of this license on the website
 http://www.gnu.org/licenses/gpl.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 MA 02110-1301, USA.
"""

import flask
import feedparser
import hashlib
import json
import logging
import cPickle as pickle
from tinydb import TinyDB
from datetime import datetime

from .forms import AddFeedList
from .forms import AddFeedURL

#Create the application
APP = flask.Flask(__name__)
APP.secret_key = 'Random Key'

db = TinyDB('./wallfe/database/db.json')

@APP.route('/', methods=['GET', 'POST'])
def index():
    """ Display the index page
    """
    return flask.render_template(
            'index.html')

@APP.route('/add-list', methods=['GET', 'POST'])
def add_list():
    """ Add a Feed URL to list
    """
    form = AddFeedList()
    if form.validate():
        feedlist_name = form.feedlist_name.data
        return flask.redirect('/%s/add-feed' % feedlist_name.lower())
    return flask.render_template(
           'add_list.html',
           form=form)

@APP.route('/<listname>/add-feed', methods=['GET', 'POST'])
def add_feed(listname):
    """ Add a Feed URL
    :args listname: The name of the list
    """
    form = AddFeedURL()
    if form.validate():
        feedurl = form.feedurl.data
        update(listname, feedurl)
    return flask.render_template(
            'add_url.html',
            form=form)

def get_channel(channels, _id, _id_value):
    return filter(lambda x: _id in x.keys() and x[_id] in _id_value, channels)

def escape(data):
    return data.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")

def update(category, feedurl):
    """ update the feed to refresh the information
    :args category: name of the category
    :args feedurl: url of the feed
    """
    channel = feedparser.parse(feedurl)

    if 'status' in channel:
        url_status = str(channel.status)
    elif 'entries' in channel and len(channel.entries)>0:
        url_status = str(200)

    if url_status == '301' and ('entries' in channel and \
            len(channel.entries) > 0):
        feedurl = channel.url
    elif url_status == '304':
        return
    elif url_status == '408':
        return
    elif int(url_status) >= 400:
        return

    with open('wallfe/database/db.json') as outfile:
        planet = json.loads(outfile.read())

    if not planet:
        planet = {}

    if category in planet:
        channels = planet[category]
    else:
        planet[category] = []
        channels = planet[category]

    # RSS required channel elements
    channel_title = channel.feed.get('title', None)
    channel_link = channel.feed.get('link', None)
    channel_description = channel.feed.get('description', None)
    channel_etag = channel.feed.get('etag', None)
    channel_modified = channel.feed.get('modified', None)
    channel_entries = channel.get('entries', None)

    if not channel_link:
        return

    _id = hashlib.md5(channel_link).hexdigest()

    channel_item = get_channel(channels, 'id', _id)
    print channel_item

    if not channel_item:
        channel_item = {}
        channel_item['title'] = channel_title
        channel_item['link'] = channel_link
        channel_item['description'] = channel_description
        channel_item['etag'] = channel_etag
        channel_item['modified'] = channel_modified
        channel_item['id'] = _id

        channel_entries_items = []
    else:
        channel_item = channel_item[0]
        channel_entries_items = channel_item['entries']

    if channel_entries:
        for news in channel_entries:
            news_item = {}
            news_id = None
            # news id - unique id for each post
            if 'id' in news:
                news_id = news.id
            elif 'link' in news:
                news_id = news.link
            elif 'title' in news:
                news_id = news.title
            elif 'summary' in news:
                news_id = news.summary

            if not news_id:
                continue

            news_item['news_id'] = news_id

            for key in news.keys():
                if key.endswith('_detail'):
                    if 'name' in news[key] and news[key].name:
                        news_item['name'] = news[key].name
                    if 'email' in news[key] and news[key].email:
                        news_item['email'] = news[key].email
                    if 'language' in news[key] and news[key].language:
                        news_item['language'] = news[key].language
                elif key == 'source':
                    if 'value' in news[key]:
                        news_item['value'] = news[key].value
                    if 'url' in news[key]:
                        news_item['url'] = news[key].url
                elif key == 'content':
                    for item in news[key]:
                        if item.type == 'text/html':
                            news_item['value'] = item.value
                        if item.type == 'text/plain':
                            news_item['value'] = escape(item.value)
                elif isinstance(news[key], (str, unicode)):
                    try:
                        detail = key + '_detail'
                        if detail in news:
                            if 'type' in news[detail]:
                                if news[detail].type == 'text/html':
                                    news_item['value'] = news[key]
                                if news[detail].type == 'text/plain':
                                    news_item['value'] = escape(news[key])
                    except:
                        pass
            channel_entries_items.append(news_item)
        channel_item['entries'] = channel_entries_items

    planet[category].append(channel_item)

    with open('wallfe/database/db.json', 'w') as outfile:
        json.dump(planet, outfile)

    return None

@APP.route('/view-list', methods=['GET', 'POST'])
def view_list():
    """ View list of feed
    """
    feedlists = db.all()
    slugs = map(lambda x: x['slug'], feedlists)
    return flask.render_template(
            'view_list.html',
            slugs=slugs)

def parse_feed(feed_url):
    """ Parse the RSS Feed URL
    :arg url: the url of the feed to be parsed
    """
    feedlist = feedparser.parse(feed_url)
    feedlist_dict = {}
    feedlist_dict['slug'] = slugify(feedlist.feed.title)
    feedlist_dict['title'] = feedlist.feed.title
    feedlist_dict['count'] = len(feedlist.entries)

    entries = feedlist.entries
    for counter, entry in enumerate(entries):
        feedlist_dict[counter] = {}
        feedlist_dict[counter]['author'] = entry.author
        feedlist_dict[counter]['publisted'] = entry.published
        feedlist_dict[counter]['link'] = entry.link
        feedlist_dict[counter]['content'] = entry.content[0]
        feedlist_dict[counter]['summary'] = entry.summary
    feedlist_dict['updated_at'] = str(datetime.now())

    db.insert(feedlist_dict)

    return feedlist_dict

def slugify(title):
    """ Slugify the feedlist title
    :arg title: the title of a feedlist
    """
    return '-'.join(title.lower().split())
