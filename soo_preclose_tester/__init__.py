"""Helper package to launch SOO PreClose Tester."""

from importlib import import_module

# Expose main for convenience
main = import_module('main').main
