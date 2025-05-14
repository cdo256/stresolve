from stresolve import util
import argparse
import os
import difflib
import sys
from pathlib import Path
import filecmp
import re
import stat
from termcolor import colored
import string
import typer
import subprocess as sp
from stresolve.automerge import merge_if_applicable


def find_sync_conflicts(directory):
    conflicts = []
    for root, _, files in directory.walk():
        for file in files:
            if ".sync-conflict-" in str(file):
                conflicts.append(root / file)
    return conflicts
