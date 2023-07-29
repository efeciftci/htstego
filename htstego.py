#!/usr/bin/env python3
import argparse
from libhtstego import htstego_errdiffbin

__version__ = '0.3'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=f'Halftone Steganography Utility Version {__version__}',
        prog='Halftone Steganography Utility')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=f'%(prog)s {__version__}')
    parser.add_argument(
        '--htmethod',
        type=str,
        default='errdiff',
        help='halftoning method (pattern, errdiff) (default: errdiff)')
    parser.add_argument(
        '--htmethodtype',
        type=str,
        default='binary',
        help='halftoning type (binary, color) (default: binary)')
    parser.add_argument(
        '--nshares',
        type=int,
        default=4,
        help='number of output shares to generate (default: 4)')
    parser.add_argument('--imparam',
                        type=str,
                        default='airplane80',
                        help='input image (default: airplane80)')
    parser.add_argument('--txtparam',
                        type=int,
                        default=512,
                        help='input payload (default: 512)')
    parser.add_argument(
        '--errdiffmethod',
        type=str,
        default='floyd',
        help='error diffusion method (fan, floyd, or jajuni) (default: floyd)')
    parser.add_argument('--no-output-files',
                        action='store_true',
                        help='do not produce output images (default: false)')
    parser.add_argument('--json',
                        action='store_true',
                        help='display output in JSON format')
    args = parser.parse_args()

    if args.htmethod == 'errdiff' and args.htmethodtype == 'binary':
        [avg_snr, avg_psnr,
         avg_ssim] = htstego_errdiffbin(NSHARES=args.nshares,
                                        imparam=args.imparam,
                                        txtparam=args.txtparam,
                                        errdiffmethod=args.errdiffmethod,
                                        nooutput=args.no_output_files)
        if args.json:
            import json
            print(
                json.dumps({
                    "method": "erdbin",
                    "nshares": args.nshares,
                    "imparam": args.imparam,
                    "txtparam": args.txtparam,
                    "avg_snr": round(avg_snr, 4),
                    "avg_psnr": round(avg_psnr, 4),
                    "avg_ssim": round(avg_ssim, 4)
                }))
        else:
            print(
                f'[erdbin] [{args.nshares} {args.imparam} {args.txtparam}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]'
            )
    else:  #errdiffcol, patbin, patcol
        print('Not yet implemented!')
