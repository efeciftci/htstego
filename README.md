
# Halftone Steganography Utility
This is a tool for generating stego images in binary format. You may check the following Wikipedia pages for detailed information:

- [Steganography](https://en.wikipedia.org/wiki/Steganography)
- [Binary image](https://en.wikipedia.org/wiki/Binary_image)
- [Digital halftoning](https://en.wikipedia.org/wiki/Halftone#Digital_halftoning)

## Setup
In order to execute, you must have the `numpy` and `scikit-image` packages installed:

    pip install numpy scikit-image

or

    pip install -r requirements.txt

## How To Use
This tool comes with the following parameters:

      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      --htmethod HTMETHOD   halftoning method (pattern, errdiff) (default: errdiff)
      --htmethodtype HTMETHODTYPE
                            halftoning type (binary, color) (default: binary)
      --nshares NSHARES     number of output shares to generate (default: 4)
      --imparam IMPARAM     input image (default: airplane80)
      --txtparam TXTPARAM   input payload (default: 512)
      --errdiffmethod ERRDIFFMETHOD
                            error diffusion method (fan, floyd, or jajuni) (default: floyd)
      --no-output-files     do not produce output images (default: false)
      --json                display output in JSON format

Executing the tool as below uses the default parameters listed above:

      ./main.py
    
When executed as above, the following output will be produced:

      [erdbin] [4 airplane80 512] [avg_snr: 15.8997] [avg_psnr: 18.0689] [avg_ssim: 0.9659]
      
and the following files will be created:

      output/airplane80_256gray_hterrdiffbin_regular_floyd.png
      output/airplane80_256gray_hterrdiffbin_stego_msg512_1of4_floyd.png
      output/airplane80_256gray_hterrdiffbin_stego_msg512_2of4_floyd.png
      output/airplane80_256gray_hterrdiffbin_stego_msg512_3of4_floyd.png
      output/airplane80_256gray_hterrdiffbin_stego_msg512_4of4_floyd.png

where the "regular" is the file with no payloads and the others are carrier images with different portions of the payload.

## Future

- XML output
- Color error diffusion method
- Binary pattern-based method
- Color pattern-based method
- Ordered dithering method
