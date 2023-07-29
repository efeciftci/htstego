#!/usr/bin/env python3
import argparse, sys
from libhtstego import htstego_errdiffbin

__version__ = '0.4'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Halftone Steganography Utility Version {__version__}')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    
    args_required = parser.add_argument_group('Required Options')
    args_required.add_argument('--htmethod', type=str, required=True, help='halftoning method (pattern, errdiff)')
    args_required.add_argument('--htmethodtype', type=str, required=True, help='halftoning type (binary, color)')
    args_required.add_argument('--cover', type=str, required=True, help='input image')
    args_required.add_argument('--payload', type=int, required=True, help='input payload')
    args_required.add_argument('--nshares', type=int, required=True, help='number of output shares to generate')
    
    args_errdiff = parser.add_argument_group('Error Diffusion Options')
    args_errdiff.add_argument('--errdiffmethod', type=str, help='error diffusion method (fan, floyd, or jajuni)')
    
    args_optional = parser.add_argument_group('Output Options')
    args_optional.add_argument('--no-output-files', action='store_true', help='do not produce output images')
    args_optional.add_argument('--output-format', type=str, help='output format (default, json)')
    args_optional.add_argument('--silent', action='store_true', help='do not display output on screen')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if args.htmethod == 'errdiff' and args.htmethodtype == 'binary':
        if args.errdiffmethod:
            [avg_snr, avg_psnr, avg_ssim] = htstego_errdiffbin(NSHARES=args.nshares,
                                            imparam=args.cover,
                                            txtparam=args.payload,
                                            errdiffmethod=args.errdiffmethod,
                                            nofileout=args.no_output_files)
            if args.silent == False:
                if args.output_format == 'json':
                    import json
                    print(
                        json.dumps({
                            'method': 'erdbin',
                            'nshares': args.nshares,
                            'imparam': args.cover,
                            'txtparam': args.payload,
                            'avg_snr': round(avg_snr, 4),
                            'avg_psnr': round(avg_psnr, 4),
                            'avg_ssim': round(avg_ssim, 4)
                        }))
                else:
                    print(f'[erdbin] [{args.nshares} {args.cover} {args.payload}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]')
        else:
            parser.error('--errdiffmethod is required when --htmethod is errdiff')
    else:  #errdiffcol, patbin, patcol
        print('Not yet implemented!')
