# Halftone Steganography and Extraction Utility
This is a steganography utility for generating stego images in halftone format and extracting payloads from such generated images. Detailed information about steganography, halftoning, and binary images can be accessed from the following Wikipedia pages:

- [Steganography](https://en.wikipedia.org/wiki/Steganography)
- [Binary image](https://en.wikipedia.org/wiki/Binary_image)
- [Digital halftoning](https://en.wikipedia.org/wiki/Halftone#Digital_halftoning)

The utility is designed to work with both color and grayscale images, serving as cover media. During the halftoning procedure, the utility embeds the desired plaintext payload within these images. The embedding process generates multiple output copies for enhanced security, each carrying a distinct set of payload bits. This strategy prevents unauthorized extraction attempts from succeeding without the need to gather all the created images. This security measure also brings an added benefit: the extraction algorithm relies only on the stego images, in contrast to specific other steganography methods where the original image is required during the extraction process.

The sample images provided in the "cover_imgs" directory are obtained from the "UC Merced Land Use Dataset" [1]. The text files in the "payloads" directory are generated randomly using Lorem Ipsum generator [2]. The error diffusion kernels in the "kernels" directory belong to Floyd-Steinberg [3], Jarvis-Judice-Ninke [4], and Stucki [5] algorithms. The files presented in these directories are for demonstration purposes only.

## Setup
To execute, the `numpy`, `scikit-image`, and `scipy` packages must be installed:

    pip install numpy scikit-image scipy

or

    pip install -r requirements.txt

## Payload Hiding
Available options for `htstego.py`:

      -h, --help                            show this help message and exit
      -v, --version                         show program's version number and exit
      --gui                                 switch to graphical user interface

Required Options:

      --htmethod {errdiff,ordered,pattern}  halftoning method
      --cover COVER                         input image
      --payload PAYLOAD                     input payload
      --nshares NSHARES                     number of output shares to generate

Error Diffusion Options:

      --kernel {stucki,floyd,jajuni}        error diffusion kernel (from kernels directory)

Ordered Dithering Options:

      --bayer-size {2,4,8}                  Bayer matrix size

Output Options:

      --no-output-files                     do not produce output images
      --generate-regular-output             generate nonstego output image
      --output-color {binary,color}         output color
      --output-format {csv,json,xml}        output format
      --silent                              do not display output on screen
      --compress-payload                    compress payload before embedding

### Example

      cd src
      ./htstego.py --cover cover_imgs/airplane80.tif --payload payloads/payload128.txt --nshares 4 --htmethod errdiff --kernel floyd

When executed as above, the following output will be displayed:

      {"status": "ok", "halftoning_method": "errdiff", "errdiff_kernel": "floyd", "bayer_size": "N/A", "output_color": "binary", "number_of_shares": 4, "cover_file": "cover_imgs/airplane80.tif", "payload_file": "payloads/payload128.txt", "payload_compression": false, "avg_snr": 21.8918, "avg_psnr": 24.0863, "avg_ssim": 0.9916}

and the following files will be created in a timestamped subdirectory under the output directory:

      airplane80_hterrdiffbin_stego_msg128_1of4_floyd.png
      airplane80_hterrdiffbin_stego_msg128_2of4_floyd.png
      airplane80_hterrdiffbin_stego_msg128_3of4_floyd.png
      airplane80_hterrdiffbin_stego_msg128_4of4_floyd.png

where each file is a stego image carrying different portions of the payload.

## Payload Extraction
Available options for `htstego-extract.py`:

      -h, --help                            show this help message and exit
      -v, --version                         show program's version number and exit
      --gui                                 switch to graphical user interface
      --extract-from EXTRACT_FROM           extract from images in this directory
      --htmethod {errdiff,ordered,pattern}  halftoning method

The directory specified with the `--extract-from` argument must contain only and only a single set of carrier images (e.g., the timestamped subdirectories under the `output` directory). `--htmethod` option must be used to specify which extraction method will be used.

### Example

      cd src
      ./htstego-extract.py --htmethod errdiff --extract-from output/2024-03-05-14-06-40-0/

Assuming the specified directory contains the whole set of images generated with the error diffusion method, the following output will be produced:

      Result: Donec ut mauris sit amet ...

## Graphical User Interface

Both utilities can also be used via a simple graphical user interface (`htstego-gui.py` and `htstego-extract-gui.py`). For GNU/Linux distributions such as Debian or Ubuntu, `python3-tk` package (and its dependencies) must be installed. For other distributions, please refer to the distribution documentation.

![htstego-gui](https://github.com/efeciftci/htstego/assets/3438150/e36e9874-bda1-4732-bc13-ca22f8cbb7dd)

![htstego-extract-gui](https://github.com/efeciftci/htstego/assets/3438150/9e86ad47-44a2-46a5-8568-e096d0b2d1a2)

## References
[1] Yi Yang and Shawn Newsam, "Bag-Of-Visual-Words and Spatial Extensions for Land-Use Classification," ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems (ACM GIS), 2010.

[2] Lorem Ipsum generator. https://www.lipsum.com/

[3] R.W. Floyd, L. Steinberg, An adaptive algorithm for spatial grey scale. Proceedings of the Society of Information Display 17, 75–77 (1976)

[4] J. F. Jarvis, C. N. Judice and W. H. Ninke, A Survey of Techniques for the Display of Continuous Tone Pictures on Bi-level Displays. Computer Graphics and Image Processing, 5 13–40, 1976.

[5] P. Stucki, MECCA - a multiple error correcting computation algorithm for bi-level image hard copy reproduction. Research report RZ1060, IBM Research Laboratory, Zurich, Switzerland, 1981.
