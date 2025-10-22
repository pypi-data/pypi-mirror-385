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


from astropy.io import fits
import numpy as np
import os
import sys

# Append parent directory to system path for importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from span_functions import utilities as uti

# ======================================
# Routine to load MUSE cubes. Inspired by the GIST pipeline of Bittner et. al 2019
# ======================================
def read_cube(config):
    """
    Reads a MUSE-WFMAON datacube and extracts spatial, spectral, and SNR information.

    Parameters:
    config (dict): Configuration dictionary with parameters for reading the cube.

    Returns:
    dict: Dictionary containing extracted cube data, including spatial coordinates,
          wavelengths, spectra, errors, and SNR.
    """

    # Log and print the start of the cube reading process
    print(f"Reading the MUSE-WFMAON cube: {config['INFO']['INPUT']}")

    # Open the FITS file and extract data and header
    hdu = fits.open(config['INFO']['INPUT'])
    hdr = hdu[1].header
    data = hdu[1].data
    s = np.shape(data)
    spec = np.reshape(data, [s[0], s[1] * s[2]])

    if len(hdu) == 3:
        print("Reading the error spectra from the cube")
        stat = hdu[2].data
        espec = np.reshape(stat, [s[0], s[1] * s[2]])
    elif len(hdu) == 2:
        print("No error extension found. Estimating error spectra from the flux.")
        espec = np.zeros(spec.shape)
        for i in range(spec.shape[1]):
            espec[:, i] = uti.noise_spec(spec[:, i])

    # Calculate the wavelength array using header information
    wave = hdr['CRVAL3'] + (np.arange(s[0])) * hdr['CD3_3']

    # Extract spatial coordinates and pixel size
    origin = [
        float(config['READ']['ORIGIN'].split(',')[0].strip()),
        float(config['READ']['ORIGIN'].split(',')[1].strip())
    ]
    xaxis = (np.arange(s[2]) - origin[0]) * hdr['CD2_2'] * 3600.0
    yaxis = (np.arange(s[1]) - origin[1]) * hdr['CD2_2'] * 3600.0
    x, y = np.meshgrid(xaxis, yaxis)
    x = np.reshape(x, [s[1] * s[2]])
    y = np.reshape(y, [s[1] * s[2]])
    pixelsize = hdr['CD2_2'] * 3600.0


    # De-redshift the spectra
    redshift = config['INFO']['REDSHIFT']
    wave /= (1 + redshift)
    print(f"Shifting spectra to rest-frame (redshift: {redshift}).")

    # Shorten spectra to the required wavelength range
    lmin = config['READ']['LMIN_TOT']
    lmax = config['READ']['LMAX_TOT']
    idx = np.where(np.logical_and(wave >= lmin, wave <= lmax))[0]
    spec = spec[idx, :]
    espec = espec[idx, :]
    wave = wave[idx]
    print(f"Shortened spectra to the range {lmin}Å - {lmax}Å.")

    # Compute the SNR per spaxel, ignoring laser guide star (LGS) region
    idx_snr = np.where(
        np.logical_and.reduce([
            wave >= config['READ']['LMIN_SNR'],
            wave <= config['READ']['LMAX_SNR'],
            np.logical_or(
                wave < 5820 / (1 + config['INFO']['REDSHIFT']),
                wave > 5970 / (1 + config['INFO']['REDSHIFT'])
            )
        ])
    )[0]
    signal = np.nanmedian(spec[idx_snr, :], axis=0)
    noise = (
        np.abs(np.nanmedian(np.sqrt(espec[idx_snr, :]), axis=0))
        if len(hdu) == 3 else espec[0, :]
    )
    snr = signal / noise
    print(f"Computed SNR in the range {lmin_snr}Å - {lmax_snr}Å, excluding LGS-affected regions.")

    # Replace NaNs in the LGS region with the median signal and noise
    idx_laser = np.where(
        np.logical_and(
            wave > 5820 / (1 + config['INFO']['REDSHIFT']),
            wave < 5970 / (1 + config['INFO']['REDSHIFT'])
        )
    )[0]
    spec[idx_laser, :] = signal
    espec[idx_laser, :] = noise
    print("Replaced LGS-affected regions (5760Å-6010Å) with median signal.")

    # Store extracted data into a dictionary
    cube = {
        'x': x, 'y': y, 'wave': wave, 'spec': spec, 'error': espec,
        'snr': snr, 'signal': signal, 'noise': noise, 'pixelsize': pixelsize
    }

    # Log and print the completion of the cube reading process
    print(f"Finished reading the MUSE cube! Total spectra: {len(cube['x'])}.")

    return cube
