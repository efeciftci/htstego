#!/usr/bin/env python3
import argparse
import sys
import settings
from libhtstego import htstego_errdiff, htstego_pattern

__version__ = '0.8'
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
    args_output.add_argument('--output-format', default='default', type=str, choices=['default', 'json'], help='output format')
    args_output.add_argument('--silent', action='store_true', help='do not display output on screen')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if args.no_output_files:
        settings.nofileout = args.no_output_files
    if args.output_format:
        settings.outputformat = args.output_format
    if args.silent:
        settings.nostdout = args.silent

    settings.nofileout = args.no_output_files if args.no_output_files else False
    settings.nostdout = args.silent if args.silent else False
    settings.outputformat = args.output_format if args.output_format else 'default'

    if args.htmethod == 'errdiff' and not args.errdiffmethod:
        parser.error('--errdiffmethod is required when --htmethod is errdiff')
        sys.exit(1)

    if args.htmethod == 'errdiff':
        m, [avg_snr, avg_psnr, avg_ssim] = 'erdbin', htstego_errdiff(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, errdiffmethod=args.errdiffmethod, outputMode=args.output_mode)
    elif args.htmethod == 'pattern':
        m, [avg_snr, avg_psnr, avg_ssim] = 'patcol', htstego_pattern(NSHARES=args.nshares, coverFile=args.cover, payloadFile=args.payload, outputMode=args.output_mode)

    if settings.nostdout == False:
        if settings.outputformat == 'json':
            import json
            print(
                json.dumps({
                    'method': m,
                    'nshares': args.nshares,
                    'coverFile': args.cover,
                    'payloadFile': args.payload,
                    'avg_snr': round(avg_snr, 4),
                    'avg_psnr': round(avg_psnr, 4),
                    'avg_ssim': round(avg_ssim, 4)
                }))
        else:
            print(f'[{m}] [{args.nshares} {args.cover} {args.payload}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]')
