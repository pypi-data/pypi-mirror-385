#SPectral ANalysis software (SPAN)
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

#******************************************************************************************
#******************************************************************************************
#*************************** SYSTEM FUNCTIONS FOR SPAN ************************************
#******************************************************************************************
#******************************************************************************************

try:#Local imports
    from FreeSimpleGUI_local import FreeSimpleGUI as sg
    from span_functions import spec_manipul as spman

except ModuleNotFoundError: #local import if executed as package
    from ..FreeSimpleGUI_local import FreeSimpleGUI as sg
    #SPAN functions import
    from . import spec_manipul as spman

#Python imports
import numpy as np
import math as mt
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import ast
from matplotlib.backend_bases import MouseButton

from astropy.io import fits
from astropy.time import Time

from scipy.optimize import curve_fit
from scipy.signal import correlate2d
from scipy.constants import h,k,c
from scipy.stats import pearsonr
import scipy.stats
from scipy.ndimage import gaussian_filter, binary_dilation
from scipy.interpolate import griddata
from scipy.ndimage import map_coordinates

import time
from time import perf_counter as clock
from os import path
import os
import re
import sys

import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

#0) Simple function to check if the spectra are linearly sampled in wavelength, as required by SPAN
def is_spec_linear(wavelength, tol=2e-4):
    """
    Checks whether the wavelength array is linearly sampled within a tolerance.

    Parameters:
        wavelength (array-like): Wavelength grid.
        tol (float): Tolerance on the relative variation of delta_lambda.

    Returns:
        is_linear (bool): True if linear within tolerance.
        delta_lambda (float): Median step size.
        max_deviation (float): Maximum relative deviation from median step.
    """
    diffs = np.diff(wavelength)
    median_step = np.median(diffs)
    rel_deviation = np.abs(diffs - median_step) / median_step
    max_deviation = np.max(rel_deviation)

    is_linear = max_deviation < tol
    return is_linear, median_step, max_deviation

#1) Read the spectra
def read_spec(spec_name, lambda_units):

    """
    This function read the 1D spectra, either in ASCII or fits format (2d
    tables of IRAF style, in the first extension of the fits).
    Input: the path (relative or absolute) and name of the 1D spectrum,
    the wavelength unit scale ('nm', 'A', 'mu').
    Output: wavelength array, flux array, step (in lambda units) array and
    object name, if present in the fits keywords, array.

    """

    fmt_spec1 = '.txt' in spec_name or '.dat' in spec_name
    fmt_spec2 = '.fits' in spec_name

    # If I have an ASCII spectrum with lambda
    if (fmt_spec1 and not fmt_spec2 or (fmt_spec1 and fmt_spec2)):
        spec_type = '2d ASCII table'
        wavelength, flux = np.loadtxt(spec_name, usecols = (0,1)).T
        start_lambda = wavelength[0]
        if (start_lambda < 12. and start_lambda > 5 and lambda_units != 'mu'):
            # print ('I think you have ln lambda, try to convert to lambda...')
            wavelength_log = wavelength
            wavelength = np.exp(wavelength_log)
        # print(spec_type, 'spec with lambda in', lambda_units)
        obj_name = spec_name

    # if I have fits files, they can be of different type
    else:
        hdu = fits.open(spec_name)
        hdr_fits = hdu[0].header
        oned_key = 'CDELT1' in hdr_fits

        #if fits table are 1d (IRAF style, with flux and delta lamba)
        if (oned_key):
            spec_type = '1d fits table IRAF style'
            # print (spec_type, 'spec with lambda in', lambda_units)
            points = hdr_fits['NAXIS1']
            start_lambda = hdr_fits['CRVAL1']
            step=hdr_fits['CDELT1']
            wavelength = np.arange(points)*step+start_lambda
            flux_tmp = hdu[0].data
            flux = np.array(flux_tmp)

            #reading 1dfits IRAF style with logaritmic wavelength
            if (start_lambda < 5. and start_lambda > 2.5 and lambda_units != 'mu'):
                # print ('I think you have log lambda, try to convert to lambda...')
                wavelength_log = wavelength
                ln_wavelength= wavelength_log*np.log(10)         # Convert lg --> ln
                wavelength = np.exp(ln_wavelength)
            if (start_lambda < 12. and start_lambda > 5 and lambda_units != 'mu'):
                # print ('I think you have ln lambda, try to convert to lambda...')
                wavelength_log = wavelength
                wavelength = np.exp(wavelength_log)

            obj_name = spec_name

        # if the fits table are 2d:
        elif (not oned_key):
            # Define the columns
            flux_tmp = 0
            spec_type = '2d fits table'
            # print (spec_type, 'spec with lambda in', lambda_units)


            # trying a connon sense fits table with wavelength and flux, like the ESO does
            try:
                flux_tmp = hdu[1].data['FLUX']
                waves_tmp = hdu[1].data['WAVE']
                eso_spec = True
            except KeyError:
                eso_spec = False

            if eso_spec:
                wavelength = np.array(waves_tmp)
                flux = np.array(flux_tmp)

                #flattening the arrays since with Xshooter new products the arrays are 2D, with the second dimension empty.
                wavelength = wavelength.flatten()
                flux = flux.flatten()
                flux_tmp = 0
                obj_name = spec_name

            #americans are different: I try to see if the spectra are in the SDSS format, where I have flux and loglam instead of flux and wave
            elif(not eso_spec):

                try:
                    t = hdu['COADD'].data
                    flux_tmp = t['flux']
                    wavelength_tmp = t['loglam']
                    sdss_new_spec = True
                except KeyError:
                    sdss_new_spec = False

                if (sdss_new_spec):
                    #the new sdss spectra have the log_wave instead of wave!
                    # print ('with log lambda')

                    wavelength_log = np.array(wavelength_tmp)
                    flux = np.array(flux_tmp)
                    #since the lambda are in log, I transform to real numbers, maintaining the log spaced values
                    ln_wavelength= wavelength_log*np.log(10)         # Convert lg --> ln
                    wavelength = np.exp(ln_wavelength)
                    obj_name = spec_name
                elif(not sdss_new_spec):

                    #trying the older release of sdss
                    t = hdu[1].data
                    flux_tmp = t['flux']
                    wavelength_tmp = t['wavelength']
                    wavelength = np.array(wavelength_tmp)
                    flux = np.array(flux_tmp)
                    obj_name = spec_name


    #replace NaN values with zeros
    nan_values = np.isnan(flux).any()
    if nan_values:
        flux = np.nan_to_num(flux)
        print ('NaN values in flux found and replaced with zeros')


    spec_components = len(flux)
    #convert all to A
    if(lambda_units == 'mu'):
        wavelength = wavelength *10000.
    elif(lambda_units == 'nm'):
        wavelength = wavelength*10.

    #calculating the step
    original_step = wavelength[1]-wavelength[0]

    is_linear, delta, dev = is_spec_linear(wavelength)
    if not is_linear:
        wavelength, flux, points_spec = spman.resample(wavelength, flux, original_step)
        # print('Resampled to linear step')

    return wavelength, flux, original_step, obj_name

#********************************************


#1b): check if the FITS files are really spectra or images.
def is_valid_spectrum(fits_file):
    """
    Verifies if a fits file contains a valid spectrum

    Args:
        fits_file (str): path to FITS file.

    Returns:
        bool: True if the FITS contains a spectrum, False elsewhere.
        str: A message to the user.
    """
    try:
        with fits.open(fits_file) as hdul:
            for hdu in hdul:
                # Check if it is a 2D fits table
                if isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
                    columns = hdu.columns.names
                    if 'wavelength' in columns or 'WAVE' in columns or 'WAVELENGTH' in columns or 'loglam' in columns or 'LOGLAM' in columns and ('FLUX' in columns or 'flux' in columns):
                        return True, "Spectrum found in a table HDU."

                # Check if it is a 1D fits table
                if isinstance(hdu, fits.PrimaryHDU):
                    data = hdu.data
                    header = hdu.header
                    if data is not None and data.ndim == 1:
                        if all(k in header for k in ['CRVAL1', 'CDELT1', 'NAXIS1']):
                            return True, "Spectrum found in Primary HDU with wavelength info in header."

                # Trying to reject FITS image data
                if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
                    data = hdu.data
                    if data is not None and data.ndim > 1:
                        return False, "Image detected in FITS file."

        return False, "No valid spectrum found in the FITS file."
    except Exception as e:
        return False, f"Error reading FITS file: {e}"

#********************************************

# 2) Read datacubes
def read_datacube(file_path):
    """
    Read a 3D datacube from various sources and return data and wavelength array.
    Supports MUSE, CALIFA, and generic cubes.
    """
    try:
        with fits.open(file_path) as hdu:
            # Try known formats
            # -----------------------------------
            # MUSE datacube: data in HDU[1], CD3_3
            if 'CD3_3' in hdu[1].header and 'CRVAL3' in hdu[1].header and len(hdu) < 4:
                data = hdu[1].data
                hdr = hdu[1].header
                nwave = data.shape[0]
                wave = hdr['CRVAL3'] + np.arange(nwave) * hdr['CD3_3']
                print("Datacube format detected: MUSE")
                return data, wave

            # CALIFA datacube: data in HDU[0], CDELT3
            elif 'CDELT3' in hdu[0].header and 'CRVAL3' in hdu[0].header:
                data = hdu[0].data
                hdr = hdu[0].header
                nwave = data.shape[0]
                wave = hdr['CRVAL3'] + np.arange(nwave) * hdr['CDELT3']
                print("Datacube format detected: CALIFA")
                return data, wave

            # --- WEAVE ---, as MUSE but with more extensions
            elif 'CD3_3' in hdu[1].header and 'CRVAL3' in hdu[1].header and len(hdu) > 4:
                data = hdu[1].data
                hdr = hdu[1].header
                nwave = data.shape[0]
                wave = hdr['CRVAL3'] + np.arange(nwave) * hdr['CD3_3']
                print("Datacube format detected: WEAVE")
                return data, wave

            # JWST NIRSpec datacube: data in HDU[1], CDELT3
            elif 'CDELT3' in hdu[1].header and 'CRVAL3' in hdu[1].header:
                data = hdu[1].data
                hdr = hdu[1].header
                nwave = data.shape[0]
                wave = (hdr['CRVAL3'] + np.arange(nwave) * hdr['CDELT3'])*1e4
                print("Datacube format detected: JWST")
                return data, wave

            # Generic: fallback if 3D and no keywords
            elif len(hdu) > 1 and len(hdu[1].data.shape) == 3:
                data = hdu[1].data
                wave = np.arange(data.shape[0])
                print("Datacube format: generic fallback (HDU[1], no wavelength calibration)")
                return data, wave

            elif len(hdu[0].data.shape) == 3:
                data = hdu[0].data
                wave = np.arange(data.shape[0])
                print("Datacube format: generic fallback (HDU[0], no wavelength calibration)")
                return data, wave

            else:
                print("Unsupported or malformed datacube format.")
                return None, None

    except Exception as e:
        print(f"Error reading datacube: {e}")
        return None, None

#********************************************

#********************************************
# FUCTIONS FOR THE FITS HEADER MANIPULATION

"""
The functions below are needed to the 'FITS header editor' sub-program
in order to read, modify and save the keywords in the fits header files
(in the first extension)

"""

#3) for the modification of just one file
def read_fits_header(file_path):
    try:
        with fits.open(file_path) as hdul:
            header = hdul[0].header
        return header
    except Exception as e:
        return str(e)

#4) Save fits header
def save_fits_header(file_path, header):
    try:
        with fits.open(file_path, mode='update') as hdul:
            hdul[0].header = header
            hdul.flush()
        return True
    except Exception as e:
        return str(e)

#5) delete keyword from the header
def delete_keyword(header, key):
    try:
        del header[key]
        return True
    except KeyError:
        return f"Keyword '{key}' not found in the header."

#6) Reading the keywords for the manipulation of a list of fits with a list of keywords:
def read_keyword_values_from_file(file_path):
    key_name = []
    key_value = []
    with open(file_path, 'r') as file:
        for line in file:
            if not line.startswith('#'):
                key, value, value_type = map(str.strip, line.split('='))
                # Recognise the value type and convert
                if value_type.lower() == 'int':
                    value = int(value)
                elif value_type.lower() == 'float':
                    value = float(value)
                elif value_type.lower() == 'string':
                    value = str(value)

                # Add the value to the list
                key_name.append(key)
                key_value.append(value)

    return key_name, key_value

#7) reading the fits file list to process
def read_file_list(file_path):
    try:
        with open(file_path, 'r') as file:
            file_paths = [line.strip() for line in file if not line.startswith('#')]
        return file_paths
    except Exception as e:
        return str(e)

#8) For the extraction and saving of the new keywords in a list of fits files:
def extract_keyword(file_path, keyword):
    try:
        with fits.open(file_path) as hdul:
            header = hdul[0].header
            if keyword in header:
                return header[keyword]
            else:
                return f"Keyword '{keyword}' non trovata nel file."
    except Exception as e:
        return str(e)

#9) exporting the keyword to a ASCII file
def save_to_text_file(data, output_file):
    with open(output_file, 'w') as file:
        # writing the header
        file.write(f"#Spectrum {data[0]['keyword']}\n")

        for entry in data:
            file.write(f"{entry['file']} {entry['value']}\n")

#********************************************

#********************************************
# FUCTIONS FOR PLOTTING SUBPROGRAM

"""
The functions below are needed for the 'Plot data' subprogram
in order to perform the plots and linear fitting of the data
generated by SPAN.

"""
#10) simple line for linear fitting of the plotted data
def linear_fit(x, m, b):
    return m * x + b

#11) reading the names (header) of the data file to plot
def get_column_names(file_path):
    try:
        data = pd.read_csv(file_path, sep=None, engine='python')
        return list(data.columns)
    except Exception as e:
        sg.popup_error(f'Error reading file: {str(e)}')
        return []

#12) Plotting the data
def plot_data(file_path, x_column, y_columns, x_label, y_label, marker_color, marker_size, plot_scale, x_label_size,
              y_label_size, x_tick_size, y_tick_size, legend, add_error_bars_x, add_error_bars_y, x_err, y_err, saveps,
              enable_linear_fit, x_log_scale, y_log_scale, x_range_min=None, x_range_max=None, y_range_min=None,
              y_range_max=None):

    try:
        #Load the data
        data = pd.read_csv(file_path, sep=None, engine='python')

        #plotting
        plt.figure(figsize=plot_scale)
        if x_log_scale:
            plt.xscale('log')
        if y_log_scale:
            plt.yscale('log')

        for column in y_columns:
            # Extract x and y values
            x = data[x_column].values
            y = data[column].values

            # Handlling the error bars
            if add_error_bars_y and not add_error_bars_x :
                error_bar_data_y = data[y_err].values
                #I need 1D arrays
                x = np.squeeze(x)
                y = np.squeeze(y)
                error_bar_data_y = np.squeeze(error_bar_data_y)
                #Adding the error bars
                plt.scatter(x, y, label=column, color=marker_color, s=marker_size)
                plt.errorbar(x, y, yerr=error_bar_data_y, linestyle='None', ecolor = 'black', capsize=2)
            elif add_error_bars_x and not add_error_bars_y:
                error_bar_data_x = data[x_err].values
                #I need 1D arrays
                x = np.squeeze(x)
                y = np.squeeze(y)
                error_bar_data_x = np.squeeze(error_bar_data_x)
                #Adding the error bars
                plt.scatter(x, y, label=column, color=marker_color, s=marker_size)
                plt.errorbar(x, y, xerr=error_bar_data_x, linestyle='None', ecolor = 'black', capsize=2)
            elif (add_error_bars_y and add_error_bars_x):
                error_bar_data_y = data[y_err].values
                error_bar_data_x = data[x_err].values
                x = np.squeeze(x)
                y = np.squeeze(y)
                error_bar_data_y = np.squeeze(error_bar_data_y)
                error_bar_data_x = np.squeeze(error_bar_data_x)
                #Adding the error bars
                plt.scatter(x, y, label=column, color=marker_color, s=marker_size)
                plt.errorbar(x, y, xerr=error_bar_data_x, yerr=error_bar_data_y, linestyle='None', ecolor = 'black', capsize=2)
            else:
                plt.scatter(x, y, label=column, color=marker_color, s=marker_size)

        if enable_linear_fit:
            popt, _ = curve_fit(linear_fit,  x.reshape(-1), y.reshape(-1))
            fit_x = np.linspace(min(x), max(x), 100)
            fit_y = linear_fit(fit_x, *popt)
            linear_regression = scipy.stats.linregress(x.reshape(-1), y.reshape(-1))
            pearson = linear_regression.rvalue
            pearson_str = ('R = ' + str(round(pearson,2)))
            x_data = x.reshape(-1)
            y_data = y.reshape(-1)

            #bootstrap for the error on R
            num_bootstrap_samples = 1000
            #removing the Nans
            nan_indices_xy = np.isnan(x_data) | np.isnan(y_data)
            x_data = x_data[~nan_indices_xy]
            y_data = y_data[~nan_indices_xy]
            bootstrap_results_xy = np.zeros(num_bootstrap_samples)
            for i in range(num_bootstrap_samples):
                #a) for the correlations with Mg2
                indices_xy = np.random.choice(len(x_data), len(y_data), replace=True)
                x_bootstrap = x_data[indices_xy]
                y_bootstrap = y_data[indices_xy]
                # Correlation coefficient of the bootstrap sample
                bootstrap_results_xy[i], _ = pearsonr(x_bootstrap, y_bootstrap)

            std_bootstrap_xy = str(round(np.std(bootstrap_results_xy),2))
            plt.plot(fit_x, fit_y, linestyle='-', color='red', label=(pearson_str + r'$\pm$'+std_bootstrap_xy))

        #Make the plot nice
        plt.xlabel(x_label, fontsize=x_label_size)
        plt.ylabel(y_label, fontsize=y_label_size)
        plt.xticks(fontsize=x_tick_size)
        plt.yticks(fontsize=y_tick_size)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        if x_range_min is not None and x_range_max is not None:
            plt.xlim(float(x_range_min), float(x_range_max))
        if y_range_min is not None and y_range_max is not None:
            plt.ylim(float(y_range_min), float(y_range_max))


        if legend:
            plt.legend()
        if saveps:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            plt.savefig('plot_'+timestamp+'.png', format='png', dpi=300)
            sg.Popup ('png file saved with success in the working directory!')
        else:
            plt.show()

    except Exception as e:
        sg.popup_error(f'Error plotting data: {str(e)}')

    finally:
        plt.close()

#********************************************


#********************************************

#********************************************
# FUNCTIONS FOR THE LONGSLIT SPECTRA EXTRACTION

"""
The functions below are needed for the 'Long-slit extraction'
subprogram in order to perform all the operations needed to
correct the 2D input fits image and extract 1D spectra, snr_single
or based on SNR threshold.

"""
#13) Opening a 2D firs image
def open_fits(file_path):
    # Function to open FITS file and return 2D spectrum
    hdu = fits.open(file_path)
    spectrum = hdu[0].data
    header = hdu[0].header
    hdu.close()
    return spectrum, header

#14) Identitying and fitting the trace (maximum photometric of the 2D image, in the pixel range defined by the user)
def find_and_fit_spectroscopic_trace(spectrum, y_range, poly_degree, first_iteration, with_plots):
    # Function to automatically find and fit spectroscopic trace
    x_axis = np.arange(len(spectrum[0]))
    y_axis = np.arange(len(spectrum))

    spectrum_subset = spectrum
    selected_y_range = slice(*y_range)
    spectrum_subset = spectrum[selected_y_range,:]

    template = np.sum(spectrum[selected_y_range, :], axis=0)

    # Compute cross-correlation between each row and the template
    cross_correlation =  correlate2d(spectrum_subset, template[np.newaxis, :], mode='same')

    # Find the row with maximum cross-correlation for each column
    trace_rows = np.argmax(cross_correlation, axis=0)

    # Fit a polynomial curve to the trace rows along the x-axis using numpy.polyfit
    coefficients = np.polyfit(x_axis, trace_rows, deg=poly_degree)
    trace_model = np.poly1d(coefficients)

    if with_plots:
        # Plot the cross-correlation and fitted trace for visualization
        plt.subplot(2, 1, 1)
        plt.imshow(cross_correlation, cmap='gray', aspect='auto')
        plt.plot(trace_rows, color='r', linestyle='--', label='Trace Rows')
        plt.legend()
        plt.title("Cross-Correlation for Trace Detection")

        plt.subplot(2, 1, 2)
        plt.plot(x_axis, trace_rows, label="Original Trace Rows")
        plt.plot(x_axis, trace_model(x_axis), label="Trace Model")
        plt.legend()
        plt.title(f"Spectroscopic Trace Model (Degree {poly_degree})")

        plt.tight_layout()
        plt.show()
        plt.close()

    return trace_model

#15) Retrieving the wavelength range in the 2D fits image
def get_wavelength_coordinates(header, x_axis):
    # Function to get wavelength coordinates from FITS header
    if 'CRVAL1' in header and 'CDELT1' in header:
        crval1 = header['CRVAL1']
        cdelt1 = header['CDELT1']
        wavelength_coordinates = crval1 + cdelt1 * x_axis
        return wavelength_coordinates
    else:
        return x_axis

#16) Correcting the distortion and slope od the 2D spectrum. IMproved to better conserve the flux
def correct_distortion_slope(spectrum, trace_model, y_range, max_iter=8, tol_delta=0.5, tol_slope=0.002):
    """
    Correct the distortion/slope of a 2D long-slit spectrum using the fitted trace.

    Parameters
    ----------
    spectrum : 2D np.ndarray  [ny, nx]
        Original 2D long-slit image.
    trace_model : callable (np.poly1d)
        Trace model: y(x).
    y_range : tuple(int, int)
        Row interval used for the trace fit (passed to find_and_fit_spectroscopic_trace).
    max_iter : int
        Maximum number of refinement iterations.
    tol_delta : float
        Tolerance on the residual correction range in pixels.
    tol_slope : float
        Tolerance on the residual slope (pixels per column), additional but non-invasive check.

    Returns
    -------
    corrected_spectrum : 2D np.ndarray
        Rectified 2D spectrum.
    """

    # Axes and original image copy (to avoid repeated resampling)
    ny, nx = spectrum.shape
    y_axis = np.arange(ny, dtype=float)
    x_axis = np.arange(nx, dtype=float)
    original = np.nan_to_num(spectrum, nan=0.0, posinf=0.0, neginf=0.0)

    # Utility: apply a per-column vertical shift with cubic interpolation
    def _apply_vertical_shift_from_original(corr_factor):
        out = np.zeros_like(original)
        y0, y1 = y_range
        # Slightly wider window for normalisation (mitigates edge losses)
        y0n = max(0, int(y0 - 3))
        y1n = min(ny, int(y1 + 3))

        for j in range(nx):
            col_shifted = map_coordinates(
                original[:, j],
                [y_axis + corr_factor[j]],
                order=3,          # cubic spline: good fidelity vs noise
                mode='nearest'    # avoids artefacts at the borders
            )
            # Flux conservation within the reference window ---
            src = original[y0n:y1n, j].sum()
            dst = col_shifted[y0n:y1n].sum()
            if dst > 0 and src > 0:
                col_shifted *= (src / dst)
            out[:, j] = col_shifted
        return out

    # Initial correction from the provided trace
    y_trace = trace_model(x_axis)
    y_ref = np.median(y_trace)                  # physical centre of the trace
    corr_factor = y_trace - y_ref               # per-column vertical shift
    corr_delta = np.ptp(corr_factor)            # range (max - min) in pixels

    # If already below threshold, perform a single pass
    if corr_delta <= tol_delta:
        corrected = _apply_vertical_shift_from_original(corr_factor)
        plt.imshow(corrected, cmap="gray", norm=LogNorm(), aspect='auto')
        plt.title("Corrected 2D Spectrum")
        plt.xlabel("Dispersion axis (pixels)"); plt.ylabel("Spatial axis (pixels)")
        plt.show(); plt.close()
        return corrected

    # Refinement iterations: ALWAYS resample from the original
    corrected = None
    for h in range(max_iter):
        corrected = _apply_vertical_shift_from_original(corr_factor)

        # Refit the trace on the corrected image (use your function, unchanged signature)
        try:
            new_trace_model = find_and_fit_spectroscopic_trace(
                corrected, y_range, poly_degree=1, first_iteration=False, with_plots=False
            )
        except Exception:
            print("Warning: unable to refit trace during rectification loop.")
            break

        y_trace = new_trace_model(x_axis)
        y_ref = np.median(y_trace)
        corr_factor = y_trace - y_ref
        corr_delta = np.ptp(corr_factor)

        # Additional check: residual slope (more physical), but does not alter your flow
        dy_dx = np.gradient(y_trace)
        max_slope = np.max(np.abs(dy_dx))

        print(f"Iter {h+1}/{max_iter} | delta={corr_delta:.3f} px | slope={max_slope:.4f} pix/col")

        # Convergence criteria: keep your delta, add a physical slope stop
        if (corr_delta <= tol_delta) or (max_slope <= tol_slope):
            print("Trace fitting convergence reached")
            break

    # Final plot
    if corrected is None:
        corrected = _apply_vertical_shift_from_original(corr_factor)

    plt.imshow(corrected, cmap="gray", norm=LogNorm(), aspect='auto')
    plt.title("Corrected 2D Spectrum")
    plt.xlabel("Dispersion axis (pixels)"); plt.ylabel("Spatial axis (pixels)")
    plt.show(); plt.close()

    return corrected

#17) Extracting the single 1D spectrum from user defined range
def extract_1d_spectrum(corrected_spectrum, y_range, header, x_axis, output_fits_path=None):
    # Function to extract 1D spectrum along x-axis with user-defined y range

    selected_y_range = slice(*y_range)
    extracted_spectrum = np.sum(corrected_spectrum[selected_y_range, :], axis=0)
    # Get wavelength coordinates if available, otherwise use x coordinates
    x_coordinates = get_wavelength_coordinates(header, x_axis)

    # Plot the extracted 1D Spectrum
    plt.plot(x_coordinates, extracted_spectrum)
    plt.title("Extracted 1D Spectrum")
    plt.show()
    plt.close()

    if output_fits_path is not None:
        # Save the extracted 1D spectrum in a FITS file
        hdu = fits.PrimaryHDU(extracted_spectrum)
        hdu.header["CTYPE1"] = 'LINEAR'  # Linear wavelength spacing
        hdu.header["CRPIX1"] = 1  # Reference pixel is the first pixel
        hdu.header["CRVAL1"] = x_coordinates[0]  # Reference value is the first wavelength
        hdu.header["CDELT1"] = np.mean(np.diff(x_coordinates))  # Average wavelength interval
        fits.writeto(output_fits_path, hdu.data, hdu.header, overwrite=True)

#18) Estimating the noise level based to user selection of two opposite regions along the full intensity profile of the spectrum. Required to extract n bins with fixed signal-to-noise
def estimate_noise_level(corrected_spectrum, y_range):
    # Function to estimate noise level along the X-axis
    start, end = map(int, y_range)
    selected_y_range = slice(start, end)
    noise_level_1 = abs(np.nanmean(corrected_spectrum[selected_y_range, :], axis=0))
    noise_level = np.mean(noise_level_1)
    return noise_level

#19) Calculating the signal-to-noise based to the noise level defined by the user
def calculate_signal_to_noise(spectrum_row, noise_level):
    spectrum_row = abs(spectrum_row)
    signal_to_noise = (np.nanmean(spectrum_row)/noise_level)
    return signal_to_noise

#20) Extracting the n 1D spectra of fixed signal-to-noise from the 2D fits image
# WITH TWO NOISE REGIONS TO SELECT. THE NOISE WILL BE A SIMPLE MEAN OF THE TWO REGIONS. COMMENT THIS AND UNCOMMENT THE FOLLOWING VERSION IF YOU PREFER TO SELECT ONLY ONE NOISE REGION.
def extract_and_save_snr_spectra(corrected_spectrum, trace_model, header, x_axis, snr_threshold, pixel_scale, file_path, y_correction_trace_position, result_long_slit_extract):

    #assign zeros to (eventual) NaN values in the 2D spec
    corrected_spectrum = np.nan_to_num(corrected_spectrum, nan=0)
    # Function to extract and save 1D spectra based on the mean signal-to-noise threshold along the X-axis
    y_axis = np.arange(len(corrected_spectrum))
    n_rows = len(y_axis)
    spectra = []

    signal_profile = np.sum(corrected_spectrum, axis=1)
    print ('Please, select two regions containing noise. Two clicks for each region: one for the start and the other for the end')
    print ('WARNING: Do not close the plot window without selecting the noise regions')
    # Allow the user to click on the corrected spectrum to select the Y-values for noise estimation
    try:
        plt.plot(y_axis, signal_profile)
        plt.title("Select TWO background regions. DO NOT CLOSE this window")
        plt.xlabel("Y-axis")
        plt.ylabel("Intensity")
        noise_region_points = plt.ginput(n=4, timeout=-1, show_clicks=True)
        noise_region_y_values_1 = [int(min(noise_region_points[0][0], noise_region_points[1][0])),
                                    int(max(noise_region_points[0][0], noise_region_points[1][0]))]
        noise_region_y_values_2 = [int(min(noise_region_points[2][0], noise_region_points[3][0])),
                                    int(max(noise_region_points[2][0], noise_region_points[3][0]))]

        plt.close()
        # Calculate mean noise level for the two regions
        noise_level_1 = estimate_noise_level(corrected_spectrum, noise_region_y_values_1)
        noise_level_2 = estimate_noise_level(corrected_spectrum, noise_region_y_values_2)
        noise_level = np.mean([noise_level_1, noise_level_2])

        y_positions = []
        y_positions_mean = []

        trace_mean_y_position = round(int(np.mean(trace_model(y_axis))))+y_correction_trace_position
    except Exception:
        return

    print ('')
    print ('Selected noise regions', noise_region_y_values_1, noise_region_y_values_2)
    print ('')
    print ('Mean noise level', noise_level)
    print ('')

    snr_array = []
    y_pos = 0
    i = 0
    while i < n_rows-1:
        if (min(noise_region_y_values_1) < np.min(y_axis) or max(noise_region_y_values_1) > np.max(y_axis) or min(noise_region_y_values_2) < np.min(y_axis) or max(noise_region_y_values_2) > np.max(y_axis)):
            sg.popup ('Noise region outside the spectrum!')
            break

        snr = calculate_signal_to_noise(corrected_spectrum[i, :], noise_level)
        if snr >= snr_threshold:
            # If the current row meets the threshold, add it to the spectra
            spectra.append(corrected_spectrum[i, :])
            y_pos = i
            y_positions.append(y_pos)
            y_positions_mean.append(y_pos)
            snr_array.append(snr)
            i += 1
        else:
            # If the current row does not meet the threshold, sum consecutive rows until the threshold is reached
            #The y position will be the snr weigthed mean position of the created bin.
            snr_for_mean = []
            y_for_mean = []

            #reading the spectra of the i row that did not meet the snr threshold, calculating the snr and storing the position
            summed_spectrum = np.copy(corrected_spectrum[i, :])
            y_for_mean.append(i)
            snr_single = calculate_signal_to_noise(corrected_spectrum[i, :], noise_level)
            snr_for_mean.append(snr_single)
            n_bins = 1

            while i + 1 < n_rows and np.nanmean(snr) < snr_threshold:
                # Now I have already at least two bins and I consider the i+1 row
                n_bins +=1
                i += 1
                snr_single = calculate_signal_to_noise(corrected_spectrum[i, :], noise_level)
                snr_for_mean.append(snr_single)
                y_for_mean.append(i)
                summed_spectrum += corrected_spectrum[i, :]
                mean_spectrum = summed_spectrum/n_bins
                noise_level_new = noise_level/mt.sqrt(n_bins)
                snr = calculate_signal_to_noise(mean_spectrum, noise_level_new)
            snr_array.append(snr)

            y_pos_mean_var = 0
            for t in range (len(y_for_mean)):
                y_pos_mean_var += (y_for_mean[t]*snr_for_mean[t])

            y_pos_mean_var = y_pos_mean_var/sum(snr_for_mean)
            y_positions_mean.append(round(y_pos_mean_var,1))
            spectra.append(summed_spectrum)

            # now I start again the analysis of the snr with the row next to the last used to build the i-bin
            i += 1

    if (min(noise_region_y_values_1) < np.min(y_axis) or max(noise_region_y_values_1) > np.max(y_axis) or min(noise_region_y_values_2) < np.min(y_axis) or max(noise_region_y_values_2) > np.max(y_axis)):
        print ('No files saved')
    else:

        spectra = np.array(spectra)
        y_positions_mean = np.array(y_positions_mean)
        y_position_from_center = y_positions_mean - trace_mean_y_position

        if pixel_scale != 0:
            trace_mean_y_position_arcsec = trace_mean_y_position*pixel_scale
            arcsec_scale_mean = y_positions_mean*pixel_scale
            y_position_from_center_arcsec = np.round((arcsec_scale_mean - trace_mean_y_position_arcsec), 2)
        else:
            y_position_from_center_arcsec = np.zeros_like(y_position_from_center)

        print ('Spectral bins Y mean position: ', y_positions_mean)
        print ('')
        print ('Number of bins: ', len(y_positions_mean))

        # Get wavelength coordinates if available, otherwise use x coordinates
        x_coordinates = get_wavelength_coordinates(header, x_axis)

        # Save the 1D spectra in IRAF-style FITS format
        extracted_filename = os.path.splitext(os.path.basename(file_path))[0]
        result_longslit_extraction = result_long_slit_extract + '/'+extracted_filename+'/'
        result_longslit_extraction_bins = result_longslit_extraction + 'bins/'
        os.makedirs(result_longslit_extraction_bins, exist_ok=True)
        bin_name_array = []
        for i, spectrum_row in enumerate(spectra):
            hdu = fits.PrimaryHDU(spectrum_row)
            hdu.header["CTYPE1"] = 'LINEAR'  # Linear wavelength spacing
            hdu.header["CRPIX1"] = 1  # Reference pixel is the first pixel
            hdu.header["CRVAL1"] = x_coordinates[0]  # Reference value is the first wavelength
            hdu.header["CDELT1"] = np.mean(np.diff(x_coordinates))  # Average wavelength interval

            #adding the position of the 1d spectra with respect to the central trace to the fits header
            hdu.header.set("Y_POS", y_position_from_center[i], "Pix position from the center")

            if pixel_scale != 0:
                hdu.header.set("R", y_position_from_center_arcsec[i], "Arcsec position from the center")

            hdu.writeto(result_longslit_extraction_bins + f"{extracted_filename}_{i+1:03}.fits", overwrite=True)
            bin_name = f"{extracted_filename}_{i+1:03}"
            bin_name_array.append(bin_name)

        #Prepare and save a text file with bin number, mean radius in pix, in arcsec and S/N
        snr_array = np.array(snr_array)
        snr_array = np.round(snr_array).astype(int)
        bin_info_file = result_longslit_extraction + f"{extracted_filename}_info.dat"
        data = {
            '#bin': bin_name_array,
            'y_pix': y_positions_mean,
            'y_arcsec': y_position_from_center_arcsec,
            'snr': snr_array
        }
        df = pd.DataFrame(data)
        df.to_csv(bin_info_file, sep=' ', index=False)

        print ('Extraction infos saved in: ', bin_info_file)
        print('')

        # Plot the extracted 1D Spectra
        plt.figure()
        for i, spectrum_row in enumerate(spectra):
            plt.plot(x_coordinates, spectrum_row, label=f"Spectrum {i+1}")

        plt.xlabel("Wavelength")
        plt.ylabel("Flux")
        plt.legend()
        plt.title("Extracted 1D SNR Spectra")
        plt.show()
        plt.close()
        sg.popup ('1D spectra saved in the working directory')


#UNCOMMENT THE FOLLOWING FUNCTION AND COMMENT THE PREVIOUS IF YOU WANT TO SELECT JUST ONE NOISE REGION INSTEAD OF TWO!
#def extract_and_save_snr_spectra(corrected_spectrum, trace_model, header, x_axis, snr_threshold, pixel_scale, file_path, y_correction_trace_position, result_long_slit_extract):
    ## Function to extract and save 1D spectra based on the mean signal-to-noise threshold along the X-axis
    #y_axis = np.arange(len(corrected_spectrum))
    #n_rows = len(y_axis)
    #spectra = []

    #signal_profile = np.sum(corrected_spectrum, axis=1)
    #print ('Please, select a region containing noise. Two clicks: one for the start and the other for the end')
    #print ('WARNING: Do not close the plot window without selecting the noise regions. Otherwise the program will freeze')
    ## Allow the user to click on the corrected spectrum to select the Y-values for noise estimation
    #plt.plot(y_axis, signal_profile)
    #plt.title("Corrected 2D Spectrum - Select Noise Region")
    #plt.xlabel("Y-axis")
    #plt.ylabel("Intensity")
    #noise_region_points = plt.ginput(n=2, timeout=-1, show_clicks=True)
    #noise_region_y_range = (int(min(noise_region_points[0][0], noise_region_points[1][0])),
                            #int(max(noise_region_points[0][0], noise_region_points[1][0])))
    #plt.close()

    #noise_level = estimate_noise_level(corrected_spectrum, noise_region_y_range)

    #y_positions = []
    #y_positions_mean = []

    #trace_mean_y_position = round(int(np.mean(trace_model(y_axis))))

    #print ('')
    #print ('Selected noise region', noise_region_y_range)
    #print ('')
    #print ('Mean noise level', noise_level)
    #print ('')
    ##print (len(corrected_spectrum))

    #y_pos = 0
    #i = 0
    #while i < n_rows-1:
        #if (min(noise_region_y_range) < np.min(y_axis) or max(noise_region_y_range) > np.max(y_axis)):
            #sg.popup ('Noise region outside the spectrum!')
            #break

        #snr = calculate_signal_to_noise(corrected_spectrum[i, :], noise_level)
        #if np.nanmean(snr) >= snr_threshold:
            ## If the current row meets the threshold, add it to the spectra
            #spectra.append(corrected_spectrum[i, :])
            #y_pos = i
            #y_positions.append(y_pos)
            #y_positions_mean.append(y_pos)
            #i += 1
        #else:
            ## If the current row does not meet the threshold, sum consecutive rows until the threshold is reached
            #snr_for_mean = []
            #y_for_mean = []
            #summed_spectrum = np.copy(corrected_spectrum[i, :])
            #n_bins = 0
            #while i + 1 < n_rows and np.nanmean(snr) < snr_threshold:
                #i += 1
                #n_bins +=1
                #snr_single = calculate_signal_to_noise(corrected_spectrum[i, :], noise_level)
                #snr_for_mean.append(snr_single)
                #y_for_mean.append(i)
                #summed_spectrum += corrected_spectrum[i, :]
                #mean_spectrum = summed_spectrum/n_bins
                #noise_level_new = noise_level/mt.sqrt(n_bins)
                #snr = calculate_signal_to_noise(mean_spectrum, noise_level_new)

            #y_pos_mean_var = 0
            #for t in range (len(y_for_mean)):
                #y_pos_mean_var += (y_for_mean[t]*snr_for_mean[t])

            #y_pos_mean_var = y_pos_mean_var/sum(snr_for_mean)
            #y_positions_mean.append(round(y_pos_mean_var,1))
            #y_pos = i
            #y_positions.append(y_pos)
            #spectra.append(summed_spectrum)

    #if (min(noise_region_y_range) < np.min(y_axis) or max(noise_region_y_range) > np.max(y_axis)):
        #print ('No files saved')
    #else:

        #spectra = np.array(spectra)
        #y_positions = np.array(y_positions)
        #y_positions_mean = np.array(y_positions_mean)

        #if pixel_scale != 0:
            #arcsec_scale = y_positions*pixel_scale
            #arcsec_scale_mean = y_positions_mean*pixel_scale

        ##print ('Spectral bins Y position: ', y_positions)
        #print ('Spectral bins Y mean position: ', y_positions_mean)
        #print ('')
        #print ('Number of bins: ', len(y_positions_mean))

        ## Get wavelength coordinates if available, otherwise use x coordinates
        #x_coordinates = get_wavelength_coordinates(header, x_axis)

        ## Save the 1D spectra in IRAF-style FITS format
        #for i, spectrum_row in enumerate(spectra):
            #hdu = fits.PrimaryHDU(spectrum_row)
            #hdu.header["CTYPE1"] = 'LINEAR'  # Linear wavelength spacing
            #hdu.header["CRPIX1"] = 1  # Reference pixel is the first pixel
            #hdu.header["CRVAL1"] = x_coordinates[0]  # Reference value is the first wavelength
            #hdu.header["CDELT1"] = np.mean(np.diff(x_coordinates))  # Average wavelength interval

            ##adding the position of the 1d spectra with respect to the central trace to the fits header
            #hdu.header.set("Y_POS", y_positions_mean[i] - trace_mean_y_position, "Pix position from the center")
            #if pixel_scale != 0:
                #hdu.header.set("R", arcsec_scale_mean[i] - (trace_mean_y_position*pixel_scale), "Arcsec position from the center")

            #base_filename = os.path.splitext(os.path.basename(file_path))[0]
            #hdu.writeto(f"{base_filename}_{i+1}.fits", overwrite=True)

        ## Plot the extracted 1D Spectra
        #plt.figure()
        #for i, spectrum_row in enumerate(spectra):
            #plt.plot(x_coordinates, spectrum_row, label=f"Spectrum {i+1}")

        #plt.xlabel("Wavelength")
        #plt.ylabel("Flux")
        #plt.legend()
        #plt.title("Extracted 1D SNR Spectra")
        #plt.show()
        #plt.close()
        #sg.popup ('1D spectra saved in the working directory')

#********************************************

#********************************************
# FUNCTIONS FOR THE TEXT EDITOR

"""
The functions below are needed for the 'Text editor'
subprogram in order to read and perform simple operations
on the ASCII files generated by SPAN.

"""

#21) Saving the file in the text editor
def save_file(filename, text):
    with open(filename, 'w') as file:
        file.write(text)

#22) find and replace function
def find_replace(text, find, replace, replace_all):
    if replace_all:
        return text.replace(find, replace)
    else:
        return text.replace(find, replace, 1)

#23) create a new column
def create_new_column(df, new_column_name, col1_name, col2_name, expression):
    try:
        df[new_column_name] = pd.eval(expression, engine='python',
                                    local_dict={col1_name: df[col1_name], col2_name: df[col2_name]})
        return df
    except Exception as e:
        sg.popup_error(f'Error creating the new column: {str(e)}')
        return None

#24) merge two text files, with the same number of rows
def merge_files(file1_path, file2_path, common_column):
    try:
        #Load the files
        data1 = pd.read_csv(file1_path, sep=' ')
        data2 = pd.read_csv(file2_path, sep=' ')

        #Merge the files with the common row
        merged_data = pd.merge(data1, data2, on=common_column)

        #Saving the new file
        merged_file_path = sg.popup_get_file('Save the merged file', save_as=True, default_extension=".txt", file_types=(("Text Files", "*.txt"),))
        if merged_file_path:
            merged_data.to_csv(merged_file_path, sep=' ', index=False)
            sg.popup(f'The files have been merged and saved to {merged_file_path}.')
    except Exception as e:
        sg.popup_error(f'Error merging files: {str(e)}')
#********************************************

#********************************************
# FUNCTIONS FOR GENERATING THE SPECTRA FILE LIST

#25) Building the file list from the selected folder
def get_files_in_folder(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            absolute_path = os.path.join(root, file).replace("\\", "/") #UNIX format which is compatible also with Windows.
            file_list.append(absolute_path)
    return sorted(file_list, key=str.lower)

#26) Saving the spectra file list
def save_to_text_file(file_list, output_file):
    with open(output_file, 'w') as f:
        f.write("#Spectrum\n")
        for absolute_path in file_list:
            f.write(f"{absolute_path}\n")

######################################################

#29) Function to save the mask file generated by SPAN in the "DataCube extraction" sub-program
def save_mask_as_fits(mask, output_filename):
    primary_hdu = fits.PrimaryHDU(np.zeros((1, 1), dtype=np.int32))
    mask_hdu = fits.ImageHDU(mask.astype(np.int32))
    mask_hdu.header['EXTNAME'] = 'MASK'
    hdul = fits.HDUList([primary_hdu, mask_hdu])
    hdul.writeto(output_filename, overwrite=True)
    print(f"Mask saved as {output_filename}")

#***********************************************

# FUNCTIONS FOR THE 2D PLOT

"""
The functions below are needed for the 'Plot maps'
subprogram in order to visualize 2D maps from datacube analysis.

"""

def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]', '_', name)

def load_fits_data(fits_file):
    """Load spaxel coordinates and BIN_ID from FITS table"""
    with fits.open(fits_file) as hdul:
        table = hdul[1].data
        x = table['X']
        y = table['Y']
        bin_id = table['BIN_ID'].astype(int)
        xbin = table['XBIN']
        ybin = table['YBIN']
    return x, y, bin_id, xbin, ybin

def load_analysis_results(txt_file):
    """Load analysis results and extract column names"""
    df = pd.read_csv(txt_file, sep=r'\s+')
    return df



def plot_voronoi_map(x, y, bin_id, result_df, quantity, cmap="inferno",
                     img_path=None, iso_levels=None, vmin=None, vmax=None):
    """
    Static Voronoi-like map of a quantity with optional isophote overlay.

    Parameters
    ----------
    x, y : array
        Coordinates [arcsec] of each spaxel.
    bin_id : array
        Voronoi bin ID for each spaxel.
    result_df : pandas.DataFrame
        Table of results with the quantity to be mapped.
    quantity : str
        Column name of the quantity to plot.
    cmap : str
        Matplotlib colormap name.
    img_path : str or None
        Optional path to FITS image to overlay isophotes.
    iso_levels : list of float or None
        Normalised levels (0–100) for the isophotes.
    """

    value_map = {}
    for _, row in result_df.iterrows():
        try:
            bin_str = row.iloc[0].split('_')[-1].split('.')[0]
            bin_num = int(bin_str)
            value_map[bin_num] = row[quantity]
        except Exception:
            continue

    signal = np.full_like(bin_id, np.nan, dtype=float)
    for i in range(len(bin_id)):
        b = bin_id[i]
        if b >= 0 and b in value_map:
            signal[i] = value_map[b]

    x_bins = np.sort(np.unique(x))
    y_bins = np.sort(np.unique(y))
    grid_data = np.full((len(y_bins), len(x_bins)), np.nan)
    for i in range(len(x)):
        x_idx = np.searchsorted(x_bins, x[i])
        y_idx = np.searchsorted(y_bins, y[i])
        grid_data[y_idx, x_idx] = signal[i]

    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_bins, y_bins, grid_data, cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)
    plt.colorbar(mesh, ax=ax, label=quantity)
    ax.set_xlabel("R [arcsec]")
    ax.set_ylabel("R [arcsec]")
    ax.set_title(f"{quantity}")

    # Isofote se immagine presente
    if img_path and os.path.isfile(img_path):
        try:
            overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
        except Exception as e:
            print(f"[WARNING] Could not overlay isophotes: {e}")

    # plt.tight_layout()
    return fig, ax



def plot_voronoi_map_clickable(x, y, bin_id, result_df, quantity, cmap="inferno", vmin=None, vmax=None):
    """Interactive 2D Voronoi map with bin ID and value popup on click."""

    # Build value map: bin_id -> quantity
    value_map = {}
    for _, row in result_df.iterrows():
        try:
            bin_str = row.iloc[0].split('_')[-1].split('.')[0]
            bin_num = int(bin_str)
            value_map[bin_num] = row[quantity]
        except Exception:
            continue

    # Create signal array per spaxel
    signal = np.full_like(bin_id, np.nan, dtype=float)
    for i in range(len(bin_id)):
        b = bin_id[i]
        if b >= 0 and b in value_map:
            signal[i] = value_map[b]

    # Create image grid
    x_bins, y_bins = np.unique(x), np.unique(y)
    grid_data = np.full((len(y_bins), len(x_bins)), np.nan)
    for i in range(len(x)):
        x_idx = np.searchsorted(x_bins, x[i])
        y_idx = np.searchsorted(y_bins, y[i])
        grid_data[y_idx, x_idx] = signal[i]

    # Setup plot
    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_bins, y_bins, grid_data, cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)
    fig.colorbar(mesh, ax=ax, label=quantity)
    ax.set_xlabel("R [arcsec]")
    ax.set_ylabel("R [arcsec]")
    ax.set_title(f"{quantity}")
    # plt.tight_layout()

    # Internal variables to track annotation and marker
    annotation = None
    highlight = None

    # On-click callback
    def onclick(event):
        nonlocal annotation, highlight
        if event.inaxes != ax:
            return
        x_click, y_click = event.xdata, event.ydata
        dist = np.sqrt((x - x_click)**2 + (y - y_click)**2)
        idx_min = np.argmin(dist)
        selected_bin = bin_id[idx_min]
        value = value_map.get(selected_bin, np.nan)

        # Clean previous
        if annotation:
            annotation.remove()
        if highlight:
            highlight.remove()

        # Add new
        annotation = ax.annotate(
            f"BIN {selected_bin} | {quantity} = {value:.3f}",
            (x[idx_min], y[idx_min]),
            xytext=(5, 5), textcoords='offset points',
            fontsize=10, color='white', weight='bold',
            bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.5)
        )

        highlight = ax.plot(
            x[idx_min], y[idx_min],
            marker='o', color='red', markersize=8, markeredgecolor='white'
        )[0]

        fig.canvas.draw()
        print(f"Clicked BIN {selected_bin}: {quantity} = {value:.3f} at (x={x[idx_min]:.1f}, y={y[idx_min]:.1f})")

    fig.canvas.mpl_connect('button_press_event', onclick)
    # plt.show()
    return fig, ax



def plot_reprojected_map(x, y, bin_id, result_df, quantity, cmap="inferno",
                          smoothing=False, sigma=0.0,
                          img_path=None, iso_levels=None, vmin=None, vmax=None):
    """
    Plot or save a reprojected map of a quantity on a regular grid.

    Parameters
    ----------
    x, y : array
        Coordinates of each spaxel [arcsec].
    bin_id : array
        Voronoi bin ID per spaxel.
    result_df : pandas.DataFrame
        Table with results, including quantity to map.
    quantity : str
        Name of the quantity to visualise.
    cmap : str
        Name of matplotlib colormap.
    smoothing : bool
        If True, apply Gaussian smoothing.
    sigma : float
        Sigma of the Gaussian kernel [pixels].
    img_path : str or None
        Path to the 2D image FITS file for isophotes.
    iso_levels : list of float or None
        Normalised levels (0–100) for the isophotes. If None, default levels used.

    """
    # Build bin -> quantity map
    value_map = {}
    for _, row in result_df.iterrows():
        try:
            bin_str = row.iloc[0].split('_')[-1].split('.')[0]
            bin_num = int(bin_str)
            value_map[bin_num] = row[quantity]
        except Exception:
            continue

    # --- Build the regular grid  ---
    x_bins = np.sort(np.unique(x))
    y_bins = np.sort(np.unique(y))
    grid_data = np.full((len(y_bins), len(x_bins)), np.nan)

    for i in range(len(x)):
        b = bin_id[i]
        if b >= 0 and b in value_map:
            x_idx = np.searchsorted(x_bins, x[i])
            y_idx = np.searchsorted(y_bins, y[i])
            # NB: searchsorted returns insertion index; if x[i] equals the last bin,
            #     it may point one past the end. Clamp safely:
            x_idx = np.clip(x_idx, 0, len(x_bins)-1)
            y_idx = np.clip(y_idx, 0, len(y_bins)-1)
            grid_data[y_idx, x_idx] = value_map[b]

    # --- Apply smoothing robustly (prevent area growth) ---
    if smoothing and sigma > 0:
        mask = ~np.isnan(grid_data)
        smoothed_data = gaussian_smooth_masked(
            grid=grid_data,
            mask=mask,
            sigma=float(sigma),       # must be in *pixels*
            threshold=0.5,            # more conservative than 1e-3
            dilate_mult=2.5,
            enforce_support=True,
            mode='constant',
            cval=0.0
        )
    else:
        smoothed_data = grid_data

    # --- Use edges to avoid visual enlargement at plot time ---
    x_edges = edges_from_centres(x_bins)
    y_edges = edges_from_centres(y_bins)

    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_edges, y_edges, smoothed_data, cmap=cmap,
                        shading='auto', vmin=vmin, vmax=vmax)
    plt.colorbar(mesh, ax=ax, label=quantity)
    ax.set_xlabel("R [arcsec]")
    ax.set_ylabel("R [arcsec]")
    ax.set_title(f"{quantity}")

    # Overlay isophotes
    if img_path and os.path.isfile(img_path):
        try:
            overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
        except Exception as e:
            print(f"[WARNING] Could not overlay isophotes: {e}")

    # plt.tight_layout()

    return fig, ax



def plot_reprojected_map_clickable(x, y, bin_id, result_df, quantity, cmap="inferno", smoothing=False, sigma=0.0, img_path=None, iso_levels=None, vmin=None, vmax=None):
    
    """
    Plot or save a reprojected map of a quantity on a regular grid.

    Parameters
    ----------
    x, y : array
        Coordinates of each spaxel [arcsec].
    bin_id : array
        Voronoi bin ID per spaxel.
    result_df : pandas.DataFrame
        Table with results, including quantity to map.
    quantity : str
        Name of the quantity to visualise.
    cmap : str
        Name of matplotlib colormap.
    smoothing : bool
        If True, apply Gaussian smoothing.
    sigma : float
        Sigma of the Gaussian kernel [pixels].
    img_path : str or None
        Path to the 2D image FITS file for isophotes.
    iso_levels : list of float or None
        Normalised levels (0–100) for the isophotes. If None, default levels used.

    Returns
    -------
    fig, ax : matplotlib figure and axes with the plotted map.
    """
    # Build bin -> quantity map
    value_map = {}
    for _, row in result_df.iterrows():
        try:
            bin_str = row.iloc[0].split('_')[-1].split('.')[0]
            bin_num = int(bin_str)
            value_map[bin_num] = row[quantity]
        except Exception:
            continue

    # --- Build the regular grid  ---
    x_bins = np.sort(np.unique(x))
    y_bins = np.sort(np.unique(y))
    grid_data = np.full((len(y_bins), len(x_bins)), np.nan)

    for i in range(len(x)):
        b = bin_id[i]
        if b >= 0 and b in value_map:
            x_idx = np.searchsorted(x_bins, x[i])
            y_idx = np.searchsorted(y_bins, y[i])
            # NB: searchsorted returns insertion index; if x[i] equals the last bin,
            #     it may point one past the end. Clamp safely:
            x_idx = np.clip(x_idx, 0, len(x_bins)-1)
            y_idx = np.clip(y_idx, 0, len(y_bins)-1)
            grid_data[y_idx, x_idx] = value_map[b]

    # --- Apply smoothing robustly (prevent area growth) ---
    if smoothing and sigma > 0:
        mask = ~np.isnan(grid_data)
        smoothed_data = gaussian_smooth_masked(
            grid=grid_data,
            mask=mask,
            sigma=float(sigma),       # must be in *pixels*
            threshold=0.5,            # more conservative than 1e-3
            dilate_mult=2.5,
            enforce_support=True,
            mode='constant',
            cval=0.0
        )
    else:
        smoothed_data = grid_data

    # --- Use edges to avoid visual enlargement at plot time ---
    x_edges = edges_from_centres(x_bins)
    y_edges = edges_from_centres(y_bins)

    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_edges, y_edges, smoothed_data, cmap=cmap,
                        shading='auto', vmin=vmin, vmax=vmax)
    plt.colorbar(mesh, ax=ax, label=quantity)
    ax.set_xlabel("R [arcsec]")
    ax.set_ylabel("R [arcsec]")
    ax.set_title(f"{quantity}")

    # Overlay isophotes
    if img_path and os.path.isfile(img_path):
        try:
            overlay_isophotes(ax, img_path, x, y, color='black', levels=iso_levels)
        except Exception as e:
            print(f"[WARNING] Could not overlay isophotes: {e}")

    # Add interactivity (clickable)
    annotation_smooth = None
    highlight_smooth = None

    def onclick(event):
        nonlocal annotation_smooth, highlight_smooth
        if event.inaxes != ax:
            return
        x_click, y_click = event.xdata, event.ydata
        dist = np.sqrt((x - x_click)**2 + (y - y_click)**2)
        idx_min = np.argmin(dist)
        selected_bin = bin_id[idx_min]
        value = value_map.get(selected_bin, np.nan)

        if annotation_smooth:
            annotation_smooth.remove()
        if highlight_smooth:
            highlight_smooth.remove()

        annotation_smooth = ax.annotate(
            f"BIN {selected_bin} | {quantity} = {value:.3f}",
            (x[idx_min], y[idx_min]),
            xytext=(5, 5), textcoords='offset points',
            fontsize=10, color='white', weight='bold',
            bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.5)
        )

        highlight_smooth = ax.plot(
            x[idx_min], y[idx_min],
            marker='o', color='red', markersize=8, markeredgecolor='white'
        )[0]

        fig.canvas.draw()
        print(f"Clicked BIN {selected_bin}: {quantity} = {value:.3f} at (x={x[idx_min]:.1f}, y={y[idx_min]:.1f})")

    fig.canvas.mpl_connect('button_press_event', onclick)
    # plt.tight_layout()

    return fig, ax




def overlay_isophotes(ax, image_path, x, y, color='white', levels=None):
    """
    Overlay isophotes from a 2D image onto an existing matplotlib axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis on which to draw the isophotes.
    image_path : str
        Path to the 2D image FITS file.
    x, y : array-like
        Coordinates of the spaxels (same as those used to plot the map).
    color : str, optional
        Color of the contour lines.
    levels : list or None
        Contour levels. If None, defaults to percentiles [90, 75, 60, 45, 30].
    """
    try:
        image_2d = fits.getdata(image_path)

        x_bins = np.sort(np.unique(x))
        y_bins = np.sort(np.unique(y))
        xx, yy = np.meshgrid(x_bins, y_bins)

        # Interpolazione se le forme non combaciano
        if image_2d.shape != xx.shape:
            ny, nx = xx.shape
            image_flat = image_2d.flatten()
            coords_flat = np.array(np.meshgrid(np.arange(image_2d.shape[1]), np.arange(image_2d.shape[0]))).reshape(2, -1).T
            target_coords = np.stack([xx.flatten(), yy.flatten()], axis=1)
            image_interp = griddata(coords_flat, image_flat, target_coords, method='linear')
            image_2d = image_interp.reshape(xx.shape)

        if levels is None:
            levels = np.nanpercentile(image_2d, [30, 45, 60, 75, 90])
        else:
            levels = np.nanpercentile(image_2d, levels)

        ax.contour(xx, yy, image_2d, levels=levels, colors=color, linewidths=1.5)
        # ax.contour(xx, yy, image_2d, levels=levels, colors=color, linewidths=1.5)

    except Exception as e:
        print(f"[WARNING] Could not overlay isophotes:\n{e}")


# Plotting radial profiles for the 'Plot maps' sub-program
def plot_radial_profile_bins(xbin, ybin, bin_id, result_df, quantity):
    """
    Plot radial profile using XBIN/YBIN positions from *_table.fits.
    One point per Voronoi bin.

    Parameters
    ----------
    xbin, ybin : array
        Coordinates [arcsec] of the bin centres for each spaxel.
    bin_id : array
        Voronoi bin ID for each spaxel.
    result_df : pandas.DataFrame
        Table of results with the quantity to plot.
    quantity : str
        Column name of the quantity to plot.
    """

    value_map = {}
    for _, row in result_df.iterrows():
        try:
            bin_str = row.iloc[0].split('_')[-1].split('.')[0]
            bin_num = int(bin_str)
            value_map[bin_num] = row[quantity]
        except Exception:
            continue

    used_bins = set()
    r_values = []
    q_values = []

    for i in range(len(bin_id)):
        b = bin_id[i]
        if b < 0 or b in used_bins or b not in value_map:
            continue

        xb = xbin[i]
        yb = ybin[i]

        r = np.sqrt((xb)**2 + (yb)**2)
        r_values.append(r)
        q_values.append(value_map[b])
        used_bins.add(b)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(r_values, q_values, s=5, c='black', alpha=0.8)
    ax.set_xlabel("Distance from center [arcsec]")
    ax.set_ylabel(quantity)
    ax.set_title(f"{quantity}")
    ax.grid(True)

    return fig, ax

#***********************************************

# Functions for the graphical masking of the 'Stars and gas kinematics' and 'Stellar populations and SFH' tasks

def graphical_masking_1D(wavelength, flux, existing_mask_str, touch_mode=False):
    """
    GUI masking tool for 1D spectrum with desktop and touch-friendly mode.
    - On desktop: Ctrl + left/right drag to mask/unmask
    - On touch: double-tap switches between mask/unmask; drag always applies current mode
    """

    # Try to load existing mask regions
    try:
        mask_regions = ast.literal_eval(existing_mask_str)
        if not isinstance(mask_regions, list):
            mask_regions = []
    except Exception:
        mask_regions = []

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(wavelength, flux, lw=0.7, color='black')
    # ax.set_title("Draw regions to mask. Close window to apply.")
    if touch_mode:
        ax.set_title("Tap and drag to mask | double tap, then tap + drag to unmask | Close window to apply")
    else:
        ax.set_title("Ctrl + left drag to mask | Ctrl + right drag to unmask | Close window to apply")
    ax.set_xlabel("Wavelength (Å)")
    ax.set_ylabel("Flux")

    # Set X/Y limits with margin
    x_margin = 0.01 * (np.max(wavelength) - np.min(wavelength))
    y_margin = 0.05 * (np.max(flux) - np.min(flux))
    ax.set_xlim(np.min(wavelength) - x_margin, np.max(wavelength) + x_margin)
    ax.set_ylim(np.min(flux) - y_margin, np.max(flux) + y_margin)

    # Visual height for the masking band
    band_height = np.max(flux) - np.min(flux) + 2 * y_margin
    band_bottom = np.min(flux) - y_margin

    # Draw existing mask regions
    patches = []
    for (x0, x1) in mask_regions:
        rect = plt.Rectangle((x0, band_bottom), x1 - x0, band_height,
                             linewidth=0, facecolor='red', alpha=0.3)
        ax.add_patch(rect)
        patches.append(rect)

    # Variables to store dragging
    start_point = None
    dragging = False
    deselecting = False

    # Touch-mode masking toggle
    masking_mode = [True]  # True = mask, False = unmask
    mode_text = None
    if touch_mode:
        mode_text = ax.text(0.99, 1.02, 'Mode: MASK', transform=ax.transAxes,
                            ha='right', va='bottom', fontsize=10, color='green')

    def toggle_mode(event):
        if not touch_mode:
            return
        # Toggle only if in axes
        if event.inaxes != ax:
            return
        masking_mode[0] = not masking_mode[0]
        if mode_text:
            mode_text.set_text('Mode: MASK' if masking_mode[0] else 'Mode: UNMASK')
            mode_text.set_color('green' if masking_mode[0] else 'red')
            fig.canvas.draw_idle()

    def on_press(event):
        nonlocal start_point, dragging, deselecting

        if event.inaxes != ax or event.xdata is None:
            return

        if touch_mode:
            start_point = event.xdata
            dragging = True
            deselecting = not masking_mode[0]
        else:
            if event.key is None or (('control' not in event.key.lower()) and ('ctrl' not in event.key.lower())):
                return
            if event.button == MouseButton.LEFT:
                start_point = event.xdata
                dragging = True
                deselecting = False
            elif event.button == MouseButton.RIGHT:
                start_point = event.xdata
                dragging = True
                deselecting = True

    def on_release(event):
        nonlocal start_point, dragging, deselecting

        if start_point is None or event.xdata is None:
            return

        end_point = event.xdata
        x0, x1 = sorted([start_point, end_point])
        dragging = False

        if not deselecting:
            # Add masked region
            mask_regions.append((x0, x1))
            rect = plt.Rectangle((x0, band_bottom), x1 - x0, band_height,
                                 linewidth=0, facecolor='red', alpha=0.3)
            ax.add_patch(rect)
            patches.append(rect)
        else:
            # Remove any region overlapping with this range
            new_regions = []
            for (a, b), patch in zip(mask_regions, patches):
                if b < x0 or a > x1:
                    new_regions.append((a, b))
                else:
                    patch.remove()
            mask_regions[:] = new_regions
            patches[:] = [p for p in ax.patches]

        fig.canvas.draw_idle()
        start_point = None

    # Connect events
    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("button_release_event", on_release)
    if touch_mode:
        fig.canvas.mpl_connect("button_press_event", toggle_mode)

    plt.show()
    plt.close()

    # Convert result to clean float
    final_regions = sorted([(float(round(a, 2)), float(round(b, 2))) for a, b in mask_regions])
    return '[' + ', '.join(f'({a}, {b})' for a, b in final_regions) + ']'



# Function for a quick estimate of the S/N during the loading of the spectra
def quick_snr(wl, fl):
    """Return a rough global SNR estimate for a spectrum."""
    wl = np.asarray(wl, dtype=float)
    fl = np.asarray(fl, dtype=float)
    ok = np.isfinite(wl) & np.isfinite(fl)
    if np.count_nonzero(ok) < 30:
        return None

    wl = wl[ok]
    fl = fl[ok]

    try:
        p = np.polyfit(wl, fl, 1)
        baseline = p[0]*wl + p[1]
        resid = fl - baseline
    except Exception:
        med = np.nanmedian(fl)
        resid = fl - med

    mad = np.nanmedian(np.abs(resid))
    sigma = mad * 1.4826 if mad > 0 else np.nanstd(resid)
    if not np.isfinite(sigma) or sigma <= 0:
        return None

    signal = np.nanmedian(np.abs(fl))
    return signal / sigma if sigma > 0 else None


# Simple function to open the PDF manual
def open_manual():
    try:
        manual_path = os.path.join(BASE_DIR, "user_manual_SPAN_7.1.pdf")

        if sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", manual_path])
        elif os.name == "nt":  # Windows
            os.startfile(manual_path) 
        elif os.name == "posix":  # Linux/Unix
            subprocess.run(["xdg-open", manual_path])
        else:
            raise RuntimeError("Unsupported platform")
    except Exception:
        sg.popup('SPAN manual not found, sorry.')


# Additional functions to properly handle the smoothing for the Plot Maps subprogram
def gaussian_smooth_masked(grid: np.ndarray,
                           mask: np.ndarray,
                           sigma: float,
                           threshold: float = 0.5,
                           dilate_mult: float = 2.5,
                           enforce_support: bool = True,
                           mode: str = 'constant',
                           cval: float = 0.0) -> np.ndarray:
    """
    Gaussian smoothing on a masked grid, preventing 'area growth' beyond the mask.

    Parameters
    ----------
    grid : 2D array
        Input image with NaNs where data are missing.
    mask : 2D boolean array
        True where data are valid (non-NaN), False elsewhere.
    sigma : float
        Gaussian sigma in *pixels*.
    threshold : float, optional
        Minimum normalised weight (0..1) to keep output; below -> NaN.
        Use 0.3–0.7 depending on how conservative you want the support.
    dilate_mult : float, optional
        Multiple of sigma to dilate the mask for a hard support clamp.
        Roughly, 2–3 * sigma gives visually pleasant boundaries.
    enforce_support : bool, optional
        If True, apply an additional binary dilation clamp on the final support.
    mode, cval : passed to gaussian_filter
        Use mode='constant', cval=0.0 to avoid reflective edge artefacts.

    Returns
    -------
    smoothed : 2D array
        Smoothed grid with NaNs outside the chosen support.
    """
    # Replace NaNs by 0 only for the convolution
    num = np.nan_to_num(grid, nan=0.0)

    # Convolve numerator (data) and denominator (weights)
    sm_num = gaussian_filter(num, sigma=sigma, mode=mode, cval=cval)
    sm_den = gaussian_filter(mask.astype(float), sigma=sigma, mode=mode, cval=cval)

    # Normalise; keep only sufficiently supported pixels
    with np.errstate(invalid='ignore', divide='ignore'):
        out = sm_num / sm_den
        out[sm_den <= float(threshold)] = np.nan

    if enforce_support:
        # Hard support clamp by dilating the original mask by ~k*sigma
        dilate_iter = max(1, int(np.ceil(dilate_mult * max(1.0, float(sigma)))))
        support = binary_dilation(mask, iterations=dilate_iter)
        out[~support] = np.nan

    return out


def _midpoints(arr: np.ndarray) -> np.ndarray:
    return 0.5 * (arr[1:] + arr[:-1])

def edges_from_centres(centres: np.ndarray) -> np.ndarray:
    centres = np.asarray(centres)
    if centres.size == 1:
        step = 1.0
        return np.array([centres[0] - 0.5*step, centres[0] + 0.5*step])
    mids = _midpoints(centres)
    first_edge = centres[0] - (mids[0] - centres[0])
    last_edge  = centres[-1] + (centres[-1] - mids[-1])
    return np.concatenate([[first_edge], mids, [last_edge]])

#********************** END OF SYSTEM FUNCTIONS *******************************************
#******************************************************************************************
