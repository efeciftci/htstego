#!/usr/bin/env python3

# libhtstego - Halftone Steganography Utility
#
# Copyright (C) 2024 by Efe Çiftci <efeciftci@cankaya.edu.tr>
# Copyright (C) 2024 by Emre Sümer <esumer@baskent.edu.tr>
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
import settings
from libhtstego import get_kernel_list, htstego_errdiff, htstego_ordered, htstego_pattern, output_formatter

__version__ = '1.0'
settings.init()

if __name__ == '__main__':
    gui_parser = argparse.ArgumentParser(add_help=False)
    gui_parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    gui_parser.add_argument('--gui', action='store_true', help='switch to graphical user interface')

    args_first, args_second = gui_parser.parse_known_args()
    if args_first.gui:
        __import__('htstego-gui')
        sys.exit(0)

    parser = argparse.ArgumentParser(description=f'Halftone Steganography Utility Version {__version__}', parents=[gui_parser])

    args_required = parser.add_argument_group('Required Options')
    args_required.add_argument('--htmethod', type=str, required=True, choices=['errdiff', 'ordered', 'pattern'], help='halftoning method')
    args_required.add_argument('--cover', type=str, required=True, help='input image')
    args_required.add_argument('--payload', type=str, required=True, help='input payload')
    args_required.add_argument('--nshares', type=int, required=True, help='number of output shares to generate')

    args_errdiff = parser.add_argument_group('Error Diffusion Options')
    args_errdiff.add_argument('--kernel', type=str, choices=get_kernel_list(), help='error diffusion kernel (from kernels directory)')

    args_ordered = parser.add_argument_group('Ordered Dithering Options')
    args_ordered.add_argument('--bayer-size', type=int, choices=[2, 4, 8], default=8, help='Bayer matrix size')

    args_output = parser.add_argument_group('Output Options')
    args_output.add_argument('--no-output-files', action='store_true', help='do not produce output images')
    args_output.add_argument('--generate-regular-output', action='store_true', help='generate nonstego output image')
    args_output.add_argument('--output-color', type=str, choices=['binary', 'color'], default='binary', help='output color')
    args_output.add_argument('--output-format', default='json', type=str, choices=['csv', 'json', 'xml'], help='output format')
    args_output.add_argument('--silent', action='store_true', help='do not display output on screen')
    args_output.add_argument('--compress-payload', action='store_true', help='compress payload before embedding')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args(args_second)
    settings.nofileout = args.no_output_files if args.no_output_files else False
    settings.regularoutput = args.generate_regular_output if args.generate_regular_output else False
    settings.nostdout = args.silent if args.silent else False
    settings.outputformat = args.output_format if args.output_format else 'json'
    settings.compress = args.compress_payload if args.compress_payload else False

    if args.htmethod == 'errdiff' and not args.kernel:
        parser.error('--kernel is required when --htmethod is errdiff')
        sys.exit(1)

    if args.htmethod == 'ordered' and not args.bayer_size:
        parser.error('--bayer-size is required when --htmethod is ordered')
        sys.exit(1)

    if args.htmethod == 'errdiff':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_errdiff(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, errDiffMethod=args.kernel, outputMode=args.output_color)
    elif args.htmethod == 'ordered':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_ordered(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, bayerN=args.bayer_size, outputMode=args.output_color)
    elif args.htmethod == 'pattern':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_pattern(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, outputMode=args.output_color)

    if settings.nostdout == False:
        params = {
            'status': ret_msg,
            'halftoning_method': args.htmethod,
            'errdiff_kernel': args.kernel if args.htmethod == 'errdiff' else 'N/A',
            'bayer_size': args.bayer_size if args.htmethod == 'ordered' else 'N/A',
            'output_color': args.output_color,
            'number_of_shares': args.nshares,
            'cover_file': args.cover,
            'payload_file': args.payload,
            'payload_compression': settings.compress,
            'avg_snr': round(avg_snr, 4),
            'avg_psnr': round(avg_psnr, 4),
            'avg_ssim': round(avg_ssim, 4)
        }
        print(output_formatter(params, settings.outputformat))
