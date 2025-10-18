from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


class EquationMarkdownNode(MarkdownNode):
    def __init__(self, expression: str, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.expression = expression

    @override
    def to_markdown(self) -> str:
        expr = self.expression.strip()
        equation_syntax = self._syntax_registry.get_equation_syntax()
        if not expr:
            return f"{equation_syntax.start_delimiter}{equation_syntax.end_delimiter}"

        return f"{equation_syntax.start_delimiter}{expr}{equation_syntax.end_delimiter}"
