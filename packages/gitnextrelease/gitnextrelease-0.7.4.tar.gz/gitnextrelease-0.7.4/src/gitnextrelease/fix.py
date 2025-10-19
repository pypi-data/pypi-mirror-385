#!/usr/bin/env python3
# from os.path import exists
# from os import environ
from .common import GitActions
import argparse
from .config import Settings
from os import getenv


class Command(object):
    def __init__(self):
        self.settings = Settings()()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "--no-remote",
            action="store_true",
            help="Dont use the remote based commands",
        )
        self.parser.add_argument(
            "--title-separator",
            dest="title_separator",
            help="the character that separates the title from the body",
            default=getenv(
                "TITLE_SEPARATOR", self.settings["config"]["title_separator"]
            ),
        )
        self.parser.add_argument(
            "--body-separator",
            dest="body_separator",
            help="the character to replaces whitespace in the body of the msg",
            default=getenv("BODY_SEPARATOR", self.settings["config"]["body_separator"]),
        )
        self.parser.add_argument(
            "fix_branch_name", nargs="*", help="name of the feature"
        )
        self.args = self.parser.parse_args()
        self.ga = GitActions(self.args)
        return

    def __call__(self):
        if len(self.args.fix_branch_name) == 0:
            return "the branch needs a name"
        name = f"{self.args.body_separator}".join(self.args.fix_branch_name)
        name = f"fix{self.args.title_separator}{name}"
        print(self.ga.git(["checkout", "-b", name]))
        if self.ga.check_for_origin_remote(self.args.no_remote):
            self.ga.git(["push", "--set-upstream", "origin", name])


def main():
    return Command()()


if __name__ == "__main__":
    print(main())
