#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Writer for .gmi files
"""

from typing import cast, Iterable
import posixpath

from docutils import writers, nodes
from docutils.nodes import Element, Text, Node
from sphinx.util import logging
from sphinx.util.docutils import SphinxTranslator
from sphinx.util.osutil import relative_uri
from sphinx import addnodes
from sphinx.writers.text import Table, Cell
from sphinx.locale import __, admonitionlabels

logger = logging.getLogger(__name__)

if False:
    # For type annotation
    from . import GeminiBuilder

MAXWIDTH = 70


class GeminiWriter(writers.Writer):
    supported = ('gemini',)
    settings_spec = ('No options', '', ())
    settings_defaults = {}

    def __init__(self, builder: "GeminiBuilder") -> None:
        super().__init__()
        self.builder = builder

    def translate(self) -> None:
        visitor = self.builder.create_translator(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = cast(GeminiTranslator, visitor).body


class GeminiTranslator(SphinxTranslator):
    """
    Gemini Translator based on native TextTranslator
    """
    builder = None

    def __init__(self, document: nodes.document, builder: "GeminiBuilder") -> None:
        super().__init__(document, builder)
        self.sectionlevel = 0
        self.first_param = 0
        self.list_counter = []
        self.table = None
        self.cell_text = []
        self.after_table = []
        self.pre = False
        self.body = ''

    def add_text(self, text: str) -> None:
        if self.table:
            if len(self.cell_text):
                self.cell_text[-1] += text or ''
            else:
                self.cell_text.append(text)
        elif text:
            self.body += text

    def add_link(self, url: str, label: str = '') -> None:
        self.body += '=> %s %s' % (url, label)

    def add_quote(self, quote: str) -> None:
        self.body += '> %s' % quote

    def add_item(self, item: str) -> None:
        self.body += '* %s' % item

    def add_title(self, title: str) -> None:
        self.body += '#' * self.sectionlevel + ' ' + title

    def end_block(self) -> None:
        self.body += '\n'

    def disable_pre(self) -> None:
        if self.pre:
            self.body += '\n```\n'
            self.pre = False

    def enable_pre(self) -> None:
        if not self.pre:
            self.body += '\n```\n'
            self.pre = True

    def visit_document(self, node: Element) -> None:
        if 'ablog' in self.builder.config.extensions and self.builder.header_enabled:
            from .ablog_compatibility import ablog_header
            self.add_text(ablog_header(self.builder))

    def depart_document(self, node: Element) -> None:
        if not self.builder.footer_enabled:
            return

        if 'ablog' in self.builder.config.extensions:
            from .ablog_compatibility import ablog_footer
            self.add_text(ablog_footer(self.builder))
        if self.builder.add_footer:
            self.add_text(self.config.gemini_footer)

    def visit_section(self, node: Element) -> None:
        self.sectionlevel += 1

    def depart_section(self, node: Element) -> None:
        self.sectionlevel -= 1

    def visit_topic(self, node: Element) -> None:
        pass

    def depart_topic(self, node: Element) -> None:
        pass

    visit_sidebar = visit_topic
    depart_sidebar = depart_topic

    def visit_rubric(self, node: Element) -> None:
        self.add_text('-[ ')

    def depart_rubric(self, node: Element) -> None:
        self.add_text(' ]-')
        self.end_block()

    def visit_compound(self, node: Element) -> None:
        pass

    def depart_compound(self, node: Element) -> None:
        pass

    def visit_glossary(self, node: Element) -> None:
        pass

    def depart_glossary(self, node: Element) -> None:
        pass

    def visit_title(self, node: Element) -> None:
        if not isinstance(node.parent, nodes.Admonition):
            self.add_title(node.astext())
            self.end_block()
            raise nodes.SkipNode

    def depart_title(self, node: Element) -> None:
        if isinstance(node.parent, nodes.Admonition):
            self.add_text(__(': '))

    def visit_subtitle(self, node: Element) -> None:
        pass

    def depart_subtitle(self, node: Element) -> None:
        pass

    def visit_attribution(self, node: Element) -> None:
        self.end_block()
        self.add_text('-- ')

    def depart_attribution(self, node: Element) -> None:
        pass

    def visit_desc(self, node: Element) -> None:
        pass

    def depart_desc(self, node: Element) -> None:
        pass

    def visit_desc_signature(self, node: Element) -> None:
        pass

    def depart_desc_signature(self, node: Element) -> None:
        pass

    def visit_desc_signature_line(self, node: Element) -> None:
        pass

    def depart_desc_signature_line(self, node: Element) -> None:
        pass

    def visit_desc_name(self, node: Element) -> None:
        pass

    def depart_desc_name(self, node: Element) -> None:
        pass

    def visit_desc_addname(self, node: Element) -> None:
        pass

    def depart_desc_addname(self, node: Element) -> None:
        pass

    def visit_desc_type(self, node: Element) -> None:
        pass

    def depart_desc_type(self, node: Element) -> None:
        pass

    def visit_desc_returns(self, node: Element) -> None:
        self.add_text(' -> ')

    def depart_desc_returns(self, node: Element) -> None:
        pass

    def visit_desc_parameterlist(self, node: Element) -> None:
        self.add_text('(')
        self.first_param = 1

    def depart_desc_parameterlist(self, node: Element) -> None:
        self.add_text(')')
        self.end_block()

    def visit_desc_parameter(self, node: Element) -> None:
        if not self.first_param:
            self.add_text(', ')
        else:
            self.first_param = 0
        self.add_text(node.astext())
        raise nodes.SkipNode

    def visit_desc_optional(self, node: Element) -> None:
        self.end_block()
        self.add_text('[')

    def depart_desc_optional(self, node: Element) -> None:
        self.add_text(']')

    def visit_desc_annotation(self, node: Element) -> None:
        pass

    def depart_desc_annotation(self, node: Element) -> None:
        pass

    def visit_desc_content(self, node: Element) -> None:
        pass

    def depart_desc_content(self, node: Element) -> None:
        pass

    def visit_figure(self, node: Element) -> None:
        pass

    def depart_figure(self, node: Element) -> None:
        pass

    def visit_caption(self, node: Element) -> None:
        pass

    def depart_caption(self, node: Element) -> None:
        pass

    def visit_productionlist(self, node: Element) -> None:
        names = []
        productionlist = cast(Iterable[addnodes.production], node)
        for production in productionlist:
            names.append(production['tokenname'])
        maxlen = max(len(name) for name in names)
        lastname = None
        for production in productionlist:
            if production['tokenname']:
                self.add_text(production['tokenname'].ljust(maxlen) + ' ::=')
                lastname = production['tokenname']
            elif lastname is not None:
                self.add_text('%s    ' % (' ' * len(lastname)))
            self.add_text(production.astext())
            self.end_block()
        raise nodes.SkipNode

    def visit_footnote(self, node: Element) -> None:
        label = cast(nodes.label, node[0])
        self._footnote = label.astext().strip()

    def depart_footnote(self, node: Element) -> None:
        self.add_text('[%s] ' % self._footnote)
        self.end_block()

    def visit_citation(self, node: Element) -> None:
        if len(node) and isinstance(node[0], nodes.label):
            self.add_quote(node[0].astext())
        else:
            self.add_quote()

    def depart_citation(self, node: Element) -> None:
        pass

    def visit_label(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_legend(self, node: Element) -> None:
        pass

    def depart_legend(self, node: Element) -> None:
        pass

    def visit_option_list(self, node: Element) -> None:
        pass

    def depart_option_list(self, node: Element) -> None:
        pass

    def visit_option_list_item(self, node: Element) -> None:
        pass

    def depart_option_list_item(self, node: Element) -> None:
        pass

    def visit_option_group(self, node: Element) -> None:
        self._firstoption = True

    def depart_option_group(self, node: Element) -> None:
        self.add_text('     ')

    def visit_option(self, node: Element) -> None:
        if self._firstoption:
            self._firstoption = False
        else:
            self.add_text(', ')

    def depart_option(self, node: Element) -> None:
        pass

    def visit_option_string(self, node: Element) -> None:
        pass

    def depart_option_string(self, node: Element) -> None:
        pass

    def visit_option_argument(self, node: Element) -> None:
        self.add_text(node['delimiter'])

    def depart_option_argument(self, node: Element) -> None:
        pass

    def visit_description(self, node: Element) -> None:
        pass

    def depart_description(self, node: Element) -> None:
        pass

    def visit_tabular_col_spec(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_colspec(self, node: Element) -> None:
        self.table.colwidth.append(node["colwidth"])
        raise nodes.SkipNode

    def visit_tgroup(self, node: Element) -> None:
        pass

    def depart_tgroup(self, node: Element) -> None:
        pass

    def visit_thead(self, node: Element) -> None:
        pass

    def depart_thead(self, node: Element) -> None:
        pass

    def visit_tbody(self, node: Element) -> None:
        self.table.set_separator()

    def depart_tbody(self, node: Element) -> None:
        pass

    def visit_row(self, node: Element) -> None:
        if self.table.lines:
            self.table.add_row()

    def depart_row(self, node: Element) -> None:
        pass

    def visit_entry(self, node: Element) -> None:
        pass

    def depart_entry(self, node: Element) -> None:
        entry = Cell(
            rowspan=node.get("morerows", 0) + 1, colspan=node.get("morecols", 0) + 1
        )
        entry.text = '\n'.join(self.cell_text)
        self.table.add_cell(entry)
        self.cell_text = []

    def visit_table(self, node: Element) -> None:
        if self.table:
            raise NotImplementedError('Nested tables are not supported.')
        self.table = Table()

    def depart_table(self, node: Element) -> None:
        self.enable_pre()
        text = str(self.table)
        self.table = None
        self.cell_text = []
        self.add_text(text)
        self.disable_pre()
        for line in self.after_table:
            self.add_text(line)
            self.end_block()
        self.after_table = []

    def visit_acks(self, node: Element) -> None:
        bullet_list = cast(nodes.bullet_list, node[0])
        list_items = cast(Iterable[nodes.list_item], bullet_list)
        self.add_text(', '.join(n.astext() for n in list_items) + '.')
        raise nodes.SkipNode

    def visit_image(self, node: Element) -> None:
        self.end_block()
        uri = relative_uri(self.builder.current_docname, node['uri'])
        full_uri = uri
        if self.builder.config.gemini_baseurl:
            full_uri = self.builder.config.gemini_baseurl + node['uri']
        if 'alt' in node.attributes:
            self.add_link(full_uri, __('[image: %s]') % node['alt'])
        else:
            self.add_link(full_uri)
        self.end_block()
        self.builder.images.append(posixpath.join(self.builder.imgpath, uri))
        raise nodes.SkipNode

    def visit_transition(self, node: Element) -> None:
        self.add_text('=' * MAXWIDTH)
        self.end_block()
        raise nodes.SkipNode

    def visit_bullet_list(self, node: Element) -> None:
        self.list_counter.append(-1)

    def depart_bullet_list(self, node: Element) -> None:
        self.list_counter.pop()

    def visit_enumerated_list(self, node: Element) -> None:
        self.list_counter.append(node.get('start', 1) - 1)

    def depart_enumerated_list(self, node: Element) -> None:
        self.list_counter.pop()

    def visit_definition_list(self, node: Element) -> None:
        self.list_counter.append(-2)

    def depart_definition_list(self, node: Element) -> None:
        self.list_counter.pop()

    def visit_list_item(self, node: Element) -> None:
        if -2 != self.list_counter[-1] != -1:
            # enumerated list
            self.list_counter[-1] += 1
            self.add_text('%s. ' % self.list_counter[-1])
        else:
            self.add_item('')

    def depart_list_item(self, node: Element) -> None:
        pass

    def visit_definition_list_item(self, node: Element) -> None:
        self._classifier_count_in_li = len(node.traverse(nodes.classifier))

    def depart_definition_list_item(self, node: Element) -> None:
        pass

    def visit_term(self, node: Element) -> None:
        pass

    def depart_term(self, node: Element) -> None:
        pass

    def visit_classifier(self, node: Element) -> None:
        self.add_text(__(': '))

    def depart_classifier(self, node: Element) -> None:
        pass

    def visit_definition(self, node: Element) -> None:
        pass

    def depart_definition(self, node: Element) -> None:
        pass

    def visit_field_list(self, node: Element) -> None:
        pass

    def depart_field_list(self, node: Element) -> None:
        pass

    def visit_field(self, node: Element) -> None:
        pass

    def depart_field(self, node: Element) -> None:
        pass

    def visit_field_name(self, node: Element) -> None:
        self.add_text(':')

    def depart_field_name(self, node: Element) -> None:
        self.add_text(':')
        self.end_block()

    def visit_field_body(self, node: Element) -> None:
        pass

    def depart_field_body(self, node: Element) -> None:
        pass

    def visit_centered(self, node: Element) -> None:
        pass

    def depart_centered(self, node: Element) -> None:
        pass

    def visit_hlist(self, node: Element) -> None:
        pass

    def depart_hlist(self, node: Element) -> None:
        pass

    def visit_hlistcol(self, node: Element) -> None:
        pass

    def depart_hlistcol(self, node: Element) -> None:
        pass

    def visit_admonition(self, node: Element) -> None:
        pass

    def depart_admonition(self, node: Element) -> None:
        pass

    def _visit_admonition(self, node: Element) -> None:
        self.add_text(admonitionlabels[node.tagname] + __(': '))

    def _depart_admonition(self, node: Element) -> None:
        self.end_block()

    visit_attention = _visit_admonition
    depart_attention = _depart_admonition
    visit_caution = _visit_admonition
    depart_caution = _depart_admonition
    visit_danger = _visit_admonition
    depart_danger = _depart_admonition
    visit_error = _visit_admonition
    depart_error = _depart_admonition
    visit_hint = _visit_admonition
    depart_hint = _depart_admonition
    visit_important = _visit_admonition
    depart_important = _depart_admonition
    visit_note = _visit_admonition
    depart_note = _depart_admonition
    visit_tip = _visit_admonition
    depart_tip = _depart_admonition
    visit_warning = _visit_admonition
    depart_warning = _depart_admonition
    visit_seealso = _visit_admonition
    depart_seealso = _depart_admonition

    def visit_versionmodified(self, node: Element) -> None:
        pass

    def depart_versionmodified(self, node: Element) -> None:
        pass

    def visit_literal_block(self, node: Element) -> None:
        self.enable_pre()
        pass

    def depart_literal_block(self, node: Element) -> None:
        self.disable_pre()
        self.end_block()

    def visit_doctest_block(self, node: Element) -> None:
        self.enable_pre()

    def depart_doctest_block(self, node: Element) -> None:
        self.disable_pre()
        self.end_block()

    def visit_line_block(self, node: Element) -> None:
        self.enable_pre()

    def depart_line_block(self, node: Element) -> None:
        self.disable_pre()

    def visit_line(self, node: Element) -> None:
        pass

    def depart_line(self, node: Element) -> None:
        pass

    def visit_block_quote(self, node: Element) -> None:
        pass

    def depart_block_quote(self, node: Element) -> None:
        pass

    def visit_compact_paragraph(self, node: Element) -> None:
        pass

    def depart_compact_paragraph(self, node: Element) -> None:
        pass

    def visit_paragraph(self, node: Element) -> None:
        if not isinstance(node.parent, nodes.Admonition) or \
           isinstance(node.parent, addnodes.seealso):
            pass

    def depart_paragraph(self, node: Element) -> None:
        if not self.table:
            self.end_block()
            self.end_block()

    def visit_target(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_index(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_toctree(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_substitution_definition(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_pending_xref(self, node: Element) -> None:
        pass

    def depart_pending_xref(self, node: Element) -> None:
        pass

    def visit_reference(self, node: Element) -> None:
        if 'refuri' in node:
            if self.table:
                self.after_table.append(
                    '=> %s %s' %
                    (node['refuri'], node.astext()))
                self.add_text(node.astext() or node['refuri'])
            else:
                self.end_block()
                self.add_link(node['refuri'], node.astext())
                self.end_block()
            raise nodes.SkipNode

    def depart_reference(self, node: Element) -> None:
        pass

    def visit_number_reference(self, node: Element) -> None:
        text = nodes.Text(node.get('title', '#'))
        self.visit_Text(text)
        raise nodes.SkipNode

    def visit_download_reference(self, node: Element) -> None:
        pass

    def depart_download_reference(self, node: Element) -> None:
        pass

    def visit_emphasis(self, node: Element) -> None:
        self.add_text('*')

    def depart_emphasis(self, node: Element) -> None:
        self.add_text('*')

    def visit_literal_emphasis(self, node: Element) -> None:
        self.add_text('*')

    def depart_literal_emphasis(self, node: Element) -> None:
        self.add_text('*')

    def visit_strong(self, node: Element) -> None:
        self.add_text('**')

    def depart_strong(self, node: Element) -> None:
        self.add_text('**')

    def visit_literal_strong(self, node: Element) -> None:
        self.add_text('**')

    def depart_literal_strong(self, node: Element) -> None:
        self.add_text('**')

    def visit_abbreviation(self, node: Element) -> None:
        self.add_text('')

    def depart_abbreviation(self, node: Element) -> None:
        if node.hasattr('explanation'):
            self.add_text(' (%s)' % node['explanation'])

    def visit_manpage(self, node: Element) -> None:
        return self.visit_literal_emphasis(node)

    def depart_manpage(self, node: Element) -> None:
        return self.depart_literal_emphasis(node)

    def visit_title_reference(self, node: Element) -> None:
        self.add_text('*')

    def depart_title_reference(self, node: Element) -> None:
        self.add_text('*')

    def visit_literal(self, node: Element) -> None:
        self.add_text('"')

    def depart_literal(self, node: Element) -> None:
        self.add_text('"')

    def visit_subscript(self, node: Element) -> None:
        self.add_text('_')

    def depart_subscript(self, node: Element) -> None:
        pass

    def visit_superscript(self, node: Element) -> None:
        self.add_text('^')

    def depart_superscript(self, node: Element) -> None:
        pass

    def visit_footnote_reference(self, node: Element) -> None:
        self.add_text('[%s]' % node.astext())
        raise nodes.SkipNode

    def visit_citation_reference(self, node: Element) -> None:
        self.add_quote('[%s]' % node.astext())
        raise nodes.SkipNode

    def visit_Text(self, node: Text) -> None:
        text = node.astext()
        if self.table:
            self.add_text(text)
            raise nodes.SkipNode

        if isinstance(node.parent, nodes.paragraph):
            text = text.replace('\r', '')
            text = text.replace('\n', ' ')
        self.add_text(text)

    def depart_Text(self, node: Text) -> None:
        pass

    def visit_generated(self, node: Element) -> None:
        pass

    def depart_generated(self, node: Element) -> None:
        pass

    def visit_inline(self, node: Element) -> None:
        pass

    def depart_inline(self, node: Element) -> None:
        pass

    def visit_container(self, node: Element) -> None:
        pass

    def depart_container(self, node: Element) -> None:
        pass

    def visit_problematic(self, node: Element) -> None:
        self.add_text('>>')

    def depart_problematic(self, node: Element) -> None:
        self.add_text('<<')

    def visit_system_message(self, node: Element) -> None:
        self.add_text('<SYSTEM MESSAGE: %s>' % node.astext())
        self.end_block()
        raise nodes.SkipNode

    def visit_comment(self, node: Element) -> None:
        raise nodes.SkipNode

    def visit_meta(self, node: Element) -> None:
        # only valid for HTML
        raise nodes.SkipNode

    def visit_raw(self, node: Element) -> None:
        if 'text' in node.get('format', '').split():
            self.enable_pre()
            self.add_text(node.astext())
            self.disable_pre()
        raise nodes.SkipNode

    def visit_math(self, node: Element) -> None:
        pass

    def depart_math(self, node: Element) -> None:
        pass

    def visit_math_block(self, node: Element) -> None:
        pass

    def depart_math_block(self, node: Element) -> None:
        self.end_block()

    def unknown_visit(self, node: Node) -> None:
        raise NotImplementedError('Unknown node: ' + node.__class__.__name__)
