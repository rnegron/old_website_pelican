#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Raúl Negrón'
SITENAME = 'Raúl Negrón\'s Website'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/Puerto_Rico'

DISPLAY_PAGES_ON_MENU = True


THEME = 'pelicanyan'
DIRECT_TEMPLATES = ('index', 'sitemap', 'robots')
ROBOTS_SAVE_AS = 'robots.txt'
SITEMAP_SAVE_AS = 'sitemap.xml'
DEFAULT_LANG = 'en'
DATE_FORMATS = { 'en': '%B %d, %Y', }
STATIC_PATHS = ['images', 'CNAME']
SITEDESCRIPTION = ''
TYPOGRIFY=True
PLUGINS = ["render_math"]

ARTICLE_URL = 'blog/{date:%Y}/{slug}'
# ARTICLE_LANG_URL = 'blog/{date:%Y}/{lang}/{slug}.html'
PAGE_URL = '{slug}.html'
CATEGORY_URL = '{slug}.html'
DRAFT_URL = 'drafts/{slug}'

ARTICLE_SAVE_AS = '{category}/{date:%Y}/{slug}/index.html'
# ARTICLE_LANG_SAVE_AS = '{category}/date:%Y}/{lang}/{slug}/index.html'
PAGE_SAVE_AS = '{slug}.html'
CATEGORY_SAVE_AS = '{slug}.html'
DRAFT_SAVE_AS = 'drafts/{slug}/index.html'

SUMMARY_MAX_LENGTH = 20

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
# LINKS = (('github', 'https://github.com/rnegron'),)

# Social widget
# SOCIAL = (('GitHub', 'https://github.com/rnegron'),
          # ('LinkedIn', 'https://www.linkedin.com/in/raulnegron/'),)

GITHUB_URL = 'https://github.com/rnegron'
DISQUS_SITENAME = "raulnegron"

RELATIVE_URLS = True
USE_FOLDER_AS_CATEGORY = False
DEFAULT_PAGINATION = False
