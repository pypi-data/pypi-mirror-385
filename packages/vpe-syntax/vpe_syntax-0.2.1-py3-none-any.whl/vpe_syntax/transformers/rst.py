"""A tree transformer for reStructuredTest.

The tree-sitter-rst parser provides a fairly simply tree with a number of
limitations as far as syntax highlighting is concerned.

1. Each section's heading is simply identified as a "title". The level of the
   heading is not available.

2. Within paragraphs, most text is broken up into individual words, each
   identified as "text" nodes. This is unwieldy.

3. Inline markup does not separately identify the delimiters.

The transformer fixes the above by:

1. Tracking heading levels and replacing "title" with "heading1", "heading2",
   *etc*.

2. Runs of 2 or more "text" nodes are combined into single "text" nodes.

3. Inline markup is deconstructed to identify the delimiters. For example
   a simple "strong" node becomes::

       strong
           markup
           text
           markup

   This is TODO!

In addtion, the "content" nodes within "code-block" and related RST directives
are prefixed by the language when possible; e.g. "python:content".
"""

from dataclasses import dataclass
from typing import Callable, cast

import vpe

from vpe_syntax.tree import (
    BufferNode, SynCursor, SynNode, SynTree, SyntaxCursor, SyntaxNode,
    SyntaxTree, PropCursor)


class RST_Transformer:
    """Class used to transform a Tree-sitter reStructuredText tree."""
    # pylint: disable=invalid-name,too-many-instance-attributes

    def __init__(self, buf: vpe.Buffer, tree: SyntaxTree):
        self.buf = buf
        self.ts_cursor: SyntaxCursor = tree.walk()
        self._dispatch_table: dict[str, Callable[[], bool | None]] = {
            'adornment': self.process_adornment,
            'text': self.process_text,
            'content': self.process_content,
        }
        self.underlines: list[str] = []
        self.text_chain: list[SyntaxNode] = []
        self.tree: SynTree = SynTree(
                SynNode.from_ts_cursor(self.ts_cursor, parent=None))
        self.parent_node: SynNode = self.tree.root_node
        self.cursor = self.tree.walk()

    @property
    def new_leaf_node(self) -> SynNode:
        """The newest leaf node of the tree under construction."""
        if self.parent_node.children:
            return self.parent_node.children[-1]
        else:
            return self.parent_node

    @property
    def cursor_text(self) -> str:
        """The text of the cursor's current node, if on a single line."""
        a, b = self.ts_cursor.node.start_point
        c, d = self.ts_cursor.node.end_point
        if c == a:
            return self.buf[a][b:d]
        else:
            return ''

    def prev_sibling(self, count: int = 1) -> BufferNode | None:
        """Retrieve a previous sibling for the cursor's current node.

        This uses the cursor for the tree under construction.
        """
        cursor = self.cursor.copy()
        for _ in range(count):
            if not cursor.goto_previous_sibling():
                return None
        return BufferNode.from_cursor(self.buf, cursor)

    def ancestor(self, count: int = 1) -> BufferNode | None:
        """Retrieve an ancestor of the cursor's current node.

        This uses the cursor for the tree under construction.
        """
        cursor = self.cursor.copy()
        for _ in range(count):
            if not cursor.goto_parent():
                return None
        return BufferNode.from_cursor(self.buf, cursor)

    def store_copy(self) -> None:
        """Store any text chain and the a copy of the current node."""
        self.store_text()
        new_node = SynNode.from_ts_cursor(
            self.ts_cursor, parent=self.parent_node)
        self.parent_node.add_child(new_node)
        self.cursor = SynCursor(self.new_leaf_node)

    def store_text(self) -> None:
        """Store any chain of text nodes as a single text node."""
        if self.text_chain:
            start = self.text_chain[0].start_point
            end = self.text_chain[-1].end_point
            new_node = SynNode('text', start, end, '', self.parent_node)
            self.parent_node.add_child(new_node)
            self.text_chain[:] = []
            self.cursor = SynCursor(self.new_leaf_node)

    def transform(self) -> SyntaxTree:
        """Perform the transformation."""
        self.process_children(self.tree.root_node)
        return cast(SyntaxTree, self.tree)

    def process_children(self, parent_node: SynNode) -> None:
        """Recursivley process all children of the cursor's current node."""
        if not self.ts_cursor.goto_first_child():
            return

        while True:
            self.parent_node = parent_node
            field_name = self.ts_cursor.field_name
            type_name = self.ts_cursor.node.type
            if field_name:
                key = f'{field_name}:{type_name}'
            else:
                key = type_name
            handler = self._dispatch_table.get(key, self.process_default)
            if not handler():
                self.process_children(self.new_leaf_node)

            if not self.ts_cursor.goto_next_sibling():
                break

        self.store_text()
        self.ts_cursor.goto_parent()

    def process_default(self) -> bool:
        """Process any node not otherwise explicitly handled."""
        self.store_copy()
        return False

    def process_text(self) -> bool:
        """Process a text node."""
        self.text_chain.append(self.ts_cursor.node)
        return False

    def process_adornment(self) -> bool:
        """Process an adornment node."""
        self.store_copy()

        c = self.cursor_text[0]
        q_title = self.prev_sibling()
        if q_title and q_title.type == 'title':
            q_above_adorn = self.prev_sibling(2)
            if (q_above_adorn and q_above_adorn.type == 'adornment'):
                c = c + c
            if c not in self.underlines:
                self.underlines.append(c)
            else:
                while self.underlines[-1] != c:
                    self.underlines.pop()
            output_title = self.parent_node.children[-2]
            output_title.type = f'heading{len(self.underlines)}'

        return False

    def process_content(self) -> None:
        """Process a content node.

        If this is a code directive body then type of code is determined, if
        possible and the field name set to that name.
        """
        self.store_copy()

        grand_parent = self.ancestor(2)
        if not grand_parent or grand_parent.type != 'directive':
            return

        cursor = SynCursor(grand_parent)
        cursor.goto_first_child()
        cursor.goto_next_sibling()
        prev_node = self.prev_sibling()
        if not prev_node or prev_node.type != 'arguments':
            return

        name = prev_node.text
        if ' ' in name:
            return

        self.new_leaf_node.field_name = name


@dataclass
class TreeHandler:
    """A SyntaxTreeProvider for reStructuredText."""

    buf: vpe.Buffer
    tree: SyntaxTree
    affected_lines: list[range]

    def __post_init__(self):
        if self.affected_lines:
            self.affected_lines = list(self.affected_lines)
        transformer = RST_Transformer(self.buf, self.tree)
        self.tree = cast(SyntaxTree, transformer.transform())

    def create_cursor(self) -> PropCursor:
        """Provide a cursor to walk the tree."""
        return PropCursor(self.tree)
