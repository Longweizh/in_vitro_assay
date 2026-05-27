import numpy as np
import pandas as pd
from pathlib import Path
import subprocess
import tempfile

# Image processing tools
import skimage.io
import glob

# Plotting tools
import bokeh
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource, PrintfTickFormatter, HoverTool
from bokeh.transform import transform
from bokeh.palettes import Viridis256
from bokeh.resources import INLINE

import cellseg.quant

def imshow(im, cmap=None):
    p = bokeh.plotting.figure(frame_height=400,
                              tools="pan,box_zoom,wheel_zoom,save,reset",)
    p.image(image=[im], 
            x=0, 
            y=1, 
            dw=1, 
            dh=1, 
            color_mapper = bokeh.models.LinearColorMapper(cmap))
    
    return(p)

def show_two_ims(im_1, 
                 im_2,
                 color_mapper=None):
    
    """Convenient function for showing two images side by side."""
    
    p_1 = imshow(im_1,
                 cmap=color_mapper[0])
    
    p_2 = imshow(im_2,
                 cmap=color_mapper[1])
    
    p_1.xaxis.major_label_text_font_size = '12pt'
    p_1.yaxis.major_label_text_font_size = '12pt'

    p_2.xaxis.major_label_text_font_size = '12pt'
    p_2.yaxis.major_label_text_font_size = '12pt'

    p_1.xaxis.axis_label_text_font_size = '18pt'
    p_1.yaxis.axis_label_text_font_size = '18pt'

    p_2.xaxis.axis_label_text_font_size = '18pt'
    p_2.yaxis.axis_label_text_font_size = '18pt'
    
    
    p_2.x_range = p_1.x_range
    p_2.y_range = p_1.y_range
    
    p_1.output_backend = "svg"
    p_2.output_backend = "svg"
    
    return bokeh.layouts.gridplot([p_1, p_2], ncols=2)

def bubble_plot(df, x_column, y_column, x_values = None, y_values = None, plot_title = None, x_axis_title = None, y_axis_title = None, plot_width = 500, plot_height = 400):

    if x_values == None:
        x_values = df[x_column].unique()

    if y_values == None:
        y_values = df[y_column].unique()
    
    source = ColumnDataSource(df)
    
    p = figure(x_range = x_values,
               y_range = y_values,
               title = plot_title,
               x_axis_label = x_axis_title,
               y_axis_label = y_axis_title,
               width = plot_width, 
               height = plot_height)

    color_mapper = LinearColorMapper(palette = Viridis256, low = df['Total Brightness per Signal Area'].min(), high = df['Total Brightness per Signal Area'].max())

    color_bar = ColorBar(color_mapper = color_mapper,
                         location = (0, 0),
                         ticker = BasicTicker())

    p.add_layout(color_bar, 'right')

    p.scatter(x = x_column, y = y_column, size = 'Percent Positive', fill_color = transform('Total Brightness per Signal Area', color_mapper), source = source)

    p.add_tools(HoverTool(tooltips = [('virus', '@virus'), ('receptor', '@receptor'), ('dose_vg/well', '@{dose_vg/well}'), ('image_time_h', '@image_time_h'), ('Percent Positive', '@{Percent Positive}')]))

    p.xaxis.major_label_orientation = np.pi/2

    p.output_backend = "svg"

    min_circle = min(df['Percent Positive'])
    max_circle = max(df['Percent Positive'])
    min_val = df['Total Brightness per Signal Area'].min() 
    max_val = df['Total Brightness per Signal Area'].max()

    return(p, min_circle, max_circle, min_val, max_val)


def simple_bubble_plot(
        df,
        x,
        y,
        size,
        color,
        x_order=None,
        y_order=None,
        width=500,
        height=400,
        title=None,
        size_range=(6, 40),
        palette=Viridis256,
        ):
    """Minimal bubble plot using dataframe columns for x, y, size, and color."""
    df_plot = df.copy()

    if x_order is None:
        x_order = [str(value) for value in df_plot[x].dropna().unique()]
    else:
        x_order = [str(value) for value in x_order]
    if y_order is None:
        y_order = [str(value) for value in df_plot[y].dropna().unique()]
    else:
        y_order = [str(value) for value in y_order]

    df_plot[x] = df_plot[x].astype(str)
    df_plot[y] = df_plot[y].astype(str)

    size_values = pd.to_numeric(df_plot[size], errors='coerce')
    if size_values.notna().sum() == 0 or size_values.min() == size_values.max():
        df_plot['_bubble_size'] = (size_range[0] + size_range[1]) / 2
    else:
        scaled = (size_values - size_values.min()) / (size_values.max() - size_values.min())
        df_plot['_bubble_size'] = size_range[0] + scaled * (size_range[1] - size_range[0])

    color_values = pd.to_numeric(df_plot[color], errors='coerce')
    color_low = color_values.min()
    color_high = color_values.max()
    if pd.isna(color_low) or pd.isna(color_high):
        color_low, color_high = 0, 1
    elif color_low == color_high:
        color_high = color_low + 1

    color_mapper = LinearColorMapper(
        palette=palette,
        low=color_low,
        high=color_high,
    )

    source = ColumnDataSource(df_plot)
    p = figure(
        x_range=x_order,
        y_range=y_order,
        width=width,
        height=height,
        title=title,
        tools="pan,box_zoom,wheel_zoom,save,reset",
    )

    p.scatter(
        x=x,
        y=y,
        size='_bubble_size',
        fill_color=transform(color, color_mapper),
        line_color='black',
        line_alpha=0.4,
        fill_alpha=0.85,
        source=source,
    )

    p.add_layout(ColorBar(color_mapper=color_mapper, title=color), 'right')
    p.add_tools(HoverTool(tooltips=[
        (x, f"@{{{x}}}"),
        (y, f"@{{{y}}}"),
        (size, f"@{{{size}}}"),
        (color, f"@{{{color}}}"),
    ]))
    p.xaxis.major_label_orientation = np.pi / 4

    return p




def export_bokeh_png_with_chrome(plot, filename, width=None, height=None, scale=2):
    """Export a Bokeh plot to PNG using a local Chrome/Chromium binary."""
    chrome_paths = [
        Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
        Path('/Applications/Chromium.app/Contents/MacOS/Chromium'),
        Path('/opt/homebrew/bin/google-chrome'),
        Path('/usr/local/bin/google-chrome'),
        Path('/opt/homebrew/bin/chromium'),
        Path('/usr/local/bin/chromium'),
    ]
    chrome = next((path for path in chrome_paths if path.exists()), None)
    if chrome is None:
        raise FileNotFoundError(
            "Chrome not found. Install Google Chrome or add its path to chrome_paths."
        )

    width = int(width or getattr(plot, 'width', None) or 1000)
    height = int(height or getattr(plot, 'height', None) or 800)
    output = Path(filename).expanduser().resolve()

    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / 'bokeh_export.html'
        profile_path = Path(tmpdir) / 'chrome-profile'
        bokeh.io.save(plot, filename=str(html_path), resources=INLINE, title=output.stem)

        cmd = [
            str(chrome),
            '--headless=new',
            '--disable-gpu',
            '--hide-scrollbars',
            f'--user-data-dir={profile_path}',
            '--virtual-time-budget=5000',
            f'--force-device-scale-factor={scale}',
            f'--window-size={width},{height}',
            f'--screenshot={output}',
            html_path.as_uri(),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)

    return output
	        
def single_experiment_viewer(im_sig,im_bf,channel=0):
    im_sig = skimage.img_as_float(skimage.io.imread(im_sig)[:,:,channel])
    im_bf = skimage.img_as_float(skimage.io.imread(im_bf))
    cellseg.quant.signal_segmentation(im_sig)
    cellseg.quant.brightfield_segmentation(im_bf, gauss_sigma = 30, truncate = 0.35,
                                           dark_thresh = 10000, light_thresh = 3000,
                                           disk_radius = 2)
    print('Segmentation Completed')
    
    brightfield_areas, total_area = cellseg.brightfield_segmentation(im_bf)
    signal_areas, signal_total_area = cellseg.signal_segmentation(im_sig)
    bf_plot = cellseg.plot.show_two_ims(im_bf, brightfield_areas, color_mapper=[bokeh.palettes.gray(256), bokeh.palettes.gray(256)])
    sig_plot = cellseg.plot.show_two_ims(im_sig, signal_areas, color_mapper=[bokeh.palettes.gray(256), bokeh.palettes.gray(256)])

    return(bf_plot, sig_plot)
