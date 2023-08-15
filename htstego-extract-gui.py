#!/usr/bin/env python3
from libhtstego import htstego_errdiff_extract, htstego_pattern_extract
import tkinter as tk
from tkinter import filedialog, ttk

__version__ = '1.0'


def browse_output():
    output_path = filedialog.askdirectory(initialdir='.')
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_path)


def generate_output():
    result_text.delete(1.0, tk.END)
    msg = htstego_errdiff_extract(output_entry.get()) if htmethod_var.get() == 'errdiff' else htstego_pattern_extract(output_entry.get())
    result_text.insert(tk.END, msg)


w = tk.Tk()
w.title('Halftone Steganography Extraction Tool')
w.resizable(False, False)

f = tk.Frame(w)
f.grid(padx=5,sticky='we')

htmethod_frame = ttk.LabelFrame(f, text='Halftone Method')
htmethod_frame.grid(column=0, row=0, sticky='we', padx=5, pady=5)

htmethod_var = tk.StringVar()
htmethod_var.set('errdiff')

htmethod_errdiff_radio = tk.Radiobutton(htmethod_frame, text='Error Diffusion', variable=htmethod_var, value='errdiff')
htmethod_errdiff_radio.grid(column=0, row=0)

htmethod_pattern_radio = tk.Radiobutton(htmethod_frame, text='Pattern', variable=htmethod_var, value='pattern')
htmethod_pattern_radio.grid(column=1, row=0)

output_frame = tk.LabelFrame(f, text='Output Directory')
output_frame.grid(column=1, row=0, sticky='we', padx=5, pady=5)

output_entry = tk.Entry(output_frame)
output_entry.pack(side=tk.LEFT, expand=True, fill='x')
output_entry.insert(0, 'output/')

output_button = tk.Button(output_frame, text='Browse...', command=browse_output)
output_button.pack(side=tk.RIGHT)

start_button = tk.Button(f, text='Start', command=generate_output)
start_button.grid(column=0, row=5, pady=5, columnspan=2)

result_frame = tk.LabelFrame(f, text='Results')
result_frame.grid(column=0, row=6, columnspan=2, sticky='we', padx=5, pady=5)

result_text = tk.Text(result_frame, height=7)
result_text.grid(column=0, row=0, sticky='we')

w.mainloop()
