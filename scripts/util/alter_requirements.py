#!/usr/bin/env python3
import asyncio
import argparse
import logging  # noqa
import os
from typing import Any, Optional
import sys
import re
from dataclasses import dataclass, field

LINE_PATTERN_STRING = r"^(?P<name>[A-z\_\-0-9]+)((?P<operator>[=<>\!]+)(?P<version>[A-z\.0-9;\+,]+))?( )+?(@ ((?P<url>(?P<protocol>([A-z\+]+)):(/)+(?P<domain>[\w/\.\-]+)))(@(?P<ref>[\w]+))? )?;?( )+(?P<constraints>[A-z0-9\<\>\=\. \!\"\(\)]+)(?P<args>(-{1,2}[A-z]+[= ][\w0-9.\+:\"\']+( )*)*)$"
LINE_PATTERN = re.compile(LINE_PATTERN_STRING)

PLATFORM_DEPENDENCIES = ["pywin32"]


class InvalidDependencyError(ValueError):
    def __init__(self, dependency: str):
        self.dependency = dependency
        super().__init__(f"Invalid dependency: {dependency}")


@dataclass
class DependencyItem():

    name: str
    """Name of the dependency."""

    operator: Optional[str] = field(default=None)
    """Version operator"""

    version: Optional[str] = field(default=None)
    """Version specifier."""

    url: Optional[str] = field(default=None)
    """Url if the package is not a usual pip package."""

    ref: Optional[str] = field(default=None)
    """Ref. Tag, used if a branch or tag is specified like for github packages."""

    constraints: Optional[str] = field(default=None)
    """If python version constraint is supplied."""

    args: Optional[str] = field(default=None)
    """Further arguments."""

    @classmethod
    def from_string(cls, value: str) -> 'DependencyItem':
        match = LINE_PATTERN.fullmatch(value)
        if match is None:
            raise InvalidDependencyError(value)
        return DependencyItem(
            name=match.group("name"),
            operator=match.group("operator"),
            version=match.group("version"),
            url=match.group("url"),
            ref=match.group("ref"),
            constraints=match.group("constraints"),
            args=match.group("args")
        )

    def to_string(self, cfg: Any) -> str:
        out = ""
        out += self.name
        if self.url is not None:
            out += f"@{self.url}"
        if not cfg.no_version_constraint:
            out += self.operator
            out += self.version
        if not cfg.no_python_constraint:
            out += " ; "
            out += self.constraints
        return out


def current_filename() -> str:
    return os.path.basename(__file__).split('.')[0]


def basic_config(level: int = logging.INFO):
    """Basic logging configuration with sysout logger.

    Parameters
    ----------
    level : logging._Level, optional
        The logging level to consider, by default logging.INFO
    """
    root = logging.getLogger()
    root.setLevel(level)
    _fmt = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    _date_fmt = '%Y-%m-%d:%H:%M:%S'
    logging.basicConfig(format=_fmt,
                        datefmt=_date_fmt,
                        level=level)
    fmt = logging.Formatter(_fmt, _date_fmt)
    root.handlers[0].setFormatter(fmt)


def config():
    basic_config()


def get_config() -> Any:
    parser = argparse.ArgumentParser(
        description='Alter requirements txt to be used with conda.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Adding a config
    parser.add_argument(
        "--requirements-file", "-f",
        help="Path to the requirements file which should be loaded.",
        type=str, default=None, required=True)
    parser.add_argument(
        "--output", "-o",
        help="Path where the file should be written to. If not provided, it will override the requirements file.",
        type=str, default=None, required=False)

    parser.add_argument(
        "--no-python-constraint", "-p",
        help="If python constrainst should be removed.",
        action="store_true", default=False, required=False)

    parser.add_argument(
        "--no-version-constraint", "-v",
        help="If version constrainings should be removed.",
        action="store_true", default=False, required=False)
    parser.add_argument(
        "--platform-dependencies",
        help="If platform specific dependencies should be included.",
        action="store_true", default=False, required=False)

    args = parser.parse_args()

    return args


def parse_requirement(dependency: str, cfg: Any) -> str:
    match = LINE_PATTERN.fullmatch(dependency)
    if match is None:
        raise InvalidDependencyError(dependency)
    out = ""
    out += match.group("name")
    if match.group("url") is not None:
        out += f"@{match.group('url')}"
    if not cfg.no_version_constraint:
        out += match.group("operator")
        out += match.group("version")
    if not cfg.no_python_constraint:
        out += " ; "
        out += match.group("constraints")
    return out


def should_add(dep: DependencyItem, cfg: Any) -> bool:
    if cfg.platform_dependencies:
        if dep.name in PLATFORM_DEPENDENCIES:
            return False
    return True


def main(cfg):
    requirements_file = os.path.abspath(
        os.path.normpath(cfg.requirements_file))
    output_file = cfg.output
    if output_file is None:
        pass
    else:
        output_file = os.path.abspath(os.path.normpath(output_file))
    if not os.path.exists(requirements_file):
        raise ValueError(f"Path: {requirements_file} could not be found.")
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with open(requirements_file, 'r') as f:
        # requirement_lines = f.readlines()
        full_text = f.read()

    # Ignore linebreaks if they are escaped
    espat = re.compile(r"\\\n( )*")
    full_text = re.sub(espat, "", full_text)
    # Break the lines
    requirement_lines = full_text.split("\n")

    requirements = [line.strip() for line in requirement_lines]
    altered_requirements = []
    misc = []
    ignoring = []
    for requirement in requirements:
        try:
            if len(requirement) == 0:
                continue
            dependency = DependencyItem.from_string(requirement)
            if should_add(dependency, cfg):
                altered_requirements.append(dependency.to_string(cfg))
            else:
                ignoring.append(dependency.name)
        except InvalidDependencyError as e:
            misc.append(requirement)
    if len(misc) > 0:
        logging.warning(f"Could not parse the following dependencies: {misc}")
    if len(ignoring) > 0:
        logging.info(f"Ignored dependencies: {', '.join(ignoring)}")

    if output_file is not None:
        with open(output_file, 'w') as f:
            f.write("\n".join(altered_requirements)+"\n")
    else:
        joined = "\n".join(altered_requirements)+"\n"
        print("No output file provided, altered dependencies: \n")
        print(joined)


if __name__ == "__main__":
    config()
    cfg = get_config()
    main(cfg)
