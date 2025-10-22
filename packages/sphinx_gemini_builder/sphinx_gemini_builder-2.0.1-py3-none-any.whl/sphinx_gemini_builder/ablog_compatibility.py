#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ablog compatibility
"""

import os
import logging

from feedgen.feed import FeedGenerator
from sphinx.locale import _
from sphinx.util.osutil import relative_uri
from docutils.utils import new_document
from docutils.io import StringOutput
from docutils import nodes

import ablog

from ablog.blog import Post, Blog, os_path_join, revise_pending_xrefs

logger = logging.getLogger(__name__)
text_type = str


class Page:
    """ Mini translator for gemini """

    def __init__(self, builder, docname: str) -> None:
        self.body = ''
        self.docname = docname
        self.builder = builder

    def add_title(self, text: str, level: int = 1) -> None:
        self.body += '#' * level
        self.body += ' ' + text + '\n'

    def add_item(self, text: str) -> None:
        self.body += '* %s\n' % text

    def add_link(self, uri: str, desc: str = None) -> None:
        self.body += '=> %s' % uri
        if desc:
            self.body += ' %s' % desc
        self.body += '\n'

    def add_raw(self, text: str) -> None:
        if text:
            self.body += text

    def end_block(self) -> None:
        self.body += '\n'

    def add_paragraph(self, text: str) -> None:
        self.body += text
        self.body += '\n\n'

    def write(self):
        path = os.path.join(self.builder.outdir, self.docname + self.builder.out_suffix)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(path, "w", encoding="utf-8") as out:
            out.write(self.body)


def to_gemini(builder, post, pagename: str, fulltext: bool = False):
    """
    Convert post to gemini format
    """
    doctree = new_document("")
    if fulltext:
        deepcopy = post.doctree.deepcopy()
        if isinstance(deepcopy, nodes.document):
            doctree.extend(deepcopy.children)
        else:
            doctree.append(deepcopy)
    else:
        for node in post.excerpt:
            doctree.append(node.deepcopy())
    revise_pending_xrefs(doctree, pagename)
    builder.env.resolve_references(doctree, pagename, builder)

    destination = StringOutput(encoding="utf-8")

    builder.secnumbers = {}
    builder.imgpath = relative_uri(builder.get_target_uri(pagename), "_images")
    builder.dlpath = relative_uri(builder.get_target_uri(pagename), "_downloads")
    builder.current_docname = pagename
    builder.writer.write(doctree, destination)
    builder.writer.assemble_parts()
    gemini = builder.writer.parts["whole"]
    return gemini


def add_post_to_page(builder, doc: Page, post) -> None:
    doc.add_title(post.title, 2)
    doc.add_link(
        builder.config.gemini_baseurl + post.docname + builder.out_suffix,
        _("Read post")
    )
    doc.end_block()
    if post.published:
        doc.add_item(_("Date: %s") % post.date.strftime(builder.config.post_date_format))
    else:
        doc.add_item(_("Draft"))

    if post.date != post.update:
        doc.add_item(_("Update: %s") % post.update.strftime(ablog.post_date_format))

    for author in post.author:
        doc.add_link(
            builder.config.gemini_baseurl + author.docname + builder.out_suffix,
            _("Author: %s" % str(author))
        )

    for location in post.location:
        doc.add_link(
            builder.config.gemini_baseurl + location.docname + builder.out_suffix,
            _("Location: %s" % str(location))
        )

    for language in post.language:
        doc.add_link(
            builder.config.gemini_baseurl + language.docname + builder.out_suffix,
            _("Language: %s" % str(language))
        )

    for category in post.category:
        doc.add_link(
            builder.config.gemini_baseurl + category.docname + builder.out_suffix,
            _("Category: %s" % str(category))
        )

    for tag in post.tags:
        doc.add_link(
            builder.config.gemini_baseurl + tag.docname + builder.out_suffix,
            _("Tag: %s" % str(tag))
        )

    doc.end_block()

    builder.footer_enabled = False
    builder.header_enabled = False
    doc.add_paragraph(to_gemini(builder, post, post.docname, fulltext=False))

    builder.footer_enabled = True
    builder.header_enabled = True


def generate_archive_pages(builder):
    """
    Generate archive pages for all posts, categories, tags, authors, and
    drafts (from ablog).
    """
    blog = Blog(builder.app)
    all_contexts = []
    for post in blog.posts:
        for redirect in post.redirect:
            doc = Page(builder, redirect)
            doc.add_title(post.title)
            doc.add_link(
                relative_uri(post.uri, redirect),
                _("Resource as been moved. Go here.")
            )
            doc.write()

    found_docs = builder.env.found_docs
    atom_feed = bool(builder.config.gemini_baseurl)
    feed_archives = blog.blog_feed_archives
    blog_path = blog.blog_path
    for title, header, catalog in [
        (_("Authors"), _("Posts by author"), blog.author),
        (_("Locations"), _("Posts from location"), blog.location),
        (_("Languages"), _("Posts in language"), blog.language),
        (_("Categories"), _("Posts in category"), blog.category),
        (_("All posts"), _("Posted in archive"), blog.archive),
        (_("Tags"), _("Posts tagged"), blog.tags),
    ]:

        if not catalog:
            continue

        context = {
            "atom_feed": False,
            "parents": [],
            "title": title,
            "header": header,
            "collection": catalog,
            "summary": True,
            "docname": catalog.docname,
        }
        if catalog.docname not in found_docs:
            all_contexts.append(context)

        for collection in catalog:

            if not collection:
                continue
            context = {
                "parents": [],
                "title": f"{header} {collection}",
                "header": header,
                "collection": collection,
                "summary": True,
                "feed_path": collection.path if feed_archives else blog_path,
                "atom_feed": atom_feed and feed_archives,
                "docname": collection.docname,
            }
            context["feed_title"] = context["title"]
            if collection.docname not in found_docs:
                all_contexts.append(context)

    context = {
        "parents": [],
        "title": _("All Posts"),
        "header": _("All"),
        "collection": blog.posts,
        "summary": True,
        "atom_feed": atom_feed,
        "feed_path": blog.blog_path,
        "docname": "blog/feeds",
    }
    all_contexts.append(context)

    context = {
        "parents": [],
        "atom_feed": False,
        "title": _("Drafts"),
        "collection": blog.drafts,
        "summary": True,
        "docname": "blog/drafts",
    }
    all_contexts.append(context)

    for context in all_contexts:
        collection = context["collection"]
        doc = Page(builder, context["docname"])
        doc.add_title(str(collection))
        if context["atom_feed"]:
            doc.add_link(
                builder.config.gemini_baseurl+collection.path+"/atom.xml",
                _("Atom feed")
            )

        doc.end_block()
        for subcoll in collection:
            if isinstance(subcoll, Post):
                add_post_to_page(builder, doc, subcoll)
                continue

            doc.add_title(str(subcoll), 2)
            doc.add_link(
                builder.get_target_uri(post.docname),
                _("Go to collection")
            )
            doc.end_block()
            for post in subcoll:
                doc.add_link(
                    builder.config.gemini_baseurl + post.docname + builder.out_suffix,
                    _("Read post")
                )

            doc.end_block()

        doc.add_raw(ablog_footer(builder))
        doc.add_paragraph(builder.config.gemini_footer)

        doc.write()


def generate_atom_feeds(builder):
    """
    Generate archive pages for all posts, categories, tags, authors, and
    drafts (from ablog).
    """
    builder.footer_enabled = False
    builder.header_enabled = False
    blog = Blog(builder.app)

    url = builder.config.gemini_baseurl
    if not url:
        return

    feed_path = os.path.join(builder.outdir, blog.blog_path, "atom.xml")

    feeds = [
        (
            blog.posts,
            blog.blog_path,
            feed_path,
            blog.blog_title,
            os_path_join(url, blog.blog_path, "atom.xml"),
        )
    ]

    if blog.blog_feed_archives:
        for header, catalog in [
            (_("Posts by author"), blog.author),
            (_("Posts from location"), blog.location),
            (_("Posts in language"), blog.language),
            (_("Posts in category"), blog.category),
            (_("Posted in archive"), blog.archive),
            (_("Posts tagged"), blog.tags),
        ]:

            for coll in catalog:
                # skip collections containing only drafts
                if not len(coll):
                    continue
                folder = os.path.join(builder.outdir, coll.path)
                if not os.path.isdir(folder):
                    os.makedirs(folder)

                feeds.append(
                    (
                        coll,
                        coll.path,
                        os.path.join(folder, "atom.xml"),
                        blog.blog_title + " - " + header + " " + text_type(coll),
                        os_path_join(url, coll.path, "atom.xml"),
                    )
                )

    # Config options
    feed_length = blog.blog_feed_length
    feed_fulltext = blog.blog_feed_fulltext

    for feed_posts, pagename, feed_path, feed_title, feed_url in feeds:

        feed = FeedGenerator()
        feed.id(builder.config.gemini_baseurl)
        feed.title(feed_title)
        feed.link(href=url)
        feed.subtitle(blog.blog_feed_subtitle)
        feed.link(href=feed_url)
        feed.language(builder.config.language)
        feed.generator("ABlog", ablog.__version__, "https://ablog.readthedocs.org")

        for i, post in enumerate(feed_posts):
            if feed_length and i == feed_length:
                break
            post_url = builder.get_target_uri(post.docname)

            if blog.blog_feed_titles:
                content = None
            else:
                content = to_gemini(builder, post, pagename, fulltext=feed_fulltext)

            feed_entry = feed.add_entry()
            feed_entry.id(post_url)
            feed_entry.title(post.title)
            feed_entry.link(href=post_url)
            feed_entry.author({"name": author.name for author in post.author})
            feed_entry.pubDate(post.date.astimezone())
            feed_entry.updated(post.update.astimezone())
            feed_entry.content(content=content, type="text/gemini")

        parent_dir = os.path.dirname(feed_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(feed_path, "w", encoding="utf-8") as out:
            feed_str = feed.atom_str(pretty=True)
            out.write(feed_str.decode())

    builder.footer_enabled = True
    builder.header_enabled = True

def ablog_header(builder) -> str:
    """ Generate header for Atom """
    header = ''
    blog = Blog(builder.app)
    if builder.current_docname in blog.posts:
        post = blog.posts[builder.current_docname]
        header = _('By %s') % ', '.join([str(author) for author in post.author]) + '\n'
        header += post.date.strftime(builder.config.post_date_format)
        header += '\n'

        if post.date != post.update:
            header += _('Updated on %s') % \
                post.update.strftime(builder.config.post_date_format)
            header += '\n'
        header += '\n'

    return header

def ablog_footer(builder) -> str:
    """ Generate footer for Atom """
    blog = Blog(builder.app)

    baseurl = builder.config.gemini_baseurl
    if not baseurl:
        return

    footer = '\n\n'
    footer += _('# Blog menu')
    footer += '\n'
    for title, catalog in [
        (_("Authors"), blog.author),
        (_("Locations"), blog.location),
        (_("Languages"), blog.language),
        (_("Categories"), blog.category),
    ]:
        footer += '## %s\n' % title
        footer += '=> %s %s\n' % (baseurl + catalog.docname + builder.out_suffix, _("All"))
        for coll in catalog:
            footer += '=> %s %s\n' % (baseurl + coll.docname + builder.out_suffix, str(coll))
        footer += '\n'

    footer += '## %s\n' % _("All posts")
    footer += '=> %s %s\n' % (baseurl + blog.archive.docname + builder.out_suffix, _("All posts"))
    footer += '\n'

    footer += '## %s\n' % _("Tags")
    footer += '=> %s %s\n' % (baseurl + blog.tags.docname + builder.out_suffix, _("Tags"))
    footer += '\n'

    return footer
