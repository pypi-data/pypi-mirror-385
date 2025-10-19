from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from jmc.compile.lexer import clean_up_paren_token

from .command.utils import eval_expr, hash_string_to_string
from .utils import is_connected, get_mc_uuid, is_number
from .header import Header, MacroFactory
from .tokenizer import Token, TokenType, Tokenizer
from .exception import (
    EvaluationException,
    HeaderDuplicatedMacro,
    HeaderFileNotFoundError,
    HeaderSyntaxException,
    JMCSyntaxException,
)
from .log import Logger

if TYPE_CHECKING:
    from ..terminal.configuration import Configuration
    from ..compile.datapack import DataPack

logger = Logger(__name__)


@dataclass()
class MacroReapplier:
    """Contains information to reapply defered macros"""

    file_name: str
    line: int
    header_str: str


def _reapply_defered_macro(
    tokens: list[Token], reapplier: MacroReapplier
) -> list[Token]:
    total_string = ""
    old_token: Token | None = None
    for token in tokens:
        if not total_string:
            total_string += token.get_full_string()
        elif old_token is None:
            total_string += token.get_full_string()
        elif is_connected(token, old_token):
            total_string += token.get_full_string()
        else:
            total_string += " " + token.get_full_string()
        old_token = token
    tokenizer = Tokenizer(
        total_string,
        reapplier.file_name,
        line=reapplier.line,
        col=2,
        expect_semicolon=False,
        file_string=reapplier.header_str,
    )
    return tokenizer.programs[0]


def __empty_macro_factory(*_) -> list[Token]:
    return []


def __copy_macro_token(
    token: Token,
    line: int,
    col: int,
    length: int,
    replaced_token_col: int,
    token_col: int | None = None,
) -> Token:
    if token_col is None:
        token_col = token.col
    return Token(
        token.token_type,
        line=line,
        col=col + token_col - replaced_token_col,
        string=token.string,
        _macro_length=length,
    )


def __custom_macro_factory(
    replaced_tokens: list[Token], key: str
) -> tuple[MacroFactory, int]:
    """Used for binding"""

    # Creating template
    template_tokens: list[Token | tuple[int, Token]] = []
    replaced_token_col = replaced_tokens[0].col
    for token in replaced_tokens:
        template_tokens.append(token)

    def macro_factory(argument_tokens: list[Token], line: int, col: int) -> list[Token]:

        return_list: list[Token] = []
        extra_col = 0
        for token_or_int in template_tokens:
            if isinstance(token_or_int, Token):
                return_list.append(
                    __copy_macro_token(
                        token_or_int,
                        line,
                        col + extra_col,
                        len(key),
                        replaced_token_col,
                    )
                )
            else:
                return_list.append(
                    __copy_macro_token(
                        argument_tokens[token_or_int[0]],
                        line,
                        col,
                        len(key),
                        replaced_token_col,
                        token_or_int[1].col,
                    )
                )
                extra_col += (
                    argument_tokens[token_or_int[0]].length - token_or_int[1].length
                )

        return return_list

    return macro_factory, 0


def __eval_macro_factory(
    argument_tokens: list[Token], line: int, col: int
) -> list[Token]:
    """Macro factory for EVAL binding"""
    string = argument_tokens[0].string
    header = Header()
    for key, replaced in header.number_macros.items():
        string = string.replace(key, replaced)
    try:
        number = eval_expr(string)
    except (TypeError, SyntaxError):
        raise EvaluationException(string)
    except ZeroDivisionError:
        raise EvaluationException(string, "ZeroDivisionError")
    new_token = Token(
        TokenType.KEYWORD, line=line, col=col, string=number, _macro_length=len(number)
    )
    return [new_token]


def __not_macro_factory(
    argument_tokens: list[Token], line: int, col: int
) -> list[Token]:
    """Macro factory for NOT binding, set 0 to 1 and everything else to 0"""
    string = argument_tokens[0].string
    header = Header()
    for key, replaced in header.number_macros.items():
        string = string.replace(key, replaced)
    if string == "0":
        number = "1"
    else:
        number = "0"
    new_token = Token(
        TokenType.KEYWORD, line=line, col=col, string=number, _macro_length=len(number)
    )
    return [new_token]


def __create_macro_factory(
    replaced_tokens: list[Token],
    parameters_token: Token | None,
    key: str,
    tokenizer: Tokenizer,
    error: HeaderSyntaxException,
    reapplier: MacroReapplier | None,
) -> tuple[MacroFactory, int]:
    if not replaced_tokens:
        return __empty_macro_factory, 0

    # Parsing parameters_token
    parameter_tokens: list[Token] = []
    if parameters_token is not None:
        parameter_tokens_, invalid_kwargs = tokenizer.parse_func_args(parameters_token)
        for parameter_token_ in parameter_tokens_:
            if parameter_token_[0].token_type != TokenType.KEYWORD:
                raise JMCSyntaxException(
                    f"Macro factory arguments can only have a keyword token (got {parameter_token_[0].token_type})",
                    parameter_token_[0],
                    tokenizer,
                )
            if len(parameter_token_) > 1:
                raise JMCSyntaxException(
                    f"Macro factory arguments can only have 1 token each (got {len(parameter_token_)})",
                    parameter_token_[1],
                    tokenizer,
                )
            parameter_tokens.append(parameter_token_[0])
        if invalid_kwargs:
            raise error

    # Creating template
    template_tokens: list[Token | tuple[int, Token]] = []
    replaced_token_col = replaced_tokens[0].col
    for token in replaced_tokens:
        for index, parameter_token in enumerate(parameter_tokens):
            if (
                token.token_type == parameter_token.token_type
                and token.string == parameter_token.string
            ):
                template_tokens.append((index, token))
                break
        else:
            template_tokens.append(token)

    def macro_factory(argument_tokens: list[Token], line: int, col: int) -> list[Token]:
        def _replace_token(token: Token) -> str:
            for index, parameter_token in enumerate(parameter_tokens):
                if (
                    token.token_type == parameter_token.token_type
                    and token.string == parameter_token.string
                ):
                    return argument_tokens[index].string
            return token.string

        return_list: list[Token] = []
        extra_col = 0
        for token_or_int in template_tokens:
            if isinstance(token_or_int, Token):
                if reapplier is not None and token_or_int.token_type in (
                    TokenType.PAREN_CURLY,
                    TokenType.PAREN_ROUND,
                    TokenType.PAREN_SQUARE,
                ):
                    token_ = Tokenizer(
                        clean_up_paren_token(
                            token_or_int,
                            tokenizer,
                            is_nbt=False,
                            keyword_token_callback=_replace_token,
                        ),
                        reapplier.file_name,
                        line=token_or_int.line,
                        col=token_or_int.col,
                        expect_semicolon=False,
                        file_string=reapplier.header_str,
                    ).programs[0][0]
                    return_list.append(
                        __copy_macro_token(
                            token_,
                            line,
                            col + extra_col,
                            len(key),
                            replaced_token_col,
                        )
                    )

                else:
                    return_list.append(
                        __copy_macro_token(
                            token_or_int,
                            line,
                            col + extra_col,
                            len(key),
                            replaced_token_col,
                        )
                    )
            else:
                return_list.append(
                    __copy_macro_token(
                        argument_tokens[token_or_int[0]],
                        line,
                        col + extra_col,
                        len(key),
                        replaced_token_col,
                        token_or_int[1].col,
                    )
                )
                extra_col += (
                    argument_tokens[token_or_int[0]].length - token_or_int[1].length
                )

        if reapplier is None:
            return return_list
        else:
            return _reapply_defered_macro(return_list, reapplier)

    return macro_factory, len(parameter_tokens)


def __parse_header(
    header_str: str,
    file_name: str,
    parent_target: Path,
    namespace_path: Path,
    config: "Configuration",
) -> Header:
    header = Header()
    lines = header_str.split("\n")
    for line, line_str in enumerate(lines):
        line += 1
        if line_str.isspace() or line_str.startswith("//") or line_str == "":
            continue

        if not line_str.startswith("#"):
            raise HeaderSyntaxException(
                "Expected '#' at the start of the line", file_name, line, line_str
            )

        if line_str == "#":
            raise HeaderSyntaxException(
                "Expected directive after '#'", file_name, line, line_str
            )

        is_deepdefine = line_str.split(maxsplit=1)[0] == "#deepdefine"

        if is_deepdefine:
            # Defer other macros
            _macros = header.macros
            header.macros = {}
        else:
            _macros = None
        tokenizer = Tokenizer(
            line_str[1:],
            file_name,
            line=line,
            col=2,
            expect_semicolon=False,
            file_string=header_str,
        )
        if is_deepdefine:
            assert _macros is not None
            header.macros = _macros
            reapplier = MacroReapplier(file_name, line, header_str)
        else:
            reapplier = None
        directive_and_args = tokenizer.programs[0]
        directive_token = directive_and_args[0]
        arg_tokens = directive_and_args[1:]
        if directive_token.token_type != TokenType.KEYWORD:
            raise HeaderSyntaxException(
                f"Expected directive(keyword) after '#' (got {directive_token.token_type.value})",
                file_name,
                line,
                line_str,
            )

        # #define
        if directive_token.string == "define":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    "Expected keyword after '#define'", file_name, line, line_str
                )

            key = arg_tokens[0].string
            if key in header.macros:
                raise HeaderDuplicatedMacro(
                    f"'{key}' macro is already defined", file_name, line, line_str
                )

            if len(arg_tokens) == 1:
                #  #define KEYWORD
                header.macros[key] = (__empty_macro_factory, 0)

            elif arg_tokens[1].token_type == TokenType.PAREN_ROUND and is_connected(
                arg_tokens[1], arg_tokens[0]
            ):
                #  #define KEYWORD(arg1, arg2)
                header.macros[key] = __create_macro_factory(
                    arg_tokens[2:],
                    arg_tokens[1],
                    key,
                    tokenizer,
                    HeaderSyntaxException(
                        "Invalid macro argument syntax", file_name, line, line_str
                    ),
                    reapplier=None,
                )
            else:
                #  #define KEYWORD TOKEN
                header.macros[key] = __create_macro_factory(
                    arg_tokens[1:],
                    None,
                    key,
                    tokenizer,
                    HeaderSyntaxException(
                        "Invalid macro argument syntax", file_name, line, line_str
                    ),
                    reapplier=None,
                )
                num = arg_tokens[1].string
                if is_number(num):
                    header.number_macros[key] = num

        # #env
        elif directive_token.string == "env":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    "Expected keyword after '#env'", file_name, line, line_str
                )

            key = arg_tokens[0].string
            if key in header.macros:
                raise HeaderDuplicatedMacro(
                    f"'{key}' macro is already defined", file_name, line, line_str
                )

            if len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    "Expected keyword after '#env'", file_name, line, line_str
                )
            if key in header.envs:
                header.envs.remove(key)
                replacement = "1"
            else:
                replacement = "0"

            header.macros[key] = __create_macro_factory(
                [Token.empty(replacement)],
                None,
                key,
                tokenizer,
                HeaderSyntaxException(
                    "Invalid macro argument syntax", file_name, line, line_str
                ),
                reapplier=None,
            )
            header.number_macros[key] = replacement

        # #deepdefine
        elif directive_token.string == "deepdefine":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    "Expected keyword after '#define'", file_name, line, line_str
                )

            key = arg_tokens[0].string
            if key in header.macros:
                raise HeaderDuplicatedMacro(
                    f"'{key}' macro is already defined", file_name, line, line_str
                )

            if len(arg_tokens) == 1:
                #  #define KEYWORD
                raise HeaderSyntaxException(
                    "'#deepdefine' is useless for normal define, simply use '#define'",
                    file_name,
                    line,
                    line_str,
                )

            #  #define KEYWORD(arg1, arg2)
            elif arg_tokens[1].token_type == TokenType.PAREN_ROUND and is_connected(
                arg_tokens[1], arg_tokens[0]
            ):
                header.macros[key] = __create_macro_factory(
                    arg_tokens[2:],
                    arg_tokens[1],
                    key,
                    tokenizer,
                    HeaderSyntaxException(
                        "Invalid macro argument syntax", file_name, line, line_str
                    ),
                    reapplier,
                )
            else:
                #  #define KEYWORD TOKEN
                raise HeaderSyntaxException(
                    "'#deepdefine' is useless for normal define, simply use '#define'",
                    file_name,
                    line,
                    line_str,
                )
        # #bind
        elif directive_token.string == "bind":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    "Expected keyword(binder) after '#define'",
                    file_name,
                    line,
                    line_str,
                )

            binder = arg_tokens[0].string
            if len(arg_tokens) == 1:
                #  #bind BINDER
                keys = [binder]
            else:
                #  #bind BINDER TOKEN
                keys = [token_.string for token_ in arg_tokens[1:]]

            for key in keys:
                replaced_tokens: list[Token] = []
                if binder == "__namespace__":
                    replaced_tokens = [Token.empty(config.namespace)]
                elif binder.startswith("__namehash") and binder.endswith("__"):
                    try:
                        length = int(binder[10:-2])
                    except ValueError:
                        raise HeaderSyntaxException(
                            f"{binder[10:-2]} is invalid string length for __namehash__ directive (non integer detected)",
                            file_name,
                            line,
                            line_str,
                        )
                    if length > 64:
                        raise HeaderSyntaxException(
                            f"__namehash__ string length must be at most 64 characters.",
                            file_name,
                            line,
                            line_str,
                        )
                    replaced_tokens = [
                        Token.empty(hash_string_to_string(config.namespace, length))
                    ]
                elif binder == "__UUID__":
                    replaced_tokens = [
                        Token.empty(get_mc_uuid(key), TokenType.PAREN_SQUARE)
                    ]
                elif binder == "EVAL":
                    header.macros[key] = __eval_macro_factory, 1
                    key = ""
                elif binder == "NOT":
                    header.macros[key] = __not_macro_factory, 1
                    key = ""
                else:
                    raise HeaderSyntaxException(
                        "Unrecognized binder for '#bind'",
                        file_name,
                        line,
                        line_str,
                        suggestion="All available binders are '__namespace__', '__namehash{number}__', '__UUID__'",
                    )

                if key:
                    if key in header.macros:
                        raise HeaderDuplicatedMacro(
                            f"'{key}' macro is already defined",
                            file_name,
                            line,
                            line_str,
                        )
                    header.macros[key] = __custom_macro_factory(replaced_tokens, key)

        # #include
        elif directive_token.string == "include":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.STRING:
                raise HeaderSyntaxException(
                    "Expected included file name(string) after '#include'",
                    file_name,
                    line,
                    line_str,
                )
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#include' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            new_file_name = arg_tokens[0].string
            if not new_file_name.endswith(".hjmc"):
                new_file_name += ".hjmc"
            header_file = parent_target / new_file_name
            if not header_file.is_file():
                raise HeaderFileNotFoundError(header_file)
            with header_file.open("r", encoding="utf-8") as file:
                header_str = file.read()
            logger.info(f"Parsing {header_file}")
            if header.is_header_exist(header_file):
                raise HeaderSyntaxException(
                    f"File {header_file.as_posix()} is already included.",
                    file_name,
                    line,
                    line_str,
                )
            header.add_file_read(header_file)
            __parse_header(
                header_str,
                header_file.as_posix(),
                parent_target,
                namespace_path,
                config,
            )

        # #credit
        elif directive_token.string == "credit":
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 0-1 arguments after '#credit' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            if arg_tokens:
                if arg_tokens[0].token_type != TokenType.STRING:
                    raise HeaderSyntaxException(
                        "Expected included file name(string) after '#include'",
                        file_name,
                        line,
                        line_str,
                    )
                header.credits.append(arg_tokens[0].string)
            else:
                header.credits.append("")

        # #forcebst
        elif directive_token.string == "forcebst":
            if arg_tokens:
                raise HeaderSyntaxException(
                    "Expected 0 arguments after '#forcebst'", file_name, line, line_str
                )
            header.force_bst = True

        # #enum
        elif directive_token.string == "enum":
            if len(arg_tokens) < 2:
                raise HeaderSyntaxException(
                    f"Expected at least 2 arguments after '#enum' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            class_name = arg_tokens[0].string
            start = 0
            if is_number(arg_tokens[1].string):
                start = int(arg_tokens[1].string)
                del arg_tokens[1]
            if len(arg_tokens) < 2:
                raise HeaderSyntaxException(
                    f"Expected at least 1 item in enum (got {len(arg_tokens) - 1})",
                    file_name,
                    line,
                    line_str,
                )
            for item in arg_tokens[1:]:
                key = class_name + "." + item.string
                header.macros[key] = __create_macro_factory(
                    [Token(TokenType.KEYWORD, line, 0, str(start))],
                    None,
                    key,
                    tokenizer,
                    HeaderSyntaxException(
                        "Invalid macro argument syntax", file_name, line, line_str
                    ),
                    reapplier=None,
                )
                num = arg_tokens[1].string
                if is_number(num):
                    header.number_macros[key] = num
                start += 1

        # #override
        elif directive_token.string == "override":
            if not arg_tokens or len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#namespace' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            header.namespace_overrides.add(arg_tokens[0].string)

        # #command
        elif directive_token.string == "command":
            if len(arg_tokens) == 3 and (
                arg_tokens[0].string,
                arg_tokens[1].string,
            ) == ("execute", "if"):
                header.conditions.add(arg_tokens[2].string)
            elif not arg_tokens or len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#command' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            if arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    f"Expected keyword after '#command' (got {arg_tokens[0].token_type.value})",
                    file_name,
                    line,
                    line_str,
                )
            header.commands.add(arg_tokens[0].string)

        # #del
        elif directive_token.string == "del":
            if not arg_tokens or len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#del' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            if arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    f"Expected keyword after '#del' (got {arg_tokens[0].token_type.value})",
                    file_name,
                    line,
                    line_str,
                )
            header.dels.add(arg_tokens[0].string)

        # #resource
        elif directive_token.string == "resource":
            if not arg_tokens or len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#resource' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            if arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    f"Expected keyword after '#resource' (got {arg_tokens[0].token_type.value})",
                    file_name,
                    line,
                    line_str,
                )
            header.resources.add(arg_tokens[0].string.replace(".", "/"))

        # #static
        elif directive_token.string == "static":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.STRING:
                raise HeaderSyntaxException(
                    "Expected static folder name(string) after '#static'",
                    file_name,
                    line,
                    line_str,
                )
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#static' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            static_folder = namespace_path / arg_tokens[0].string
            if not static_folder.is_dir():
                raise HeaderSyntaxException(
                    f"Static folder not found: {static_folder.as_posix()}",
                    file_name,
                    line,
                    line_str,
                    suggestion="Please recheck that the path is correct so that JMC won't accidentally delete your folder.",
                )
            header.statics.add(static_folder)

        # #uninstall
        elif directive_token.string == "uninstall":
            if arg_tokens:
                raise HeaderSyntaxException(
                    f"Expected 0 arguments after '#uninstall' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            _line = line
            _line_str = line_str
            _file_name = file_name

            def __uninstall(datapack: "DataPack"):
                if "uninstall" not in datapack.functions:
                    raise HeaderSyntaxException(
                        "'#uninstall' requires an existing 'uninstall' function",
                        _file_name,
                        _line,
                        _line_str,
                        suggestion="Add 'function uninstall() {}' to a jmc file",
                    )
                datapack.functions["uninstall"].extend(
                    [
                        *(
                            f"scoreboard objectives remove {obj}"
                            for obj in datapack.scoreboards
                        ),
                        *(
                            f"scoreboard objectives remove {obj}"
                            for obj in datapack.data.scoreboards
                        ),
                        *(f"team remove {team}" for team in datapack.data.teams),
                        *(
                            f"bossbar remove {bossbar}"
                            for bossbar in datapack.data.bossbars
                        ),
                    ]
                )

            header.post_process.append(__uninstall)
        # #nometa
        elif directive_token.string == "nometa":
            if arg_tokens:
                raise HeaderSyntaxException(
                    f"Expected 0 arguments after '#nometa' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            header.nometa = True
        # #show_private_command
        elif directive_token.string == "show_private_command":
            if arg_tokens:
                raise HeaderSyntaxException(
                    f"Expected 0 arguments after '#nometa' (got {len(arg_tokens)})",
                    file_name,
                    line,
                    line_str,
                )
            header.show_private_command = True

        else:
            raise HeaderSyntaxException(
                f"Unrecognized directive '{directive_token.string}'",
                file_name,
                line,
                line_str,
            )

    return header


def parse_header(
    header_str: str,
    file_name: str,
    parent_target: Path,
    namespace_path: Path,
    config: "Configuration",
) -> Header:
    """
    Parse header and store the information in the header object

    :param header_str: String that was read from the file
    :param file_name: Header file's name
    :param parent_target: Path to parent of the main jmc file
    :raises HeaderSyntaxException: A line in the file doesn't start with '#'
    :raises HeaderDuplicatedMacro: Define same macro twice
    :raises HeaderSyntaxException: Too many/little argument for define
    :raises HeaderSyntaxException: File name isn't wrapped in quote or angle bracket (For `#include`)
    :raises HeaderFileNotFoundError: Can't find header file
    :raises HeaderSyntaxException: Include same file twice
    :raises HeaderSyntaxException: Whitespace found in header file's name
    :raises NotImplementedError: WORKING ON `#replace`
    :raises NotImplementedError: WORKING ON `#credit`
    :raises HeaderSyntaxException: Directive (`#something`) is unrecognized
    :return: Header singleton object
    """
    header = Header()
    header.is_enable_macro = False
    return_value = __parse_header(
        header_str, file_name, parent_target, namespace_path, config
    )
    header.is_enable_macro = True
    return return_value
