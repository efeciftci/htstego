#!/usr/bin/env python3
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
    print('Result:', msg)
