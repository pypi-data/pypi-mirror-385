"""Custom Rich highlighters for usage with Nebulog sample code."""

from rich.highlighter import RegexHighlighter

SEMVER_REGEX = (
    r"(?:v)?(?P<MAJOR>0|[1-9]\d*)\.(?P<MINOR>0|[1-9]\d*)\.(?P<PATCH>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)


class SemverHighlighter(RegexHighlighter):
    """Highlighter to mark SemVer 2.0 compliant versions in Rich."""

    highlights = [SEMVER_REGEX]  # noqa: RUF012
    base_style = "regex."
