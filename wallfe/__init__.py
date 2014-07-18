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
from tinydb import TinyDB
from datetime import datetime

from .forms import AddFeedList

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
        feedlist_url = form.feedlist_url.data
        feedlist_dict = parse_feed(feedlist_url)
        return flask.redirect('/')
    return flask.render_template(
           'add_list.html',
           form=form)

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
