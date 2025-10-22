#SPectral ANalysis software (SPAN).
#Written by Daniele Gasparri#

"""
    Copyright (C) 2020-2025, Daniele Gasparri

    E-mail: daniele.gasparri@gmail.com

    SPAN is a GUI software that allows to modify and analyze 1D astronomical spectra.

    1. This software is licensed for non-commercial, academic and personal use only.
    2. The source code may be used and modified for research and educational purposes, 
    but any modifications must remain for private use unless explicitly authorized 
    in writing by the original author.
    3. Redistribution of the software in its original, unmodified form is permitted 
    for non-commercial purposes, provided that this license notice is always included.
    4. Redistribution or public release of modified versions of the source code 
    is prohibited without prior written permission from the author.
    5. Any user of this software must properly attribute the original author 
    in any academic work, research, or derivative project.
    6. Commercial use of this software is strictly prohibited without prior 
    written permission from the author.

    DISCLAIMER:
    THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

# Sub-programs definition and implementation routines

try: #try local import if executed as script
    #GUI import
    from FreeSimpleGUI_local import FreeSimpleGUI as sg
    #SPAN functions import
    from span_functions import system_span as stm
    from span_functions import cube_extract as cubextr
    from span_functions.sauron_colormap import register_sauron_colormap
    from span_modules import misc
    from span_modules import layouts
    from span_modules import utility_tasks
    from params import SpectraParams
    from span_modules.ui_zoom import open_subwindow, ZoomManager

except ModuleNotFoundError: #local import if executed as package
    #GUI import
    from span.FreeSimpleGUI_local import FreeSimpleGUI as sg
    #SPAN functions import
    from span.span_functions import system_span as stm
    from span.span_functions import cube_extract as cubextr
    from span.span_functions.sauron_colormap import register_sauron_colormap
    from . import misc
    from . import layouts
    from . import utility_tasks
    from .params import SpectraParams
    from .ui_zoom import open_subwindow, ZoomManager

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg
from matplotlib.ticker import MultipleLocator
from matplotlib.backend_bases import MouseButton
from matplotlib.widgets import Slider, RadioButtons
from matplotlib.colors import LogNorm, Normalize
from matplotlib.gridspec import GridSpec

from skimage.measure import label, regionprops
import os
import numpy as np
from astropy.io import fits
from astropy.table import Table

from dataclasses import replace
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

zm = ZoomManager.get()


# 1) PLOT DATA
def plot_data_window(BASE_DIR, layout):

    # Example file to plot
    file_to_plot = os.path.join(BASE_DIR, "example_files", "results", "NGC5320_populations.dat")

    layout, scale_win, fontsize, default_size = misc.get_layout()
    sg.theme('DarkBlue3')
    markers = ['red', 'green', 'yellow', 'blue', 'purple', 'black', 'orange']
    plot_layout = [
        [sg.Text('File to plot:', font=("Helvetica", 15, 'bold'), text_color = 'lightgreen'), sg.InputText(file_to_plot,key='-FILE-', readonly=True, size=(35, 1), font = ('', default_size)), sg.FileBrowse(file_types=(('Text Files', '*.*'),),tooltip='Browse an ASCII file with space or tab soaced columns and first line containing the names of columns', font = ('', default_size)), sg.Button('Load', button_color=('black','light green'), size=(7, 1), font=("Helvetica", 15), tooltip='After you browse for your data file, click here to load it')],
        [sg.Text(' x-axis data:', font=("Helvetica", 15, 'bold')), sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='-X_COLUMN-', enable_events=True, size=(20, 5), font = ('', default_size)), sg.Text('y-axis data:', font=("Helvetica", 15, 'bold')), sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='-Y_COLUMNS-', size=(20, 5), font = ('', default_size))],
        [sg.Checkbox('x errbars:',default = False, key = '-XERRBARS-', font=("Helvetica", 15)), sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='-X_ERR-', enable_events=True, size=(20, 5), font = ('', default_size)), sg.Checkbox('y errbars:',default = False, key = '-YERRBARS-', font=("Helvetica", 15)), sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='-Y_ERR-', size=(20, 5), font = ('', default_size))],
        [sg.Checkbox('Linear Fit of the data', default=False, key='-LINEAR_FIT-', font = ('', default_size)), sg.Push(), sg.Checkbox('X log scale', default=False, key='-X_LOG-', font = ('', default_size)),sg.Checkbox('Y log scale', default=False, key='-Y_LOG-', font = ('', default_size))],
        [sg.HorizontalSeparator()],
        [sg.Text('X-axis Range:', font = ('', default_size)), sg.InputText(key='-X_RANGE_MIN-', size=(8, 1), font = ('', default_size)), sg.Text(' to ', font = ('', default_size)), sg.InputText(key='-X_RANGE_MAX-', size=(8, 1), font = ('', default_size)),
        sg.Text('Y-axis Range:', font = ('', default_size)), sg.InputText(key='-Y_RANGE_MIN-', size=(8, 1), font = ('', default_size)), sg.Text(' to ', font = ('', default_size)), sg.InputText(key='-Y_RANGE_MAX-', size=(8, 1), font = ('', default_size))],
        [sg.Text('X-axis label:', font = ('', default_size)), sg.InputText(key='-X_LABEL-', size=(20, 1), font = ('', default_size)),sg.Text('Y-axis label:', font = ('', default_size)), sg.InputText(key='-Y_LABEL-', size=(20, 1), font = ('', default_size))],
        [sg.Text('X-axis label size:', font = ('', default_size)), sg.InputText(default_text='14', key='-X_LABEL_SIZE-', size=(5, 1), font = ('', default_size)), sg.Text('Y-axis label size:', font = ('', default_size)), sg.InputText(default_text='14', key='-Y_LABEL_SIZE-', size=(5, 1), font = ('', default_size))],
        [sg.Text('X-ticks size:', font = ('', default_size)), sg.InputText(default_text='14', key='-X_TICKS_SIZE-', size=(5, 1), font = ('', default_size)), sg.Text('Y-ticks size:', font = ('', default_size)), sg.InputText(default_text='14', key='-Y_TICKS_SIZE-', size=(5, 1), font = ('', default_size))],
        [sg.Text('Marker color:', font = ('', default_size)), sg.InputCombo(markers, key='-MARKER_COLOR-',default_value=markers[0],readonly=True, font = ('', default_size)), sg.Text('Marker size:', font = ('', default_size)), sg.Slider(range=(1, 100), orientation='h', default_value=40, key='-MARKER_SIZE-', font = ('', default_size))],
        [sg.Text('Plot size (inches):', font = ('', default_size)), sg.InputText('8, 6', key='-PLOT_SIZE-', size=(5, 1), font = ('', default_size)), sg.Checkbox ('Show legend', default = True, key = '-LEGEND-', font = ('', default_size))],
        [sg.Button('Plot!', button_color=('white','orange'), size=(15, 1), font=("Helvetica", 15)), sg.Button('Save img', button_color=('black','light gray'), size=(15, 1), font=("Helvetica", 15)), sg.Button("Help", size=(12, 1),button_color=('black','orange'), font = ('', default_size)), sg.Push(), sg.Button('Exit', size=(15, 1), font = ('', default_size))]
    ]

    print ('*** Plotting window open. The main panel will be inactive until you close the window ***')

    plot_window = open_subwindow('Data Plotter', plot_layout, zm=zm)

    while True:
        plot_event, plot_values = plot_window.read()

        if plot_event == sg.WIN_CLOSED or plot_event == 'Exit':
            print('Plot window closed. This main panel is now active again')
            print('')
            break

        try:
            file_to_plot = plot_values['-FILE-']
        except Exception:
            sg.popup ('Cannot read the file to plot')
            continue


        if plot_event == 'Load':
            file_path = plot_values['-FILE-']
            if file_path:
                column_names = stm.get_column_names(file_path)
                plot_window['-X_COLUMN-'].update(values=column_names)
                plot_window['-Y_COLUMNS-'].update(values=column_names)
                plot_window['-X_ERR-'].update(values=column_names)
                plot_window['-Y_ERR-'].update(values=column_names)

        elif plot_event == 'Plot!' or plot_event == 'Save img':
            file_path = plot_values['-FILE-']
            x_column = plot_values['-X_COLUMN-']
            y_columns = plot_values['-Y_COLUMNS-']
            x_err = plot_values['-X_ERR-']
            y_err = plot_values['-Y_ERR-']
            x_label = plot_values['-X_LABEL-']
            y_label = plot_values['-Y_LABEL-']
            legend = plot_values['-LEGEND-']
            marker_color = plot_values['-MARKER_COLOR-']
            add_error_bars_x = plot_values['-XERRBARS-']
            add_error_bars_y = plot_values['-YERRBARS-']
            marker_size = int(plot_values['-MARKER_SIZE-'])
            plot_size = tuple(map(float, plot_values['-PLOT_SIZE-'].split(',')))
            x_label_size = int(plot_values['-X_LABEL_SIZE-'])
            y_label_size = int(plot_values['-Y_LABEL_SIZE-'])
            x_tick_size = int(plot_values['-X_TICKS_SIZE-'])
            y_tick_size = int(plot_values['-Y_TICKS_SIZE-'])
            enable_linear_fit = plot_values['-LINEAR_FIT-']
            x_log_scale = plot_values['-X_LOG-']
            y_log_scale = plot_values['-Y_LOG-']

            try:
                x_range_min = float(plot_values['-X_RANGE_MIN-']) if plot_values['-X_RANGE_MIN-'] else None
                x_range_max = float(plot_values['-X_RANGE_MAX-']) if plot_values['-X_RANGE_MAX-'] else None
                y_range_min = float(plot_values['-Y_RANGE_MIN-']) if plot_values['-Y_RANGE_MIN-'] else None
                y_range_max = float(plot_values['-Y_RANGE_MAX-']) if plot_values['-Y_RANGE_MAX-'] else None
            except ValueError:
                sg.popup ('Range values not valid!')
                continue

            if plot_event == 'Plot!':
                stm.plot_data(file_path, x_column, y_columns, x_label, y_label, marker_color, marker_size, plot_size, x_label_size, y_label_size, x_tick_size, y_tick_size, legend, add_error_bars_x, add_error_bars_y, x_err, y_err, False, enable_linear_fit, x_log_scale, y_log_scale, x_range_min, x_range_max, y_range_min, y_range_max)

            if plot_event == 'Save img':
                stm.plot_data(file_path, x_column, y_columns, x_label, y_label, marker_color, marker_size, plot_size, x_label_size, y_label_size, x_tick_size, y_tick_size, legend, add_error_bars_x, add_error_bars_y, x_err, y_err, True, enable_linear_fit, x_log_scale, y_log_scale, x_range_min, x_range_max, y_range_min, y_range_max)

        if plot_event == 'Help':
            f = open(os.path.join(BASE_DIR, "help_files", "help_me_plot.txt"), 'r')
            file_contents = f.read()
            if layout == layouts.layout_android:
                sg.popup_scrolled(file_contents, size=(120, 30))
            else:
                sg.popup_scrolled(file_contents, size=(100, 40))

    plot_window.close()



# 2) PLOT MAPS
def plot_maps_window(BASE_DIR, layout, params):
        
    fits_path = params.fits_path
    txt_path = params.txt_path
    plot_maps_fits_image = params.plot_maps_fits_image
    plot_maps_contour_percentiles = params.plot_maps_contour_percentiles
    plot_maps_xlim_min = params.plot_maps_xlim_min
    plot_maps_xlim_max = params.plot_maps_xlim_max
    plot_maps_ylim_min = params.plot_maps_ylim_min
    plot_maps_ylim_max = params.plot_maps_ylim_max
    plot_maps_map_range_min = params.plot_maps_map_range_min
    plot_maps_map_range_max = params.plot_maps_map_range_max
    plot_maps_offet = params.plot_maps_offet
    plot_maps_offset_value = params.plot_maps_offset_value 
    plot_maps_gaussian_smooth = params.plot_maps_gaussian_smooth
    plot_maps_gaussian_smooth_value = params.plot_maps_gaussian_smooth_value 
    plot_maps_radial_profiles = params.plot_maps_radial_profiles
    plot_maps_colormap = params.plot_maps_colormap
    
    layout, scale_win, fontsize, default_size = misc.get_layout()   
    register_sauron_colormap()
    sg.theme("DarkBlue3")

    if layout == layouts.layout_windows:
        map_layout = [
            [sg.Text("1. Select the FITS file (*_table.fits) with spaxel and bin info", font=("Helvetica", 14))],
            [sg.Input(fits_path, key="-FITS-", size=(46, 1), font=("Helvetica", 12)), sg.FileBrowse(file_types=(("FITS files", "*.fits"),), font=("Helvetica", 12))],
            [sg.Text("2. Select the text file with spectral analysis results", font=("Helvetica", 14))],
            [sg.Input(txt_path, key="-TXT-", size=(46, 1), font=("Helvetica", 12)), sg.FileBrowse(file_types=(("Text files", "*.txt *.dat"),), font=("Helvetica", 12))],
            [sg.Text("3. (Optional) FITS image (*_2dimage.fits) for isophotes", font=("Helvetica", 14))],
            [sg.Input(plot_maps_fits_image, key="-IMG-", size=(46, 1), font=("Helvetica", 12)), sg.FileBrowse(file_types=(("FITS files", "*.fits"),), font=("Helvetica", 12))],
            [sg.Text("Contour levels (percentiles):", font=("Helvetica", 12)), sg.Input(plot_maps_contour_percentiles, key="-ISOLEVELS-", size=(30, 1), font=("Helvetica", 12))],
            [sg.Button("Load Files", font=("Helvetica", 14), button_color=('black','light green')), sg.Push(), sg.Button('Help', size=(9, 1), font=("Helvetica", 14), button_color=('black','orange'))],
            [sg.HorizontalSeparator()],
            [sg.Text("Select the quantity to plot:", font=("Helvetica", 14)), sg.Push(), sg.Text("Colormap:", font=("Helvetica", 14)), sg.Combo(values=["inferno", "viridis", "plasma", "magma", "cividis", "seismic", "jet","sauron", "sauron_r"], default_value=plot_maps_colormap, key="-CMAP-", readonly=True, font=("Helvetica", 12))],
            [sg.Listbox(values=[], size=(44, 10), key="-LIST-", enable_events=True, font=("Helvetica", 14))],
            [sg.Text("X lim:"), sg.Input(plot_maps_xlim_min, size=(4,1), key="-XMIN-"), sg.Text("-"), sg.Input(plot_maps_xlim_max, size=(4,1), key="-XMAX-"), sg.Text("Y lim:"), sg.Input(plot_maps_ylim_min, size=(4,1), key="-YMIN-"), sg.Text("-"), sg.Input(plot_maps_ylim_max, size=(4,1), key="-YMAX-"), sg.Push(), sg.Text("Map range:"), sg.Input(plot_maps_map_range_min, size=(4,1), key="-VMIN-", tooltip="Leave empty for auto-scaling"), sg.Text("-"), sg.Input(plot_maps_map_range_max, size=(4,1), key="-VMAX-", tooltip="Leave empty for auto-scaling")],
            [sg.Checkbox("Offset:", key = 'offset', default = plot_maps_offet, font=("Helvetica", 12), tooltip='Apply a custom offset value to the data'), sg.Input(plot_maps_offset_value, size=(4,1), key="offset_value"), sg.Checkbox("Gauss smoothing:", key="-SMOOTH-", default = plot_maps_gaussian_smooth, font=("Helvetica", 12), tooltip='If spaxel re-projection is activated, this will smooth the colours of the maps. You just get cooler plots'), sg.Slider(range=(0.0, 5.0), resolution=0.1, default_value=plot_maps_gaussian_smooth_value, orientation='h', size=(20, 20), key="-SIGMA-", enable_events=True)],
            [sg.Checkbox("Plot radial profile (instead of 2D map)", key="-RADIAL-", default = plot_maps_radial_profiles, font=("Helvetica", 12), tooltip="If selected, plots the quantity as a function of distance from center")],
            [sg.Button("Plot Map", size=(9, 1), font=("Helvetica", 14), button_color=('white','orange')), sg.Button("Save selected", size=(13, 1), font=("Helvetica", 14), button_color=('black','light gray')), sg.Button("Save ALL", size=(9, 1), font=("Helvetica", 14), button_color=('black','gray')), sg.Button("Exit", size=(9, 1), font=("Helvetica", 14))]
        ]


    elif layout == layouts.layout_android:
        map_layout = [
            [sg.Text("1. Select the FITS file (*_table.fits) with spaxel and bin info", font=("Helvetica", 12))],
            [sg.Input(fits_path, key="-FITS-", size=(42, 1), font=("Helvetica", 11)), sg.FileBrowse(file_types=(("FITS files", "*.fits"),), font=("Helvetica", 11))],
            [sg.Text("2. Select the text file with spectral analysis results", font=("Helvetica", 12))],
            [sg.Input(txt_path, key="-TXT-", size=(42, 1), font=("Helvetica", 11)), sg.FileBrowse(file_types=(("Text files", "*.txt *.dat"),), font=("Helvetica", 11))],
            [sg.Text("3. (Optional) FITS image (*_2dimage.fits) for isophotes", font=("Helvetica", 12))],
            [sg.Input(plot_maps_fits_image, key="-IMG-", size=(42, 1), font=("Helvetica", 11)), sg.FileBrowse(file_types=(("FITS files", "*.fits"),), font=("Helvetica", 11))],
            [sg.Text("Contour levels (percentiles):", font=("Helvetica", 11)), sg.Input(plot_maps_contour_percentiles, key="-ISOLEVELS-", size=(25, 1), font=("Helvetica", 12))],
            [sg.Button("Load Files", font=("Helvetica", 12), button_color=('black','light green')), sg.Push(), sg.Button('Help', size=(7, 1), font=("Helvetica", 12), button_color=('black','orange'))],
            [sg.HorizontalSeparator()],
            [sg.Text("Select the quantity to plot:", font=("Helvetica", 12)), sg.Push(), sg.Text("Colormap:", font=("Helvetica", 14)), sg.Combo(values=["inferno", "viridis", "plasma", "magma", "cividis", "seismic", "jet","sauron", "sauron_r"], default_value=plot_maps_colormap, key="-CMAP-", readonly=True, font=("Helvetica", 12))],
            [sg.Listbox(values=[], size=(47, 8), key="-LIST-", enable_events=True, font=("Helvetica", 12))],
            [sg.Text("X lim:"), sg.Input(plot_maps_xlim_min, size=(4,1), key="-XMIN-"), sg.Text("-"), sg.Input(plot_maps_xlim_max, size=(4,1), key="-XMAX-"), sg.Text("Y lim:"), sg.Input(plot_maps_ylim_min, size=(4,1), key="-YMIN-"), sg.Text("-"), sg.Input(plot_maps_ylim_max, size=(4,1), key="-YMAX-"), sg.Push(), sg.Text("Map range:"), sg.Input(plot_maps_map_range_min, size=(4,1), key="-VMIN-", tooltip="Leave empty for auto-scaling"), sg.Text("-"), sg.Input(plot_maps_map_range_max, size=(4,1), key="-VMAX-", tooltip="Leave empty for auto-scaling")],
            [sg.Checkbox("Offset:", key = 'offset', default = plot_maps_offet, font=("Helvetica", 11), tooltip='Apply a custom offset value to the data'), sg.Input(plot_maps_offset_value, size=(4,1), key="offset_value"), sg.Checkbox("Gauss smoothing:", key="-SMOOTH-", default = plot_maps_gaussian_smooth, font=("Helvetica", 11), tooltip='If spaxel re-projection is activated, this will smooth the colours of the maps. You just get cooler plots'), sg.Slider(range=(0.0, 5.0), resolution=0.1, default_value=plot_maps_gaussian_smooth_value, orientation='h', size=(19, 20), key="-SIGMA-", enable_events=True)],
            [sg.Checkbox("Plot radial profile (instead of 2D map)", key="-RADIAL-", default = plot_maps_radial_profiles, font=("Helvetica", 12), tooltip="If selected, plots the quantity as a function of distance from center")],
            [sg.Button("Plot Map", size=(8, 1), font=("Helvetica", 12), button_color=('white','orange')), sg.Button("Save selected", size=(11, 1), font=("Helvetica", 12), button_color=('black','light gray')), sg.Button("Save ALL", size=(8, 1), font=("Helvetica", 12), button_color=('black','gray')), sg.Button("Exit", size=(8, 1), font=("Helvetica", 12))]

        ]

    else:
        map_layout = [
            [sg.Text("1. Select the FITS file (*_table.fits) with spaxel and bin info", font=("Helvetica", 14))],
            [sg.Input(fits_path, key="-FITS-", size=(50, 1), font=("Helvetica", 12)), sg.FileBrowse(file_types=(("FITS files", "*.fits"),), font=("Helvetica", 12))],
            [sg.Text("2. Select the text file with spectral analysis results", font=("Helvetica", 14))],
            [sg.Input(txt_path, key="-TXT-", size=(50, 1), font=("Helvetica", 12)), sg.FileBrowse(file_types=(("Text files", "*.txt *.dat"),), font=("Helvetica", 12))],
            [sg.Text("3. (Optional) FITS image (*_2dimage.fits) for isophotes", font=("Helvetica", 14))],
            [sg.Input(plot_maps_fits_image, key="-IMG-", size=(50, 1), font=("Helvetica", 12)), sg.FileBrowse(file_types=(("FITS files", "*.fits"),), font=("Helvetica", 12))],
            [sg.Text("Contour levels (percentiles):", font=("Helvetica", 12)), sg.Input(default_text=plot_maps_contour_percentiles, key="-ISOLEVELS-", size=(35, 1), font=("Helvetica", 12))],
            [sg.Button("Load Files", font=("Helvetica", 14), button_color=('black','light green')), sg.Push(), sg.Button('Help', size=(9, 1), font=("Helvetica", 14), button_color=('black','orange'))],
            [sg.HorizontalSeparator()],
            [sg.Text("Select the quantity to plot:", font=("Helvetica", 14)), sg.Push(), sg.Text("Colormap:", font=("Helvetica", 14)), sg.Combo(values=["inferno", "viridis", "plasma", "magma", "cividis", "seismic", "jet","sauron", "sauron_r"], default_value=plot_maps_colormap, key="-CMAP-", readonly=True, font=("Helvetica", 12))],
            [sg.Listbox(values=[], size=(54, 10), key="-LIST-", enable_events=True, font=("Helvetica", 14))],
            [sg.Text("X lim:"), sg.Input(plot_maps_xlim_min, size=(4,1), key="-XMIN-"), sg.Text("-"), sg.Input(plot_maps_xlim_max, size=(4,1), key="-XMAX-"), sg.Text("Y lim:"), sg.Input(plot_maps_ylim_min, size=(4,1), key="-YMIN-"), sg.Text("-"), sg.Input(plot_maps_ylim_max, size=(4,1), key="-YMAX-"), sg.Push(), sg.Text("Map range:"), sg.Input(plot_maps_map_range_min, size=(4,1), key="-VMIN-", tooltip="Leave empty for auto-scaling"), sg.Text("-"), sg.Input(plot_maps_map_range_max, size=(4,1), key="-VMAX-", tooltip="Leave empty for auto-scaling")],
            [sg.Checkbox("Offset:", key = 'offset', default = plot_maps_offet, font=("Helvetica", 12), tooltip='Apply a custom offset value to the data'), sg.Input(plot_maps_offset_value, size=(4,1), key="offset_value"), sg.Checkbox("Gauss smoothing:", key="-SMOOTH-", default = plot_maps_gaussian_smooth, font=("Helvetica", 12), tooltip='If spaxel re-projection is activated, this will smooth the colours of the maps. You just get cooler plots'), sg.Slider(range=(0.0, 5.0), resolution=0.1, default_value=plot_maps_gaussian_smooth_value, orientation='h', size=(28, 20), key="-SIGMA-", enable_events=True)],
            [sg.Checkbox("Plot radial profile (instead of 2D map)", key="-RADIAL-", default = plot_maps_radial_profiles, font=("Helvetica", 12), tooltip="If selected, plots the quantity as a function of distance from center")],
            [sg.Button("Plot Map", size=(9, 1), font=("Helvetica", 14), button_color=('white','orange')), sg.Button("Save selected", size=(13, 1), font=("Helvetica", 14), button_color=('black','light gray')), sg.Button("Save ALL", size=(9, 1), font=("Helvetica", 14), button_color=('black','gray')), sg.Button("Exit", size=(9, 1), font=("Helvetica", 14))]

        ]

    map_window = open_subwindow("2D Map Viewer", map_layout, zm=zm)
    x, y, bin_id = None, None, None
    result_df = None
    selected_quantity = None

    while True:
        map_event, map_values = map_window.read()

        if map_event == sg.WIN_CLOSED:
            break
        
        # Setting up the values
        fits_path = map_values["-FITS-"]
        txt_path = map_values["-TXT-"]
        plot_maps_fits_image = map_values["-IMG-"]
        plot_maps_contour_percentiles = map_values["-ISOLEVELS-"]
        plot_maps_xlim_min = map_values["-XMIN-"]
        plot_maps_xlim_max = map_values["-XMAX-"]
        plot_maps_ylim_min = map_values["-YMIN-"]
        plot_maps_ylim_max = map_values["-YMAX-"]
        plot_maps_map_range_min = map_values["-VMIN-"]
        plot_maps_map_range_max = map_values["-VMAX-"]
        plot_maps_offet = map_values["offset"]
        plot_maps_offset_value = map_values["offset_value"]
        plot_maps_gaussian_smooth = map_values["-SMOOTH-"]
        plot_maps_gaussian_smooth_value = map_values["-SIGMA-"]
        plot_maps_radial_profiles = map_values["-RADIAL-"]
        plot_maps_colormap = map_values["-CMAP-"]
        
        if map_event == "Load Files":
            try:
                fits_path = map_values["-FITS-"]
                txt_path = map_values["-TXT-"]

                # Extract RUN_NAME
                fits_run = fits_path.split("/")[-1].split("_table")[0]
                txt_run = txt_path.split("/")[-1].split("_bins_list")[0]

                if fits_run != txt_run:
                    proceed = sg.popup_yes_no(
                        "WARNING: The selected files appear to belong to different runs.\n\n"
                        f"FITS table run: {fits_run}\nTXT run: {txt_run}\n\n"
                        "Proceed anyway?",
                        title="Run name mismatch"
                    )
                    if proceed != "Yes":
                        sg.popup("File loading aborted.")
                        continue

                x, y, bin_id, xbin, ybin = stm.load_fits_data(fits_path)
                result_df = stm.load_analysis_results(txt_path)
                col_names = list(result_df.columns)[1:]
                map_window["-LIST-"].update(values=col_names)
                sg.popup("Files loaded successfully.")

            except Exception as e:
                sg.popup_error(f"Error loading files:\n{e}")

        elif map_event == "-LIST-":
            if map_values["-LIST-"]:
                selected_quantity = map_values["-LIST-"][0]

        # First event: Plotting
        elif map_event == "Plot Map":
            offset = map_values['offset']
            plot_radial = map_values.get("-RADIAL-", False)
            smoothing = map_values['-SMOOTH-']
            
            if x is not None and result_df is not None and selected_quantity:
                
                
                if offset:
                    result_df_mod = result_df.copy()
                    try:
                        offset_value = float(map_values['offset_value'])
                        try:
                            result_df_mod[selected_quantity] += offset_value
                        except Exception as e:
                            sg.popup_error(f"Could not apply offset: {e}")
                            result_df_mod = result_df
                    except Exception:
                        sg.popup('Offset value not valid!')
                        offset_value = 0                       
                
                # Set X and Y limits if provided
                try:
                    xmin = float(map_values["-XMIN-"]) if map_values["-XMIN-"] else None
                    xmax = float(map_values["-XMAX-"]) if map_values["-XMAX-"] else None
                    ymin = float(map_values["-YMIN-"]) if map_values["-YMIN-"] else None
                    ymax = float(map_values["-YMAX-"]) if map_values["-YMAX-"] else None
                except Exception as e:
                    print(f"[WARNING] Invalid axis limits: {e}")
                    
                # Optional colormap limits
                try:
                    vmin = float(map_values["-VMIN-"]) if map_values["-VMIN-"] else None
                    vmax = float(map_values["-VMAX-"]) if map_values["-VMAX-"] else None
                except Exception as e:
                    print(f"[WARNING] Invalid colormap range: {e}")
                    vmin, vmax = None, None
                
                if plot_radial:
                    try:
                        if offset:
                            fig, ax = stm.plot_radial_profile_bins(xbin, ybin, bin_id, result_df_mod, selected_quantity)
                        else:
                            fig, ax = stm.plot_radial_profile_bins(xbin, ybin, bin_id, result_df, selected_quantity)
                        
                        if xmin is not None and xmax is not None:
                            ax.set_xlim(xmin, xmax)
                        if ymin is not None and ymax is not None:
                            ax.set_ylim(ymin, ymax)

                        plt.tight_layout()
                        plt.show()
                        plt.close()
                    except Exception as e:
                        sg.popup_error(f"Error in radial profile plot:\n{e}")

                elif smoothing:
                    try:                          
                        iso_levels = None
                        img_path = map_values["-IMG-"]
                        
                        if offset:
                            fig, ax = stm.plot_reprojected_map_clickable(x, y, bin_id, result_df_mod, selected_quantity, cmap=map_values["-CMAP-"], smoothing=map_values["-SMOOTH-"], sigma=float(map_values["-SIGMA-"]), vmin=vmin, vmax=vmax)
                        else:
                            fig, ax = stm.plot_reprojected_map_clickable(x, y, bin_id, result_df, selected_quantity, cmap=map_values["-CMAP-"], smoothing=map_values["-SMOOTH-"], sigma=float(map_values["-SIGMA-"]), vmin=vmin, vmax=vmax)

                        if img_path and os.path.isfile(img_path):
                            if img_path and os.path.isfile(img_path):
                                try:
                                    level_str = map_values["-ISOLEVELS-"]
                                    iso_levels = [float(val) for val in level_str.split(",") if val.strip() != ""]
                                    iso_levels.sort()
                                except Exception:
                                    iso_levels = None
                                stm.overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
                        
                        if xmin is not None and xmax is not None:
                            ax.set_xlim(xmin, xmax)
                        if ymin is not None and ymax is not None:
                            ax.set_ylim(ymin, ymax)
                        
                        plt.tight_layout()
                        plt.show()
                        plt.close()
                        
                    except Exception as e:
                        sg.popup_error(f"Error in re-projection mode:\n{e}")

                else:
                    
                    if offset:
                        fig, ax = stm.plot_voronoi_map_clickable(x, y, bin_id, result_df_mod, selected_quantity, cmap=map_values["-CMAP-"], vmin=vmin, vmax=vmax)
                    else:
                        fig, ax = stm.plot_voronoi_map_clickable(x, y, bin_id, result_df, selected_quantity, cmap=map_values["-CMAP-"], vmin=vmin, vmax=vmax)
                   
                    img_path = map_values["-IMG-"]
                    if img_path and os.path.isfile(img_path):
                        try:
                            level_str = map_values["-ISOLEVELS-"]
                            iso_levels = [float(val) for val in level_str.split(",") if val.strip() != ""]
                            iso_levels.sort()
                        except Exception:
                            iso_levels = None
                        stm.overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
                        
                    if xmin is not None and xmax is not None:
                        ax.set_xlim(xmin, xmax)
                    if ymin is not None and ymax is not None:
                        ax.set_ylim(ymin, ymax)

                    plt.tight_layout()
                    plt.show()
                    plt.close()
            else:
                sg.popup("Please load files and select a quantity.")

        elif map_event == "Save selected":
            offset = map_values['offset']
            plot_radial = map_values.get("-RADIAL-", False)
            smoothing = map_values['-SMOOTH-']
            
            if x is not None and result_df is not None and selected_quantity:
                save_path = sg.popup_get_file("Save PNG file", save_as=True, no_window=True, file_types=(("PNG Files", "*.png"),), default_extension=".png")
                
                if save_path:             
                    
                    if offset:
                        result_df_mod = result_df.copy()
                        try:
                            offset_value = float(map_values['offset_value'])
                            try:
                                result_df_mod[selected_quantity] += offset_value
                            except Exception as e:
                                sg.popup_error(f"Could not apply offset: {e}")
                                result_df_mod = result_df
                        except Exception:
                            sg.popup('Offset value not valid!')
                            offset_value = 0  
                        
                    # Set X and Y limits if provided
                    try:
                        xmin = float(map_values["-XMIN-"]) if map_values["-XMIN-"] else None
                        xmax = float(map_values["-XMAX-"]) if map_values["-XMAX-"] else None
                        ymin = float(map_values["-YMIN-"]) if map_values["-YMIN-"] else None
                        ymax = float(map_values["-YMAX-"]) if map_values["-YMAX-"] else None
                    except Exception as e:
                        print(f"[WARNING] Invalid axis limits: {e}")
                    
                    # Optional colormap limits
                    try:
                        vmin = float(map_values["-VMIN-"]) if map_values["-VMIN-"] else None
                        vmax = float(map_values["-VMAX-"]) if map_values["-VMAX-"] else None
                    except Exception as e:
                        print(f"[WARNING] Invalid colormap range: {e}")
                        vmin, vmax = None, None
                    
                    if plot_radial:
                        try:
                            
                            if offset:
                                fig, ax = stm.plot_radial_profile_bins(xbin, ybin, bin_id, result_df_mod, selected_quantity)
                            else:
                                fig, ax = stm.plot_radial_profile_bins(xbin, ybin, bin_id, result_df, selected_quantity)
                            
                            if xmin is not None and xmax is not None:
                                ax.set_xlim(xmin, xmax)
                            if ymin is not None and ymax is not None:
                                ax.set_ylim(ymin, ymax)

                            plt.tight_layout()
                            fig.savefig(save_path, dpi=300)
                            plt.close(fig)
                            sg.popup("Image saved successfully.")
                        except Exception as e:
                            sg.popup_error(f"Error in radial profile plot:\n{e}")
                    
                    elif smoothing:
                        img_path = map_values["-IMG-"]

                        try:
                            
                            if offset:
                                fig, ax = stm.plot_reprojected_map(x, y, bin_id, result_df_mod, selected_quantity, cmap=map_values["-CMAP-"], smoothing=map_values["-SMOOTH-"], sigma=float(map_values["-SIGMA-"]), vmin=vmin, vmax=vmax)
                            else:
                                fig, ax = stm.plot_reprojected_map(x, y, bin_id, result_df, selected_quantity, cmap=map_values["-CMAP-"], smoothing=map_values["-SMOOTH-"], sigma=float(map_values["-SIGMA-"]), vmin=vmin, vmax=vmax)

                            if img_path and os.path.isfile(img_path):
                                try:
                                    level_str = map_values["-ISOLEVELS-"]
                                    iso_levels = [float(val) for val in level_str.split(",") if val.strip() != ""]
                                    iso_levels.sort()
                                except Exception:
                                    iso_levels = None
                                stm.overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
                                    
                            # Set X and Y limits if provided
                            if xmin is not None and xmax is not None:
                                ax.set_xlim(xmin, xmax)
                            if ymin is not None and ymax is not None:
                                ax.set_ylim(ymin, ymax)

                            plt.tight_layout()
                            fig.savefig(save_path, dpi=300)
                            plt.close(fig)
                            sg.popup("Image saved successfully.")
                            
                        except Exception as e:
                            sg.popup_error(f"Error saving reprojected image:\n{e}")
                    else:
                        
                        img_path = map_values["-IMG-"]
                        
                        try:
                            level_str = map_values["-ISOLEVELS-"]
                            iso_levels = [float(val.strip()) for val in level_str.split(",") if val.strip()]
                            iso_levels = sorted(set(iso_levels)) if len(iso_levels) >= 2 else None
                        except Exception:
                            iso_levels = None

                        if offset:
                            fig, ax = stm.plot_voronoi_map(x, y, bin_id, result_df_mod, selected_quantity, cmap=map_values["-CMAP-"], img_path=img_path, iso_levels=iso_levels, vmin=vmin, vmax=vmax)
                        else:
                            fig, ax = stm.plot_voronoi_map(x, y, bin_id, result_df, selected_quantity, cmap=map_values["-CMAP-"], img_path=img_path, iso_levels=iso_levels, vmin=vmin, vmax=vmax)

                        # Set X and Y limits if provided
                        if xmin is not None and xmax is not None:
                            ax.set_xlim(xmin, xmax)
                        if ymin is not None and ymax is not None:
                            ax.set_ylim(ymin, ymax)

                        plt.tight_layout()
                        fig.savefig(save_path, dpi=300)
                        plt.close(fig)
                        sg.popup("Image saved successfully.")
            else:
                sg.popup("Please load files and select a quantity before saving.")

        elif map_event == "Save ALL":
            offset = map_values['offset']
            plot_radial = map_values.get("-RADIAL-", False)
            smoothing = map_values['-SMOOTH-']
            
            if x is not None and result_df is not None:
                folder = sg.popup_get_folder("Select output folder for PNGs", no_window=True)
                if folder:
                    
                    
                    if offset:
                        result_df_mod = result_df.copy()
                        try:
                            offset_value = float(map_values['offset_value'])
                            try:
                                numeric_cols = result_df_mod.select_dtypes(include='number').columns
                                result_df_mod[numeric_cols] += offset_value
                            except Exception as e:
                                sg.popup_error(f"Could not apply offset: {e}")
                                result_df_mod = result_df
                        except Exception:
                            sg.popup('Offset value not valid!')
                            offset_value = 0  
                    
                    # Set X and Y limits if provided
                    try:
                        xmin = float(map_values["-XMIN-"]) if map_values["-XMIN-"] else None
                        xmax = float(map_values["-XMAX-"]) if map_values["-XMAX-"] else None
                        ymin = float(map_values["-YMIN-"]) if map_values["-YMIN-"] else None
                        ymax = float(map_values["-YMAX-"]) if map_values["-YMAX-"] else None
                    except Exception as e:
                        print(f"[WARNING] Invalid axis limits: {e}")

                    # Optional colormap limits
                    try:
                        vmin = float(map_values["-VMIN-"]) if map_values["-VMIN-"] else None
                        vmax = float(map_values["-VMAX-"]) if map_values["-VMAX-"] else None
                    except Exception as e:
                        print(f"[WARNING] Invalid colormap range: {e}")
                        vmin, vmax = None, None
                            
                    success = True
                    for quantity in result_df.columns[1:]:
                        filename = f"{folder}/{stm.sanitize_filename(quantity)}.png"
                        filename_radial = f"{folder}/{stm.sanitize_filename(quantity)}_profile.png"
                        try:
                            if plot_radial:
                                try:
                                    if offset:
                                        fig, ax = stm.plot_radial_profile_bins(xbin, ybin, bin_id, result_df_mod, quantity)
                                    else:
                                        fig, ax = stm.plot_radial_profile_bins(xbin, ybin, bin_id, result_df, quantity)
                                    
                                    if xmin is not None and xmax is not None:
                                        ax.set_xlim(xmin, xmax)
                                    if ymin is not None and ymax is not None:
                                        ax.set_ylim(ymin, ymax)

                                    plt.tight_layout()
                                    fig.savefig(filename_radial, dpi=300)
                                    plt.close(fig)
                                except Exception as e:
                                    sg.popup_error(f"Error in radial profile plot:\n{e}")
                                    
                            elif smoothing:
                                img_path = map_values["-IMG-"]
                                
                                if offset:
                                    fig, ax = stm.plot_reprojected_map(x, y, bin_id, result_df_mod, quantity, cmap=map_values["-CMAP-"], smoothing=map_values["-SMOOTH-"], sigma=float(map_values["-SIGMA-"]), vmin=vmin, vmax=vmax)
                                else:
                                    fig, ax = stm.plot_reprojected_map(x, y, bin_id, result_df, quantity, cmap=map_values["-CMAP-"], smoothing=map_values["-SMOOTH-"], sigma=float(map_values["-SIGMA-"]), vmin=vmin, vmax=vmax)

                                if img_path and os.path.isfile(img_path):
                                    try:
                                        level_str = map_values["-ISOLEVELS-"]
                                        iso_levels = [float(val) for val in level_str.split(",") if val.strip() != ""]
                                        iso_levels.sort()
                                    except Exception:
                                        iso_levels = None
                                    stm.overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
                                    
                                # Set X and Y limits if provided
                                if xmin is not None and xmax is not None:
                                    ax.set_xlim(xmin, xmax)
                                if ymin is not None and ymax is not None:
                                    ax.set_ylim(ymin, ymax)
                                
                                plt.tight_layout()
                                fig.savefig(filename, dpi=300)
                                plt.close(fig)
                            
                            else:
                                img_path = map_values["-IMG-"]
                                try:
                                    level_str = map_values["-ISOLEVELS-"]
                                    iso_levels = [float(val.strip()) for val in level_str.split(",") if val.strip()]
                                    iso_levels = sorted(set(iso_levels)) if len(iso_levels) >= 2 else None
                                except Exception:
                                    iso_levels = None

                                if offset:
                                    fig, ax = stm.plot_voronoi_map(x, y, bin_id, result_df_mod, quantity, cmap=map_values["-CMAP-"], img_path=img_path, iso_levels=iso_levels, vmin=vmin, vmax=vmax)
                                else:
                                    fig, ax = stm.plot_voronoi_map(x, y, bin_id, result_df, quantity, cmap=map_values["-CMAP-"], img_path=img_path, iso_levels=iso_levels, vmin=vmin, vmax=vmax)

                                # Set X and Y limits if provided
                                if xmin is not None and xmax is not None:
                                    ax.set_xlim(xmin, xmax)
                                if ymin is not None and ymax is not None:
                                    ax.set_ylim(ymin, ymax)
                                
                                plt.tight_layout()
                                fig.savefig(filename, dpi=300)
                                plt.close(fig)
                        except Exception as e:
                            success = False
                            sg.popup_error(f"Error saving image {quantity}:\n{e}")
                    if success:
                        sg.popup("All maps saved successfully.")
            else:
                sg.popup("Please load files before saving.")

        elif map_event == 'Help':
            f = open(os.path.join(BASE_DIR, "help_files", "help_maps.txt"), 'r')
            file_contents = f.read()
            if layout == layouts.layout_android:
                sg.popup_scrolled(file_contents, size=(120, 30))
            else:
                sg.popup_scrolled(file_contents, size=(100, 40))

        elif map_event == "Exit":
            break

    map_window.close()

    #updating the parameters
    params = replace(params,
                    fits_path = fits_path,
                    txt_path = txt_path,
                    plot_maps_fits_image = plot_maps_fits_image,
                    plot_maps_contour_percentiles = plot_maps_contour_percentiles,
                    plot_maps_xlim_min = plot_maps_xlim_min,
                    plot_maps_xlim_max = plot_maps_xlim_max,
                    plot_maps_ylim_min = plot_maps_ylim_min,
                    plot_maps_ylim_max = plot_maps_ylim_max,
                    plot_maps_map_range_min = plot_maps_map_range_min,
                    plot_maps_map_range_max = plot_maps_map_range_max,
                    plot_maps_offet = plot_maps_offet,
                    plot_maps_offset_value = plot_maps_offset_value,
                    plot_maps_gaussian_smooth = plot_maps_gaussian_smooth,
                    plot_maps_gaussian_smooth_value = plot_maps_gaussian_smooth_value,
                    plot_maps_radial_profiles = plot_maps_radial_profiles,
                    plot_maps_colormap = plot_maps_colormap,
                     )
    
    return params


#3) TEXT EDITOR
def text_editor_window(layout):
    print('***** Text editor open. The main panel will be inactive until you close the editor *****')

    layout, scale_win, fontsize, default_size = misc.get_layout()
    sg.theme('DarkBlue3')

    if layout == layouts.layout_android:
        editor_layout = [
            [sg.Multiline(size=(120, 20), key='-TEXT-', font=('Helvetica', 12))],
            [sg.Button('Open', key='-OPEN-', size = (15,1), font=('Helvetica', 12), button_color=('black','light green')), sg.Button('Save', key='-SAVE-', size = (15,1), font=('Helvetica', 12)),  sg.Button('Find', size = (15,1), font=('Helvetica', 12)), sg.Button('Undo', size = (15,1), font=('Helvetica', 12)) ],
            [sg.Button('Find/Replace', size = (15,1), font=('Helvetica', 12)), sg.Button('Match rows', size = (15,1), font=('Helvetica', 12)), sg.Button('Create New Column', size = (15,1), font=('Helvetica', 12)), sg.Button('Delete Columns', size = (15,1), font=('Helvetica', 12)), sg.Push(), sg.Button('Close', button_color=('white','orange'), size = (15,1), font=('Helvetica', 12, 'bold'))]
        ]
    else:
        editor_layout = [
            [sg.Multiline(size=(90, 30), key='-TEXT-', font=('Helvetica', 12))],
            [sg.Button('Open', key='-OPEN-', size = (15,1), font=('Helvetica', 12), button_color=('black','light green')), sg.Button('Save', key='-SAVE-', size = (15,1), font=('Helvetica', 12)),  sg.Button('Find', size = (15,1), font=('Helvetica', 12)), sg.Button('Undo', size = (15,1), font=('Helvetica', 12)) ],
            [sg.Button('Find/Replace', size = (15,1), font=('Helvetica', 12)), sg.Button('Match rows', size = (15,1), font=('Helvetica', 12)), sg.Button('Create New Column', size = (15,1), font=('Helvetica', 12)), sg.Button('Delete Columns', size = (15,1), font=('Helvetica', 12)), sg.Push(), sg.Button('Close', button_color=('white','orange'), size = (15,1), font=('Helvetica', 12, 'bold'))]
        ]

    window_editor = open_subwindow('Text editor', editor_layout, zm=zm)
    file_modified = False
    text_backup = ""

    while True:
        editor_event, editor_values = window_editor.read()

        if editor_event == sg.WIN_CLOSED or editor_event == 'Close':
            if file_modified:
                confirm_close = sg.popup_yes_no(
                    'Changes have not been saved. Are you sure you want to close?', 'Close')
                if confirm_close == 'Yes':
                    print('Text editor closed. This main panel is now active again')
                    print('')
                    break
            else:
                print('Text editor closed. This main panel is now active again')
                print('')
                break
        elif editor_event == '-SAVE-':
            text = editor_values['-TEXT-']
            filename = sg.popup_get_file('Save the file', save_as=True, default_extension=".txt")
            if filename:
                stm.save_file(filename, text)
                sg.popup(f'The file {filename} has been saved.')
                file_modified = False  # Reset the modification flag
        elif editor_event == '-OPEN-':
            if file_modified:
                confirm_open = sg.popup_yes_no(
                    'Changes have not been saved. Are you sure you want to open a new file?', 'Open')
                if confirm_open == 'No':
                    continue
            filename = sg.popup_get_file('Open file', default_extension=".txt")
            if filename:
                with open(filename, 'r') as file:
                    try:
                        text = file.read()
                        text_backup = text  # Backup the original text
                    except UnicodeDecodeError:
                        sg.popup('Invalid file. I just read simple txt files!')
                        continue
                window_editor['-TEXT-'].update(text)
                file_modified = False  # Reset the modification flag
        elif editor_event == 'Find':
            find_text = sg.popup_get_text('Enter text to find:')
            if find_text:
                text_to_search = editor_values['-TEXT-']
                if find_text in text_to_search:
                    sg.popup(f'Text found at position: {text_to_search.find(find_text)}')
                else:
                    sg.popup('Text not found.')
        elif editor_event == 'Find/Replace':
            find_text = sg.popup_get_text('Enter text to find:')
            if find_text:
                replace_text = sg.popup_get_text('Enter text to replace with:')
                if replace_text is not None:
                    replace_all = sg.popup_yes_no('Replace all occurrences?', 'Replace All')
                    if replace_all == 'Yes':
                        text_to_search = editor_values['-TEXT-']
                        updated_text = stm.find_replace(text_to_search, find_text, replace_text, replace_all)
                        window_editor['-TEXT-'].update(updated_text)
                        file_modified = True  # Set the modification flag
        elif editor_event == 'Match rows':
            sg.theme('DarkBlue3')

            match_layout = [
                [sg.Text('Select the first file:'), sg.InputText(key='-FILE1-', readonly=True),
                    sg.FileBrowse(file_types=(("Text Files", "*.*"),))],
                [sg.Text('Select the second file:'), sg.InputText(key='-FILE2-', readonly=True),
                    sg.FileBrowse(file_types=(("Text Files", "*.*"),))],
                [sg.Text('Select the common column:'), sg.InputText(key='-COMMON_COLUMN-')],
                [sg.Button('Merge'), sg.Button('Exit')]
            ]

            match_window = open_subwindow('Match and merge rows', match_layout, zm=zm)

            while True:
                match_event, match_values = match_window.read()

                if match_event == sg.WIN_CLOSED or match_event == 'Exit':
                    break
                elif match_event == 'Merge':
                    file1_path = match_values['-FILE1-']
                    file2_path = match_values['-FILE2-']
                    common_column = match_values['-COMMON_COLUMN-']

                    if file1_path and file2_path and common_column:
                        stm.merge_files(file1_path, file2_path, common_column)
                    else:
                        sg.popup_error('Please select both files and enter a common column.')

            match_window.close()
        elif editor_event == 'Create New Column':
            new_column_name = sg.popup_get_text('Enter the name for the new column:')
            if new_column_name:
                col1_name = sg.popup_get_text('Enter the name of the first column:')
                col2_name = sg.popup_get_text('Enter the name of the second column:')
                expression = sg.popup_get_text('Enter the algebraic expression (e.g., col1 + col2):')
                if col1_name and col2_name and expression:
                    try:
                        df = pd.read_csv(io.StringIO(editor_values['-TEXT-']), delimiter=r'\s+')

                        col1_name_clean = col1_name.replace(' ', '_')
                        col2_name_clean = col2_name.replace(' ', '_')

                        df = stm.create_new_column(df, new_column_name, col1_name_clean, col2_name_clean, expression)

                        if df is not None:
                            window_editor['-TEXT-'].update(df.to_csv(index=False, sep=' ', na_rep=''))
                            file_modified = True  # Set the modification flag
                    except Exception as e:
                        sg.popup_error(f'Error creating the new column: {str(e)}')
                else:
                    sg.popup_error('Please enter names for both columns and the algebraic expression.')

        elif editor_event == 'Delete Columns':
            columns_to_delete = sg.popup_get_text(
                'Enter column names to delete (comma-separated):')
            if columns_to_delete:
                try:
                    df = pd.read_csv(io.StringIO(editor_values['-TEXT-']), delimiter=r'\s+')
                    columns_to_delete_list = [col.strip() for col in columns_to_delete.split(',')]
                    df = df.drop(columns=columns_to_delete_list, errors='ignore')
                    window_editor['-TEXT-'].update(df.to_csv(index=False, sep=' ', na_rep=''))
                    file_modified = True  # Set the modification flag
                except Exception as e:
                    sg.popup_error(f'Error deleting columns: {str(e)}')


        elif editor_event == 'Undo':
            # Undo
            window_editor['-TEXT-'].update(text_backup)
            file_modified = True
        elif editor_event == '-TEXT-':
            text_backup = editor_values['-TEXT-']
            file_modified = True


    window_editor.close()



# 4) FITS HEADER EDITOR
def fits_header_window():

    layout, scale_win, fontsize, default_size = misc.get_layout()
    sg.theme('DarkBlue3')
    fitsheader_layout = [
        [sg.Text('Please, select what operation you want to perform on the header of the fits file(s)', font = ('', default_size))],
        [sg.Button('Single fits header editor',button_color= ('black','orange'), size = (22,2), key ='hdr_single_file', font = ('', default_size)), sg.Button('List of fits header editor',button_color= ('black','orange'), size = (22,2), key ='hdr_list_file', font = ('', default_size)), sg.Button('Extract keyword from a list',button_color= ('black','orange'), size = (22,2), key ='extract_keyword', font = ('', default_size))],
        [sg.Button('Close')]
        ]

    print ('*** Fits header editor open. The main panel will be inactive until you close the window ***')
    fitsheader_window = open_subwindow('Fits header editor', fitsheader_layout, zm=zm)

    while True:

        fitsheader_event, fitsheader_values = fitsheader_window.read()

        if fitsheader_event == sg.WIN_CLOSED or fitsheader_event == 'Close':
            print ('Fits editor closed. This main panel is now active again')
            print ('')
            break

        #modify/add/delete keyword for a single fits
        if fitsheader_event == 'hdr_single_file':
            sg.theme('DarkBlue3')
            subfitsheader_layout = [
                [sg.Text("Select a FITS file")],
                [sg.Input(key='-FILE-', enable_events=True), sg.FileBrowse()],
                [sg.Multiline(key='-HEADER-', size=(60, 15), disabled=True)],
                [sg.Text("Modify/Add Keyword"),
                sg.Input(key='-KEY-', size=(20, 1)),
                sg.Input(key='-VALUE-', size=(20, 1)),
                sg.Checkbox("Numerical value", key='-NUMERIC-', enable_events=True),
                sg.Button("Add/Modify"), sg.Button("Delete")],  # Added "Delete" button
                [sg.Button("Save Header"), sg.Button("Exit")]
            ]

            subfitsheader_window = open_subwindow("Single FITS header editor", subfitsheader_layout, zm=zm)

            while True:
                subfitsheader_event, subfitsheader_values = subfitsheader_window.read()

                if subfitsheader_event == sg.WINDOW_CLOSED or subfitsheader_event == 'Exit':
                    break

                if subfitsheader_event == '-FILE-':
                    file_path = subfitsheader_values['-FILE-']
                    header = stm.read_fits_header(file_path)
                    subfitsheader_window['-HEADER-'].update(repr(header))

                if subfitsheader_event == 'Add/Modify':
                    key = subfitsheader_values['-KEY-']
                    value = subfitsheader_values['-VALUE-']
                    is_numeric = subfitsheader_values['-NUMERIC-']

                    if key:
                        if is_numeric:
                            try:
                                value = float(value)
                            except ValueError:
                                sg.popup_error("Vale must be a number")
                                continue

                        header[key] = value
                        subfitsheader_window['-HEADER-'].update(repr(header))

                if subfitsheader_event == 'Delete':
                    key_to_delete = subfitsheader_values['-KEY-']
                    if key_to_delete:
                        delete_result = stm.delete_keyword(header, key_to_delete)
                        if delete_result is True:
                            subfitsheader_window['-HEADER-'].update(repr(header))
                        else:
                            sg.popup_error(f"Error during deletion: {delete_result}")


                if subfitsheader_event == 'Save Header':
                    if 'file_path' in locals():
                        save_result = stm.save_fits_header(file_path, header)
                        if save_result is True:
                            sg.popup("Header saved with succes!")
                        else:
                            sg.popup_error(f"Error during the saving of the header: {save_result}")
                    else:
                        sg.popup_error("First select a FITS file.")

            subfitsheader_window.close()


        if fitsheader_event == 'hdr_list_file':
            sg.theme('DarkBlue3')

            hdr_list_layout = [
                [sg.Text("Select a list containing only FITS files")],
                [sg.Input(key='-FILELIST-', enable_events=True), sg.FileBrowse()],
                [sg.Text("Select a list containing the keyword you want to change (format: key=value=type)"), sg.Input(key='-KEYFILE-', enable_events=True), sg.FileBrowse()],
                [sg.Multiline(key='-HEADER-', size=(60, 15), disabled=True)],
                [sg.Button("Add/Modify"), sg.Button("Delete"), sg.Button("Exit")]
            ]

            hdr_list_window = open_subwindow("FITS header editor", hdr_list_layout, zm=zm)

            while True:
                hdr_list_event, hdr_list_values = hdr_list_window.read()

                if hdr_list_event == sg.WINDOW_CLOSED or hdr_list_event == 'Exit':
                    break

                if hdr_list_event == '-FILELIST-':
                    file_list_path = hdr_list_values['-FILELIST-']

                if hdr_list_event == '-KEYFILE-':
                    key_file_path = hdr_list_values['-KEYFILE-']
                try:
                    if hdr_list_event == 'Add/Modify':
                        if not file_list_path or not key_file_path:
                            sg.popup_error("Something is wrong. Check the files")
                            continue

                        file_paths = stm.read_file_list(file_list_path)
                        if not file_paths:
                            sg.popup_error("Something is wrong. Check the files")
                            continue

                        try:
                            key_paths = stm.read_file_list(key_file_path)
                            key_name, key_value = stm.read_keyword_values_from_file(key_file_path)
                        except ValueError:
                            sg.popup_error('The keyword file is not correct. Chek it!')
                            continue

                        if len(file_paths) != len(key_paths):
                            sg.popup ('The length of the fits file is different from the length of the key file, or you just loaded wrong files. Try again')
                            continue

                        cond = 0

                        try:
                            for i in range (len(file_paths)):
                                with fits.open(file_paths[i], mode='update') as hdul:
                                # Put the keyword in the first HDU)
                                    hdul[0].header[key_name[i]] = (key_value[i])

                                # Save
                                    hdul.flush()

                                cond = cond +1
                                hdr = hdul[0].header

                                hdr_list_window['-HEADER-'].update(repr(hdr))

                        except (AttributeError, ValueError):
                            sg.popup_error('Something is wrong. Check and try again')

                        sg.popup('Successfully modified headers: ', cond, '/', len(file_paths))
                except Exception:
                    sg.popup('File missing')
                    continue

                try:
                    if hdr_list_event == 'Delete':
                        file_paths = stm.read_file_list(file_list_path)
                        key_to_delete = sg.popup_get_text("Enter the keyword to delete:")
                        if key_to_delete:
                            cond = 0
                            try:
                                for i in range(len(file_paths)):
                                    try:
                                        with fits.open(file_paths[i], mode='update') as hdul:
                                            # Aggiungi la keyword all'header del primo HDU (Header Data Unit)
                                            header = hdul[0].header
                                            header.remove(key_to_delete)
                                            # Salva le modifiche
                                            hdul.flush()

                                        cond = cond + 1
                                        hdr = hdul[0].header
                                    except KeyError:
                                        print ('Keyword not found')
                                        continue

                                    hdr_list_window['-HEADER-'].update(repr(hdr))
                            except FileNotFoundError:
                                sg.popup ('Incorrect file or missing')
                                continue
                            if cond > 0:
                                sg.popup(f'Successfully deleted keyword "{key_to_delete}" from headers: {cond}/{len(file_paths)}')
                            else:
                                sg.popup ('Keyword not found')
                except NameError:
                    sg.popup ('No file to process!')
                    continue
            hdr_list_window.close()


        if fitsheader_event == 'extract_keyword':

            sg.theme('DarkBlue3')

            ext_key_layout = [
                [sg.Text("Select a list of FITS files")],
                [sg.Input(key='-FILELIST-', enable_events=True), sg.FileBrowse()],
                [sg.Text("Insert the keyword to extract (case insensitive)"), sg.Input(key='-KEYWORD-')],
                [sg.Multiline(key='-OUTPUT-', size=(60, 15), disabled=True)],
                [sg.Button("Extract and Save"), sg.Button("Exit")]
            ]

            ext_key_window = open_subwindow("Extract and Save Keyword", ext_key_layout, zm=zm)

            while True:
                ext_key_event, ext_key_values = ext_key_window.read()

                if ext_key_event == sg.WINDOW_CLOSED or ext_key_event == 'Exit':
                    break

                if ext_key_event == '-FILELIST-':
                    file_list_path = ext_key_values['-FILELIST-']

                try:
                    if ext_key_event == 'Extract and Save':
                        if not file_list_path:
                            sg.popup_error("Select a list of FITS files with relative path included.")
                            continue

                        keyword = ext_key_values['-KEYWORD-'].strip()
                        if not keyword:
                            sg.popup_error("Insert the keyword you want to extract")
                            continue
                        try:
                            file_paths = [line.strip() for line in open(file_list_path) if not line.startswith('#')]
                            data = []
                        except Exception:
                            sg.popup ('Problems with the fits list file. Chek it, please')
                            continue

                        for file_path in file_paths:
                            file_path = file_path.strip()
                            value = stm.extract_keyword(file_path, keyword)
                            data.append({'file': file_path, 'keyword': keyword, 'value': value})

                        ext_key_window['-OUTPUT-'].update('')
                        for entry in data:
                            ext_key_window['-OUTPUT-'].print(f"{entry['file']} - {entry['keyword']}: {entry['value']}")

                        output_file = sg.popup_get_file('Save on file', save_as=True, file_types=(("Text Files", "*.txt"),))
                        if output_file:
                            stm.save_to_text_file(data, output_file)
                            sg.popup(f"Results saved on: '{output_file}'")
                except NameError:
                    sg.popup ('File not found!')
                    continue

            ext_key_window.close()

    fitsheader_window.close()



# 5) LONG-SLIT EXTRACTION
def long_slit_extraction(BASE_DIR, layout, params):

    file_path_spec_extr = params.file_path_spec_extr
    trace_y_range_str = params.trace_y_range_str
    poly_degree_str = params.poly_degree_str
    extract_y_range_str = params.extract_y_range_str
    snr_threshold_str = params.snr_threshold_str
    pixel_scale_str = params.pixel_scale_str
    result_data = params.result_data
    result_long_slit_extract = params.result_long_slit_extract
    result_list_dir = params.result_list_dir

    layout, scale_win, fontsize, default_size = misc.get_layout()
    sg.theme('DarkBlue3')
    x_axis = np.array([])
    # Define FreeSimpleGUI layout
    spec_extr_layout = [
        [sg.Text("Select FITS File:", font=("Helvetica", 15, 'bold'), text_color = 'light blue'), sg.InputText(default_text = file_path_spec_extr, key="file_path", size = (38,1), font = ('', default_size)), sg.FileBrowse(font = ('', default_size))],
        [sg.Text("Select Y Range for Trace Fitting:", font = ('', default_size)), sg.InputText(default_text= trace_y_range_str, key="trace_y_range",size=(12, 1), font = ('', default_size)), sg.Text("Degree to fit:", font = ('', default_size)), sg.InputText(default_text= poly_degree_str, key="poly_degree",size=(5, 1), font = ('', default_size))],
        [sg.Button("1) Open 2D Spectrum", button_color=('black','light blue'), size=(18, 1), tooltip='First we have to load and visualize the spectrum', font = ('', default_size)), sg.Button("2) Fit Trace",button_color=('black','light green'), size=(19, 1), tooltip='Now we find the trace of the spectrum along the dispersion axis', font = ('', default_size)), sg.Button("3) Correct Spectrum",button_color=('black','orange'), size=(18, 1), tooltip='Finally we correct the distortion of the spectrum before the extraction', font = ('', default_size))],
        [sg.HorizontalSeparator()],
        [sg.Button("Extract 1D Spectrum",size=(20, 1), tooltip='Extract 1D spectrum within the selected Y range. Useful for point sources', font = ('', default_size)), sg.Text("Y Range for Extract 1D Spectrum:", font = ('', default_size)), sg.InputText(default_text=extract_y_range_str, key="extract_y_range",size=(12, 1), font = ('', default_size))],
        [sg.Button("Extract SNR bin Spectra",size=(20, 1), tooltip='Extract n bins with the selected SNR Threshold. Useful for extended sources', font = ('', default_size)), sg.Text('SNR Threshold:', font = ('', default_size)), sg.InputText(key='snr',size=(4, 1), default_text=snr_threshold_str, font = ('', default_size)), sg.Text('Pix scale ("/pix):', font = ('', default_size)), sg.InputText(key='pix_scale',size=(5, 1), default_text=pixel_scale_str, font = ('', default_size))],
        [sg.Canvas(key="-CANVAS-")],
        [sg.Button("Help", size=(12, 1),button_color=('black','orange'), font = ('', default_size)), sg.Push(), sg.Button("Exit", size=(12, 1), font = ('', default_size))]
    ]

    print ('*** 2D spectra extraction open. The main panel will be inactive until you close the window ***')

    spec_extr_window = open_subwindow("2D spectra extraction", spec_extr_layout, zm=zm)
    canvas_elem = spec_extr_window["-CANVAS-"]
    canvas = canvas_elem.Widget

    trace_model = None

    # Event loop
    while True:
        spec_extr_event, spec_extr_values = spec_extr_window.read()

        if spec_extr_event == (sg.WIN_CLOSED):
            print('2D spec window closed. This main panel is now active again')
            print('')
            break

        file_path_spec_extr= spec_extr_values['file_path']
        trace_y_range_str= spec_extr_values['trace_y_range']
        poly_degree_str= spec_extr_values['poly_degree']
        extract_y_range_str= spec_extr_values['extract_y_range']
        snr_threshold_str= spec_extr_values['snr']
        pixel_scale_str= spec_extr_values['pix_scale']

        if spec_extr_event == ('Exit'):
            print('2D spec window closed. This main panel is now active again')
            print('')
            break

        if spec_extr_event == "1) Open 2D Spectrum":

            try:
                trace_model = None
                spectrum, header = stm.open_fits(file_path_spec_extr)
                x_axis = np.arange(len(spectrum[0]))
                plt.imshow(spectrum, cmap="viridis", norm=LogNorm())
                plt.title("2D Spectrum")
                plt.show()
                plt.close()
            except Exception:
                sg.popup ('Spectrum not valid. Must be a 2D fits image!')

        if spec_extr_event == "2) Fit Trace":

            try:
                trace_y_range = eval(trace_y_range_str)
                poly_degree = int(poly_degree_str)

                if poly_degree < 1 or poly_degree > 5:
                    sg.popup ('The polynomial degree should be between 1 and 5')
                    continue

                trace_model = stm.find_and_fit_spectroscopic_trace(spectrum, trace_y_range, poly_degree, True, True)

            except Exception as e:
                sg.popup_error(f"Error: {str(e)}")

        if spec_extr_event == "3) Correct Spectrum":
            trace_y_range = eval(trace_y_range_str)

            if trace_model is not None:
                corrected_spectrum = stm.correct_distortion_slope(spectrum, trace_model, trace_y_range)
            else:
                sg.popup_error("Please find and fit the spectroscopic trace first.")

        if spec_extr_event == "Extract 1D Spectrum":
            if trace_model is not None:
                try:
                    extract_y_range = eval(extract_y_range_str)
                    extracted_filename = os.path.splitext(os.path.basename(file_path_spec_extr))[0]
                    #creating the directory
                    result_longslit_extraction = result_data+'/longslit_extracted/'+extracted_filename+'/'
                    os.makedirs(result_longslit_extraction, exist_ok=True)
                    stm.extract_1d_spectrum(corrected_spectrum, extract_y_range, header, x_axis, output_fits_path= (result_longslit_extraction + f"{extracted_filename}_extracted_.fits"))
                    sg.popup ('1D spectrum saved in ', result_longslit_extraction)
                except Exception:
                    sg.popup('Extraction parameters not valid. Spectrum not extracted')
                    continue
            else:
                sg.popup_error("Please find and fit the spectroscopic trace first.")

        if spec_extr_event == "Extract SNR bin Spectra":
            if trace_model is not None and 'corrected_spectrum' in locals():

                try:
                    snr_threshold = float(snr_threshold_str)
                    pixel_scale = float(pixel_scale_str)
                except Exception:
                    sg.popup ('SNR or pixel scale values not valid!')
                    continue

                if snr_threshold < 0 or pixel_scale < 0:
                    sg.popup ('SNR and pixel scale values canoot be negative')
                    continue

                y_correction_trace_position = trace_y_range[0]
                stm.extract_and_save_snr_spectra(corrected_spectrum, trace_model, header, x_axis, snr_threshold, pixel_scale, file_path_spec_extr, y_correction_trace_position, result_long_slit_extract)

                #create spectra list of the bins to use with SPAN
                extracted_filename = os.path.splitext(os.path.basename(file_path_spec_extr))[0]
                result_longslit_extraction_bins = result_data+'/longslit_extracted/'+extracted_filename+'/bins/'
                os.makedirs(result_longslit_extraction_bins, exist_ok=True)
                file_list = stm.get_files_in_folder(result_longslit_extraction_bins)
                output_file = result_list_dir +'/' + extracted_filename +'_bins_list.txt'
                stm.save_to_text_file(file_list, output_file)
                sg.Popup('Spectra file list of the bins saved in ', output_file, 'You can now browse and load this list file')

            else:
                sg.popup_error("Please correct the spectrum and find the spectroscopic trace first.")

        if spec_extr_event == 'Help':
            f = open(os.path.join(BASE_DIR, "help_files", "help_2d_spec.txt"), 'r')
            file_contents = f.read()
            if layout == layouts.layout_android:
                sg.popup_scrolled(file_contents, size=(120, 30))
            else:
                sg.popup_scrolled(file_contents, size=(100, 40))

    spec_extr_window.close()

    #updating the params
    params = replace(params,
                    file_path_spec_extr = file_path_spec_extr,
                    trace_y_range_str = trace_y_range_str,
                    poly_degree_str = poly_degree_str,
                    extract_y_range_str = extract_y_range_str,
                    snr_threshold_str = snr_threshold_str,
                    pixel_scale_str = pixel_scale_str,
                     )

    return params



# 6) DATACUBE EXTRACTION
def datacube_extraction(params):

    result_data = params.result_data
    result_list_dir = params.result_list_dir
    ifs_run_id = params.ifs_run_id
    ifs_input = params.ifs_input
    ifs_redshift = params.ifs_redshift
    ifs_ow_output = params.ifs_ow_output
    ifs_lmin_tot = params.ifs_lmin_tot
    ifs_lmax_tot = params.ifs_lmax_tot
    ifs_preloaded_routine = params.ifs_preloaded_routine
    ifs_min_snr_mask = params.ifs_min_snr_mask
    ifs_target_snr_voronoi = params.ifs_target_snr_voronoi
    ifs_target_snr_elliptical = params.ifs_target_snr_elliptical
    ifs_routine_read = params.ifs_routine_read
    ifs_routine_read_default = params.ifs_routine_read_default
    ifs_user_routine = params.ifs_user_routine
    ifs_user_routine_file = params.ifs_user_routine_file
    ifs_origin = params.ifs_origin
    ifs_mask = params.ifs_mask
    ifs_output = params.ifs_output
    ifs_lmin_snr = params.ifs_lmin_snr
    ifs_lmax_snr = params.ifs_lmax_snr
    ifs_manual_bin = params.ifs_manual_bin
    ifs_voronoi = params.ifs_voronoi
    ifs_existing_bin = params.ifs_existing_bin
    ifs_existing_bin_folder = params.ifs_existing_bin_folder
    ifs_bin_method = params.ifs_bin_method
    ifs_covariance = params.ifs_covariance
    ifs_elliptical = params.ifs_elliptical
    ifs_pa_user = params.ifs_pa_user
    ifs_q_user = params.ifs_q_user
    ifs_ell_r_max = params.ifs_ell_r_max
    ifs_ell_min_dr = params.ifs_ell_min_dr
    isf_auto_pa_q = params.isf_auto_pa_q
    isf_auto_center = params.isf_auto_center


    layout, scale_win, fontsize, default_size = misc.get_layout()
    sg.theme('LightBlue1')

    cube_ifs_layout = [
        [sg.Text('Select a fits cube:', font = ('', default_size, 'bold'), tooltip='Select a datacube WITHIN the inputData folder'), sg.InputText(ifs_input, size=(45, 1), key = 'ifs_input', font = ('', default_size)), sg.FileBrowse(file_types=(('fits file', '*.fits *.fit'),), font = ('', default_size)), sg.Button('View datacube', button_color=('black','light blue'), size = (18,1), tooltip='Take a look at the datacube, it may be useful', font = ('', default_size))],
        [sg.Text('Name of the run:', tooltip='Just give a name for this session', font = ('', default_size)), sg.InputText(ifs_run_id, size = (15,1), key = 'ifs_run_id', font = ('', default_size)), sg.Text('z:', tooltip='Redshift estimation. Put zero to not correct for redshift', font = ('', default_size)), sg.InputText(ifs_redshift, size = (8,1), key = 'ifs_redshift', font = ('', default_size)), sg.Text('Wave to extract (A):', tooltip='Wavelength range you want to extract. Look at the datacube if you do not know', font = ('', default_size)), sg.InputText(ifs_lmin_tot, size = (6,1), key = 'ifs_lmin_tot', font = ('', default_size)), sg.Text('-', font = ('', default_size)), sg.InputText(ifs_lmax_tot, size = (6,1), key = 'ifs_lmax_tot', font = ('', default_size))],

        [sg.HorizontalSeparator()],

        [sg.Radio('Using a pre-loaded routine for extraction:', "RADIOCUBEROUTINE", default = ifs_preloaded_routine, key = 'ifs_preloaded_routine', font = ('', default_size, 'bold'), tooltip='These are pre-loaded routines for reading the most commin datacubes'), sg.InputCombo(ifs_routine_read,key='ifs_routine_read',default_value=ifs_routine_read_default, readonly=True, size = (18,1), font = ('', default_size))],
        [sg.Radio('Using a user defined routine for extraction:', "RADIOCUBEROUTINE", default = ifs_user_routine, key = 'ifs_user_routine', font = ('', default_size, 'bold'), tooltip='If you have your .py datacube read routine, load it here'), sg.InputText(ifs_user_routine_file, size=(15, 1), key = 'ifs_user_routine_file', font = ('', default_size)), sg.FileBrowse(file_types=(('py file', '*.py'),), font = ('', default_size))],
        [sg.Text('Origin (in pixel) of the coordinates:', tooltip='Pixel coordinates of the centre or the object you want to study. Look at the datacube to know it', font = ('', default_size)), sg.InputText(ifs_origin, size = (9,1), key = 'ifs_origin', font = ('', default_size)), sg.Text('Wavelength range for S/N:', tooltip='Insert the wavelength range (min, max) for S/N measurements. Leave empty to use the whole wave range inserted above', font = ('', default_size)), sg.InputText(ifs_lmin_snr, size = (6,1), key = 'ifs_lmin_snr', font = ('', default_size)), sg.Text('-', font = ('', default_size)), sg.InputText(ifs_lmax_snr, size = (6,1), key = 'ifs_lmax_snr', font = ('', default_size))],

        [sg.HorizontalSeparator()],

        [sg.Text('Select a mask:', font = ('', default_size, 'bold'), tooltip='If you do not have a mask file, you can create with the button on the right'), sg.InputText(ifs_mask, size=(20, 1), key = 'ifs_mask', font = ('', default_size)), sg.FileBrowse(file_types=(('fits file', '*.fits'),), font = ('', default_size)), sg.Button('Generate mask',button_color=('black','light blue'), size = (18,1), tooltip='Generate a mask, even without really masking any spaxel', font = ('', default_size)), sg.Text('Min S/N to mask:', tooltip='Masking all the spaxels with low S/N', font = ('', default_size)), sg.InputText(ifs_min_snr_mask, size = (6,1), key = 'ifs_min_snr_mask', font = ('', default_size))],

        [sg.HorizontalSeparator()],

        [sg.Text('Binning modes:', font = ('', default_size, 'bold'))],
        [sg.Radio('Voronoi binning with the following signal-to-noise:', "RADIOVOR", default=ifs_voronoi, key='ifs_voronoi', tooltip='Automatic voronoi rebinning', font = ('', default_size)), sg.Text('S/N:', tooltip='Select the S/N treshold of the binned spaxels. A good starting value is 30-50', font = ('', default_size)), sg.InputText(ifs_target_snr_voronoi, size = (4,1), key = 'ifs_target_snr_voronoi', font = ('', default_size))],
        [sg.Radio('Elliptical binning:', "RADIOVOR", default=ifs_elliptical, key='ifs_elliptical', tooltip='Elliptical/radial rebinning using the photometric center and the ellipticity of your galaxy', font = ('', default_size)), sg.Text('PA:', tooltip='PA of the galaxy', font = ('', default_size)), sg.InputText(ifs_pa_user, size = (4,1), key = 'ifs_pa_user', font = ('', default_size)), sg.Text('q:', tooltip='Insert the ellipticity of the bins. 1 is for circular annuli', font = ('', default_size)), sg.InputText(ifs_q_user, size = (3,1), key = 'ifs_q_user', font = ('', default_size)), sg.Checkbox('Auto ellipses', default = isf_auto_pa_q, key = 'isf_auto_pa_q', tooltip='If activated, SPAN will find the PA and q for you', font = ('', default_size)), sg.Checkbox('Auto center', default = isf_auto_center, key = 'isf_auto_center', tooltip='If activated, SPAN will find the photometric center instead using the origin of the coordinates', font = ('', default_size)), sg.Push(),  sg.Text('S/N:', tooltip='Select the minimum S/N of the bins. Set low to let dR decide the bin radiii', font = ('', default_size)), sg.InputText(ifs_target_snr_elliptical, size = (3,1), key = 'ifs_target_snr_elliptical', font = ('', default_size)), sg.Text('R max:', tooltip='Maximum radius in arcsec to consider for binning', font = ('', default_size)), sg.InputText(ifs_ell_r_max, size = (4,1), key = 'ifs_ell_r_max', font = ('', default_size)), sg.Text('dR:', tooltip='Minimum R thickness of the bins, in arcsec. Must be >= of the spaxel sampling', font = ('', default_size)), sg.InputText(ifs_ell_min_dr, size = (4,1), key = 'ifs_ell_min_dr', font = ('', default_size))],
        [sg.Radio('Manual binning by selecting custom regions or spaxels:', "RADIOVOR", default=ifs_manual_bin, key='ifs_manual_bin', tooltip='Select region(s) to bin. Masking is not applied here', font = ('', default_size)), sg.Button('Perform manual binning', tooltip='Open the datacube and draw regions to be binned together', font = ('', default_size))],
        [sg.Radio('Use already generated bin scheme stored in your pc', "RADIOVOR", default=ifs_existing_bin, key='ifs_existing_bin', tooltip='Use already available mask and bin info', font = ('', default_size)), sg.Input(ifs_existing_bin_folder, key='ifs_existing_bin_folder', size = (21,1), font = ('', default_size)), sg.FolderBrowse(tooltip='Browse the folder where your *_table.fits and *_mask.fits are located', font = ('', default_size))],

        [sg.HorizontalSeparator()],

        [sg.Button('Preview bins',button_color=('black','light green'), size = (18,1), font = ('', default_size)), sg.Button('Extract!',button_color= ('white','black'), size = (18,1), font = ('', default_size)), sg.Push(), sg.Button('I need help',button_color=('black','orange'), size = (12,1), font = ('', default_size)), sg.Exit(size=(18, 1), font = ('', default_size))],
    ]

    print ('*** Cube extraction routine open. The main panel will be inactive until you close the window ***')
    cube_ifs_window = open_subwindow('Cube extraction using GIST standard', cube_ifs_layout, zm=zm)

    while True:

        cube_ifs_event, cube_ifs_values = cube_ifs_window.read()

        if cube_ifs_event == (sg.WIN_CLOSED):
            print ('Cube extraction routine closed. This main panel is now active again')
            print ('')
            break



        #assigning user values
        ifs_run_id = cube_ifs_values['ifs_run_id']
        ifs_input = cube_ifs_values['ifs_input']
        ifs_routine_read_default = cube_ifs_values['ifs_routine_read']
        ifs_routine_selected  = os.path.join(BASE_DIR, "span_functions", "cube_extract_functions", f"{ifs_routine_read_default}.py")

        ifs_origin = cube_ifs_values['ifs_origin']
        ifs_mask = cube_ifs_values['ifs_mask']
        ifs_output_dir = ifs_output + ifs_run_id

        ifs_preloaded_routine = cube_ifs_values['ifs_preloaded_routine']
        ifs_user_routine = cube_ifs_values['ifs_user_routine']
        ifs_user_routine_file = cube_ifs_values['ifs_user_routine_file']

        ifs_manual_bin = cube_ifs_values['ifs_manual_bin']
        ifs_voronoi = cube_ifs_values['ifs_voronoi']
        ifs_elliptical = cube_ifs_values['ifs_elliptical']
        elliptical = ifs_elliptical
        
        isf_auto_pa_q = cube_ifs_values['isf_auto_pa_q']
        isf_auto_center = cube_ifs_values['isf_auto_center']

        if ifs_voronoi:
            ifs_bin_method = 'VORONOI'
        elif ifs_manual_bin:
            ifs_bin_method = 'SPAXEL'
        elif ifs_elliptical:
            ifs_bin_method = 'ELLIPTICAL'
            
        ifs_existing_bin = cube_ifs_values['ifs_existing_bin']
        if ifs_existing_bin:
            ifs_existing_bin_folder = cube_ifs_values['ifs_existing_bin_folder']

        try:
            ifs_redshift = float(cube_ifs_values['ifs_redshift'])
            ifs_lmin_tot = float(cube_ifs_values['ifs_lmin_tot'])
            ifs_lmax_tot = float(cube_ifs_values['ifs_lmax_tot'])
            ifs_min_snr_mask = float(cube_ifs_values['ifs_min_snr_mask'])
            
            ifs_target_snr_voronoi = float(cube_ifs_values['ifs_target_snr_voronoi'])
            ifs_target_snr_elliptical = float(cube_ifs_values['ifs_target_snr_elliptical'])
            
            ifs_target_snr = ifs_target_snr_elliptical if ifs_bin_method == 'ELLIPTICAL'  else ifs_target_snr_voronoi
            ifs_pa_user = float(cube_ifs_values['ifs_pa_user'])
            ifs_q_user = float(cube_ifs_values['ifs_q_user'])
            ifs_ell_r_max = float(cube_ifs_values['ifs_ell_r_max'])
            ifs_ell_min_dr = float(cube_ifs_values['ifs_ell_min_dr'])
            
            #Assumung the center of the new coordinate system is zero
            ell_x0=0
            ell_y0=0
            
            if isf_auto_pa_q and ifs_bin_method == 'ELLIPTICAL':
                ifs_pa = None
                ifs_q = None
            else: 
                ifs_pa = ifs_pa_user
                ifs_q = ifs_q_user
            if isf_auto_center and ifs_bin_method == 'ELLIPTICAL':
                ell_x0=None
                ell_y0=None
                
            
            user_lmin_snr = cube_ifs_values['ifs_lmin_snr']
            user_lmax_snr = cube_ifs_values['ifs_lmax_snr']

            if user_lmin_snr.strip() == '' or user_lmax_snr.strip() == '':
                # Using the wavelength range provided
                ifs_lmin_snr = ifs_lmin_tot
                ifs_lmax_snr = ifs_lmax_tot
                print(f"No S/N range specified, using full extraction range: {ifs_lmin_snr} - {ifs_lmax_snr}")
            else:
                try:
                    # Checking the input values
                    ifs_lmin_snr = float(user_lmin_snr)
                    ifs_lmax_snr = float(user_lmax_snr)
                except ValueError:
                    sg.popup("Invalid wavelength range for S/N. Please enter valid numbers.")
                    continue
            
        except Exception:
            sg.popup ('Invalid input parameters!')
            continue


        if ifs_user_routine:
            ifs_routine_selected = ifs_user_routine_file

        #routine to view the datacube
        if cube_ifs_event == 'View datacube':
            try:
                # Load the datacube
                data, wave = stm.read_datacube(ifs_input)

                # Create figure
                fig = plt.figure(figsize=(12, 7))
                gs = GridSpec(nrows=6, ncols=6, figure=fig)

                # === Image ===
                ax_img = fig.add_subplot(gs[:, :5])  # columns 0–4

                # === Initial data and scaling ===
                index = 0
                current_slice = data[index]
                masked_slice = np.ma.masked_invalid(current_slice)

                if masked_slice.count() > 0:
                    finite_values = masked_slice.compressed()
                    vmin = np.min(finite_values)
                    vmax = np.max(finite_values)
                else: #fallback
                    vmin, vmax = 0, 1

                # Show image
                img = ax_img.imshow(current_slice, cmap="gray", origin='lower', norm=Normalize(vmin=vmin, vmax=vmax))
                ax_img.set_title(f'Wavelength: {wave[index]:.2f} Å', pad=15)

                # SLIDERS
                ax_slider_wave = fig.add_axes([0.84, 0.20, 0.04, 0.75])  # [left, bottom, width, height]
                ax_slider_vmin = fig.add_axes([0.89, 0.20, 0.04, 0.75])
                ax_slider_vmax = fig.add_axes([0.94, 0.20, 0.04, 0.75])

                slider_wave = Slider(ax_slider_wave, 'λ', wave[0], wave[-1], valinit=wave[0], valfmt='%0.0f', orientation='vertical')
                slider_vmin = Slider(ax_slider_vmin, 'Min', vmin, vmax, valinit=vmin, orientation='vertical')
                slider_vmax = Slider(ax_slider_vmax, 'Max', vmin, vmax * 10, valinit=vmax, orientation='vertical')

                # RADIO BUTTON
                ax_radio = fig.add_axes([0.84, 0.05, 0.14, 0.08], facecolor='lightgoldenrodyellow')
                radio = RadioButtons(ax_radio, ('Linear scale', 'Log scale'), active=0)

                # Update function
                def update(val):
                    wave_val = slider_wave.val
                    i = (np.abs(wave - wave_val)).argmin()
                    current_data = data[i]
                    ax_img.set_title(f'Wavelength: {wave[i]:.2f} Å')

                    vmin_val = slider_vmin.val
                    vmax_val = slider_vmax.val
                    scale = radio.value_selected

                    if scale == 'Linear scale':
                        img.set_data(current_data)
                        img.set_norm(Normalize(vmin=vmin_val, vmax=vmax_val))
                    else:
                        safe_slice = np.array(current_data, copy=True)
                        safe_slice[~np.isfinite(safe_slice)] = np.nan
                        min_positive = np.nanmin(safe_slice[safe_slice > 0]) if np.any(safe_slice > 0) else 1e-3
                        safe_slice[safe_slice <= 0] = min_positive
                        img.set_data(safe_slice)

                        vmin_safe = max(vmin_val, min_positive)
                        if vmax_val <= vmin_safe * 1.01:
                            vmax_safe = vmin_safe * 1.01
                        else:
                            vmax_safe = vmax_val

                        img.set_norm(LogNorm(vmin=vmin_safe, vmax=vmax_safe))

                    fig.canvas.draw_idle()

                # === Connect widgets ===
                slider_wave.on_changed(update)
                slider_vmin.on_changed(update)
                slider_vmax.on_changed(update)
                radio.on_clicked(update)

                plt.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.05)
                plt.show()
                plt.close()

            except Exception as e:
                sg.popup('Datacube not found or not valid')
                continue


        #routine for generating a mask
        if cube_ifs_event == 'Generate mask':
            try:
                data, wave = stm.read_datacube(ifs_input)
                mask = np.zeros(data.shape[1:], dtype=int)

                # Layout
                fig = plt.figure(figsize=(12, 7))
                gs = GridSpec(nrows=6, ncols=6, figure=fig)
                ax_img = fig.add_subplot(gs[:, :5])

                current_slice = data[0]
                masked_slice = np.ma.masked_invalid(current_slice)
                if masked_slice.count() > 0:
                    finite_values = masked_slice.compressed()
                    vmin = np.min(finite_values)
                    vmax = np.max(finite_values)
                else:
                    vmin, vmax = 0, 1

                img = ax_img.imshow(current_slice, cmap="gray", origin='lower', norm=Normalize(vmin=vmin, vmax=vmax))
                mask_overlay = ax_img.imshow(np.ma.masked_where(mask == 0, mask), cmap='Reds', alpha=0.5, origin='lower')
                ax_img.set_title(f'Wavelength Index: 0')

                # Vertical slider
                ax_slider_wave = fig.add_axes([0.84, 0.20, 0.04, 0.75])
                ax_slider_vmin = fig.add_axes([0.89, 0.20, 0.04, 0.75])
                ax_slider_vmax = fig.add_axes([0.94, 0.20, 0.04, 0.75])
                slider_wave = Slider(ax_slider_wave, 'λ', 0, data.shape[0]-1, valinit=0, valfmt='%0.0f', orientation='vertical')
                slider_vmin = Slider(ax_slider_vmin, 'Min', vmin, vmax, valinit=vmin, orientation='vertical')
                slider_vmax = Slider(ax_slider_vmax, 'Max', vmin, vmax * 10, valinit=vmax, orientation='vertical')

                # Linear or log scale
                ax_radio = fig.add_axes([0.84, 0.05, 0.14, 0.08], facecolor='lightgoldenrodyellow')
                radio = RadioButtons(ax_radio, ('Linear scale', 'Log scale'), active=0)

                # User instructions
                instructions = (
                    "Ctrl + left click: mask a pixel\n"
                    "Ctrl + right click: unmask a pixel\n"
                    "Ctrl + drag: mask/unmask area\n"
                    "Close this window to save"
                    if layout != layouts.layout_android else
                    "Left click: mask a pixel\n"
                    "Right click: unmask a pixel\n"
                    "Drag: mask/unmask area\n"
                    "Close this window to save"
                )
                ax_img.text(1.05, 0.5, instructions, transform=ax_img.transAxes, fontsize=10, va='center', ha='left', color='blue')

                # State of the user interaction
                state = {'start_point': None, 'dragging': False, 'deselecting': False}

                # Visual update
                def update(val):
                    idx = int(slider_wave.val)
                    current_data = data[idx]
                    vmin_val = slider_vmin.val
                    vmax_val = slider_vmax.val
                    scale = radio.value_selected
                    ax_img.set_title(f'Wavelength Index: {idx}')

                    if scale == 'Linear scale':
                        img.set_data(current_data)
                        img.set_norm(Normalize(vmin=vmin_val, vmax=vmax_val))
                    else:
                        safe_slice = np.array(current_data, copy=True)
                        safe_slice[~np.isfinite(safe_slice)] = np.nan
                        min_positive = np.nanmin(safe_slice[safe_slice > 0]) if np.any(safe_slice > 0) else 1e-3
                        safe_slice[safe_slice <= 0] = min_positive
                        img.set_data(safe_slice)
                        vmin_safe = max(vmin_val, min_positive)
                        vmax_safe = max(vmax_val, vmin_safe * 1.01)
                        img.set_norm(LogNorm(vmin=vmin_safe, vmax=vmax_safe))

                    fig.canvas.draw_idle()

                slider_wave.on_changed(update)
                slider_vmin.on_changed(update)
                slider_vmax.on_changed(update)
                radio.on_clicked(update)

                # Mouse click and drag events
                def on_click(event):
                    if event.inaxes != ax_img or event.xdata is None or event.ydata is None:
                        return

                    if layout != layouts.layout_android:
                        if event.key is None or not any(k in event.key.lower() for k in ['ctrl', 'control']):
                            return

                    if event.button == 1:
                        state['start_point'] = (int(event.xdata), int(event.ydata))
                        state['dragging'] = True
                        state['deselecting'] = False
                    elif event.button == 3:
                        state['start_point'] = (int(event.xdata), int(event.ydata))
                        state['dragging'] = False
                        state['deselecting'] = True

                def on_release(event):
                    if event.inaxes == ax_img and state['start_point'] and event.xdata and event.ydata:
                        end_point = (int(event.xdata), int(event.ydata))
                        x0, y0 = state['start_point']
                        x1, y1 = end_point

                        if state['dragging']:
                            mask[min(y0, y1):max(y0, y1)+1, min(x0, x1):max(x0, x1)+1] = 1
                        elif state['deselecting']:
                            mask[min(y0, y1):max(y0, y1)+1, min(x0, x1):max(x0, x1)+1] = 0

                        mask_overlay.set_data(np.ma.masked_where(mask == 0, mask))
                        fig.canvas.draw()
                        state['start_point'] = None
                        state['dragging'] = False
                        state['deselecting'] = False

                fig.canvas.mpl_connect("button_press_event", on_click)
                fig.canvas.mpl_connect("button_release_event", on_release)

                plt.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.05)
                plt.show()
                plt.close()

                # Saving and updating the gui
                mask_name = f"mask_{ifs_run_id}_.fits"
                mask_path = os.path.join(result_data, mask_name)
                stm.save_mask_as_fits(mask, mask_path)

                sg.popup("Mask saved as", mask_name, "in", result_data, "folder and loaded.")
                cube_ifs_window['ifs_mask'].update(mask_path)

            except Exception as e:
                sg.popup("Fits datacube not valid.")
                continue

        if ifs_existing_bin:
            cubextr.handle_existing_bin_files(ifs_existing_bin_folder, ifs_output_dir, ifs_run_id)

        # preview mode for voronoi or elliptical binning
        if cube_ifs_event == 'Preview bins' and not ifs_manual_bin:
            voronoi = ifs_voronoi
            # elliptical = ifs_elliptical
            preview = True

            # Creating the disctionary to be passed to the cube_extract module
            config = cubextr.buildConfigFromGUI(
                ifs_run_id, ifs_input, ifs_output_dir, ifs_redshift,
                ifs_ow_output, ifs_routine_selected, ifs_origin,
                ifs_lmin_tot, ifs_lmax_tot, ifs_lmin_snr, ifs_lmax_snr,
                ifs_min_snr_mask, ifs_mask, ifs_bin_method, ifs_target_snr,
                ifs_covariance, ell_pa_astro_deg=ifs_pa, ell_x0=ell_x0, ell_y0=ell_y0, ell_q=ifs_q,
                       ell_min_dr=ifs_ell_min_dr, ell_r_max=ifs_ell_r_max)
            
                                                                                
            try:
                cubextr.extract(config, preview, voronoi, elliptical, ifs_manual_bin, ifs_existing_bin)
            except Exception as e:
                sg.popup("Error showing the bins:", str(e))
                continue

        # Performing manual binning by the user, by selecting one or multiple regions in a matplotlib iterative window
        # Using a modified version of the mask routine above to select the manual binning regions. Then inverting the mask to consider ONLY the selected spaxels.
        if cube_ifs_event == 'Perform manual binning':
            cube_ifs_window['ifs_manual_bin'].update(True)
            ifs_manual_bin = cube_ifs_values['ifs_manual_bin']

            try:
                data, wave = stm.read_datacube(ifs_input)
                bin_mask = np.zeros(data.shape[1:], dtype=int)

                # Matplotlib layout
                fig = plt.figure(figsize=(12, 7))
                gs = GridSpec(nrows=6, ncols=6, figure=fig)
                ax_img = fig.add_subplot(gs[:, :5])

                current_slice = data[0]
                masked_slice = np.ma.masked_invalid(current_slice)
                if masked_slice.count() > 0:
                    finite_values = masked_slice.compressed()
                    vmin = np.min(finite_values)
                    vmax = np.max(finite_values)
                else:
                    vmin, vmax = 0, 1

                img = ax_img.imshow(current_slice, cmap="gray", origin='lower',
                                    norm=Normalize(vmin=vmin, vmax=vmax))
                bin_mask_overlay = ax_img.imshow(np.ma.masked_where(bin_mask == 0, bin_mask),
                                                cmap='Reds', alpha=0.5, origin='lower')
                ax_img.set_title(f'Wavelength Index: 0')

                # Sliders for wave and luminosity
                ax_slider_wave = fig.add_axes([0.84, 0.20, 0.04, 0.75])
                ax_slider_vmin = fig.add_axes([0.89, 0.20, 0.04, 0.75])
                ax_slider_vmax = fig.add_axes([0.94, 0.20, 0.04, 0.75])
                slider_wave = Slider(ax_slider_wave, 'λ', 0, data.shape[0]-1,
                                    valinit=0, valfmt='%0.0f', orientation='vertical')
                slider_vmin = Slider(ax_slider_vmin, 'Min', vmin, vmax,
                                    valinit=vmin, orientation='vertical')
                slider_vmax = Slider(ax_slider_vmax, 'Max', vmin, vmax * 10,
                                    valinit=vmax, orientation='vertical')

                # Log or linear scale
                ax_radio = fig.add_axes([0.84, 0.05, 0.14, 0.08], facecolor='lightgoldenrodyellow')
                radio = RadioButtons(ax_radio, ('Linear scale', 'Log scale'), active=0)

                # Screen instructions
                instructions = (
                    "Ctrl + Left click: Select a spaxel\n"
                    "Ctrl + Right click: Deselect a spaxel\n"
                    "Ctrl + Drag: Select/Deselect area\n"
                    "Close this window to save"
                    if layout != layouts.layout_android else
                    "Left click: Select a spaxel\n"
                    "Right click: Deselect a spaxel\n"
                    "Drag: Select/Deselect area\n"
                    "Close this window to save"
                )
                ax_img.text(1.05, 0.5, instructions, transform=ax_img.transAxes,
                            fontsize=10, va='center', ha='left', color='blue')

                # States of the interaction
                interaction_state = {
                    'start_point': None,
                    'dragging': False,
                    'deselecting': False
                }

                # Visual update
                def update(val):
                    idx = int(slider_wave.val)
                    current_data = data[idx]
                    vmin_val = slider_vmin.val
                    vmax_val = slider_vmax.val
                    scale = radio.value_selected
                    ax_img.set_title(f'Wavelength Index: {idx}')

                    if scale == 'Linear scale':
                        img.set_data(current_data)
                        img.set_norm(Normalize(vmin=vmin_val, vmax=vmax_val))
                    else:
                        safe_slice = np.array(current_data, copy=True)
                        safe_slice[~np.isfinite(safe_slice)] = np.nan
                        min_positive = np.nanmin(safe_slice[safe_slice > 0]) if np.any(safe_slice > 0) else 1e-3
                        safe_slice[safe_slice <= 0] = min_positive
                        img.set_data(safe_slice)
                        vmin_safe = max(vmin_val, min_positive)
                        vmax_safe = max(vmax_val, vmin_safe * 1.01)
                        img.set_norm(LogNorm(vmin=vmin_safe, vmax=vmax_safe))

                    fig.canvas.draw_idle()

                slider_wave.on_changed(update)
                slider_vmin.on_changed(update)
                slider_vmax.on_changed(update)
                radio.on_clicked(update)

                # Mouse events
                def on_click(event):
                    if event.inaxes != ax_img or event.xdata is None or event.ydata is None:
                        return

                    if layout != layouts.layout_android:
                        if event.key is None or not any(k in event.key.lower() for k in ['ctrl', 'control']):
                            return

                    if event.button == 1:
                        interaction_state['start_point'] = (int(event.xdata), int(event.ydata))
                        interaction_state['dragging'] = True
                        interaction_state['deselecting'] = False
                    elif event.button == 3:
                        interaction_state['start_point'] = (int(event.xdata), int(event.ydata))
                        interaction_state['dragging'] = False
                        interaction_state['deselecting'] = True

                def on_release(event):
                    if event.inaxes == ax_img and interaction_state['start_point'] and event.xdata and event.ydata:
                        end_point = (int(event.xdata), int(event.ydata))
                        x0, y0 = interaction_state['start_point']
                        x1, y1 = end_point

                        if interaction_state['dragging']:
                            bin_mask[min(y0, y1):max(y0, y1)+1, min(x0, x1):max(x0, x1)+1] = 1
                        elif interaction_state['deselecting']:
                            bin_mask[min(y0, y1):max(y0, y1)+1, min(x0, x1):max(x0, x1)+1] = 0

                        bin_mask_overlay.set_data(np.ma.masked_where(bin_mask == 0, bin_mask))
                        fig.canvas.draw()
                        interaction_state['start_point'] = None
                        interaction_state['dragging'] = False
                        interaction_state['deselecting'] = False

                fig.canvas.mpl_connect("button_press_event", on_click)
                fig.canvas.mpl_connect("button_release_event", on_release)

                plt.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.05)
                plt.show()
                plt.close()

                #DOING THE MAGIC: Finding all the contigous selected spaxels, assign an integer flag for each region selected by the user.
                labeled_mask = label(bin_mask, connectivity=1)

                #inverting the mask: the selected regions will be the active regions to bin
                bin_mask = 1 - bin_mask

                #saving the masked regions
                bin_mask_name = "bin_mask2D_"+ifs_run_id+"_.fits"
                stm.save_mask_as_fits(bin_mask, result_data+"/"+bin_mask_name)
                bin_mask_path = result_data + '/'+ bin_mask_name

                # Generating the text file with all spaxel info:
                txt_filename = f"mask_regions_{ifs_run_id}.txt"
                mask_labels = save_mask_regions_txt(labeled_mask, result_data + "/" + txt_filename)

                sg.Popup("Manual binned regions computed. Now click 'Extract!' to extract the binned spectra")

            except Exception as e:
                sg.Popup('Sorry, manual binning has failed and I do not know why. Maybe the datacube does not exist?')
                continue


        # preview mode for the manual binning: reading the datacube and showing the S/N of the spaxels contained in the selected regions
        if cube_ifs_event == 'Preview bins' and ifs_manual_bin:
            ifs_min_snr_mask_bin = 0 #No S/N cut
            ifs_bin_method_manual = 'False' #No voronoi binning
            voronoi_bin = False #No voronoi binning
            ifs_target_snr_manual = 0
            ifs_covariance_manual = 0

            # 2) extracting the label column of all the spaxels with the bin_info of the selected manual regions
            try:

                # Creating the dictionary to be passed to the cube_extract module
                config_manual = cubextr.buildConfigFromGUI(
                    ifs_run_id, ifs_input, ifs_output_dir, ifs_redshift,
                    ifs_ow_output, ifs_routine_selected, ifs_origin,
                    ifs_lmin_tot, ifs_lmax_tot, ifs_lmin_snr, ifs_lmax_snr,
                    ifs_min_snr_mask_bin, bin_mask_path, ifs_bin_method_manual, ifs_target_snr_manual,
                    ifs_covariance_manual)
                try:
                    cubextr.extract(config_manual, True, voronoi_bin, elliptical, ifs_manual_bin, ifs_existing_bin)
                except Exception as e:
                    sg.popup("Sorry, Error.", str(e))
                    continue

            except Exception as e:
                sg.Popup('You first need to define the regions to be binned!\nOtherwise Select the Voronoi rebinning to automatically rebin the data')
                continue

        # NOW WE HAVE THE MAP WITH THE LABELED SPAXELS. Negative labels means spaxels not selected, therefore not considered. Positive labels identify the spaxels to consider for binning. Contiguous regions are marked with the same identifier (e.g. 1). This map has been stretched to 1D following the same order that the cubextr stores the spaxel infos in the _table.fit file. Now we need to generate the _table.fit file without any rebinning in order to have the BIN_ID of each spaxel, then we replace the BIN_ID array of the file with the bin info stored in the third component of the mask_labels array.

        # now we apply the manual bin by running the cube_extract_module in two steps
        if cube_ifs_event == 'Extract!': #and ifs_manual_bin:

            if ifs_manual_bin:
            # 1) RUNNING cubextract in preview mode without any rebinning to extract the info of the spaxels stored in the _table.fits file.
                ifs_min_snr_mask_bin = 0 #No S/N cut
                ifs_bin_method_manual = 'False'
                voronoi_bin = False #No voronoi binning
                ifs_target_snr_manual = 0
                ifs_covariance_manual = 0

            # 2) extracting the label column of all the spaxels with the bin_info of the selected manual regions
                try:
                    region_labels = mask_labels[:, 2].copy() #creating a copy, otherwise if exectuted more than one time is erodes the bin number
                    #Starting from BIN_ID zero and not one!
                    region_labels[region_labels > 0] -= 1
                except Exception as e:
                    sg.Popup('You first need to define the regions to be binned!\nOtherwise Select the Voronoi rebinning to automatically rebin the data')
                    continue

                # Creating the dictionary to be passed to the cube_extract module
                config_manual = cubextr.buildConfigFromGUI(
                    ifs_run_id, ifs_input, ifs_output_dir, ifs_redshift,
                    ifs_ow_output, ifs_routine_selected, ifs_origin,
                    ifs_lmin_tot, ifs_lmax_tot, ifs_lmin_snr, ifs_lmax_snr,
                    ifs_min_snr_mask_bin, bin_mask_path, ifs_bin_method_manual, ifs_target_snr_manual,
                    ifs_covariance_manual)
                try:
                    #running the cubextract module to produce the spaxel and BIN_ID map
                    cubextr.extract(config_manual, True, voronoi_bin, elliptical, ifs_manual_bin, ifs_existing_bin)
                except Exception as e:
                    sg.popup("Error! Cannot show the bins", str(e))
                    continue

                # #3) REPLACE THE BIN_INFO IN THE _TABLE.FITS WITH THE LABELLED VALUES STORED IN region_labels
                fits_table_path = result_data + '/' + ifs_run_id + '/' + ifs_run_id + '_table.fits'

                # Opening fits
                with fits.open(fits_table_path, mode="update") as hdul:
                    data_table = hdul[1].data

                    # Checking
                    if len(data_table) != len(region_labels):
                        raise ValueError("Mismatch size between the labelled spaxels list and the actual spaxel list in the _table.fits file")

                    # Updating
                    data_table['BIN_ID'] = region_labels
                    hdul.flush()

                # 4) Now calculate the mean position and SNR of the spaxels to be binned
                with fits.open(fits_table_path, mode="update") as hdul:
                    data_hdu = hdul[1]
                    tbl = Table(data_hdu.data)  # Convert to Astropy Table for better handling

                    # Spaxels selected for binning
                    valid_mask = (tbl['BIN_ID'] >= 0)
                    unique_bins = np.unique(tbl['BIN_ID'][valid_mask])

                    # Calculating the positions
                    for b in unique_bins:
                        region_mask = (tbl['BIN_ID'] == b)

                        # Mean (NOT weighted) position of the bins
                        mean_x = np.mean(tbl['X'][region_mask])
                        mean_y = np.mean(tbl['Y'][region_mask])

                        # Spaxel number to be binned
                        n_spax = np.count_nonzero(region_mask)

                        # Calculate the S/N of the bins
                        flux_i = tbl['FLUX'][region_mask]
                        sn_i = tbl['SNR'][region_mask]
                        S_total = np.sum(flux_i)
                        noise_i = flux_i / sn_i
                        noise_quad_sum = np.sum(noise_i**2)
                        SNR_bin = S_total / np.sqrt(noise_quad_sum)

                        # Updating the values
                        tbl['XBIN'][region_mask] = mean_x
                        tbl['YBIN'][region_mask] = mean_y
                        tbl['NSPAX'][region_mask] = n_spax
                        tbl['SNRBIN'][region_mask] = SNR_bin

                    # updating
                    hdul[1].data = tbl.as_array()
                    hdul.flush()

                # 5) Run cubextract again with the new bin configuration
                try:
                    mock_voronoi = True # Fake voronoi bin required
                    cubextr.extract(config_manual, False, mock_voronoi, elliptical, ifs_manual_bin, ifs_existing_bin)
                except Exception as e:
                    sg.Popup("ERROR performing the extraction")


            # With voronoi or elliptical rebinning things are easier:
            if not ifs_manual_bin:

            # Creating the dictionary to be passed to the cube_extract module
                config = cubextr.buildConfigFromGUI(
                    ifs_run_id, ifs_input, ifs_output_dir, ifs_redshift,
                    ifs_ow_output, ifs_routine_selected, ifs_origin,
                    ifs_lmin_tot, ifs_lmax_tot, ifs_lmin_snr, ifs_lmax_snr,
                    ifs_min_snr_mask, ifs_mask, ifs_bin_method, ifs_target_snr,
                    ifs_covariance, ell_pa_astro_deg=ifs_pa, ell_x0=ell_x0, ell_y0=ell_y0, ell_q=ifs_q,
                        ell_min_dr=ifs_ell_min_dr, ell_r_max=ifs_ell_r_max)

                print ('This might take a while. Please, relax...')

                # try:
                voronoi = True
                preview = False
                #calling the cube_extraction routine
                cubextr.extract(config, preview, voronoi, elliptical, ifs_manual_bin, ifs_existing_bin)
                # except Exception as e:
                #     sg.Popup ('ERROR performing the extraction')
                #     continue

            #extracting the bin positions infos and saving in a txt file and in lists
            root_spectra_file_bin_info = result_data+'/'+ifs_run_id+'/'+ifs_run_id+'_table.fits'
            output_file_bin_data = result_data+'/'+ifs_run_id+'/'+ifs_run_id+'_bin_info.txt'

            try:
                with fits.open(root_spectra_file_bin_info) as hdul:
                    tbl = Table(hdul[1].data)
            except Exception as e:
                sg.Popup('Cannot read the datacube')
                continue

            # Select only binned spaxels
            valid_mask = (tbl['BIN_ID'] >= 0)
            unique_bins = np.unique(tbl['BIN_ID'][valid_mask])

            bin_id_array = []
            bin_x_array = []
            bin_y_array = []

            with open(output_file_bin_data, "w") as f:
                # Header
                f.write("#BIN_ID BIN_NUMBER XBIN YBIN SNRBIN NSPAX\n")

                # For all the bins
                for b in unique_bins:
                    region_mask = (tbl['BIN_ID'] == b)

                    # Taking the first index of the binned regions
                    idx_first = np.where(region_mask)[0][0]

                    bin_number = b + 1

                    # Extracting the values
                    bin_id   = b
                    bin_x    = tbl['XBIN'][idx_first]
                    bin_y    = tbl['YBIN'][idx_first]
                    bin_snr  = tbl['SNRBIN'][idx_first]
                    bin_nspx = tbl['NSPAX'][idx_first]

                    #Storing the interesting values in a list to be used later
                    bin_id_array.append(bin_id)
                    bin_x_array.append(bin_x)
                    bin_y_array.append(bin_y)

                    # writing to a file
                    f.write(f"{bin_id} {bin_number} {bin_x} {bin_y} {bin_snr} {bin_nspx}\n")

            print("Text file written with BIN info:", output_file_bin_data)

            #saving the extracted spectra also in single fits files SPAN-ready
            try:
                root_spectra_file = result_data+'/'+ifs_run_id+'/'+ifs_run_id+'_BinSpectra_linear.fits'
                hdul = fits.open(root_spectra_file)
                data_flux = hdul[1].data['SPEC']
                data_variance = hdul[1].data['ESPEC']
                wavelengths = hdul[2].data['WAVE']

                #creating the subdirectoy to store the single bins spectra
                single_bins_dir = result_data+'/'+ifs_run_id+'/bins'
                os.makedirs(single_bins_dir, exist_ok=True)
            except Exception:
                sg.popup('Wavelength interval not covered by the spectra!')
                continue

            #saving the spectra
            # writing the single spectra with 'BIN_ID' in the filename
            try:
                for i in range(data_flux.shape[0]):
                    flux = data_flux[i]
                    variance = data_variance[i]
                    t = Table([wavelengths, flux, variance], names=('wavelength', 'flux', 'variance'))

                    # Primary HDU and keywords
                    primary_hdu = fits.PrimaryHDU()
                    primary_hdu.header['BIN_ID'] = bin_id_array[i]
                    primary_hdu.header['X'] = bin_x_array[i]
                    primary_hdu.header['Y'] = bin_y_array[i]

                    # Creating bintable to store the data
                    table_hdu = fits.BinTableHDU(t)

                    # Craring the HDU
                    hdulist = fits.HDUList([primary_hdu, table_hdu])
                    filename = f"{single_bins_dir}/{ifs_run_id}_bin_id_{i:04}.fits"
                    hdulist.writeto(filename, overwrite=True)
            except Exception as e:
                sg.Popup('Results already present in the folder. Please, change the run_id name and try again')
                continue

            print('Single binned spectra saved in:', single_bins_dir, 'Wavelength units: A')

            #closing the fits file _BinSpectra_linear.
            hdul.close()

            #create spectra list of the bins to use with SPAN
            folder_path = single_bins_dir
            if folder_path:
                file_list = stm.get_files_in_folder(folder_path)
                output_file = result_list_dir +'/' + ifs_run_id + '_bins_list.txt'
                stm.save_to_text_file(file_list, output_file)
                sg.Popup('Spectra file list of the bins saved in ', output_file, 'You can now browse and load this list file\n\nWARNING: change the name of the run to process again')

        if cube_ifs_event == ('Exit'):
            print ('Cube extraction routine closed. This main panel is now active again')
            print ('')
            break

        #showing the help file
        if cube_ifs_event == 'I need help':
            f = open(os.path.join(BASE_DIR, "help_files", "help_3d_spec.txt"), 'r')
            file_contents = f.read()
            if layout == layouts.layout_android:
                sg.popup_scrolled(file_contents, size=(120, 30))
            else:
                sg.popup_scrolled(file_contents, size=(100, 40))

    cube_ifs_window.close()

    #updating the parameters
    params = replace(params,
                    ifs_run_id = ifs_run_id,
                    ifs_input = ifs_input,
                    ifs_redshift = ifs_redshift,
                    ifs_ow_output = ifs_ow_output,
                    ifs_lmin_tot = ifs_lmin_tot,
                    ifs_lmax_tot = ifs_lmax_tot,
                    ifs_preloaded_routine = ifs_preloaded_routine,
                    ifs_min_snr_mask = ifs_min_snr_mask,
                    ifs_target_snr_voronoi = ifs_target_snr_voronoi,
                    ifs_target_snr_elliptical = ifs_target_snr_elliptical,
                    ifs_routine_read = ifs_routine_read,
                    ifs_routine_read_default = ifs_routine_read_default,
                    ifs_user_routine = ifs_user_routine,
                    ifs_user_routine_file = ifs_user_routine_file,
                    ifs_origin = ifs_origin,
                    ifs_mask = ifs_mask,
                    ifs_lmin_snr = ifs_lmin_snr,
                    ifs_lmax_snr = ifs_lmax_snr,
                    ifs_manual_bin = ifs_manual_bin,
                    ifs_voronoi = ifs_voronoi,
                    ifs_existing_bin = ifs_existing_bin,
                    ifs_existing_bin_folder = ifs_existing_bin_folder,
                    ifs_bin_method = ifs_bin_method,
                    ifs_covariance = ifs_covariance,
                    ifs_elliptical = ifs_elliptical,
                    ifs_pa_user = ifs_pa_user,
                    ifs_q_user = ifs_q_user,
                    # ifs_ell_min = ifs_ell_min,
                    ifs_ell_r_max = ifs_ell_r_max,
                    ifs_ell_min_dr = ifs_ell_min_dr,
                    isf_auto_pa_q = isf_auto_pa_q,
                    isf_auto_center = isf_auto_center
                    
                     )

    return params


# saving the spaxels for the Cube extract panel and manual bin info in a txt file and store in the array.
def save_mask_regions_txt(labeled_mask, output_filename):
    """
    - If labeled_mask[y,x] == 0 → label = -1 (not selected)
    - Otherwise label = labeled_mask[y,x]
    """
    rows, cols = labeled_mask.shape

    # Prepare a list to store the values (y, x, label)
    mask_labels_list = []

    with open(output_filename, "w") as f:
        f.write("# y\tx\tregion_label\n")
        for y in range(rows):
            for x in range(cols):
                lbl = labeled_mask[y, x]
                region_label = lbl if lbl != 0 else -1
                # Saving the text file
                f.write(f"{y}\t{x}\t{region_label}\n")
                # Fill the list
                mask_labels_list.append([y, x, region_label])

    # Converting the list to numpy and return it
    mask_labels = np.array(mask_labels_list, dtype=int)
    return mask_labels


#7) UTILITIES WINDOW
def utilities_window(params, one_spec_flag: bool):
    
    utilities_show_header = params.utilities_show_header
    utilities_step = params.utilities_step
    utilities_resolution = params.utilities_resolution
    utilities_resolution_wmin = params.utilities_resolution_wmin
    utilities_resolution_wmax = params.utilities_resolution_wmax
    utilities_convert = params.utilities_convert
    utilities_convert_tofit = params.utilities_convert_tofit
    utilities_convert_totxt = params.utilities_convert_totxt
    utilities_compare = params.utilities_compare
    utilities_compare_spec = params.utilities_compare_spec
    utilities_convert_flux = params.utilities_convert_flux
    utilities_convert_flux_fnu = params.utilities_convert_flux_fnu
    utilities_convert_flux_flambda = params.utilities_convert_flux_flambda
    utilities_snr = params.utilities_snr
    utilities_snr_wave = params.utilities_snr_wave
    utilities_snr_wave_epsilon = params.utilities_snr_wave_epsilon

    layout, scale_win, fontsize, default_size = misc.get_layout()
    if layout == layouts.layout_windows:
        sg.theme('DarkBlue3')
        utilities_layout = [

                [sg.Frame('Utilities', [
                [sg.Checkbox('Show the header of the selected spectrum', default = utilities_show_header, font = ('Helvetica', 11, 'bold'), key = 'show_hdr',tooltip='Show fits header')],
                [sg.Checkbox('Show the wavelength step of the spectrum', default = utilities_step, font = ('Helvetica', 11, 'bold'), key = 'show_step',tooltip='Show spectrum wavelength step')],
                [sg.Checkbox('Estimate the resolution:', default = utilities_resolution, font = ('Helvetica', 11, 'bold'), key = 'show_res',tooltip='Show resolution, by fitting a sky emission line within the wavelength 1(W1) and wavelength 2(W2) values'),sg.Text('W1'), sg.InputText(utilities_resolution_wmin, size = (5,1), key = 'lambda_res_left'), sg.Text('W2'), sg.InputText(utilities_resolution_wmax, size = (5,1), key = 'lambda_res_right')],
                [sg.HorizontalSeparator()],
                [sg.Checkbox('Convert the spectrum to:', default = utilities_convert, font = ('Helvetica', 11, 'bold'), key = 'convert_spec',tooltip='Convert one or all the spectra from fits to ASCII and viceversa'), sg.Radio('Text', "RADIOCONV", default = utilities_convert_totxt, key = 'convert_to_txt'), sg.Radio('FITS', "RADIOCONV", default = utilities_convert_tofit, key = 'convert_to_fits')],
                [sg.Checkbox('Compare spectrum with: ', default = utilities_compare, font = ('Helvetica', 11, 'bold'), key = 'compare_spec',tooltip='Compare the selected spectrum with any other loaded spectrum'), sg.InputText(utilities_compare_spec, size = (11,1), key = 'spec_to_compare'), sg.FileBrowse(tooltip='Load the 1D spectrum (ASCII or fits)to use as comparison')],
                [sg.Checkbox('Convert Flux', default = utilities_convert_flux, font = ('Helvetica', 11, 'bold'), key = 'convert_flux',tooltip='Convert the flux from Jansky to F_lambda and viceversa'), sg.Radio('Jy-->F_nu', "FLUX", default = utilities_convert_flux_fnu, key = 'convert_to_fnu'), sg.Radio('Jy-->F_l', "FLUX", default = utilities_convert_flux_flambda, key = 'convert_to_fl'),sg.Button('See plot',button_color=('black','light gray')), sg.Text(' ', font = ('Helvetica', 1)) ],
                [sg.Checkbox('S/N:', default = utilities_snr, font = ('Helvetica', 11, 'bold'), key = 'show_snr',tooltip='Show the S/N of the selected spectrum centered on an user defined wavelength(W)'), sg.Text(' W.'), sg.InputText(utilities_snr_wave, size = (4,1), key = 'wave_snr'), sg.Text('+/-'), sg.InputText(utilities_snr_wave_epsilon, size = (3,1), key = 'delta_wave_snr'), sg.Button('Save one',button_color=('black','light gray')), sg.Button('Save all',button_color=('black','light gray'))],
                ], font=("Helvetica", 12, 'bold')),

                #Buttons to perform the utility actions
                sg.Frame('Utility Actions',[
                [sg.Text('')],
                [sg.Button('Show info',button_color=('black','light gray'), size = (11,1))],
                [sg.Text('',font=("Helvetica", 5))],
                [sg.Text('')],
                [sg.HorizontalSeparator()],
                [sg.Button('One',button_color=('black','light gray'), size = (5,1)), sg.Button('All',button_color=('black','light gray'), size = (4,1))],
                [sg.Button('Compare',button_color=('black','light gray'), size = (11,1))],
                [sg.Button('One',button_color=('black','light gray'), size = (5,1), key = ('convert_one')), sg.Button('All',button_color=('black','light gray'), size = (4,1), key = 'convert_all')],
                [sg.Button('Show snr',button_color=('black','light gray'), size = (11,1))],
                ] ,font=("Helvetica", 10, 'bold'))],
                [sg.Exit(size=(18, 1))]

        ]

    if layout == layouts.layout_linux:
        sg.theme('DarkBlue3')
        utilities_layout = [
            #Utility frame
            [sg.Frame('Utilities', [
            [sg.Checkbox('Show the header of the selected spectrum', default = utilities_show_header, font = ('Helvetica', 11, 'bold'), key = 'show_hdr',tooltip='Show fits header')],
            [sg.Checkbox('Show the wavelength step of the spectrum', default = utilities_step, font = ('Helvetica', 11, 'bold'), key = 'show_step',tooltip='Show spectrum wavelength step')],
            [sg.Checkbox('Estimate the resolution:', default = utilities_resolution, font = ('Helvetica', 11, 'bold'), key = 'show_res',tooltip='Show resolution, by fitting a sky emission line within the wavelength 1(W1) and wavelength 2(W2) values'),sg.Text('W1'), sg.InputText(utilities_resolution_wmin, size = (4,1), key = 'lambda_res_left'), sg.Text('W2'), sg.InputText(utilities_resolution_wmax, size = (4,1), key = 'lambda_res_right')],
            [sg.HorizontalSeparator()],
            [sg.Checkbox('Convert the spectrum to:', default = utilities_convert, font = ('Helvetica', 11, 'bold'), key = 'convert_spec',tooltip='Convert one or all the spectra from fits to ASCII and viceversa'), sg.Radio('Text', "RADIOCONV", default = utilities_convert_totxt, key = 'convert_to_txt'), sg.Radio('FITS', "RADIOCONV", default = utilities_convert_tofit, key = 'convert_to_fits')],
            [sg.Checkbox('Compare with: ', default = utilities_compare, font = ('Helvetica', 11, 'bold'), key = 'compare_spec',tooltip='Compare the selected spectrum with any other loaded spectrum'), sg.InputText(utilities_compare_spec, size = (7,1), key = 'spec_to_compare'), sg.FileBrowse(tooltip='Load the 1D spectrum (ASCII or fits)to use as comparison')],
            [sg.Checkbox('Convert Flux', default = utilities_convert_flux, font = ('Helvetica', 11, 'bold'), key = 'convert_flux',tooltip='Convert the flux from Jansky to F_lambda and viceversa'), sg.Radio('Jy-->F_nu', "FLUX", default = utilities_convert_flux_fnu, key = 'convert_to_fnu'), sg.Radio('Jy-->F_l', "FLUX", default = utilities_convert_flux_flambda, key = 'convert_to_fl'),sg.Button('See plot',button_color=('black','light gray')), sg.Text(' ', font = ('Helvetica', 1)) ],
            [sg.Checkbox('S/N:', default = utilities_snr, font = ('Helvetica', 11, 'bold'), key = 'show_snr',tooltip='Show the S/N of the selected spectrum centered on an user defined wavelength(W)'), sg.Text(' W.'), sg.InputText(utilities_snr_wave, size = (4,1), key = 'wave_snr'), sg.Text('+/-'), sg.InputText(utilities_snr_wave_epsilon, size = (3,1), key = 'delta_wave_snr'), sg.Button('Save one',button_color=('black','light gray')), sg.Button('Save all',button_color=('black','light gray'))],
            ], font=("Helvetica", 12, 'bold')),

            #Buttons to perform the utility actions
            sg.Frame('Utility Actions',[
            [sg.Text('')],
            [sg.Button('Show info',button_color=('black','light gray'), size = (11,1))],
            [sg.Text('')],
            [sg.HorizontalSeparator()],
            [sg.Button('One',button_color=('black','light gray'), size = (3,1)), sg.Button('All',button_color=('black','light gray'), size = (2,1))],
            [sg.Button('Compare',button_color=('black','light gray'), size = (11,1))],
            [sg.Button('One',button_color=('black','light gray'), size = (3,1), key ='convert_one'), sg.Button('All',button_color=('black','light gray'), size = (2,1), key = 'convert_all')],
            [sg.Button('Show snr',button_color=('black','light gray'), size = (11,1))],
            ] ,font=("Helvetica", 10, 'bold'))],
            [sg.Exit(size=(18, 1))]

        ]

    if layout == layouts.layout_android:

        sg.theme('DarkBlue3')
        utilities_layout = [

                    #Utility frame
            [sg.Frame('Utilities', [
            [sg.Checkbox('Header', default = utilities_show_header, font = ('Helvetica', 11, 'bold'), key = 'show_hdr',tooltip='Show fits header'), sg.Checkbox('Step', default = utilities_step, font = ('Helvetica', 11, 'bold'), key = 'show_step',tooltip='Show spectrum wavelength step'), sg.Checkbox('Resolution:', default = utilities_resolution, font = ('Helvetica', 11, 'bold'), key = 'show_res',tooltip='Show resolution, by fitting a sky emission line within the wavelength 1(W1) and wavelength 2(W2) values'),sg.Text('W1'), sg.InputText(utilities_resolution_wmin, size = (5,1), key = 'lambda_res_left'), sg.Text('W2'), sg.InputText(utilities_resolution_wmax, size = (5,1), key = 'lambda_res_right')],
            [sg.Checkbox('Convert spectrum or spectra to:', default = utilities_convert, font = ('Helvetica', 11, 'bold'), key = 'convert_spec',tooltip='Convert one or all the spectra from fits to ASCII and viceversa'), sg.Radio('Text', "RADIOCONV", default = utilities_convert_totxt, key = 'convert_to_txt'), sg.Radio('FITS', "RADIOCONV", default = utilities_convert_tofit, key = 'convert_to_fits')],
            [sg.Checkbox('Compare spec. with: ', default = utilities_compare, font = ('Helvetica', 11, 'bold'), key = 'compare_spec',tooltip='Compare the selected spectrum with any other loaded spectrum'), sg.InputText(utilities_compare_spec, size = (18,1), key = 'spec_to_compare'), sg.FileBrowse(tooltip='Load the 1D spectrum (ASCII or fits)to use as comparison')],
            [sg.Checkbox('Convert the flux', default = utilities_convert_flux, font = ('Helvetica', 11, 'bold'), key = 'convert_flux',tooltip='Convert the flux from Jansky to F_lambda and viceversa'), sg.Radio('Jy-->F_nu', "FLUX", default = utilities_convert_flux_fnu, key = 'convert_to_fnu'), sg.Radio('Jy-->F_l', "FLUX", default = utilities_convert_flux_flambda, key = 'convert_to_fl'),sg.Button('See plot',button_color=('black','light gray')) ],
            [sg.Checkbox('S/N:', default = utilities_snr, font = ('Helvetica', 11, 'bold'), key = 'show_snr',tooltip='Show the S/N of the selected spectrum centered on an user defined wavelength(W)'), sg.Text(' W.'), sg.InputText(utilities_snr_wave, size = (7,1), key = 'wave_snr'), sg.Text('+/-'), sg.InputText(utilities_snr_wave_epsilon, size = (4,1), key = 'delta_wave_snr'), sg.Text(''), sg.Button('Save one',button_color=('black','light gray')), sg.Button('Save all',button_color=('black','light gray'))]
            ], font=("Helvetica", 12, 'bold')),

            #Buttons to perform the utility actions
            sg.Frame('Utility Actions',[
            [sg.Button('Show info',button_color=('black','light gray'), size = (10,1))],
            [sg.Button('One',button_color=('black','light gray'), size = (3,1)), sg.Button('All',button_color=('black','light gray'), size = (3,1))],
            [sg.Button('Compare',button_color=('black','light gray'), size = (10,1))],
            [sg.Button('One',button_color=('black','light gray'), size = (3,1), key ='convert_one'), sg.Button('All',button_color=('black','light gray'), size = (3,1), key = 'convert_all')],
            [sg.Button('Show snr',button_color=('black','light gray'), size = (10,1))]
            ] ,font=("Helvetica", 8, 'bold'))],
            [sg.Exit(size=(18, 1))]
        ]
           
           
    if layout == layouts.layout_macos:

        sg.theme('DarkBlue3')
        utilities_layout = [

                    #Utility frame
            [sg.Frame('Utilities', [
            [sg.Checkbox('Show the header of the selected spectrum',key = 'show_hdr',tooltip='Show fits header')],
            [sg.Checkbox('Show the wavelength step of the spectrum', key = 'show_step',tooltip='Show spectrum wavelength step')],
            [sg.Checkbox('Estimate the resolution:', key = 'show_res',tooltip='Show resolution, by fitting a sky emission line within the wavelength 1(W1) and wavelength 2(W2) values'),sg.Text('W1'), sg.InputText('5500', size = (4,1), key = 'lambda_res_left'), sg.Text('W2'), sg.InputText('5650', size = (4,1), key = 'lambda_res_right')],
            [sg.HorizontalSeparator()],
            [sg.Checkbox('Convert the spectrum to:', key = 'convert_spec',tooltip='Convert one or all the spectra from fits to ASCII and viceversa'), sg.Radio('Text', "RADIOCONV", default = True, key = 'convert_to_txt'), sg.Radio('FITS', "RADIOCONV", key = 'convert_to_fits')],
            [sg.Checkbox('Compare with: ', key = 'compare_spec',tooltip='Compare the selected spectrum with any other loaded spectrum'), sg.InputText('Spec.', size = (7,1), key = 'spec_to_compare'), sg.FileBrowse(tooltip='Load the 1D spectrum (ASCII or fits)to use as comparison')],
            [sg.Checkbox('Convert Flux', key = 'convert_flux',tooltip='Convert the flux from Jansky to F_lambda and viceversa'), sg.Radio('Jy-->F_nu', "FLUX", default = True, key = 'convert_to_fnu'), sg.Radio('Jy-->F_l', "FLUX", key = 'convert_to_fl'),sg.Button('See plot',button_color=('black','light gray')) ],
            [sg.Checkbox('S/N:', key = 'show_snr',tooltip='Show the S/N of the selected spectrum centered on an user defined wavelength(W)'), sg.Text(' W.'), sg.InputText('6450', size = (4,1), key = 'wave_snr'), sg.Text('+/-'), sg.InputText(30, size = (3,1), key = 'delta_wave_snr'), sg.Button('Save one',button_color=('black','light gray')), sg.Button('Save all',button_color=('black','light gray'))]
            ], font=("Helvetica", 18, 'bold')),
            
            
            #Buttons to perform the utility actions
            sg.Frame('Utility Actions',[
            [sg.Text('')],
            [sg.Button('Show info',button_color=('black','light gray'), size = (11,1))],
            [sg.Text('', font = ('Helvetica', 16))],
            [sg.HorizontalSeparator()],
            [sg.Button('One',button_color=('black','light gray'), size = (4,1)), sg.Button('All',button_color=('black','light gray'), size = (4,1))],
            [sg.Button('Compare',button_color=('black','light gray'), size = (11,1))],
            [sg.Button('One',button_color=('black','light gray'), size = (4,1), key ='convert_one'), sg.Button('All',button_color=('black','light gray'), size = (4,1), key = 'convert_all')],
            [sg.Button('Show snr',button_color=('black','light gray'), size = (11,1))]
            ] ,font=("Helvetica", 10, 'bold'))],
            [sg.Exit(size=(18, 1))]
        ]
        
    win = sg.Window('SPAN Utilities', utilities_layout, modal=False, finalize=True, resizable=False)

    # event loop della sottofinestra
    while True:
        ev, vals = win.read()
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        if ev  == sg.WIN_CLOSED:
            break

        # Parameter definition and first check. Later I will perform a better check
        utilities_show_header = vals['show_hdr']
        utilities_step = vals['show_step']
        utilities_resolution = vals['show_res']
        utilities_convert = vals['convert_spec']
        utilities_convert_tofit = vals['convert_to_fits']
        utilities_convert_totxt = vals['convert_to_txt']
        utilities_compare = vals['compare_spec']
        utilities_convert_flux = vals['convert_flux']
        utilities_convert_flux_fnu = vals['convert_to_fnu']
        utilities_convert_flux_flambda = vals['convert_to_fl']
        utilities_snr = vals['show_snr']
        utilities_compare_spec = vals['spec_to_compare']

        try:
            utilities_resolution_wmin = float(vals['lambda_res_left'])
            utilities_resolution_wmax = float(vals['lambda_res_right'])
            utilities_snr_wave = float(vals['wave_snr'])
            utilities_snr_wave_epsilon  = float(vals['delta_wave_snr'])
        except Exception:
            sg.popup('Parameters not valid')

        # Check function
        def need_selection():
            if getattr(params, 'prev_spec', '') == '':
                sg.popup('No spectrum selected. Please, select one spectrum in the main list.')
                return True
            return False

        # === SHOW INFO ===
        if ev == 'Show info':
            if need_selection():
                continue

            # 1) header
            if utilities_show_header:
                try:
                    utility_tasks.show_fits_header(params.prev_spec)
                except Exception as e:
                    sg.popup(f'Header failed: {e}')

            # 2) sampling
            if utilities_step:
                try:
                    wl, _, *_ = stm.read_spec(params.prev_spec, params.lambda_units)
                    utility_tasks.show_sampling(wl)
                except Exception as e:
                    sg.popup(f'Sampling failed: {e}')

            # 3) resolution
            if utilities_resolution:
                try:
                    utilities_resolution_wmin = float(vals['lambda_res_left'])
                    utilities_resolution_wmax = float(vals['lambda_res_right'])
                    if utilities_resolution_wmin >= utilities_resolution_wmax:
                        sg.popup('Wave1 must be SMALLER than Wave2')
                        continue
                    wl, fl, *_ = stm.read_spec(params.prev_spec, params.lambda_units)
                    utility_tasks.show_resolution(wl, fl, utilities_resolution_wmin, utilities_resolution_wmax)
                except ValueError:
                    sg.popup('Wave is not a number!')
                except Exception as e:
                    sg.popup(f'Resolution failed: {e}')

            if not (utilities_show_header or utilities_step or utilities_resolution):
                sg.popup('You need to select an option before click Show info')

        # === CONVERT (One / All) ===
        if ev in ('One', 'All'):
            if not utilities_convert:
                sg.popup('You need to activate the option if you expect something!')
                continue
            if need_selection():
                continue
            try:
                wl, fl, *_ = stm.read_spec(params.prev_spec, params.lambda_units)
                to_txt = utilities_convert_totxt
                if ev == 'One':
                    utility_tasks.convert_spectrum(wl, fl, params.prev_spec, to_txt, params.lambda_units)
                else:  # All
                    if one_spec_flag:
                        sg.popup('You have just one spectrum. The button ALL does not work!')
                        continue
                    for i in range(params.spectra_number):
                        utility_tasks.convert_spectrum(wl, fl, params.spec_names[i], to_txt, params.lambda_units)
            except Exception as e:
                sg.popup(f'Convert failed: {e}')

        # === COMPARE ===
        if ev == 'Compare':
            if not utilities_compare:
                sg.popup('You need to select the option if you expect something!')
                continue
            if need_selection():
                continue
            try:
                utility_tasks.compare_spectra(params.prev_spec, utilities_compare_spec, params.lambda_units)
            except Exception as e:
                sg.popup(f'Compare failed: {e}')

        # === FLUX CONVERT / PLOT ===
        if ev in ('convert_one', 'convert_all', 'See plot'):
            if not utilities_convert_flux:
                sg.popup('You need to activate the option if you expect something!')
                continue
            if ev == 'convert_all' and one_spec_flag:
                sg.popup('"All" does not work anyway with just one spectrum!')
                continue
            try:
                utility_tasks.convert_flux_task(
                    ev,
                    params.prev_spec,
                    params.prev_spec_nopath,
                    params.spec_names,
                    params.spec_names_nopath,
                    params.spectra_number,
                    vals.get('convert_flux', False),
                    vals.get('convert_to_fl', False),
                    vals.get('convert_to_fnu', True),
                    params.lambda_units,
                    params.result_spec,
                    params.result_data,
                    one_spec_flag
                )
            except Exception as e:
                sg.popup(f'Flux convert failed: {e}')

        # === SNR ===
        if ev in ('Show snr', 'Save one', 'Save all'):
            if not vals.get('show_snr', False):
                sg.popup('You need to activate the option if you expect something!')
                continue
            if ev == 'Save all' and one_spec_flag:
                sg.popup('"Save all" does not work anyway with just one spectrum!')
                continue
            try:
                utilities_snr_wave = float(vals['wave_snr'])
                utilities_snr_wave_epsilon = float(vals['delta_wave_snr'])
                utility_tasks.snr_analysis(
                    ev,
                    params.prev_spec,
                    params.spec_names,
                    params.spec_names_nopath,
                    params.spectra_number,
                    True,
                    utilities_snr_wave,
                    utilities_snr_wave_epsilon,
                    params.lambda_units,
                    one_spec_flag,
                    params.result_snr_dir,
                    params.spectra_list_name,
                    timestamp
                )
            except ValueError:
                sg.popup('Wave interval / epsilon is not a number!')
            except Exception as e:
                sg.popup(f'SNR failed: {e}')

        if ev == ('Exit'):
            break

    win.close()

    params = replace(params,
                    utilities_show_header = utilities_show_header,
                    utilities_step = utilities_step,
                    utilities_resolution = utilities_resolution,
                    utilities_resolution_wmin = utilities_resolution_wmin,
                    utilities_resolution_wmax = utilities_resolution_wmax,
                    utilities_convert = utilities_convert,
                    utilities_convert_tofit = utilities_convert_tofit,
                    utilities_convert_totxt = utilities_convert_totxt,
                    utilities_compare = utilities_compare,
                    utilities_compare_spec = utilities_compare_spec,
                    utilities_convert_flux = utilities_convert_flux,
                    utilities_convert_flux_fnu = utilities_convert_flux_fnu,
                    utilities_convert_flux_flambda = utilities_convert_flux_flambda,
                    utilities_snr = utilities_snr,
                    utilities_snr_wave = utilities_snr_wave,
                    utilities_snr_wave_epsilon = utilities_snr_wave_epsilon,
                     )

    return params
