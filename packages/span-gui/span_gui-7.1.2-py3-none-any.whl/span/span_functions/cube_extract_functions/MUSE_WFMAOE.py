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

# Add the parent directory to the system path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from span_functions import utilities as uti

# ======================================
# Function to load MUSE cubes. Inspired by the GIST pipeline of Bittner et. al 2019
# ======================================
def read_cube(config):
    """
    Reads a MUSE-WFMAOE data cube, processes it, and returns a structured dictionary.

    Parameters:
        config (dict): Configuration dictionary with keys:
            - INFO: Includes 'INPUT' (path to FITS file) and 'REDSHIFT' (redshift value).
            - READ: Includes 'ORIGIN', 'LMIN_TOT', 'LMAX_TOT', 'LMIN_SNR', 'LMAX_SNR'.

    Returns:
        dict: Processed data cube containing:
            - x, y: Spatial coordinates of pixels.
            - wave: Wavelength array (rest-frame).
            - spec: Spectra array.
            - error: Error spectra.
            - snr: Signal-to-noise ratio.
            - signal: Median signal per spaxel.
            - noise: Noise per spaxel.
            - pixelsize: Spatial pixel size in arcseconds.
    """

    # Read the MUSE cube
    print(f"Reading the MUSE-WFMAOE cube: {config['INFO']['INPUT']}")
    hdu = fits.open(config['INFO']['INPUT'])

    # Validate FITS structure
    if len(hdu) < 2:
        raise ValueError("The FITS file does not contain the required data extensions.")

    hdr = hdu[1].header
    data = hdu[1].data
    s = data.shape
    spec = np.reshape(data, [s[0], s[1] * s[2]])

    # Handle error spectra
    if len(hdu) >= 3:
        print("Reading the error spectra from the cube.")
        stat = hdu[2].data
        espec = np.reshape(stat, [s[0], s[1] * s[2]])
    else:
        print("No error extension found. Estimating error spectra from the flux.")
        espec = np.array([uti.noise_spec(spec[:, i]) for i in range(spec.shape[1])]).T

    # Extract wavelength and spatial information
    wave = hdr['CRVAL3'] + np.arange(s[0]) * hdr['CD3_3']
    origin = list(map(float, config['READ']['ORIGIN'].split(',')))
    xaxis = (np.arange(s[2]) - origin[0]) * hdr['CD2_2'] * 3600.0
    yaxis = (np.arange(s[1]) - origin[1]) * hdr['CD2_2'] * 3600.0
    x, y = np.meshgrid(xaxis, yaxis)
    x, y = x.ravel(), y.ravel()
    pixelsize = hdr['CD2_2'] * 3600.0


    # De-redshift the spectra
    redshift = config['INFO']['REDSHIFT']
    wave /= (1 + redshift)
    print(f"Shifting spectra to rest-frame (redshift: {redshift}).")

    # Shorten spectra to the specified wavelength range
    lmin, lmax = config['READ']['LMIN_TOT'], config['READ']['LMAX_TOT']
    idx = (wave >= lmin) & (wave <= lmax)
    wave, spec, espec = wave[idx], spec[idx, :], espec[idx, :]
    print(f"Shortened spectra to the range {lmin}Å - {lmax}Å.")

    # Compute SNR for each spaxel
    lmin_snr, lmax_snr = config['READ']['LMIN_SNR'], config['READ']['LMAX_SNR']
    idx_snr = (wave >= lmin_snr) & (wave <= lmax_snr) & (
        (wave < 5760 / (1 + config['INFO']['REDSHIFT'])) |
        (wave > 6010 / (1 + config['INFO']['REDSHIFT']))
    )
    signal = np.nanmedian(spec[idx_snr, :], axis=0)
    noise = np.nanmedian(np.sqrt(espec[idx_snr, :]), axis=0) if len(hdu) >= 3 else espec[0, :]
    snr = signal / noise
    print(f"Computed SNR in the range {lmin_snr}Å - {lmax_snr}Å, excluding LGS-affected regions.")

    # Replace laser-affected regions with median values
    idx_laser = (wave > 5760 / (1 + config['INFO']['REDSHIFT'])) & \
                (wave < 6010 / (1 + config['INFO']['REDSHIFT']))
    spec[idx_laser, :] = signal
    espec[idx_laser, :] = noise
    print("Replaced LGS-affected regions (5760Å-6010Å) with median signal.")

    # Return structured data cube
    cube = {
        'x': x, 'y': y, 'wave': wave, 'spec': spec, 'error': espec,
        'snr': snr, 'signal': signal, 'noise': noise, 'pixelsize': pixelsize
    }

    print(f"Finished reading the MUSE cube! Total spectra: {len(cube['x'])}.")
    return cube
