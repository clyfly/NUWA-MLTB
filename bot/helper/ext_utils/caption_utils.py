import re

ESCAPED = {"|": "\ue000", "{": "\ue001", "}": "\ue002", "s": "\ue003"}
RESTORED = {value: key for key, value in ESCAPED.items()}


def split_template(template):
    parts = [""]
    index = 0
    while index < len(template):
        char = template[index]
        if (
            char == "\\"
            and index + 1 < len(template)
            and template[index + 1] in ESCAPED
        ):
            parts[-1] += ESCAPED[template[index + 1]]
            index += 2
        elif char == "|":
            parts.append("")
            index += 1
        else:
            parts[-1] += char
            index += 1
    return parts


def render(template, values):
    parts = split_template(template)
    parts[0] = re.sub(
        r"\{([^}]+)\}",
        lambda match: "{" + match.group(1).lower() + "}",
        parts[0],
    )
    result = parts[0].format(**values)
    for patch in parts[1:]:
        args = patch.split(":")
        count = int(args[2]) if len(args) == 3 else -1
        replacement = args[1] if len(args) > 1 else ""
        result = result.replace(args[0], replacement, count)
    for escaped, literal in RESTORED.items():
        result = result.replace(escaped, " " if literal == "s" else literal)
    return result
