
# Halftone Steganography and Extraction Utility
This is a tool for generating stego images in binary format and extracting payloads from generated images. You may check the following Wikipedia pages for detailed information:

- [Steganography](https://en.wikipedia.org/wiki/Steganography)
- [Binary image](https://en.wikipedia.org/wiki/Binary_image)
- [Digital halftoning](https://en.wikipedia.org/wiki/Halftone#Digital_halftoning)

## Setup
In order to execute, you must have the `numpy`, `scikit-image` and `scipy` packages installed:

    pip install numpy scikit-image scipy

or

    pip install -r requirements.txt

## Payload Hiding
Available options for `htstego.py`:

      -h, --help                          show this help message and exit
      -v, --version                       show program's version number and exit

Required Options:

      --htmethod {pattern,errdiff}        halftoning method
      --output-mode {binary,color}        output mode
      --cover COVER                       input image
      --payload PAYLOAD                   input payload
      --nshares NSHARES                   number of output shares to generate

Error Diffusion Options:

      --errdiffmethod {fan,floyd,jajuni}  error diffusion method

Output Options:

      --no-output-files                   do not produce output images
      --output-format OUTPUT_FORMAT       output format (default, json)
      --silent                            do not display output on screen

### Example

      ./htstego.py --htmethod errdiff --errdiffmethod floyd --cover airplane80_256rgb.png --payload payload512.txt --nshares 4 --output-mode binary 
    
When executed as above, the following output will be produced:

      [erdbin] [4 airplane80_256rgb.png payload512.txt] [avg_snr: 15.8741] [avg_psnr: 18.0685] [avg_ssim: 0.9661]
      
and the following files will be created:

      output/airplane80_256rgb_hterrdiffbin_regular_floyd.png
      output/airplane80_256rgb_hterrdiffbin_stego_msg512_1of4_floyd.png
      output/airplane80_256rgb_hterrdiffbin_stego_msg512_2of4_floyd.png
      output/airplane80_256rgb_hterrdiffbin_stego_msg512_3of4_floyd.png
      output/airplane80_256rgb_hterrdiffbin_stego_msg512_4of4_floyd.png

where the "regular" is the file with no payloads and the others are carrier images with different portions of the payload.

## Payload Extraction
Available options for `htstego-extract.py`:

      -h, --help                          show this help message and exit
      -v, --version                       show program's version number and exit
      --extract-from EXTRACT_FROM         extract from images in this directory
      --htmethod {pattern,errdiff}        halftoning method

By default, images in `output` directory will be used for extraction but this can be overridden with `--extract-from`. This directory must contain only and only the carrier images. `--htmethod` must be used to specify which extraction method will be used.

## Future

- XML output
- Ordered dithering method
- A graphical user interface
