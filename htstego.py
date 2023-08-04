#!/usr/bin/env python3
import argparse, sys, settings
from libhtstego import htstego_errdiffbin, htstego_errdiffcol, htstego_patbin, htstego_patcol

__version__ = '0.5'

settings.init()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Halftone Steganography Utility Version {__version__}')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    args_required = parser.add_argument_group('Required Options')
    args_required.add_argument('--htmethod', type=str, required=True, help='halftoning method (pattern, errdiff)')
    args_required.add_argument('--colormode', type=str, required=True, help='halftoning type (binary, color)')
    args_required.add_argument('--cover', type=str, required=True, help='input image')
    args_required.add_argument('--payload', type=str, required=True, help='input payload')
    args_required.add_argument('--nshares', type=int, required=True, help='number of output shares to generate')

    args_errdiff = parser.add_argument_group('Error Diffusion Options')
    args_errdiff.add_argument('--errdiffmethod', type=str, help='error diffusion method (fan, floyd, or jajuni)')

    args_optional = parser.add_argument_group('Output Options')
    args_optional.add_argument('--no-output-files', action='store_true', help='do not produce output images')
    args_optional.add_argument('--output-format', default='default', type=str, help='output format (default, json)')
    args_optional.add_argument('--silent', action='store_true', help='do not display output on screen')

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

    if args.htmethod == 'errdiff' and args.colormode == 'binary':
        m, [avg_snr, avg_psnr, avg_ssim] = 'erdbin', htstego_errdiffbin(NSHARES=args.nshares, imparam=args.cover, payloadFile=args.payload, errdiffmethod=args.errdiffmethod)
    elif args.htmethod == 'errdiff' and args.colormode == 'color':
        m, [avg_snr, avg_psnr, avg_ssim] = 'erdcol', htstego_errdiffcol(NSHARES=args.nshares, imparam=args.cover, payloadFile=args.payload, errdiffmethod=args.errdiffmethod)
    elif args.htmethod == 'pattern' and args.colormode == 'binary':
        m, [avg_snr, avg_psnr, avg_ssim] = 'patbin', htstego_patbin(NSHARES=args.nshares, imparam=args.cover, payloadFile=args.payload)
    elif args.htmethod == 'pattern' and args.colormode == 'color':
        m, [avg_snr, avg_psnr, avg_ssim] = 'patcol', htstego_patcol(NSHARES=args.nshares, imparam=args.cover, payloadFile=args.payload)
    else:
        print('Incorrect method selection!')
        sys.exit(1)

    if settings.nostdout == False:
        if settings.outputformat == 'json':
            import json
            print(json.dumps({
                    'method': m,
                    'nshares': args.nshares,
                    'imparam': args.cover,
                    'txtparam': args.payload,
                    'avg_snr': round(avg_snr, 4),
                    'avg_psnr': round(avg_psnr, 4),
                    'avg_ssim': round(avg_ssim, 4)}))
        else:
            print(f'[{m}] [{args.nshares} {args.cover} {args.payload}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]')
