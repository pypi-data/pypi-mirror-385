import re


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


def join_code_member_name(name: str, first_names: str) -> str:
    result = first_names + '.' if first_names else ''

    result += name

    return result


def make_code_member_ref(full_name: str, prefix: str = '', name: str | None = None) -> str:
    if name is None:
        name = full_name

    return f":ref:`{name} <{make_code_member_label_target(full_name, prefix)}>`"


def make_code_member_type_ref(full_name: str, prefix: str = '') -> str:
    result = normalize_code_member(full_name)

    # Substitute class names for refs
    result = re.sub(
        r"([\w]+)",
        lambda match: make_code_member_ref(match.group(1), prefix),
        full_name,
    )

    return result


def make_property_signature(
    full_name: str,
    type: str = '',
    prefix: str = '',
    default: str = '',
    is_static: bool = False,
    make_ref: bool = True
) -> str:
    result = 'static ' if is_static else ''
    result += make_code_member_type_ref(type, prefix) + ' ' if type else ''

    name = full_name.split('.').pop()

    result += make_code_member_ref(full_name,
                                   prefix, name) if make_ref else name

    result += f" = ``{default}``" if default else ''

    return result


def make_method_signature(
    full_name: str,
    type: str = '',
    prefix: str = '',
    args: list[dict[str, str]] = [],
    is_static: bool = False,
    make_ref: bool = True
) -> str:
    result = 'static ' if is_static else ''
    result += make_code_member_type_ref(type, prefix) + ' ' if type else ''

    name = full_name.split('.').pop()

    result += make_code_member_ref(full_name,
                                   prefix, name) if make_ref else name

    args_output = r"\("

    for i in range(len(args)):
        arg = args[i]

        args_output += make_property_signature(
            arg["name"],
            arg["type"],
            prefix,
            arg["default"],
            False,
            False,
        )

        if i < len(args) - 1:
            args_output += ", "

    args_output += r"\)"

    result += args_output

    return result
