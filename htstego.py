#!/usr/bin/env python3
import argparse
import sys
import settings
from libhtstego import htstego_errdiff, htstego_pattern, output_formatter

__version__ = '1.0'
settings.init()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Halftone Steganography Utility Version {__version__}')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    args_required = parser.add_argument_group('Required Options')
    args_required.add_argument('--htmethod', type=str, required=True, choices=['pattern', 'errdiff'], help='halftoning method')
    args_required.add_argument('--output-mode', type=str, required=True, choices=['binary', 'color'], help='output mode')
    args_required.add_argument('--cover', type=str, required=True, help='input image')
    args_required.add_argument('--payload', type=str, required=True, help='input payload')
    args_required.add_argument('--nshares', type=int, required=True, help='number of output shares to generate')

    args_errdiff = parser.add_argument_group('Error Diffusion Options')
    args_errdiff.add_argument('--errdiffmethod', type=str, choices=['fan', 'floyd', 'jajuni'], help='error diffusion method')

    args_output = parser.add_argument_group('Output Options')
    args_output.add_argument('--no-output-files', action='store_true', help='do not produce output images')
    args_output.add_argument('--no-regular-output', action='store_true', help='do not produce regular output image')
    args_output.add_argument('--output-format', default='json', type=str, choices=['csv', 'json', 'xml'], help='output format')
    args_output.add_argument('--silent', action='store_true', help='do not display output on screen')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    settings.nofileout = args.no_output_files if args.no_output_files else False
    settings.noregularoutput = args.no_regular_output if args.no_regular_output else False
    settings.nostdout = args.silent if args.silent else False
    settings.outputformat = args.output_format if args.output_format else 'json'

    if args.htmethod == 'errdiff' and not args.errdiffmethod:
        parser.error('--errdiffmethod is required when --htmethod is errdiff')
        sys.exit(1)

    if args.htmethod == 'errdiff':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_errdiff(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, errdiffmethod=args.errdiffmethod, outputMode=args.output_mode)
    elif args.htmethod == 'pattern':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_pattern(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, outputMode=args.output_mode)

    if settings.nostdout == False:
        params = {
            'status': ret_msg,
            'halftoning_method': args.htmethod,
            'output_mode': args.output_mode,
            'number_of_shares': args.nshares,
            'cover_file': args.cover,
            'payload_file': args.payload,
            'avg_snr': round(avg_snr, 4),
            'avg_psnr': round(avg_psnr, 4),
            'avg_ssim': round(avg_ssim, 4)
        }
        print(output_formatter(params, settings.outputformat))
