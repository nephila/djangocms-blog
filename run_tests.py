#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run():
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    argv = sys.argv
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    if len(argv) == 1:
        argv.append("test")
    if len(argv) == 2 and argv[1] == "test":
        argv.append("tests")
    execute_from_command_line(argv)
