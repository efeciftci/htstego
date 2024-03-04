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

import settings
from libhtstego import get_kernel_list, htstego_errdiff, htstego_ordered, htstego_pattern, output_formatter
import tkinter as tk
from tkinter import filedialog, ttk

__version__ = '1.0'
settings.init()


def update_htoptions():
    if htmethod_var.get() == 'errdiff':
        errdiffmethod_drop.config(state=tk.NORMAL)
        bayersize_drop.config(state=tk.DISABLED)
    if htmethod_var.get() == 'ordered':
        errdiffmethod_drop.config(state=tk.DISABLED)
        bayersize_drop.config(state=tk.NORMAL)
    if htmethod_var.get() == 'pattern':
        errdiffmethod_drop.config(state=tk.DISABLED)
        bayersize_drop.config(state=tk.DISABLED)


def update_noregularoutput_state():
    if nooutputfiles_var.get() == 0:
        regularoutput_check.config(state=tk.NORMAL)
    else:
        regularoutput_check.config(state=tk.DISABLED)


def browse_cover_image():
    cover_image_path = filedialog.askopenfilename(initialdir='.', filetypes=[('Image files', '*.jpg *.jpeg *.png *.bmp *.tif')])
    cover_entry.delete(0, tk.END)
    cover_entry.insert(0, cover_image_path)


def browse_payload():
    payload_path = filedialog.askopenfilename(initialdir='.', filetypes=[('Text files', '*.txt')])
    payload_entry.delete(0, tk.END)
    payload_entry.insert(0, payload_path)


def generate_output():
    settings.nofileout = bool(nooutputfiles_var.get())
    settings.regularoutput = bool(regularoutput_var.get())
    settings.nostdout = False
    settings.outputformat = outputformat_var.get()
    settings.compress = compress_var.get()

    result_text.delete(1.0, tk.END)
    if htmethod_var.get() == 'errdiff':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_errdiff(NSHARES=int(nshares_entry.get()), coverFile=cover_entry.get(), payloadFile=payload_entry.get(), errDiffMethod=errdiffmethod_var.get(), outputMode=outputmode_var.get())
    elif htmethod_var.get() == 'ordered':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_ordered(NSHARES=int(nshares_entry.get()), coverFile=cover_entry.get(), payloadFile=payload_entry.get(), bayerN=int(bayersize_var.get()), outputMode=outputmode_var.get())
    else:
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_pattern(NSHARES=int(nshares_entry.get()), coverFile=cover_entry.get(), payloadFile=payload_entry.get(), outputMode=outputmode_var.get())
    params = {
        'status': ret_msg,
        'halftoning_method': htmethod_var.get(),
        'errdiff_kernel': errdiffmethod_var.get() if htmethod_var.get() == 'errdiff' else 'N/A',
        'bayer_size': bayersize_var.get() if htmethod_var.get() == 'ordered' else 'N/A',
        'output_mode': outputmode_var.get(),
        'number_of_shares': nshares_entry.get(),
        'cover_file': cover_entry.get(),
        'payload_file': payload_entry.get(),
        'payload_compression': settings.compress,
        'avg_snr': round(avg_snr, 4),
        'avg_psnr': round(avg_psnr, 4),
        'avg_ssim': round(avg_ssim, 4)
    }
    result_text.insert(tk.END, output_formatter(params, settings.outputformat))


w = tk.Tk()
w.title('Halftone Steganography Tool')
w.resizable(False, False)

f = tk.Frame(w)
f.grid(padx=5, sticky='we')

htoptions_frame = ttk.LabelFrame(f, text='Halftoning Method')
htoptions_frame.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)

htmethod_var = tk.StringVar()
htmethod_var.set('errdiff')

htmethod_errdiff_radio = tk.Radiobutton(htoptions_frame, text='Error Diffusion', variable=htmethod_var, value='errdiff', command=update_htoptions)
htmethod_errdiff_radio.grid(row=0, column=0, sticky='w')

htmethod_pattern_radio = tk.Radiobutton(htoptions_frame, text='Ordered Dithering', variable=htmethod_var, value='ordered', command=update_htoptions)
htmethod_pattern_radio.grid(row=1, column=0, sticky='w')

htmethod_pattern_radio = tk.Radiobutton(htoptions_frame, text='Pattern', variable=htmethod_var, value='pattern', command=update_htoptions)
htmethod_pattern_radio.grid(row=2, column=0, sticky='w')

errdiffmethod_frame = tk.LabelFrame(f, text='Halftoning Options', padx=5)
errdiffmethod_frame.grid(row=0, column=1, sticky='nswe', padx=5, pady=5)

errdiff_kernels = get_kernel_list()
errdiffmethod_var = tk.StringVar()
errdiffmethod_var.set(errdiff_kernels[0])

errdiffmethod_label = tk.Label(errdiffmethod_frame, text='Kernel:')
errdiffmethod_label.grid(row=0, column=0, sticky='w')

errdiffmethod_drop = tk.OptionMenu(errdiffmethod_frame, errdiffmethod_var, *errdiff_kernels)
errdiffmethod_drop.grid(row=0, column=1, sticky='we')

bayersizes = [2, 4, 8]
bayersize_var = tk.StringVar()
bayersize_var.set(8)

bayersize_label = tk.Label(errdiffmethod_frame, text='Bayer Size:')
bayersize_label.grid(row=1, column=0, sticky='w')

bayersize_drop = tk.OptionMenu(errdiffmethod_frame, bayersize_var, *bayersizes)
bayersize_drop.grid(row=1, column=1, sticky='we')
bayersize_drop.config(state=tk.DISABLED)

cover_frame = tk.LabelFrame(f, text='Cover Image')
cover_frame.grid(row=1, column=0, sticky='nswe', padx=5, pady=5, ipadx=5, ipady=5)

cover_entry = tk.Entry(cover_frame)
cover_entry.pack(side=tk.LEFT, expand=True, fill='x', padx=5)

cover_button = tk.Button(cover_frame, text='Browse...', command=browse_cover_image)
cover_button.pack(side=tk.RIGHT, padx=5)

payload_frame = tk.LabelFrame(f, text='Payload')
payload_frame.grid(row=1, column=1, sticky='nswe', padx=5, pady=5, ipadx=5, ipady=5)

payload_entry = tk.Entry(payload_frame)
payload_entry.pack(side=tk.LEFT, expand=True, fill='x', padx=5)

payload_button = tk.Button(payload_frame, text='Browse...', command=browse_payload)
payload_button.pack(side=tk.RIGHT, padx=5)

output_mode_frame = tk.LabelFrame(f, text='Output Mode')
output_mode_frame.grid(row=2, column=0, sticky='nswe', padx=5, pady=5)

outputmode_var = tk.StringVar()
outputmode_var.set('binary')

outputmode_binary = tk.Radiobutton(output_mode_frame, text='Binary', variable=outputmode_var, value='binary')
outputmode_binary.grid(row=0, column=0)

outputmode_color = tk.Radiobutton(output_mode_frame, text='Color', variable=outputmode_var, value='col')
outputmode_color.grid(row=0, column=1)

nshares_frame = tk.LabelFrame(f, text='Number of Shares')
nshares_frame.grid(row=2, column=1, sticky='nswe', padx=5, pady=5, ipadx=5, ipady=5)

nshares_entry = tk.Spinbox(nshares_frame, from_=3, to=100, textvariable=tk.IntVar(value=4))
nshares_entry.grid(row=0, column=0, padx=5)

options_frame = tk.LabelFrame(f, text='Options')
options_frame.grid(row=3, column=0, sticky='nswe', padx=5, pady=5)

nooutputfiles_var = tk.IntVar()
nooutputfiles_check = tk.Checkbutton(options_frame, text='Do not generate output files', variable=nooutputfiles_var, command=update_noregularoutput_state)
nooutputfiles_check.grid(row=0, column=0, sticky='w')

regularoutput_var = tk.IntVar()
regularoutput_check = tk.Checkbutton(options_frame, text='Generate regular output file', variable=regularoutput_var)
regularoutput_check.grid(row=1, column=0, sticky='w')

compress_var = tk.IntVar()
compress_check = tk.Checkbutton(options_frame, text='Compress payload before embedding', variable=compress_var)
compress_check.grid(row=2, column=0, sticky='w')

outputformat_frame = tk.LabelFrame(f, text='Output Format')
outputformat_frame.grid(row=3, column=1, sticky='nwe', padx=5, pady=5)

outputformat_var = tk.StringVar()
outputformat_var.set('json')

outputformat_csv = tk.Radiobutton(outputformat_frame, text='CSV', variable=outputformat_var, value='csv')
outputformat_csv.grid(row=0, column=0, sticky='w')

outputformat_json = tk.Radiobutton(outputformat_frame, text='JSON', variable=outputformat_var, value='json')
outputformat_json.grid(row=1, column=0, sticky='w')

outputformat_xml = tk.Radiobutton(outputformat_frame, text='XML', variable=outputformat_var, value='xml')
outputformat_xml.grid(row=2, column=0, sticky='w')

start_button = tk.Button(f, text='Start', command=generate_output)
start_button.grid(row=4, column=0, pady=5, columnspan=2)

result_frame = tk.LabelFrame(f, text='Results')
result_frame.grid(row=5, column=0, columnspan=2, sticky='we', padx=5, pady=5)

result_text = tk.Text(result_frame, height=7)
result_text.grid(row=0, column=0, sticky='we')

w.mainloop()
