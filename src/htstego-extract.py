#!/usr/bin/env python3

# libhtstego - Halftone Steganography Utility
#
# Copyright (C) 2023 by Efe Çiftci <efeciftci@cankaya.edu.tr>
# Copyright (C) 2023 by Emre Sümer <esumer@baskent.edu.tr>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys
from libhtstego import htstego_errdiff_extract, htstego_pattern_extract

__version__ = '1.0'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Halftone Steganography Extraction Utility Version {__version__}')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--extract-from', type=str, help='extract from images in this directory')
    parser.add_argument('--htmethod', type=str, required=True, choices=['pattern', 'errdiff'], help='halftoning method')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    dirName = args.extract_from if args.extract_from else 'output'
    msg = htstego_errdiff_extract(dirName) if args.htmethod == 'errdiff' else htstego_pattern_extract(dirName)
    print(msg)
