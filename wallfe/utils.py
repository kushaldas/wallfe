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

def get_channel(channels, _id, _id_value):
    """ get the channel if it already exists
    :args channels: the list of dictionaries containing channel_info
    :args _id: the key for the filter
    :args _id_value: the value of the key
    """
    return filter(lambda x: _id in x.keys() and x[_id] in _id_value, channels)

def escape(data):
    """ escape the HTML in the content
    """
    return data.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")

def slugify(title):
    """ Slugify the feedlist title
    :arg title: the title of a feedlist
    """
    return '-'.join(title.lower().split())
