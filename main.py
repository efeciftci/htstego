#!/usr/bin/env python3
import argparse
from libhtstego import *

VERSION = '0.0.2'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=f'Halftone steganography utility version {VERSION}')
    parser.add_argument(
        '--htmethod',
        type=str,
        default='errdiff',
        help='halftoning method (pattern, errdiff) (default=errdiff)')
    parser.add_argument(
        '--htmethodtype',
        type=str,
        default='binary',
        help='halftoning type (binary, color) (default=binary)')
    parser.add_argument('--nshares',
                        type=int,
                        default=4,
                        help='number of output shares to generate (default=4)')
    parser.add_argument('--imparam',
                        type=str,
                        default='airplane80',
                        help='input image (default=airplane80)')
    parser.add_argument('--txtparam',
                        type=int,
                        default=512,
                        help='input payload (default=512)')
    parser.add_argument(
        '--method',
        type=str,
        default='floyd',
        help='error diffusion method (fan, floyd, or jajuni) (default=floyd)')
    parser.add_argument('--no-output',
                        action='store_true',
                        help='do not produce output images (default=false)')
    args = parser.parse_args()

    if args.htmethod == 'errdiff' and args.htmethodtype == 'binary':
        [avg_snr, avg_psnr,
         avg_ssim] = htstego_errdiffbin(NSHARES=args.nshares,
                                        imparam=args.imparam,
                                        txtparam=args.txtparam,
                                        errdiffmethod=args.method,
                                        nooutput=args.no_output)
        print(
            f'[erdbin] [{args.nshares:2d} {args.imparam:10s} {args.txtparam:4d}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]'
        )
    else:  #errdiffcol, patbin, patcol
        print('Not yet implemented!')
