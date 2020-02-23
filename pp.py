#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2017 Leandro T. C. Melo (LTCMELO@GMAIL.COM)
#
# All rights reserved. Unauthorized copying of this file, through any
# medium, is strictly prohibited.
#
# This software is provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, explicit or implicit. In no event shall the
# author be liable for any claim or damages.
# -----------------------------------------------------------------------------


import argparse
import os
import shutil
import sys
from distutils.dir_util import copy_tree
from typing import List


def _warn(msg):
    print(f'*** WARN: {msg}')


def _error(msg):
    sys.exit(f'*** ERROR: {msg}')


def _parse_comand():
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\tTMTMIPP - The Most Trivial Markup Include Pre-Processor\n',
        epilog='example:\n'
               '  ./pp.py path/to/website/\n')

    parser.add_argument('proj_dir',
                        metavar='<path>',
                        type=str,
                        help="path of project's directory")

    parser.add_argument('-x', '--ext',
                        action='append',
                        default=['html'],
                        type=str,
                        help='file extension to be considered (e.g., html)')

    parser.add_argument('-o', '--output',
                        metavar='DIR',
                        action='store',
                        default='output',
                        type=str,
                        help='(project-relative) output directory')

    return parser.parse_args()


class Options:
    def __init__(self, base_dir: str, out_dir: str, exts: List[str]):
        self.base_dir = base_dir
        self.out_dir = out_dir
        self.exts = set(['.' + x for x in exts])


def _validate_input(cmd):
    proj_dir = cmd.proj_dir
    if not os.path.isdir(proj_dir):
        _error(f'invalid input directory: {proj_dir}')

    out_dir = os.path.join(proj_dir, cmd.output)
    if os.path.exists(out_dir):
        if os.path.isdir(out_dir):
            print(f'directory {out_dir} will be overwritten')
            shutil.rmtree(out_dir)
        else:
            _error(f"{out_dir} isn't a directory")

    opt = Options(proj_dir, out_dir, cmd.ext)
    return opt


class Preprocessor:
    """
    The "engine".
    """

    # The markers are expected at the start of a line.
    INCLUDE_MARKER = '<!--@#$ '

    def __init__(self, opts: Options):
        self._opts = opts
        self._files: List[str] = []

    def _collect_files(self, dir: str, prefix: str=''):
        for p in os.listdir(dir):
            if p.startswith('.'):
                continue

            if '.' in p:
                suffix = p[p.index('.'):]
                if suffix in self._opts.exts:
                    self._files.append(os.path.join(prefix, p))
                    continue

            sub_dir = os.path.join(dir, p)
            if os.path.isdir(sub_dir):
                copy_tree(sub_dir,
                          os.path.join(self._opts.base_dir, self._opts.out_dir, p))
                self._collect_files(sub_dir, p)

    def _replace_content(self):
        for f in self._files:
            f_path = os.path.join(self._opts.base_dir, f)
            assert os.path.isfile(f_path)

            print(f"\npp'ing {f_path}")

            content = ''
            with open(f_path) as f_obj:
                for line in f_obj:
                    content += line

                    line = line.strip()
                    if line.startswith(Preprocessor.INCLUDE_MARKER):
                        if not line.endswith('-->'):
                            _warn(f'skip invalid inclusion: {line}')
                            continue

                        inc = line[len(Preprocessor.INCLUDE_MARKER):-3]
                        inc = inc.strip()

                        inc_path = os.path.join(self._opts.base_dir, inc)
                        if not os.path.isfile(inc_path):
                            _warn(f'skip non-relative inclusion: {inc}')
                            continue

                        with open(inc_path) as inc_obj:
                            content += '<!-- vvv -->\n'
                            content += inc_obj.read()
                            content += '<!-- ^^^ -->\n\n'

            self._create_out_file(f, content)

    def _create_out_file(self, f_rel_path: str, content: str):
        if not content:
            return

        f_out_path = os.path.join(self._opts.base_dir,
                                  self._opts.out_dir,
                                  f_rel_path)

        out_dir = os.path.dirname(f_out_path)
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except OSError as e:
                _error(f'output directory creation failed: {e}')

        with open(f_out_path, 'w') as f_obj:
            f_obj.write(content)
            print(f"pp'ed into {f_out_path}")

    def go(self):
        self._collect_files(self._opts.base_dir)
        print(f'collected {self._files}')
        self._replace_content()


if __name__ == "__main__":
    cmd = _parse_comand()
    opts = _validate_input(cmd)
    Preprocessor(opts).go()
