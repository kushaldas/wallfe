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

def update(listname, feedurl):
    """ update the feed to refresh the information
    """
    feed_info = feedparser.parse(feedurl)

    # RSS required channel elements
    feed_title = feed_info.get('title', None)
    feed_link = feed_info.get('link', None)
    feed_description = feed_info.get('description', None)
    feed_etag = feed_info.get('etag', None)
    feed_modified = feed_info.get('modified', None)

    feed_entries = feed_info.get('entries', None)

    list_feed = feedlist[listname]

    if feed_entries:
        for feed_entry in feed_entries:
            # entry id - unique id for each post
            if 'id' in feed_entry:
                entry_id = feed_entry.id
            elif 'link' in feed_entry:
                entry_id = feed_entry.link
            elif 'title' in feed_entry:
                entry_id = feed_entry.title
            elif 'summary' in feed_entry:
                entry_id = feed_entry.summary

            entryf['entry_id'] = entry_id

            for key in feed_entry.keys():
                if key.endswith('_detail'):
                    if 'name' in feed_entry[key] and entry[key].name:
                        entryf['name'] = feed_entry[key].name
                    if 'email' in feed_entry[key] and entry[key].email:
                        entryf['email'] = feed_entry[key].email
                    if 'language' in feed_entry[key] and entry[key].email:
                        entryf['language'] = feed_entry[key].language
                elif key == 'source':
                    if 'value' in feed_entry[key]:
                        entryf['value'] = feed_entry[key].value
                    if 'url' in feed_entry[key]:
                        entryf['url'] = feed_entry[key].url
                elif key == 'content':
                    for item in feed_entry[key]:
                        if item.type == 'text/html':
                            entryf['value'] = item.value
                        if item.type == 'text/plain':
                            entryf['value'] = escape(item.value)
                elif isinstance(feed_entry[key], (str, unicode)):
                    try:
                        detail = key + '_detail'
                        if detail in feed_entry:
                            if 'type' in feed_entry[detail]:
                                if feed_entry[detail].type == 'text/html':
                                    entryf['value'] = feed_entry[key]
                                if feed_entry[detail].type == 'text/plain':
                                    entryf['value'] = escape(feed_entry[key])
                    except:
                        pass

    return feed_info
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
