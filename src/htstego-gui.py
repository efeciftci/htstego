#!/usr/bin/env python3

# libhtstego - Halftone Steganography Utility
#
# Copyright (C) 2023 by Efe Çiftci <efeciftci@cankaya.edu.tr>
# Copyright (C) 2023 by Emre Sümer <esumer@baskent.edu.tr>
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
from libhtstego import htstego_errdiff, htstego_pattern, output_formatter
import tkinter as tk
from tkinter import filedialog, ttk

__version__ = '1.0'
settings.init()


def update_errdiffmethod_state():
    if htmethod_var.get() == 'errdiff':
        errdiffmethod_fan.config(state=tk.NORMAL)
        errdiffmethod_floyd.config(state=tk.NORMAL)
        errdiffmethod_jajuni.config(state=tk.NORMAL)
    else:
        errdiffmethod_fan.config(state=tk.DISABLED)
        errdiffmethod_floyd.config(state=tk.DISABLED)
        errdiffmethod_jajuni.config(state=tk.DISABLED)


def update_noregularoutput_state():
    if nooutputfiles_var.get() == 0:
        noregularoutput_check.config(state=tk.NORMAL)
    else:
        noregularoutput_check.config(state=tk.DISABLED)


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

    result_text.delete(1.0, tk.END)
    if htmethod_var.get() == 'errdiff':
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_errdiff(NSHARES=int(nshares_entry.get()), coverFile=cover_entry.get(), payloadFile=payload_entry.get(), errdiffmethod=errdiffmethod_var.get(), outputMode=outputmode_var.get())
    else:
        ret_msg, avg_snr, avg_psnr, avg_ssim = htstego_pattern(NSHARES=int(nshares_entry.get()), coverFile=cover_entry.get(), payloadFile=payload_entry.get(), outputMode=outputmode_var.get())
    params = {
        'status': ret_msg,
        'halftoning_method': htmethod_var.get(),
        'output_mode': outputmode_var.get(),
        'number_of_shares': nshares_entry.get(),
        'cover_file': cover_entry.get(),
        'payload_file': payload_entry.get(),
        'avg_snr': round(avg_snr, 4),
        'avg_psnr': round(avg_psnr, 4),
        'avg_ssim': round(avg_ssim, 4)
    }
    result_text.insert(tk.END, output_formatter(params, settings.outputformat))


w = tk.Tk()
w.title('Halftone Steganography Tool')
w.resizable(False, False)

f = tk.Frame(w)
f.grid(padx=5,sticky='we')

htmethod_frame = ttk.LabelFrame(f, text='Halftone Method')
htmethod_frame.grid(column=0, row=0, sticky='we', padx=5, pady=5)

htmethod_var = tk.StringVar()
htmethod_var.set('errdiff')

htmethod_errdiff_radio = tk.Radiobutton(htmethod_frame, text='Error Diffusion', variable=htmethod_var, value='errdiff', command=update_errdiffmethod_state)
htmethod_errdiff_radio.grid(column=0, row=0)

htmethod_pattern_radio = tk.Radiobutton(htmethod_frame, text='Pattern', variable=htmethod_var, value='pattern', command=update_errdiffmethod_state)
htmethod_pattern_radio.grid(column=1, row=0)

errdiffmethod_frame = tk.LabelFrame(f, text='Error Diffusion Method')
errdiffmethod_frame.grid(column=1, row=0, sticky='we', padx=5, pady=5)

errdiffmethod_var = tk.StringVar()
errdiffmethod_var.set('fan')

errdiffmethod_fan = tk.Radiobutton(errdiffmethod_frame, text='Fan', variable=errdiffmethod_var, value='fan')
errdiffmethod_fan.grid(column=0, row=0)

errdiffmethod_floyd = tk.Radiobutton(errdiffmethod_frame, text='Floyd', variable=errdiffmethod_var, value='floyd')
errdiffmethod_floyd.grid(column=1, row=0)

errdiffmethod_jajuni = tk.Radiobutton(errdiffmethod_frame, text='JaJuNi', variable=errdiffmethod_var, value='jajuni')
errdiffmethod_jajuni.grid(column=2, row=0)

output_mode_frame = tk.LabelFrame(f, text='Output Mode')
output_mode_frame.grid(column=0, row=1, sticky='we', padx=5, pady=5)

outputmode_var = tk.StringVar()
outputmode_var.set('binary')

outputmode_binary = tk.Radiobutton(output_mode_frame, text='Binary', variable=outputmode_var, value='binary')
outputmode_binary.grid(column=0, row=0)

outputmode_color = tk.Radiobutton(output_mode_frame, text='Color', variable=outputmode_var, value='col')
outputmode_color.grid(column=1, row=0)

nshares_frame = tk.LabelFrame(f, text='Number of Shares')
nshares_frame.grid(column=1, row=1, sticky='we', padx=5, pady=5)

nshares_entry = tk.Entry(nshares_frame)
nshares_entry.grid(column=0, row=0)

cover_frame = tk.LabelFrame(f, text='Cover Image')
cover_frame.grid(column=0, row=2, sticky='we', padx=5, pady=5)

cover_entry = tk.Entry(cover_frame)
cover_entry.pack(side=tk.LEFT, expand=True, fill='x')

cover_button = tk.Button(cover_frame, text='Browse...', command=browse_cover_image)
cover_button.pack(side=tk.RIGHT)

payload_frame = tk.LabelFrame(f, text='Payload')
payload_frame.grid(column=1, row=2, sticky='we', padx=5, pady=5)

payload_entry = tk.Entry(payload_frame)
payload_entry.pack(side=tk.LEFT, expand=True, fill='x')

payload_button = tk.Button(payload_frame, text='Browse...', command=browse_payload)
payload_button.pack(side=tk.RIGHT)

options_frame = tk.LabelFrame(f, text='Options')
options_frame.grid(column=0, row=3, sticky='we', padx=5, pady=5)

nooutputfiles_var = tk.IntVar()
nooutputfiles_check = tk.Checkbutton(options_frame, text='Do not generate output files', variable=nooutputfiles_var, command=update_noregularoutput_state)
nooutputfiles_check.grid(column=0, row=0, sticky='w')

regularoutput_var = tk.IntVar()
regularoutput_check = tk.Checkbutton(options_frame, text='Generate regular output file', variable=regularoutput_var)
regularoutput_check.grid(column=0, row=1, sticky='w')

outputformat_frame = tk.LabelFrame(f, text='Output Format')
outputformat_frame.grid(column=1, row=3, sticky='wne', padx=5, pady=5)

outputformat_var = tk.StringVar()
outputformat_var.set('json')

outputformat_json = tk.Radiobutton(outputformat_frame, text='JSON', variable=outputformat_var, value='json')
outputformat_json.grid(column=0, row=0)

outputformat_csv = tk.Radiobutton(outputformat_frame, text='CSV', variable=outputformat_var, value='csv')
outputformat_csv.grid(column=1, row=0)

outputformat_xml = tk.Radiobutton(outputformat_frame, text='XML', variable=outputformat_var, value='xml')
outputformat_xml.grid(column=2, row=0)

start_button = tk.Button(f, text='Start', command=generate_output)
start_button.grid(column=0, row=5, pady=5, columnspan=2)

result_frame = tk.LabelFrame(f, text='Results')
result_frame.grid(column=0, row=6, columnspan=2, sticky='we', padx=5, pady=5)

result_text = tk.Text(result_frame, height=7)
result_text.grid(column=0, row=0, sticky='we')

w.mainloop()
