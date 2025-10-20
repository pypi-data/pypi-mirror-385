from functools import reduce
from textwrap import indent
import re
from typing import TYPE_CHECKING

from godocs.translation.translator.syntax_translator import SyntaxTranslator
# from godocs.constructor.jinja_constructor.rst.filters import make_code_member_ref

if TYPE_CHECKING:
    from godocs.translation import ast


def normalize_code_member(name: str) -> str:
    # Substitute Array notation from "type[]" to "Array[type]"
    result = re.sub(
        r"(\S+)\[\]",
        lambda match: f"Array[{match.group(1)}]",
        name,
    )
    # Substitute dot notation from "A.B" to "A_B" so it works better
    # in refs and labels.
    result = result.replace('.', '_')

    return result


def make_code_member_label_target(name: str, prefix: str = '') -> str:
    result = f"{prefix + '_' if prefix else ''}"

    result += normalize_code_member(name)

    return result


def make_code_member_ref(full_name: str, prefix: str = '', name: str | None = None) -> str:
    if name == None:
        name = full_name

    return f":ref:`{name} <{make_code_member_label_target(full_name, prefix)}>`"


class RSTSyntaxTranslator(SyntaxTranslator):

    def make_directive(
        self,
        name: str,
        args: list[str] | None = None,
        options: dict[str, str] | None = None,
        content: str = '',
    ) -> str:
        if args is None:
            args = []
        if options is None:
            options = {}

        name_output = name

        args_output = reduce(
            lambda prev, next: prev + next + ' ',
            args,
            '',
        )

        options_output = ''

        for i, option in enumerate(options):
            value = options[option]

            options_output += f":{option}: {value}"

            if i < len(options) - 1:
                options_output += "\n"

        if options_output:
            options_output = indent(options_output, "   ")

        content_output = indent(content, "   ")

        result = f".. {name_output}::"

        if args_output:
            result += f" {args_output}"
        if options_output:
            result += f"\n{options_output}"
        if content_output:
            result += f"\n\n{content_output}"

        return result

    def make_codeblock(self, content: str, language: str = '') -> str:
        return self.make_directive("codeblock", [language], {}, content)

    def translate_text(self, node: "ast.TextNode") -> str:
        return node.content

    def translate_tag(self, node: "ast.TagNode") -> str:
        # First of all, translates the children of the node received.
        content = reduce(
            lambda prev, next: prev + next.translate(self),
            node.children,
            '',
        )

        # Depending on the node name, the resultant syntax will change.
        match node.name:
            case "root": return content
            case "bold": return f"**{content}**"
            case "newline": return f"\n"
            case "italic": return f"*{content}*"
            case "paragraph": return content
            case "code": return f"``{content}``"
            case "codeblock": return self.make_codeblock(
                content,
                node.params.get("language", '')
            )
            case "link": return f"{content} <{node.params.get("url", '')}>_"
            case "reference": return make_code_member_ref(node.params.get("name", ''))
            case _: return ''

        return content
