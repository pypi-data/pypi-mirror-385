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
#*************************** SPECTRA ANALYSIS FUNCTIONS FOR SPAN **************************
#******************************************************************************************
#******************************************************************************************


try:#Local imports
    from span_functions import spec_manipul as spman
    from span_functions import system_span as stm
    from span_functions import utilities as uti
    from span_functions import build_templates as template

except ModuleNotFoundError: #local import if executed as package
    from . import spec_manipul as spman
    from . import system_span as stm
    from . import utilities as uti
    from . import build_templates as template

#pPXF import
from ppxf.ppxf import ppxf
import ppxf.ppxf_util as util
import ppxf.sps_util as lib
from urllib import request
from pathlib import Path

import ssl
import certifi
import shutil
import urllib.request

#Python imports
import numpy as np
import math as mt
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec

from scipy import interpolate
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.constants import h,k,c
from scipy.integrate import quad
from scipy.optimize import leastsq
import scipy.stats
from scipy.interpolate import griddata
from scipy.interpolate import CubicSpline
from scipy.signal import savgol_filter
from scipy.signal import medfilt, correlate, find_peaks

from astropy.cosmology import Planck18 as cosmo

from time import perf_counter as clock
from os import path
import os
import joblib

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, Matern
from sklearn.model_selection import GridSearchCV

from scipy.signal import medfilt, correlate, find_peaks
import emcee
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import minimize
import multiprocessing as mp

from scipy import optimize, fft as spfft
from scipy.ndimage import gaussian_filter1d

import warnings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)



# 1) BLACK-BODY FITTING FUNCTION.
def blackbody_angstrom(wavelength_A, T):
    """
    Planck's law in wavelength units of Ångström (Å).
    Input: wavelength in Ångström, temperature in K
    Output: blackbody flux (arbitrary units)
    """
    wavelength_m = wavelength_A * 1e-10  # Convert Å to meters
    exponent = (h * c) / (wavelength_m * k * T)
    bb = (2.0 * h * c**2) / (wavelength_m**5 * (np.exp(exponent) - 1.0))
    return bb

def scaled_blackbody_angstrom(wavelength_A, T, scale):
    return scale * blackbody_angstrom(wavelength_A, T)

def blackbody_fit(wavelength, flux, initial_wave, final_wave, t_guess, with_plots=False, save_plot=False, result_plot_dir='', spec_name=''):

    """
    Fit a blackbody curve (in Ångström) to an input stellar spectrum.

    Parameters
    ----------
    wavelength : array_like
        Wavelength in Ångström.
    flux : array_like
        Flux (arbitrary units).
    initial_wave : float
        Lower fitting limit in Ångström.
    final_wave : float
        Upper fitting limit in Ångström.
    t_guess : float
        Initial temperature guess in K.
    with_plots : bool
        Whether to show the fit plot.
    save_plot : bool
        Whether to save the plot to file.
    result_plot_dir : str
        Directory path where to save the plot.
    spec_name : str
        Spectrum name for saving the figure.

    Returns
    -------
    temperature : int
        Fitted temperature in Kelvin.
    residuals : ndarray
        Flux residuals between data and model.
    T_err : float
        1-sigma uncertainty on the fitted temperature.
    chi2_red : float
        Reduced chi-squared of the fit.
    """

    # Select fitting range
    mask = (wavelength >= initial_wave) & (wavelength <= final_wave)
    wave_fit = wavelength[mask]
    flux_fit = flux[mask]

    if len(wave_fit) == 0:
        print("ERROR: No data in the selected wavelength range.")
        return None, None, None, None

    # Optional normalisation step (replace with your method)
    try:
        norm_flux = spman.norm_spec(wave_fit, flux_fit, np.median(wave_fit), 5., flux_fit)
    except Exception:
        norm_flux = flux_fit  # fallback: use original flux if norm fails

    try:
        # Fit blackbody (T, scale)
        p0 = [t_guess, 1.0]
        popt, pcov = curve_fit(scaled_blackbody_angstrom, wave_fit, norm_flux, p0=p0, maxfev=10000)
        T_fit, scale_fit = popt
        T_err = np.sqrt(np.diag(pcov))[0]
        bb_fit = scaled_blackbody_angstrom(wave_fit, T_fit, scale_fit)
        residuals = norm_flux - bb_fit
        temperature = int(round(T_fit))

        # chi² reduced
        dof = len(wave_fit) - 2
        chi2_red = np.sum(residuals**2) / dof if dof > 0 else np.nan

    except Exception as e:
        print(f"Blackbody fit failed: {str(e)}")
        return None, None, None, None

    # Plotting
    if with_plots or save_plot:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6))
        ax1.plot(wave_fit, norm_flux, label="Data")
        ax1.plot(wave_fit, bb_fit, 'r-', label=f"Fit (T = {temperature} ± {int(round(T_err))} K)")
        ax1.set_ylabel("Relative flux")
        ax1.set_xlabel("Wavelength (Å)")
        ax1.legend()
        ax1.set_title(f"Blackbody Fit – χ²_red = {chi2_red:.3f}")

        ax2.plot(wave_fit, residuals, 'g.', label="Residuals")
        ax2.set_xlabel("Wavelength (Å)")
        ax2.set_ylabel("Residual flux")

        plt.tight_layout()

        if with_plots:
            plt.show()
        if save_plot and result_plot_dir:
            filename = f"{result_plot_dir}/blackbody_{spec_name}.png"
            plt.savefig(filename, dpi=300)
        plt.close()

    return temperature, residuals, T_err, chi2_red



################## CROSS-CORRELATION FUNCTIONS ##################################
def preprocess_spectrum(wavelength, flux, kernel_size=51):
    flux = flux.astype(np.float64)
    continuum = medfilt(flux, kernel_size=kernel_size)
    continuum[continuum < 1e-6] = 1e-6
    norm_flux = flux / continuum
    return wavelength, norm_flux


def estimate_shift_crosscorr(wave_obs, flux_obs, wave_temp, flux_temp, grid, mode='z'):
    c = 299792.458  # speed of light in km/s
    interp_obs = interp1d(wave_obs, flux_obs, kind='linear', bounds_error=False, fill_value=0)
    cc_values = []

    for shift in grid:
        if mode == 'z':
            wave_shifted = wave_temp * (1 + shift)
        else:  # velocity in km/s
            wave_shifted = wave_temp * (1 + shift / c)

        flux_obs_interp = interp_obs(wave_shifted)
        cc = correlate(flux_obs_interp - np.mean(flux_obs_interp),
                       flux_temp - np.mean(flux_temp), mode='valid')
        cc_values.append(np.max(cc))

    cc_values = np.array(cc_values)

    # Normalise the cross-correlation curve between 0 and 1
    if np.max(cc_values) != np.min(cc_values):
        cc_values = (cc_values - np.min(cc_values)) / (np.max(cc_values) - np.min(cc_values))

    # peaks, _ = find_peaks(cc_values, prominence=np.std(cc_values))
    peaks, properties = find_peaks(cc_values, prominence=np.std(cc_values))
    if len(peaks) > 0:
        prominences = properties['prominences']
        best_peak_index = peaks[np.argmax(prominences)]

        # best_peak_index = peaks[np.argmax(cc_values[peaks])]
        best_shift = grid[best_peak_index]
    else:
        best_shift = grid[np.argmax(cc_values)]

    if len(peaks) > 0:
        peak_vals = grid[peaks]
        peak_cc = cc_values[peaks]
        top_indices = np.argsort(peak_cc)[-3:][::-1]
        print("Top candidates:")
        for idx in top_indices:
            unit = 'z' if mode == 'z' else 'km/s'
            print(f"  {unit} = {peak_vals[idx]:.5f}, correlation = {peak_cc[idx]:.5e}")


    # Estimate uncertainty based on FWHM around the main peak
    try:
        peak_idx = np.argmin(np.abs(grid - best_shift))
        peak_val = cc_values[peak_idx]
        half_max = peak_val / 2.0

        # Find left and right indices where the cc_value drops below half max
        left_idx = peak_idx
        while left_idx > 0 and cc_values[left_idx] > half_max:
            left_idx -= 1

        right_idx = peak_idx
        while right_idx < len(cc_values) - 1 and cc_values[right_idx] > half_max:
            right_idx += 1

        fwhm = grid[right_idx] - grid[left_idx]
        sigma = fwhm / 2.355 if fwhm > 0 else np.nan
    except:
        sigma = np.nan

    return best_shift, cc_values, grid, sigma


def estimate_from_template(wave_obs, flux_obs, wave_temp, flux_temp, grid, mode='z'):
    wave_obs, flux_obs = preprocess_spectrum(wave_obs, flux_obs)
    wave_temp, flux_temp = preprocess_spectrum(wave_temp, flux_temp)
    shift, cc, grid_out, sigma = estimate_shift_crosscorr(wave_obs, flux_obs, wave_temp, flux_temp, grid, mode=mode)
    return shift, cc, grid_out, sigma


def plot_cross_correlation(grid, cc_values, best_val, wave_obs, flux_obs, wave_temp, flux_temp, shift, save_plot, spec_name, result_plot_dir, mode='z'):
   # Normalize template over the wavelength range of the observed spectrum if necessary
    min_obs, max_obs = wave_obs.min(), wave_obs.max()
    mask_temp_in_obs = (wave_temp >= min_obs) & (wave_temp <= max_obs)
    if np.sum(mask_temp_in_obs) > 10:  # Require enough points to avoid artefacts
        flux_temp = flux_temp / np.nanmax(np.abs(flux_temp[mask_temp_in_obs]))
    else:
        flux_temp = flux_temp / np.nanmax(np.abs(flux_temp))
    if mode == 'z':
        wave_temp_shifted = wave_temp * (1 + shift)
    else:
        wave_temp_shifted = wave_temp * (1 + shift / c)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=False, gridspec_kw={'height_ratios': [1, 1]})

    # Upper panel: cross-correlation function
    ax1.plot(grid, cc_values, label='Cross-correlation')
    ax1.axvline(best_val, color='red', linestyle='--', label=f"Best {mode} = {best_val:.5f}")
    ax1.set_xlabel('Redshift z' if mode == 'z' else 'Radial Velocity (km/s)')
    ax1.set_ylabel('Correlation strength')
    ax1.set_title('Cross-Correlation and Spectrum Comparison')
    ax1.legend()
    ax1.grid(True)

    # Lower panel: observed vs shifted template
    ax2.plot(wave_obs, flux_obs / np.median(flux_obs), label='Observed', alpha=0.7, color='blue')
    ax2.plot(wave_temp_shifted, flux_temp, label='Template (shifted)', alpha=0.7, color='orange')
    ax2.set_xlabel('Wavelength (Å)')
    ax2.set_ylabel('Normalized Flux')
    ax2.set_xlim(left=np.min(wave_obs))
    ax2.set_xlim(right=np.max(wave_obs))
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    if save_plot:
        plt.savefig(result_plot_dir + '/'+ 'Xcorr_' + spec_name + '_' + '.png', format='png', dpi=300)
        plt.close()
    else:
        plt.show()
        plt.close()



#*************************************************************************************************
# 5) Velocity dispersion measurement
def measure_sigma_simple(wave_obs_A, flux_obs, spec_test_template, lambda_units_template, band_A, spec_res_mode, spec_res_value, tpl_res_mode, tpl_res_value, err_obs=None, mask_obs=None, poly_degree: int = 4, sigma_bounds=(5.0, 450.0), estimate_delta_v: bool = True, bootstrap: int = 100):
    
    """Return (sigma_kms, sigma_err, dv_kms, chi2, dof, velscale, upper_limit_flag).

    Notes
    -----
    * All wavelengths are Å; input spectra are linear in λ. The routine log-rebins internally.
    * If the template is broader than the observed spectrum (instrumental), σ is an upper limit.
    * Errors, if provided, are used as weights (1/err^2). Mask, if provided, is boolean (True=keep).
    """

    _C = 299_792.458                 # km/s
    _FWHM_TO_SIG = 1.0 / 2.354820045 # FWHM → σ for Gaussian

    # ---- helpers (kept local for a single-file drop-in) ---------------------
    def _slice_band(w, f, band, e=None, m=None):
        wmin, wmax = float(band[0]), float(band[1])
        sel = (w >= wmin) & (w <= wmax)
        if m is not None:
            if m.shape != w.shape:
                raise ValueError("mask shape must match wavelength array")
            sel &= m.astype(bool)
        w, f = w[sel], f[sel]
        e = None if e is None else e[sel]
        ok = np.isfinite(w) & np.isfinite(f)
        if e is not None:
            ok &= np.isfinite(e)
        return w[ok], f[ok], (None if e is None else e[ok])

    def _log_rebin(w_A, f):
        # Constant velocity scale from median linear step
        dlam = np.median(np.diff(w_A))
        if dlam <= 0:
            raise ValueError("wavelength must be strictly increasing")
        dln = np.log(w_A[0] + dlam) - np.log(w_A[0])
        velscale = _C * dln
        ln0, ln1 = np.log(w_A[0]), np.log(w_A[-1])
        n = int(np.floor((ln1 - ln0) / dln)) + 1
        loglam = ln0 + dln * np.arange(n)
        lam_log = np.exp(loglam)
        flog = np.interp(lam_log, w_A, f, left=np.nan, right=np.nan)
        ok = np.isfinite(flog)
        return loglam[ok], flog[ok], velscale

    def _res_to_sigma_kms(mode, val, lam_A):
        mode = str(mode).upper()
        if mode == 'FWHM_A':
            fwhm_A = float(val)
            if fwhm_A <= 0: raise ValueError('FWHM_A must be > 0')
            sigma_A = fwhm_A * _FWHM_TO_SIG
            return (sigma_A / lam_A) * _C
        if mode == 'R':
            R = float(val)
            if R <= 0: raise ValueError('R must be > 0')
            fwhm_A = lam_A / R
            sigma_A = fwhm_A * _FWHM_TO_SIG
            return (sigma_A / lam_A) * _C
        raise ValueError("spec/tpl mode must be 'FWHM_A' or 'R'")

    def _match_template_resolution(tpl_log, vscale, sig_spec, sig_tpl):
        # Broaden template to match instrumental resolution of the spectrum
        if sig_tpl >= sig_spec - 1e-6:
            return tpl_log.copy(), True  # cannot deconvolve → upper limit
        sig_match = np.sqrt(max(0.0, sig_spec**2 - sig_tpl**2))
        sig_pix = sig_match / vscale
        return gaussian_filter1d(tpl_log, sigma=sig_pix, mode='nearest'), False

    def _shift_log(flux_log, dv_kms, vscale):
        if abs(dv_kms) < 1e-9: return flux_log
        n = flux_log.size
        shift_pix = dv_kms / vscale
        freqs = spfft.fftfreq(n)
        phase = np.exp(2j * np.pi * freqs * shift_pix)
        return np.real(spfft.ifft(spfft.fft(flux_log) * phase))

    def _legendre_X(x, deg):
        if deg <= 0:
            return np.ones((x.size, 1))
        xs = 2*(x - x.min())/(x.max()-x.min()) - 1
        P0 = np.ones_like(xs); P1 = xs
        cols = [P0, P1]
        for n in range(2, deg+1):
            Pn = ((2*n-1)*xs*cols[-1] - (n-1)*cols[-2]) / n
            cols.append(Pn)
        return np.vstack(cols[:deg+1]).T

    def _chi2_sigma(sig_kms, dv_kms, tpl_matched, obs_log, loglam, vscale, err_log, deg, scale):
        # Apply kinematic broadening
        sig_pix = max(0.0, float(sig_kms)) / vscale
        model = gaussian_filter1d(tpl_matched, sigma=sig_pix, mode='nearest')
        if dv_kms:
            model = _shift_log(model, dv_kms, velscale)
        # Multiplicative polynomial
        X = _legendre_X(loglam, deg)
        A = X * model[:, None]
        # Rescale data and errors for conditioning
        y = obs_log / scale
        if err_log is not None:
            e = err_log / scale
            w = 1.0 / np.clip(e, 1e-10, np.inf)
            Aw, yw = A * w[:, None], y * w
        else:
            Aw, yw = A, y
        # Linear solve for polynomial coefficients
        coeffs, *_ = np.linalg.lstsq(Aw, yw, rcond=None)
        fit = A @ coeffs
        resid = y - fit
        if err_log is not None:
            chi2 = float(np.sum((resid / np.clip(e, 1e-10, np.inf))**2))
        else:
            chi2 = float(np.sum(resid**2))
        dof = y.size - coeffs.size - 1
        return chi2, max(dof, 1)

    def _xcorr_dv(y, t, vscale, dv_win=450.0):
        a = y - np.nanmedian(y); b = t - np.nanmedian(t)
        xcorr = np.real(spfft.ifft(spfft.fft(a) * np.conj(spfft.fft(b))))
        i = int(np.argmax(xcorr)); n = a.size
        if i > n//2: i -= n
        dv = i * vscale
        return float(np.clip(dv, -dv_win, dv_win))

    # ---- prepare inputs ------------------------------------------------------
    wave_obs_A = np.asarray(wave_obs_A, float)
    flux_obs   = np.asarray(flux_obs,   float)
    
    wave_tpl_A, flux_tpl, step_template, name = stm.read_spec(spec_test_template, lambda_units_template)
    err_obs    = None if err_obs is None else np.asarray(err_obs, float)
    mask_obs   = None if mask_obs is None else np.asarray(mask_obs, bool)

    # Normalize
    flux_obs = flux_obs/np.median(flux_obs)
    flux_tpl = flux_tpl/np.median(flux_tpl)
    
    # 1) band cut + mask
    w_obs, f_obs, e_obs = _slice_band(wave_obs_A, flux_obs, band_A, e=err_obs, m=mask_obs)
    w_tpl, f_tpl, _ = _slice_band(wave_tpl_A, flux_tpl, band_A)

    # 2) log-rebin both, resample template onto obs log grid
    loglam_obs, flog_obs, velscale = _log_rebin(w_obs, f_obs)
    loglam_tpl, flog_tpl, _ = _log_rebin(w_tpl, f_tpl)
    lam_log_obs = np.exp(loglam_obs)
    lam_log_tpl = np.exp(loglam_tpl)
    flog_tpl_on_obs = np.interp(lam_log_obs, lam_log_tpl, flog_tpl, left=np.nan, right=np.nan)

    if e_obs is not None:
        _, err_log, _ = _log_rebin(w_obs, e_obs)
    else:
        err_log = None

    ok = np.isfinite(flog_obs) & np.isfinite(flog_tpl_on_obs)
    if err_log is not None: ok &= np.isfinite(err_log)
    loglam_obs = loglam_obs[ok]
    flog_obs   = flog_obs[ok]
    flog_tpl_on_obs = flog_tpl_on_obs[ok]
    if err_log is not None: err_log = err_log[ok]
    if flog_obs.size < 20:
        raise ValueError('Insufficient overlap between spectrum and template in the band')

    # Robust scale for conditioning (kept >0 and finite)
    scale = np.nanmedian(np.abs(flog_obs))
    if not np.isfinite(scale) or scale <= 0:
        scale = 1.0

    # 3) instrumental resolutions (convert to σ_kms at band centre)
    lam_c = 0.5*(band_A[0] + band_A[1])
    sig_spec = _res_to_sigma_kms(spec_res_mode, spec_res_value, lam_c)
    sig_tpl  = _res_to_sigma_kms(tpl_res_mode,  tpl_res_value,  lam_c)

    # 4) match template resolution to spectrum
    tpl_matched, upper_limit = _match_template_resolution(flog_tpl_on_obs, velscale, sig_spec, sig_tpl)

    # Print a simple terminal message if template is not sharper than the spectrum
    if upper_limit:
        print("WARNING: Template instrumental resolution ≥ spectrum instrumental resolution. "
        "Kinematic sigma will act as an UPPER LIMIT and may be biased high. Calculation continues.")

    # 5) coarse Δv
    dv0 = _xcorr_dv(flog_obs, tpl_matched, velscale) if estimate_delta_v else 0.0

    # 6) optimise σ (bounded 1D)
    def objective(s_kms: float) -> float:
        chi2, _ = _chi2_sigma(s_kms, dv0, tpl_matched, flog_obs, loglam_obs, velscale, err_log, poly_degree, scale)
        return chi2

    res = optimize.minimize_scalar(objective, bounds=sigma_bounds, method='bounded', options={'xatol': 1e-2})
    sigma_best = float(res.x)
    chi2_best, dof = _chi2_sigma(sigma_best, dv0, tpl_matched, flog_obs, loglam_obs, velscale, err_log, poly_degree, scale)

    # 7) error from curvature + optional bootstrap
    def chi2_at(s):
        return _chi2_sigma(s, dv0, tpl_matched, flog_obs, loglam_obs, velscale, err_log, poly_degree, scale)[0]

    eps = max(0.5, 0.01*sigma_best)
    s_vec = np.array([sigma_best - eps, sigma_best, sigma_best + eps])
    c_vec = np.array([chi2_at(s_vec[0]), chi2_at(s_vec[1]), chi2_at(s_vec[2])])
    a = ((c_vec[0] - 2*c_vec[1] + c_vec[2]) / (eps**2)) / 2.0
    sigma_err = float(np.sqrt(1.0/a)) if a > 0 else None

    if bootstrap and bootstrap > 0:
        rng = np.random.default_rng(42)
        # Build best-fit model once (unscaled here to keep returned arrays on original scale)
        sig_pix_b = sigma_best / velscale
        model_b = gaussian_filter1d(tpl_matched, sigma=sig_pix_b, mode='nearest')
        if estimate_delta_v:
            model_b = _shift_log(model_b, dv0, velscale)
        Xb = _legendre_X(loglam_obs, poly_degree)
        Ab = Xb * model_b[:, None]
        if err_log is not None:
            w = 1.0 / np.clip(err_log, 1e-10, np.inf)
            Abw, yw = Ab * w[:, None], flog_obs * w
        else:
            Abw, yw = Ab, flog_obs
        coeffs_b, *_ = np.linalg.lstsq(Abw, yw, rcond=None)
        fit_b = Ab @ coeffs_b
        resid = flog_obs - fit_b
        boots = []
        for _ in range(int(bootstrap)):
            yb = fit_b + rng.choice(resid, size=resid.size, replace=True)
            def obj_b(s):
                chi2, _ = _chi2_sigma(s, dv0, tpl_matched, yb, loglam_obs, velscale, err_log, poly_degree, scale)
                return chi2
            rb = optimize.minimize_scalar(obj_b, bounds=sigma_bounds, method='bounded', options={'xatol': 1e-1})
            boots.append(float(rb.x))
        if len(boots):
            sigma_err = float(np.nanstd(boots, ddof=1))

    # --- build best-fit broadened template and final model on the log grid (unscaled) ---
    sig_pix = sigma_best / velscale
    tpl_broadened = gaussian_filter1d(tpl_matched, sigma=sig_pix, mode='nearest')
    if estimate_delta_v:
        tpl_broadened = _shift_log(tpl_broadened, dv0, velscale)
    X = _legendre_X(loglam_obs, poly_degree)
    A = X * tpl_broadened[:, None]
    if err_log is not None:
        w = 1.0 / np.clip(err_log, 1e-10, np.inf)
        Aw, yw = A * w[:, None], flog_obs * w
    else:
        Aw, yw = A, flog_obs
    coeffs, *_ = np.linalg.lstsq(Aw, yw, rcond=None)
    fit_model = A @ coeffs

    lam_band_A = np.exp(loglam_obs)

    print (f'Velocity dispersion = {sigma_best}')

    return sigma_best, sigma_err, dv0 if estimate_delta_v else 0.0, chi2_best, dof, velscale, bool(upper_limit), lam_band_A, flog_obs, tpl_broadened, fit_model


#*****************************************************************************************************
# 6) Single line fitting
def line_fitting (wavelength, flux, wave_interval, guess_param):

    """
    This function fits an emission or absorption line with a convolution of
    a gussian function with a line, in order to account for the continuum
    slope.
    Input: wavelength and flux arrays of the spectrum, array containing the
           wavelength range of the spectral that contains the line to fit ([min_wave, max_wave])
            array containing the initial guess for the fit [y_offset, line_wave, relative_intensity,
            sigma_gauss, slope_continuum_line, intercept_continuum_line].
    Output: wavelength and normalised flux arrays of the spectrum within the fitted band,
            array of the model fit, array of the best fit parameters found.

    """

    step = wavelength[1]-wavelength[0]
    wave1 = min(wave_interval)
    wave2 = max(wave_interval)

    #isolating the region of interest
    line_wave = wavelength[(wavelength >= wave1) & (wavelength <= wave2)]
    line_flux_spec = flux[(wavelength >= wave1) & (wavelength <= wave2)]

    #normalize the spectrum
    wave_norm = line_wave[10] # guessing for now. fix it later
    epsilon_norm = step*10
    line_flux_spec_norm = spman.norm_spec(line_wave, line_flux_spec, wave_norm, epsilon_norm, line_flux_spec)

    #fitting to the spectra
    popt_spec, pconv_spec = curve_fit(uti.Gauss_slope, line_wave, line_flux_spec_norm, p0=guess_param)

    fit = uti.Gauss_slope(line_wave, *popt_spec)
    return line_wave, line_flux_spec_norm, fit, popt_spec


#*****************************************************************************************************
# 7) fitting threee gaussians to the CaT lines
def cat_fitting (wavelength, flux):

    """
    This function fits the Calcium Trilet (CaT) lines in the NIR with
    a convolution of three gussians with a line, in order to account for the continuum
    slope.
    Input: wavelength and flux arrays of the spectrum.
    Output: wavelength and normalised flux arrays of the spectrum within the fitted band,
            array of the model fit, array of the best fit parameters found.

    """

    step = wavelength[1]-wavelength[0]

    wave1 = 8440
    wave2 = 8720

    #extract the line flux and wavelength arrays
    line_wave = wavelength[(wavelength >= wave1) & (wavelength <= wave2)]
    line_flux_spec = flux[(wavelength >= wave1) & (wavelength <= wave2)]

    #normalize the spectrum
    wave_norm = line_wave[10] # guessing for now. fix it later
    epsilon_norm = step*10
    line_flux_spec_norm = spman.norm_spec(line_wave, line_flux_spec, wave_norm, epsilon_norm, line_flux_spec)

    #initial guesses
    y0 = 1
    x0 = 8500
    a = -0.8
    sigma = 0.1
    m = 0.1
    c = 1

    guess = [y0,x0,a,sigma,m,c]
    for i in range(3):
        if i == 0:
            guess = guess
        if i == 1:
            guess+= [y0,8540,-0.6, 0.2, m, c]
        if i == 2:
            guess+= [y0,8660,-0.6, 0.2, m, c]

    #fitting to the spectra
    popt_spec, pconv_spec = curve_fit(uti.multiple_gauss, line_wave, line_flux_spec_norm, p0=guess)
    fit = uti.multiple_gauss(line_wave, *popt_spec)

    return line_wave, line_flux_spec_norm, fit, popt_spec


#*****************************************************************************************************
# 8) kinematics with ppxf and EMILES SSP models
def ppxf_kinematics(wavelength, flux, wave1, wave2, FWHM_gal, is_resolution_gal_constant, R, muse_resolution, z, sigma_guess, stellar_library, additive_degree, multiplicative_degree, kin_moments, kin_noise, kin_fit_gas, kin_fit_stars, kin_best_noise, with_errors_kin, custom_lib, custom_lib_folder, custom_lib_suffix, generic_lib, generic_lib_folder, FWHM_tem_generic, dust_correction_gas, dust_correction_stars, tied_balmer, two_stellar_components, age_model1, met_model1, age_model2, met_model2, vel_guess1, sigma_guess1, vel_guess2, sigma_guess2, mask_lines, have_user_mask, mask_ranges, mc_sim, fixed_moments, mode, stars_templates=None, lam_temp = None, velscale_cached = None, FWHM_gal_cached = None, two_components_cached = None, kinematics_fixed = None, bias = None):

    """
     This function uses the pPXF algorith to retrieve the n kinematics moments
     by fitting SPS and gas templates to the selected wavelength
     range of the selected spectrum.
     Input: wavelength and flux arrays of the spectrum, array containing the
            wavelength range to fit ([min_wave, max_wave]), delta lambda resolution
            of the spectrum in the wavelength range considered (FWHM value, in Angstrom),
            bool constant (True) or not (False) FWHM resolution, resolving power (R)
            redshift guess, velocity dispersion guess, stellar library to use
            additive degree polynomial to use for the fit, kin moments to fit (2-6)
            constant noise estimation of the spectrum, bool with (True) or without (False)
            gas component to include, bool auto noise estimation (True) or not (False),
            bool uncertainties estimation with MonteCarlo simulations.
     Output: array containing the kinematics moments fitted, array containing the formal errors
             array of the best fit template flux, wavelength array,
             array of the model fit, array of the best fit parameters found, components found,
             S/N of the spectrum measured in the fit range, array of uncertainties in the
             kinematics moments (zero if not estimated).
    """

    ppxf_default_lib = ["emiles", "fsps", "galaxev"]
    wave1 = wave1
    wave2 = wave2
    galaxy = flux

    # Definitions in case everything goes bad, to prevent the crash
    gas_flux = 0
    gas_flux_err = 0
    bestfit_gas_flux = 0
    emission_corrected_flux = 0
    gas_without_continuum = 0
    gas_names = None
    gas_component = 0

    line_wave = wavelength[(wavelength >= wave1) & (wavelength <= wave2)]
    line_flux_spec = galaxy[(wavelength >= wave1) & (wavelength <= wave2)]

    #updating the variables
    galaxy = line_flux_spec
    wave = line_wave

    # In case I have High or low redshift
    redshift = z #placeholder to not loose the real redshift
    high_z = 0.01
    lam_range_gal = np.array([np.min(wave), np.max(wave)])/(1 + z) #de-redshift
    if z > high_z:
        FWHM_gal /= 1 + z
        redshift_0 = redshift
    else:
        redshift_0 = redshift
    z = 0

    print('Rebinning to log')
    galaxy, ln_lam1, velscale = util.log_rebin(lam_range_gal, galaxy)

    #normalize to unity but store the original galaxy flux also for measurement of real gas flux, if any
    galaxy_median_flux = np.median(galaxy)
    galaxy = galaxy/galaxy_median_flux

    wave = np.exp(ln_lam1) #converting the ln wavelength to wavelength, but keeping the ln sampling
    noise = np.full_like(galaxy, kin_noise) #noise per pixel

    c = 299792.458

    lam_range_temp = [lam_range_gal[0]/1.02, lam_range_gal[1]*1.02]

    use_cached_templates = False
    if stars_templates is not None and velscale_cached is not None: #and not two_stellar_components:
        if np.isclose(velscale, velscale_cached, rtol=1e-5): #using the same precision of pPXF to compare the different velscales (1e-5)
            use_cached_templates = True

            print("Using cached stellar templates")
            lam_temp = np.array(lam_temp)
            FWHM_gal = FWHM_gal_cached
            if two_stellar_components:
                component = two_components_cached
            pass
        else:
            print("Cached templates invalid (velscale mismatch), will reload.")
            use_cached_templates = False

    if not use_cached_templates:
        print("Loading stellar templates...")

        sps_name = stellar_library

        # Read SPS models file
        if not custom_lib and not generic_lib:

            #requesting the pPXF preloaded templates, if needed
            if stellar_library in ppxf_default_lib:
                print(stellar_library)
                ppxf_dir = Path(util.__file__).parent
                basename = f"spectra_{sps_name}_9.0.npz"
                filename = ppxf_dir / 'sps_models' / basename
                if not filename.is_file():
                    url = "https://raw.githubusercontent.com/micappe/ppxf_data/main/" + basename
                    download_file(url, filename)

            #loading the templates and convolve them with the FWHM of the galaxy spectrum
            if is_resolution_gal_constant:
                print('Convolving to fixed FWHM resolution')
                if stellar_library == 'xshooter':
                    print(stellar_library)
                    pathname_xsl = os.path.join(BASE_DIR, "spectralTemplates", "xsl_mod", "*XSL_SSP*.fits" )
                    sps = template.xshooter(pathname_xsl, velscale, FWHM_gal, wave_range=lam_range_temp)
                else:
                    sps = lib.sps_lib(filename, velscale, FWHM_gal, lam_range=lam_range_temp)

            elif not is_resolution_gal_constant and not muse_resolution:
                print('Convolving to fixed R resolving power')
                FWHM_gal = wave/R
                if stellar_library == 'xshooter':
                    print(stellar_library)
                    pathname_xsl = os.path.join(BASE_DIR, "spectralTemplates", "xsl_mod", "*XSL_SSP*.fits" )
                    sps = template.xshooter(pathname_xsl, velscale, FWHM_gal, wave_range=lam_range_temp, R = R)
                else:
                    FWHM_gal = {"lam": wave, "fwhm": FWHM_gal}
                    sps = lib.sps_lib(filename, velscale, FWHM_gal, lam_range=lam_range_temp)
                    #extracting the FWHM gal in numpy array, needed for the gas template building
                    FWHM_gal = FWHM_gal["fwhm"]


            elif muse_resolution:
                print('Convolving to MUSE resolution')
                # Muse LSF polynomial equation 8 from Bacon et al., 2017
                FWHM_gal = 5.866e-8*wave**2-9.187e-4*wave+6.040
                if stellar_library == 'xshooter':
                    print(stellar_library)
                    pathname_xsl = os.path.join(BASE_DIR, "spectralTemplates", "xsl_mod", "*XSL_SSP*.fits" )
                    sps = template.xshooter(pathname_xsl, velscale, FWHM_gal, wave_range=lam_range_temp)
                else:
                    # FWHM_gal = 5.866e-8*wave**2-9.187e-4*wave+6.040
                    FWHM_gal = {"lam": wave, "fwhm": FWHM_gal}
                    sps = lib.sps_lib(filename, velscale, FWHM_gal, lam_range=lam_range_temp)
                    #extracting the FWHM gal in numpy array, needed for the gas template building
                    FWHM_gal = FWHM_gal["fwhm"]


            stars_templates = sps.templates.reshape(sps.templates.shape[0], -1)


        if custom_lib:
            print ('Using custom (E)MILES templates')
            pathname = custom_lib_folder + '/' + custom_lib_suffix

            if is_resolution_gal_constant:
                print('Convolving to fixed FWHM resolution')
                sps = template.miles(pathname, velscale, FWHM_gal, wave_range=lam_range_temp)

            elif not is_resolution_gal_constant and not muse_resolution:
                print('Convolving to fixed R resolving power')
                FWHM_gal = wave/R
                sps = template.miles(pathname, velscale, FWHM_gal, wave_range=lam_range_temp, R = R)
            elif muse_resolution:
                print('Convolving to MUSE resolution')
                FWHM_gal = 5.866e-8*wave**2-9.187e-4*wave+6.040
                sps = template.miles(pathname, velscale, FWHM_gal, wave_range=lam_range_temp)


            #reshaping the templates
            stars_templates = sps.templates.reshape(sps.templates.shape[0], -1)

        if generic_lib:
            print ('Using generic templates')
            pathname = generic_lib_folder + '/*.fits'

            if is_resolution_gal_constant:
                print('Convolving to fixed FWHM resolution')
                sps = template.KinematicTemplates(pathname, velscale, FWHM_gal, wave_range=lam_range_temp, FWHM_tem = FWHM_tem_generic)

            elif not is_resolution_gal_constant and not muse_resolution:
                print('Convolving to fixed R resolving power')
                FWHM_gal = wave/R
                sps = template.KinematicTemplates(pathname, velscale, FWHM_gal, wave_range=lam_range_temp, R = R, FWHM_tem = FWHM_tem_generic)
            elif muse_resolution:
                print('Convolving to MUSE resolution')
                FWHM_gal = 5.866e-8*wave**2-9.187e-4*wave+6.040
                sps = template.KinematicTemplates(pathname, velscale, FWHM_gal, wave_range=lam_range_temp, FWHM_tem = FWHM_tem_generic)


            #reshaping the templates
            stars_templates = sps.templates.reshape(sps.templates.shape[0], -1)

        lam_temp=sps.lam_temp
        FWHM_gal_cached = FWHM_gal


        if two_stellar_components:
            if custom_lib or stellar_library == 'xshooter':
                #retrieving age and metallicity grids
                age_grid = sps.get_full_age_grid()
                met_grid = sps.get_full_metal_grid()
                age_bins = age_grid[:,0]
                age_values = age_bins[::-1]
                met_bins = met_grid[0,:]
                met_values = met_bins
            else:
                #using the wrapper to pPXF
                sps_data_ppxf = template.SPSLibWrapper(filename, velscale, fwhm_gal= None, lam_range=lam_range_temp)
                age_values = sps_data_ppxf.get_age_grid()[::-1]
                met_values = sps_data_ppxf.get_metal_grid()[::-1]

            # Old and young
            if mode == 'old_young':
                print ('Using old and young components')
                blocks, stars_templates, component = build_stellar_blocks_gui(sps.templates, age_values, met_values, mode="old_young", n_components=2)
            if mode == 'metal_rich_poor':
                # Metal rich and metal poor
                print ('Using metal rich and metal poor components')
                blocks, stars_templates, component = build_stellar_blocks_gui(sps.templates, age_values, met_values, mode="metal_rich_poor", n_components=2)
            
            if mode == 'all':
                print ('Using all templates')
                blocks, stars_templates, component = build_stellar_blocks_gui(sps.templates, age_values, met_values, mode="all", n_components=2)
                
            if mode == 'two_templates':
                print ('Two templates with fixed age and metallicity')
                model1, i_closest1, j_closest1 = pick_ssp_template(age_model1, met_model1, age_values, met_values, sps.templates)
                model2, i_closest2, j_closest2 = pick_ssp_template(age_model2, met_model2, age_values, met_values, sps.templates)
                model1 /= np.median(model1)
                model2 /= np.median(model2)
                stars_templates = np.column_stack([model1, model2, model1, model2])
                component = [0, 0, 1, 1]
                component = np.asarray(component, dtype=int)
                
            two_components_cached = component

    #Detecting when the emission mask is needed
    if kin_fit_stars and mask_lines:
        use_emission_mask = True
    else:
        use_emission_mask = False

    #loading or not the mask emission, if activated and only for stars fitting
    goodpix = build_goodpixels_with_mask(
        ln_lam1, lam_range_temp, z, redshift_0, mask_ranges=mask_ranges, user_mask = have_user_mask,
        use_emission_mask=use_emission_mask)

    error_kinematics_mc = 0


###################### Only stellar ##################
    if kin_fit_stars:
        print ('Fitting only the stellar component')

        try:
            
            if two_stellar_components: # two stellar components
                if dust_correction_stars:
                    print('WARNING: skipping star dust correction!')
                    dust_correction_stars = False
                    
                if mode != 'two_templates':
                    comp_labels = np.unique(component)
                    n_comp = comp_labels.size
                    vel_sys = c * np.log(1 + z)
                    start = []
                    if n_comp >= 1:
                        start.append([vel_sys + vel_guess1, sigma_guess1])
                    if n_comp >= 2:
                        start.append([vel_sys + vel_guess2, sigma_guess2])
                    moments = [kin_moments] * n_comp
                    templates = stars_templates
                    global_search = True
                else: # two extracted templates
                    templates = stars_templates
                    vel = c*np.log(1 + z)
                    vel1 = vel + vel_guess1
                    vel2 = vel + vel_guess2
                    start = [[vel1, sigma_guess1], [vel2, sigma_guess2]]
                    component = [0, 0, 1, 1]
                    n_temps = stars_templates.shape[1]
                    moments = [kin_moments, kin_moments]
                    global_search = True #in case of two stellar components, this keyword should be set to true, according to pPXF manual
            else: # Single component
                templates = stars_templates
                vel = c*np.log(1 + z)
                start = [vel, sigma_guess]
                n_temps = stars_templates.shape[1]
                component = [0]*n_temps
                gas_component = np.array(component) > 0
                moments = kin_moments
                global_search = False # No need for single component

            t = clock()

            #define the dust components, if activated
            if dust_correction_stars or dust_correction_gas:
                if (dust_correction_stars and dust_correction_gas):
                    print('You are fitting only stars, discarding the dust for gas')
                    dust_gas = None
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]
                if not dust_correction_stars and dust_correction_gas:
                    print('You do not have gas to correct for dust. No dust correction applied')
                    dust = None
                if dust_correction_stars and not dust_correction_gas:
                    print('Considering dust for the stellar component')
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]

            else:
                dust = None

            #routine to find automatically the best noise for ppxf
            if kin_best_noise:
                print('')
                print ('Running ppxf in silent mode to find the best noise level...')

                pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, degree= additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=lam_temp, quiet = True, bias =0, dust = dust, component = component, global_search = global_search) #no penalty for estimation of the noise

                nonregul_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                best_noise = np.full_like(galaxy, noise*mt.sqrt(pp.chi2))
                noise = best_noise

                print ('Best noise: ', round(best_noise[0],5))
                print ('Now fitting with this noise estimation')
                print ('')


            #do the fit!
            pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                moments=moments, plot = True, degree= additive_degree, mdegree=multiplicative_degree,
                lam=wave, lam_temp=lam_temp, dust = dust, component = component, global_search = global_search, bias = bias)
                
            if not two_stellar_components:
                errors = pp.error*np.sqrt(pp.chi2)  # Assume the fit is good chi2/DOF=1
                stellar_components = None # I do not have two stellar components
            else:
                errors = [array * np.sqrt(pp.chi2) for array in pp.error]
                
                # Generating the two bestfit templates separated
                spec_comp1, spec_comp2 = extract_stellar_components_from_matrix(pp=pp, component=component, stars_templates=stars_templates, gas_templates=None,         
                additive_degree=additive_degree)
                stellar_components = spec_comp1, spec_comp2

            # errors = pp.error*np.sqrt(pp.chi2)  # Assume the fit is good chi2/DOF=1
            redshift_fit = (1 + redshift_0)*np.exp(pp.sol[0]/c) - 1  # eq. (5c) C22
            redshift_err = (1 + redshift_fit)*errors[0]/c            # eq. (5d) C22

            print("Formal errors in stellar component:")
            print("     dV    dsigma   dh3      dh4")
            if not two_stellar_components:
                print("".join("%8.2g" % f for f in errors))
                print('Elapsed time in pPXF: %.2f s' % (clock() - t))
                try:
                    prec = int(1 - np.floor(np.log10(redshift_err)))  # two digits of uncertainty
                except Exception:
                    prec = 7
                print(f"Best-fitting redshift z = {redshift_fit:#.{prec}f} "
                    f"+/- {redshift_err:#.{prec}f}")
            else:
                stellar_uncertainties = errors[0]
                print("".join("%8.2g" % f for f in stellar_uncertainties))
                print('Elapsed time in pPXF: %.2f s' % (clock() - t))
                if redshift_err[0] == 0 or not np.isfinite(redshift_err[0]):
                    prec = 7
                    print(f"Best-fitting redshift z = {redshift_fit[0]:#.{prec}f} "
                    f"+/- {redshift_err[0]:#.{prec}f}")
                else:
                    prec = int(1 - np.floor(np.log10(redshift_err[0])))  # two digits of uncertainty
                    print(f"Best-fitting redshift z = {redshift_fit[0]:#.{prec}f} "
                        f"+/- {redshift_err[0]:#.{prec}f}")


            #output kinematics parameters
            kinematics = pp.sol
            error_kinematics = errors

            #output fit_model
            bestfit_flux = pp.bestfit
            bestfit_wavelength = wave

            #adding the mock h3, h4, h5, h6 column to the kinematic array in order to not change the main code
            all_moments = 6
            if kin_moments < all_moments:
                missing_moments = all_moments - kin_moments
                moments_to_add = np.zeros(missing_moments)

                if not two_stellar_components:
                    kinematics = np.hstack((kinematics, moments_to_add))
                    error_kinematics = np.hstack((error_kinematics, moments_to_add))
                else:
                    components = np.max(component)
                    for k in range (components+1):

                        kinematics[k] = np.hstack((kinematics[k], moments_to_add))
                        error_kinematics[k] = np.hstack((error_kinematics[k], moments_to_add))


            residual = galaxy - bestfit_flux
            snr = 1/np.std(residual)
            print ('S/N of the spectrum:', round(snr))


        # Uncertainties estimation with MonteCarlo simulations
            if with_errors_kin: #calculating the errors of age and metallicity with MonteCarlo simulations
                print('Calculating the uncertainties with MonteCarlo simulations')

                n_sim = mc_sim #how many simulated templates I want to create. Watch out for the computation time!

                #if fitting only one stellar component
                if not two_stellar_components:
                    #initialising the arrays containing the n_sim simulated kinematics
                    vel_dist = []
                    sigma_dist = []
                    h3_dist = []
                    h4_dist = []
                    h5_dist = []
                    h6_dist = []

                    for i in range(n_sim):
                        noisy_template = spman.add_noise(bestfit_wavelength, bestfit_flux, snr)

                        #no regularization!
                        pp = ppxf(templates, noisy_template, noise, velscale, start, goodpixels = goodpix,
                        moments=kin_moments, degree=additive_degree, mdegree=multiplicative_degree,
                        lam=bestfit_wavelength, lam_temp=lam_temp,
                        quiet = True, dust = dust, component = component, global_search = global_search, bias = bias)

                        kinematics_mc = pp.sol

                        vel_mc = int(kinematics_mc[0])
                        sigma_mc = int(kinematics_mc[1])
                        vel_dist.append(vel_mc)
                        sigma_dist.append(sigma_mc)

                        if kin_moments > 2:
                            h3_mc = round(kinematics_mc[2],3)
                            h3_dist.append(h3_mc)

                        if kin_moments > 3:
                            h4_mc = round(kinematics_mc[3],3)
                            h4_dist.append(h4_mc)

                        if kin_moments > 4:
                            h5_mc = round(kinematics_mc[4],3)
                            h5_dist.append(h5_mc)

                        if kin_moments > 5:
                            h6_mc = round(kinematics_mc[5],3)
                            h6_dist.append(h6_mc)


                    error_vel = np.std(vel_dist)
                    error_sigma = np.std(sigma_dist)
                    error_h3 = 0
                    error_h4 = 0
                    error_h5 = 0
                    error_h6 = 0

                    if kin_moments > 1:
                        error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))

                    if kin_moments > 2:
                        error_h3 = np.std(h3_dist)
                        error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))

                    if kin_moments > 3:
                        error_h4 = np.std(h4_dist)
                        error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))
                    if kin_moments > 4:
                        error_h5 = np.std(h5_dist)
                        error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))
                    if kin_moments > 5:
                        error_h6 = np.std(h6_dist)
                        error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))

                    print('Uncertainties with MonteCarlo simulations:')
                    print(error_kinematics_mc)

                # if fitting two stellar components
                else:
                    #initialising the arrays containing the n_sim simulated kinematics
                    vel_dist1 = []
                    sigma_dist1 = []
                    h3_dist1 = []
                    h4_dist1 = []
                    h5_dist1 = []
                    h6_dist1 = []

                    vel_dist2 = []
                    sigma_dist2 = []
                    h3_dist2 = []
                    h4_dist2 = []
                    h5_dist2 = []
                    h6_dist2 = []

                    for i in range(n_sim):
                        noisy_template = spman.add_noise(bestfit_wavelength, bestfit_flux, snr)

                        #fitting the noisy templates
                        pp = ppxf(templates, noisy_template, noise, velscale, start, goodpixels = goodpix,
                        moments=kin_moments, degree=additive_degree, mdegree=multiplicative_degree,
                        lam=bestfit_wavelength, lam_temp=lam_temp,
                        quiet = True, dust = dust, component = component, global_search = global_search, bias = bias)

                        kinematics_mc = pp.sol

                        vel_mc1 = int(kinematics_mc[0][0])
                        sigma_mc1 = int(kinematics_mc[0][1])
                        vel_dist1.append(vel_mc1)
                        sigma_dist1.append(sigma_mc1)

                        vel_mc2 = int(kinematics_mc[1][0])
                        sigma_mc2 = int(kinematics_mc[1][1])
                        vel_dist2.append(vel_mc2)
                        sigma_dist2.append(sigma_mc2)

                        if kin_moments > 2:
                            h3_mc1 = round(kinematics_mc[0][2],3)
                            h3_dist1.append(h3_mc1)
                            h3_mc2 = round(kinematics_mc[1][2],3)
                            h3_dist2.append(h3_mc2)

                        if kin_moments > 3:
                            h4_mc1 = round(kinematics_mc[0][3],3)
                            h4_dist1.append(h4_mc1)
                            h4_mc2 = round(kinematics_mc[1][3],3)
                            h4_dist2.append(h4_mc2)

                        if kin_moments > 4:
                            h5_mc1 = round(kinematics_mc[0][4],3)
                            h5_dist1.append(h5_mc1)
                            h5_mc2 = round(kinematics_mc[1][4],3)
                            h5_dist2.append(h5_mc2)

                        if kin_moments > 5:
                            h6_mc1 = round(kinematics_mc[0][5],3)
                            h6_dist1.append(h6_mc1)
                            h6_mc2 = round(kinematics_mc[1][5],3)
                            h6_dist2.append(h6_mc2)

                    error_vel1 = np.std(vel_dist1)
                    error_sigma1 = np.std(sigma_dist1)
                    error_h31 = 0
                    error_h41 = 0
                    error_h51 = 0
                    error_h61 = 0

                    error_vel2 = np.std(vel_dist2)
                    error_sigma2 = np.std(sigma_dist2)
                    error_h32 = 0
                    error_h42 = 0
                    error_h52 = 0
                    error_h62 = 0

                    if kin_moments > 1:
                        error_kinematics_mc = np.column_stack((error_vel1, error_sigma1, error_h31, error_h41, error_h51, error_h61, error_vel2, error_sigma2, error_h32, error_h42, error_h52, error_h62))

                    if kin_moments > 2:
                        error_h31 = np.std(h3_dist1)
                        error_h32 = np.std(h3_dist2)
                        error_kinematics_mc = np.column_stack((error_vel1, error_sigma1, error_h31, error_h41, error_h51, error_h61, error_vel2, error_sigma2, error_h32, error_h42, error_h52, error_h62))

                    if kin_moments > 3:
                        error_h41 = np.std(h4_dist1)
                        error_h42 = np.std(h4_dist2)
                        error_kinematics_mc = np.column_stack((error_vel1, error_sigma1, error_h31, error_h41, error_h51, error_h61, error_vel2, error_sigma2, error_h32, error_h42, error_h52, error_h62))

                    if kin_moments > 4:
                        error_h51 = np.std(h5_dist1)
                        error_h52 = np.std(h5_dist2)
                        error_kinematics_mc = np.column_stack((error_vel1, error_sigma1, error_h31, error_h41, error_h51, error_h61, error_vel2, error_sigma2, error_h32, error_h42, error_h52, error_h62))

                    if kin_moments > 5:
                        error_h61 = np.std(h6_dist1)
                        error_h62 = np.std(h6_dist2)
                        error_kinematics_mc = np.column_stack((error_vel1, error_sigma1, error_h31, error_h41, error_h51, error_h61, error_vel2, error_sigma2, error_h32, error_h42, error_h52, error_h62))

                    print('Uncertainties with MonteCarlo simulations:')
                    print(error_kinematics_mc)

            components = component[0] #only to return the number of gas components, that is zero!
            return kinematics, error_kinematics, bestfit_flux, bestfit_wavelength, bestfit_gas_flux, emission_corrected_flux, gas_without_continuum, components, gas_component, snr, error_kinematics_mc, gas_names, gas_flux, gas_flux_err, stars_templates, lam_temp, velscale, FWHM_gal_cached, two_components_cached, stellar_components

        except Exception:
            print ('ERROR')
            kinematics = error_kinematics = bestfit_flux = bestfit_wavelength = bestfit_gas_flux = emission_corrected_flux = gas_without_continuum = component = gas_component =  snr =  error_kinematics_mc = gas_names = gas_flux = gas_flux_err = stars_templates = lam_temp = velscale = FWHM_gal_cached = two_components_cached = stellar_components= 0


#################### WITH GAS AND STARS #########################

    if kin_fit_gas:

        print ('Fitting the stars and at least one gas component')
       
        try:
            tie_balmer=tied_balmer
            limit_doublets=False

            #retrieving the emission lines in the wavelength range
            gas_templates, gas_names, line_wave = emission_lines(
            np.log(lam_temp), lam_range_gal, FWHM_gal,
            tie_balmer=tie_balmer, limit_doublets=limit_doublets, wave_galaxy = wave)

            if tie_balmer and not two_stellar_components:
                dust_correction_gas = True
                print ('With tied Balmer lines, I activate the gas dust correction for you')

            templates = np.column_stack([stars_templates, gas_templates])

            if two_stellar_components:
                if dust_correction_stars or dust_correction_gas:
                    print(f'\nWARNING: Dust correction not available for two stellar compoent mode!')
                    dust_correction_stars = False
                    dust_correction_gas = False
                global_search = True
                comp_stars = np.asarray(component, dtype=int).ravel()
                star_labels = np.unique(comp_stars)
                n_star_comp = len(star_labels)

                vel_sys = c * np.log(1 + z)
                start_stars = []
                if 0 in star_labels:
                    start_stars.append([vel_sys + vel_guess1, sigma_guess1])
                if 1 in star_labels:
                    start_stars.append([vel_sys + vel_guess2, sigma_guess2])

                kin_moments_stars = [kin_moments] * n_star_comp

            else:
                global_search = False
                # One stellar component
                n_temps = stars_templates.shape[1]
                comp_stars = np.zeros(n_temps, dtype=int)
                n_star_comp = 1
                vel_sys = c * np.log(1 + z)
                start_stars = [vel_sys, sigma_guess]
                kin_moments_stars = [kin_moments]
                
            # If I fix the stellar moments, here I define them
            if fixed_moments and kinematics_fixed is not None:
                print('\n*** Fixing the kinematics of stars ***')          
                if two_stellar_components:
                    start_stars = []
                    kin_moments_stars = []
                    for kin_fix in kinematics_fixed:
                        arr = np.asarray(kin_fix, float)
                        vec = arr[:kin_moments].tolist()
                        n = int(np.count_nonzero(vec))
                        n = max(2, min(n, kin_moments))
                        start_stars.append(vec[:n])
                        kin_moments_stars.append(-n)
                else:
                    vec = list(kinematics_fixed[:kin_moments])
                    start_stars = vec
                    kin_moments_stars = [-len(vec)]

                # Gas is free
                vel = c*np.log(1 + z)
                start =  [vel, sigma_guess]

            else:
                vel = c*np.log(1 + z)
                start = [vel, sigma_guess]

            n_temps = stars_templates.shape[1]

            # grouping the emission lines: 1) balmer, 2) forbidden, 3) others
            n_forbidden = np.sum(["[" in a for a in gas_names])
            if not tie_balmer:
                n_balmer = np.sum(["(" in a for a in gas_names])
            else:
                n_balmer = np.sum(["Balmer" in a for a in gas_names])
                print ('Tied Balmer lines')

            n_others = np.sum(["-" in a for a in gas_names])

            #looking for the existence of at least one line of each group in the selected spectral window
            gas_moments = 2
            if n_forbidden !=0 and n_balmer !=0 and n_others !=0:
                ##### THREE GAS COMPONETS
                gas = True
                print('Balmer, forbidden and other lines')
                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_balmer \
                        + [next_label+1]*n_forbidden \
                        + [next_label+2]*n_others

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*3
                
                if two_stellar_components:
                    start   = start_stars +[start, start, start]
                else: 
                    start   = [start_stars, start, start, start]

            if n_forbidden !=0 and n_balmer !=0 and n_others == 0:
                #####
                gas = True
                print ('Forbidden and Balmer lines')
                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_balmer \
                        + [next_label+1]*n_forbidden

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*2
                if two_stellar_components:
                    start   = start_stars +[start, start]
                else: 
                    start   = [start_stars, start, start]

            if n_forbidden !=0 and n_balmer == 0 and n_others !=0:
                #####
                gas = True
                print ('Forbidden and other lines')        
                
                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_others \
                        + [next_label+1]*n_forbidden

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*2
                if two_stellar_components:
                    start   = start_stars +[start, start]
                else: 
                    start   = [start_stars, start, start]

            if n_forbidden !=0 and n_balmer == 0 and n_others ==0:
                #######
                gas = True
                print ('Only forbidden lines')            
                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_forbidden

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*1
                if two_stellar_components:
                    start   = start_stars +[start]
                else: 
                    start   = [start_stars, start]


            if n_forbidden ==0 and n_balmer != 0 and n_others ==0:
                ######
                gas = True
                print('Only balmer lines')
                
                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_balmer

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*1
                if two_stellar_components:
                    start   = start_stars +[start]
                else: 
                    start   = [start_stars, start]

            if n_forbidden ==0 and n_balmer != 0 and n_others !=0:
                #######
                gas = True
                print ('Balmer and other lines')
                
                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_balmer \
                        + [next_label+1]*n_others

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*2
                if two_stellar_components:
                    start   = start_stars +[start, start]
                else: 
                    start   = [start_stars, start, start]


            if n_forbidden ==0 and n_balmer == 0 and n_others !=0:
                ########
                gas = True
                print ('Only other lines')

                next_label = n_star_comp
                component = comp_stars.tolist() \
                        + [next_label]*n_balmer

                gas_component = np.array(component) >= n_star_comp
                moments = kin_moments_stars + [gas_moments]*1
                
                if two_stellar_components:
                    start   = start_stars +[start]
                else: 
                    start   = [start_stars, start]

            if n_forbidden ==0 and n_balmer == 0 and n_others ==0:
                ########### NO GAS COMPONENT
                gas = False
                print ('No gas lines found. Fitting only the stellar component')

                if two_stellar_components:
                    next_label = n_star_comp
                    component = comp_stars.tolist()
                    gas_component = np.array(component) >= n_star_comp
                    moments = kin_moments_stars + [gas_moments]*0
                    start   = start_stars
                else: 
                    next_label = n_star_comp
                    
                    component = comp_stars.tolist()
                    gas_component = np.array(component) >= n_star_comp
                    component = 0 # bring to zero to activate the switch in the apply_analysis task. Just a trick 
                    moments = kin_moments_stars + [gas_moments]*0
                    start   = start_stars
                    
            t = clock()

            #define the dust components, if activated
            if dust_correction_stars or dust_correction_gas:
                if (dust_correction_stars and dust_correction_gas):
                    print('Considering dust for stars and gas')
                    if not gas:
                        print('No gas lines to correct for dust, considering onlty stars')
                        dust_gas = None
                        dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                        dust = [dust_stars]
                    else:
                        dust_gas = {"start": [0.1], "bounds": [[0, 8]], "component": gas_component}
                        dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                        dust = [dust_gas, dust_stars]
                if not dust_correction_stars and dust_correction_gas:
                    print ('Considering dust for gas')
                    if not gas:
                        print('No gas lines to correct for dust, skipping')
                        dust_gas = None
                    else:
                        dust_gas = {"start": [0.1], "bounds": [[0, 8]], "component": gas_component}
                        dust = [dust_gas]
                if dust_correction_stars and not dust_correction_gas:
                    print('Considering dust for the stellar component')
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]

            else:
                dust = None

            #routine to find automatically the best noise for ppxf
            if kin_best_noise:
                print('')
                print ('Running ppxf in silent mode to find the best noise level...')

                if gas:
                    pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                        moments=moments, degree= additive_degree, mdegree=multiplicative_degree,
                        lam=wave, lam_temp=lam_temp,component=component, gas_component=gas_component, gas_names=gas_names, quiet = True, bias = 0, dust = dust, global_search = global_search)
                else:
                    pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                        moments=moments, degree= additive_degree, mdegree=multiplicative_degree,
                        lam=wave, lam_temp=lam_temp,component=component, gas_names=gas_names, quiet = True, bias = 0, dust = dust, global_search = global_search)

                nonregul_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                best_noise = np.full_like(galaxy, noise*mt.sqrt(pp.chi2))
                noise = best_noise

                print ('Best noise: ', round(best_noise[0],5))
                print ('Now fitting with this noise estimation')
                print ('')

            #finally fitting
            if gas: #with gas np.sum(component)==0
                pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, plot = True, degree= additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=lam_temp,component=component, gas_component=gas_component, gas_names=gas_names, dust = dust, bias = bias, global_search = global_search)

                errors = [array * np.sqrt(pp.chi2) for array in pp.error]
                gas_flux = pp.gas_flux*galaxy_median_flux #real physical flux per Angstrom
                gas_flux_err = pp.gas_flux_error*galaxy_median_flux #real physical flux errors per Angstrom

                if not two_stellar_components:
                    stellar_components = None # I do not have two stellar components
                else:
                    # Generating the two bestfit templates separated
                    spec_comp1, spec_comp2 = extract_stellar_components_from_matrix(pp=pp, component=component, stars_templates=stars_templates, gas_templates=None,         
                    additive_degree=additive_degree)
                    stellar_components = spec_comp1, spec_comp2

            else: #without gas
                pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, plot = True, degree= additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=lam_temp,component=component, dust = dust, bias = bias, global_search = global_search)

                try:
                    errors = pp.error*np.sqrt(pp.chi2)  # Assume the fit is good chi2/DOF=1
                except Exception:
                    errors = [array * np.sqrt(pp.chi2) for array in pp.error]
                
                if not two_stellar_components:
                    stellar_components = None # I do not have two stellar components
                else:
                    # Generating the two bestfit templates separated
                    spec_comp1, spec_comp2 = extract_stellar_components_from_matrix(pp=pp, component=component, stars_templates=stars_templates, gas_templates=None,         
                    additive_degree=additive_degree)
                    stellar_components = spec_comp1, spec_comp2
                    

            redshift_fit = (1 + redshift_0)*np.exp(pp.sol[0]/c) - 1  # eq. (5c) C22
            redshift_err = (1 + redshift_fit)*errors[0]/c            # eq. (5d) C22

            print("Formal errors in stellar component:")
            print("     dV    dsigma   dh3      dh4")
            if not gas:
                if not two_stellar_components:
                    print("".join("%8.2g" % f for f in errors))
                    print('Elapsed time in pPXF: %.2f s' % (clock() - t))
                    try:
                        prec = int(1 - np.floor(np.log10(redshift_err)))  # two digits of uncertainty
                    except Exception:
                        prec = 7
                    print(f"Best-fitting redshift z = {redshift_fit:#.{prec}f} "
                        f"+/- {redshift_err:#.{prec}f}")
                else:
                    stellar_uncertainties = errors[0]
                    print("".join("%8.2g" % f for f in stellar_uncertainties))
                    print('Elapsed time in pPXF: %.2f s' % (clock() - t))
                    if redshift_err[0] == 0 or not np.isfinite(redshift_err[0]):
                        prec = 7
                        print(f"Best-fitting redshift z = {redshift_fit[0]:#.{prec}f} "
                        f"+/- {redshift_err[0]:#.{prec}f}")
                    else:
                        prec = int(1 - np.floor(np.log10(redshift_err[0])))  # two digits of uncertainty
                        print(f"Best-fitting redshift z = {redshift_fit[0]:#.{prec}f} "
                            f"+/- {redshift_err[0]:#.{prec}f}")
            else:
                stellar_uncertainties = errors[0]
                print("".join("%8.2g" % f for f in stellar_uncertainties))
                print('Elapsed time in pPXF: %.2f s' % (clock() - t))
                try:
                    prec = int(1 - np.floor(np.log10(redshift_err[0])))  # two digits of uncertainty
                except Exception:
                    prec = 7
                print(f"Best-fitting redshift z = {redshift_fit[0]:#.{prec}f} "
                    f"+/- {redshift_err[0]:#.{prec}f}")


            #output kinematics parameters
            kinematics = pp.sol
            error_kinematics = errors

            bestfit_flux = pp.bestfit
            bestfit_wavelength = wave
            residual = galaxy - bestfit_flux
            snr = 1/np.std(residual)
            print ('S/N of the spectrum:', round(snr))


            try:
                bestfit_gas_flux = pp.gas_bestfit
                bestfit_stellar = bestfit_flux - bestfit_gas_flux
                emission_corrected_flux = galaxy - bestfit_gas_flux
                gas_without_continuum = galaxy - bestfit_stellar
            except TypeError:
                emission_corrected_flux = galaxy
                bestfit_gas_flux = 0
                gas_without_continuum = galaxy


            #adding the mock h3, h4, h5, and h6 column to the kinematic array in order to not change the main code
            all_moments = 6
            if kin_moments < all_moments:
                missing_moments = all_moments - kin_moments
                moments_to_add = np.zeros(missing_moments)
                if not gas:
                    if not two_stellar_components:
                        kinematics = np.hstack((kinematics, moments_to_add))
                        error_kinematics = np.hstack((error_kinematics, moments_to_add))
                    else:
                        components = np.max(component)
                        for k in range (components+1):

                            kinematics[k] = np.hstack((kinematics[k], moments_to_add))
                            error_kinematics[k] = np.hstack((error_kinematics[k], moments_to_add))
                else:
                    components = np.max(component)
                    for k in range (components+1):

                        kinematics[k] = np.hstack((kinematics[k], moments_to_add))
                        error_kinematics[k] = np.hstack((error_kinematics[k], moments_to_add))


        # Uncertainties estimation on the stellar kinematics with MonteCarlo simulations
            if with_errors_kin: #calculating the errors of age and metallicity with MonteCarlo simulations

                start = [vel, sigma_guess]

                print('Calculating the uncertainties with MonteCarlo simulations')
                n_sim = mc_sim #how many simulated templates I want to create. Watch out for the computation time!

                #initialising the arrays containing the n_sim simulated kinematics
                vel_dist = []
                sigma_dist = []
                h3_dist = []
                h4_dist = []
                h5_dist = []
                h6_dist = []

                for i in range(n_sim):
                    noisy_template = spman.add_noise(bestfit_wavelength, bestfit_flux, snr)

                    #fitting!
                    pp = ppxf(templates, noisy_template, noise, velscale, start, goodpixels = goodpix,
                    moments=kin_moments, degree=additive_degree, mdegree=multiplicative_degree,
                    lam=bestfit_wavelength, lam_temp=lam_temp,
                    component=0, quiet = True, dust = dust,bias = bias, global_search = global_search)

                    kinematics_mc = pp.sol

                    vel_mc = int(kinematics_mc[0])
                    sigma_mc = int(kinematics_mc[1])
                    vel_dist.append(vel_mc)
                    sigma_dist.append(sigma_mc)

                    if kin_moments > 2:
                        h3_mc = round(kinematics_mc[2],3)
                        h3_dist.append(h3_mc)

                    if kin_moments > 3:
                        h4_mc = round(kinematics_mc[3],3)
                        h4_dist.append(h4_mc)

                    if kin_moments > 4:
                        h5_mc = round(kinematics_mc[4],3)
                        h5_dist.append(h5_mc)

                    if kin_moments > 5:
                        h6_mc = round(kinematics_mc[5],3)
                        h6_dist.append(h6_mc)

                # calculating the uncertainties
                error_vel = np.std(vel_dist)
                error_sigma = np.std(sigma_dist)
                error_h3 = 0
                error_h4 = 0
                error_h5 = 0
                error_h6 = 0

                if kin_moments > 1:
                    error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))

                if kin_moments > 2:
                    error_h3 = np.std(h3_dist)
                    error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))

                if kin_moments > 3:
                    error_h4 = np.std(h4_dist)
                    error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))
                if kin_moments > 4:
                    error_h5 = np.std(h5_dist)
                    error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))
                if kin_moments > 5:
                    error_h6 = np.std(h6_dist)
                    error_kinematics_mc = np.column_stack((error_vel, error_sigma, error_h3, error_h4, error_h5, error_h6))


                print('Uncertainties with MonteCarlo simulations:')
                print(error_kinematics_mc)

            return kinematics, error_kinematics, bestfit_flux, bestfit_wavelength, bestfit_gas_flux, emission_corrected_flux, gas_without_continuum, component, gas_component, snr, error_kinematics_mc, gas_names, gas_flux, gas_flux_err, stars_templates, lam_temp, velscale, FWHM_gal_cached, two_components_cached, stellar_components

        except AssertionError:
            print ('The selected template does not cover the wavelength range you want to fit')
            kinematics = error_kinematics = bestfit_flux = bestfit_wavelength = bestfit_gas_flux = emission_corrected_flux = gas_without_continuum = component = gas_component =  snr =  error_kinematics_mc = gas_names = gas_flux = gas_flux_err = stars_templates = lam_temp = FWHM_gal_cached= two_components_cached = stellar_components= 0



#*****************************************************************************************************
# 9) stellar populations with ppxf
def ppxf_pop(wave, flux, wave1, wave2, FWHM_gal, z, sigma_guess, fit_components, with_plots, with_errors, save_plot, spec_name, regul_err, additive_degree, multiplicative_degree, tied_balmer, stellar_library, dust_correction_stars, dust_correction_gas, noise_per_pix, age_range, metal_range, custom_emiles, custom_emiles_folder, custom_npz, filename_npz, mask_emission, custom_temp_suffix, best_param, best_noise_estimate, frac_chi, convolve_temp, have_user_mask, mask_ranges, nrand, lg_age, lg_met, result_plot_dir):

    """
     This function uses the pPXF algorith to retrieve the properties of the
     stellar populations (age, metallicity, alpha/Fe if available) and the non
     parametric Star Formation History (SFH) of a galaxy spectrum
     by fitting SPS and (eventually) gas templates to the selected wavelength
     range of the selected spectrum.
     Input: wavelength and flux arrays of the spectrum, min and max wavelength
            to fit, delta lambda resolution of the spectrum in the wavelength
            range considered (FWHM value, in Angstrom), float redshift guess, float
            velocity dispersion guess, string wether fit the gas ('with gas')
            or just the stars ()'whitout gas'), bool whether showing (True) or not
            (False) the plots, bool whether calculate (True) or not (False) the uncertainties,
            bool whether save (True) or not (False) the plots, string name of the spectrum,
            float regularization error, int degree of additive polynomials, int degree of
            multiplicative polynomials, bool wheter to tie (True) or not (False) the Balmer lines,
            string SPS library to use, bool whether to correct (True) or not (False) for the dust
            the stellar component, bool wheter to correct (True) or not (False) for the dust the
            gas component, floas neano noise per pixel, array with the minimum and maximum age
            to consider for the models, array with the minimum and maximum metallocity [M/H] to
            consider for the models, bool whether use (True) or not (False) custom (E)MILES models,
            path of the folder containing the custom (E)MILES models to use, bool whether to mask (True)
            or not (False) the emission lines, string with the common suffix of the custom templates to use,
            bool whether estimate (True) or not (False) automatically the best noise and regul. error,
            bool whether estimate (True) or not (False) only the noise level of the spectrum,
            float fraction of the delta chi2 to reach in case of auto determination of the noise and
            regul. error parameters, bool whether convolve (True) or not (False) the SPS templates
            to the resolution of the galaxy spectrum, bool whether to include (True) or not (False)
            a user defined mask, touple wavelength interval(s) to mask, int number of bootstrap
            simulations in case the 'with_errors' option is activated (True).
     Output: array containing the kinematics moments fitted, array containing the properties fo the
             stellar populations fitted weighted in luminosity, array containing the properties fo the
             stellar populations fitted weighted in mass, array with the formal uncertainties in the
             kinematics moments, array containing the flux of the best fit template found, array containing the
             wavelength grid of the best fit template found, array containing the flux of the best
             fit gas template found, float chi2 value of the fit, float lum age lower 1sigma uncertainties
             (if with_errors = True), float lum age  1sigma uncertainties
             (if with_errors = True), float lum met 1sigma uncertainties
             (if with_errors = True), float lum alpha/Fe 1sigma uncertainties
             (if with_errors = True), float mass age 1sigma uncertainties
             (if with_errors = True), float mass met 1sigma uncertainties
             (if with_errors = True), float mass alpha/Fe 1sigma uncertainties
             (if with_errors = True), arrays fractional mass and cumulative mass 1sigma uncertainties
             (if with_errors = True), array of the emission corrected flux of the spectrum,
             array of the age bins of the templates, array of the mass fraction per age bin, array of the
             cumulative mass per age bin, floar S/N measured from the residuals, array of the
             light weights calculated by ppxf, array of the mass weights calculated by ppxf
    """

    ppxf_default_lib = ["emiles", "fsps", "galaxev"]
    #converting wavelength to angstrom
    wave = wave
    galaxy = flux


    #selecting the input range
    wave1 = wave1
    wave2 = wave2
    line_wave = wave[(wave >= wave1) & (wave <= wave2)]
    line_flux_spec = galaxy[(wave >= wave1) & (wave <= wave2)]

    #updating the variables
    galaxy = line_flux_spec
    wave = line_wave

    #normalise to unity
    galaxy = galaxy/np.median(galaxy)

    # Setting the new lambda ranges to the rest-frame
    redshift = z #placeholder to not loose the real redshift
    high_z = 0.01
    lam_range_gal = np.array([np.min(wave), np.max(wave)])/(1 + z)
    if z > high_z:
        FWHM_gal /= 1 + z
        redshift_0 = redshift
    else:
        redshift_0 = redshift
    z = 0

    #Log rebin to the restframe wavelength
    print('Rebinning to log')
    galaxy, ln_lam1, velscale = util.log_rebin(lam_range_gal, galaxy)
    wave = np.exp(ln_lam1) #converting the ln wavelength to wavelength, but keeping the ln sampling

    noise = np.full_like(galaxy, noise_per_pix) #noise per pixel
    c = 299792.458

    #setting up the wavelength range of the templates with a little of margin (1.02)
    lam_range_temp = [np.min(lam_range_gal)/1.02, np.max(lam_range_gal)*1.02]

    min_age_range = np.min(age_range)
    max_age_range = np.max(age_range)
    min_met_range = np.min(metal_range)
    max_met_range = np.max(metal_range)

    sps_name = stellar_library
    #loading the ppxf templates...
    if not custom_emiles and not custom_npz: #Using the incorporated templates with SPAN

        #requesting the pPXF preloaded templates, only if needed
        if stellar_library in ppxf_default_lib:
            ppxf_dir = Path(util.__file__).parent
            basename = f"spectra_{sps_name}_9.0.npz"
            filename = ppxf_dir / 'sps_models' / basename
            if not filename.is_file():
                url = "https://raw.githubusercontent.com/micappe/ppxf_data/main/" + basename
                download_file(url, filename)

        if stellar_library == 'xshooter': #Xshooter templates require the custom xshooter_ppxf module
            print(stellar_library)
            pathname_xsl = os.path.join(BASE_DIR, "spectralTemplates", "xsl_mod", "*XSL_SSP*.fits" )
            if convolve_temp:
                sps = template.xshooter(pathname_xsl, velscale, FWHM_gal, norm_range=[5070, 5950],wave_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range]) #normalization range
            else:
                sps = template.xshooter(pathname_xsl, velscale, norm_range=[5070, 5950],wave_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range]) #normalization range

        elif stellar_library == 'sMILES':
            print(stellar_library)
            pathname_smiles = os.path.join(BASE_DIR, "spectralTemplates", "sMILES_afeh", "M*.fits" ) #using only the M identified, so I do not give constrain on the IMF.
            if convolve_temp:
                sps = template.smiles(pathname_smiles, velscale, FWHM_gal, norm_range=[5070, 5950], wave_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range]) #normalization range
            else:
                sps = template.smiles(pathname_smiles, velscale, norm_range=[5070, 5950], wave_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range]) #normalization range

        else: #The other templates comes with pPXF distribution and require the sps_util module
            print(stellar_library)
            if convolve_temp:
                sps = lib.sps_lib(filename, velscale, FWHM_gal, norm_range=[5070, 5950], lam_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range])
            else:
                sps = lib.sps_lib(filename, velscale, norm_range=[5070, 5950], lam_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range])

        reg_dim = sps.templates.shape[1:]
        stars_templates = sps.templates.reshape(sps.templates.shape[0], -1)

    #Loading the custom emiles templates selected by the user
    if custom_emiles and not custom_npz:
        print('Custom EMILES')
        pathname = custom_emiles_folder + '/' + custom_temp_suffix
        if convolve_temp:
            sps = template.miles(pathname, velscale, FWHM_gal, norm_range=[5070, 5950],wave_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range]) #normalization range
        else:
            sps = template.miles(pathname, velscale, norm_range=[5070, 5950],wave_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range]) #normalization range

        reg_dim = sps.templates.shape[1:]
        stars_templates = sps.templates.reshape(sps.templates.shape[0], -1)


    # Loading the custom .npz templates
    if custom_npz:
        print ('Custon templates in .npz format')
        filename = filename_npz

        if convolve_temp:
            sps = lib.sps_lib(filename, velscale, FWHM_gal, norm_range=[5070, 5950], lam_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range])
        else:
            sps = lib.sps_lib(filename, velscale, norm_range=[5070, 5950], lam_range=lam_range_temp, age_range = [min_age_range, max_age_range], metal_range = [min_met_range, max_met_range])

        reg_dim = sps.templates.shape[1:]
        stars_templates = sps.templates.reshape(sps.templates.shape[0], -1)


    #Detecting when the emission mask is needed
    if mask_emission:
        use_emission_mask = True
    else:
        use_emission_mask = False

    #loading or not the mask emission, if activated and only for stars fitting
    goodpix = build_goodpixels_with_mask(
        ln_lam1, lam_range_temp, z, redshift_0, mask_ranges=mask_ranges, user_mask = have_user_mask,
        use_emission_mask=use_emission_mask)

    #definying and check on regularization value
    if regul_err > 0:
        regularization = 1/regul_err
    else:
        regularization = 0
        print ('Non-regularized fit')

    age_err = 0
    met_err = 0
    alpha_err = 0
    mass_age_err = 0
    mass_met_err = 0
    mass_alpha_err = 0
    mass_weights_age_std = 0
    light_weights_age_std = 0
    cumulative_mass_std = 0
    cumulative_light_std = 0


  ###################### Now without gas ##################
    if fit_components == 'without_gas':
        print ('Fitting without gas component')

        try:
            templates = stars_templates
            vel = c*np.log(1 + z)
            start = [vel, sigma_guess]
            n_temps = stars_templates.shape[1]
            component = [0]*n_temps
            gas_component = np.array(component) > 0
            moments = 4
            start = start
            gas = False
            t = clock()


            #define the dust components, if activated
            if dust_correction_stars or dust_correction_gas:
                if (dust_correction_stars and dust_correction_gas) and gas:
                    print('Considering dust for stars and gas')
                    dust_gas = {"start": [0.1], "bounds": [[0, 8]], "component": gas_component}
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_gas, dust_stars]
                if (dust_correction_stars and dust_correction_gas) and not gas:
                    print('You only have stars, considering only dust for the stellar component')
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]
                if not dust_correction_stars and dust_correction_gas and not gas:
                    print('You do not have gas to correct for dust')
                    dust = None
                if not dust_correction_stars and dust_correction_gas and gas:
                    print ('Considering dust for gas')
                    dust_gas = {"start": [0.1], "bounds": [[0, 8]], "component": gas_component}
                    dust = [dust_gas]
                if dust_correction_stars and not dust_correction_gas:
                    print('Considering dust for the stellar component')
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]

            else:
                dust = None


            #routine to find automatically the best parameters for ppxf (noise and regul_err)
            if best_param or best_noise_estimate:
                print('')
                print ('Running ppxf in silent mode to find the best noise level...')
                try_regularization = 0


                pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=sps.lam_temp,
                    regul=try_regularization, reg_dim=reg_dim,
                    component=component, dust = dust, quiet = True)
                nonregul_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                best_noise = np.full_like(galaxy, noise*mt.sqrt(pp.chi2))
                noise = best_noise

                print ('Best noise: ', round(best_noise[0],5))

                if not best_param:
                    print ('Now fitting with this noise level...')
                    print('')

            if best_param:
                #now finding the best regul_err
                max_iter = 10 #maximum iteration in order to find the best regul err
                desired_deltachi_square = round(np.sqrt(2*galaxy.size),2)
                target_deltachi_square = round(desired_deltachi_square*frac_chi, 2) #the real delta chi is a fracion of the desired one
                epsilon_chi = 0.1*target_deltachi_square # if the deltachi2 found will be up to 10% smaller than the desired delta chi2, I will accept the parameters.
                min_meaningful_regul = 0.30/n_temps #empirical value from test and errors.
                print ('Maximum delta chi2: ',desired_deltachi_square)
                print ('Trying to reach target delta chi2: ',target_deltachi_square)
                current_deltachi_square = 0 #nonregul_deltachi_square


                min_regul_err, max_regul_err = 0, 0.2 # min regul err = 0 and max likely 0.05

                #starting from the regul_err guess, if it's reasonable
                if regul_err < max_regul_err:
                    max_regul_err = regul_err

                print('')
                print ('Running iteratively ppxf in silent mode to find the best regul err...')

                #this is the regul_err you entered in the GUI
                input_regul_err = regul_err

                #finding the best regul_err with the bisection algorithm
                for k in range(max_iter):
                    print('Trying regul error: ',regul_err)

                    if regul_err < min_meaningful_regul:
                        regul_err = round(min_meaningful_regul, 3)
                        print ('')
                        print ('WARNING: your spectra are too noisy for a proper regul err estimation')
                        print ('Minimum accettable regul err ', regul_err, ' reached. Using this regardless the delta chi2 value.')
                        print('')
                        regularization = 1/regul_err
                        break



                    pp = ppxf(templates, galaxy, best_noise, velscale, start, goodpixels = goodpix,
                        moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                        lam=wave, lam_temp=sps.lam_temp,
                        regul=1/regul_err, reg_dim=reg_dim,
                        component=component, dust = dust, quiet = True)
                    current_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                    print(f"Current Delta Chi^2: {(pp.chi2 - 1)*galaxy.size:#.4g}")
                    print(f"Desired Delta Chi^2: {np.sqrt(2*galaxy.size):#.4g}")
                    print('')


                    #Checking if I reached the good value according th the tolerance epsilon_chi, and only if the current deltachi is smaller or equal to the derired, not greater.
                    if abs(target_deltachi_square - current_deltachi_square) < epsilon_chi:
                        print ('Best Regul. err found!', round(regul_err,3))
                        print('Now running ppxf with noise: ', round(best_noise[0],5), 'and Regul. err: ', round(regul_err,3))
                        print('')
                        regularization = 1/regul_err
                        break

                    #simple bisection method
                    elif current_deltachi_square > target_deltachi_square:
                        min_regul_err = regul_err
                    else:
                        max_regul_err = regul_err

                    #splitting the regul err interval and trying a new value
                    regul_err = round((min_regul_err + max_regul_err) / 2, 5)

                    if k == max_iter-1:
                        print ('Convergence not reached, using the input regul err')
                        regularization = 1/input_regul_err

                    #In case the regul err is too small, I adjust the search range to include greater values
                    if k == 1:
                        if regul_err == input_regul_err:
                            print ('The regul err you entered is too small. I will guess a better value for you')
                            max_regul_err = 0.2
                            min_regul_err = regul_err
                            regul_err = max_regul_err


            #do the fit!
            pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                moments=moments, degree= additive_degree, mdegree=multiplicative_degree,
                lam=wave, lam_temp=sps.lam_temp,
                regul=regularization, reg_dim=reg_dim, dust = dust)


            #setting up the result parameters
            light_weights = pp.weights[~gas_component]
            light_weights = light_weights.reshape(reg_dim)
            mass_weights = light_weights/sps.flux #converting to mass weigths
            #Normalizing
            light_weights /= light_weights.sum() # Normalize to light fractions
            mass_weights /= mass_weights.sum()

# NOTE: Following what states Cappellari (in sps_util.py), please be aware that:
# "One can use the output attribute ``.flux`` to convert light-normalized
        # weights into mass weights, without repeating the ``ppxf`` fit.
        # However, when using regularization in ``ppxf`` the results will not
        # be identical. In fact, enforcing smoothness to the light-weights is
        # not quite the same as enforcing it to the mass-weights."


            # Retrieving the mean weighted age, metallicity, and alpha values (if available).
            # For the embedded pPXF libraries I need to extract the data from auxiliary functions, since I cannot modify the sps.util function.
            if custom_emiles or stellar_library in ['sMILES', 'xshooter']:
                print('\nLuminosity weighted stellar populations:')
                info_pop = sps.mean_age_metal(light_weights, lg_age, lg_met)
                print('\nMass weighted stellar populations:')
                info_pop_mass = sps.mean_age_metal(mass_weights, lg_age, lg_met)
                mass_light = 0  # No photometry info available
            else:
                sps_data_ppxf = template.SPSLibWrapper(
                    filename, velscale, fwhm_gal=FWHM_gal, age_range=[min_age_range, max_age_range],
                    lam_range=lam_range_temp, metal_range=[min_met_range, max_met_range],
                    norm_range=[5070, 5950], norm_type='mean'
                )
                print('\nLuminosity weighted stellar populations:')
                info_pop = sps_data_ppxf.mean_age_metal(light_weights, lg_age, lg_met)
                print('\nMass weighted stellar populations:')
                info_pop_mass = sps_data_ppxf.mean_age_metal(mass_weights, lg_age, lg_met)
                mass_light = sps.mass_to_light(mass_weights, band="v")

            # Printing output infos
            print(f"\nCurrent Delta Chi^2: {(pp.chi2 - 1) * galaxy.size:#.4g}")
            print(f"Desired Delta Chi^2: {np.sqrt(2 * galaxy.size):#.4g}")
            print(f"Chi^2: {pp.chi2:#.4g}")
            print(f"Elapsed time in pPXF: {clock() - t:.2f}")

            # Extracting the output parameters
            kinematics = pp.sol
            bestfit_flux = pp.bestfit
            bestfit_wave = wave
            bestfit_gas_flux = 0.
            chi_square = pp.chi2
            emission_corrected_flux = galaxy
            errors = pp.error * np.sqrt(pp.chi2)

            residual = galaxy - bestfit_flux
            snr = 1 / np.std(residual)
            print('S/N of the spectrum:', round(snr))

            # Adjusting weights and building the SFH plot
            if stellar_library == 'sMILES' and not custom_emiles:
                reduced_mass_weights = np.sum(mass_weights, axis=2)
                mass_weights_age_bin = np.sum(reduced_mass_weights, axis=1)[::-1]
                mass_weights_met_bin = np.sum(reduced_mass_weights, axis=0)[::-1]

                reduced_light_weights = np.sum(light_weights, axis=2)
                light_weights_age_bin = np.sum(reduced_light_weights, axis=1)[::-1]
                light_weights_met_bin = np.sum(reduced_light_weights, axis=0)[::-1]

                #retrieving age and metallicity grids
                age_grid = sps.get_full_age_grid()
                met_grid = sps.get_full_metal_grid()
                alpha_grid = sps.get_full_alpha_grid()
                age_bins = age_grid[:,0] #extracting
                age_bins = np.mean(age_bins, axis=1)[::-1] #inverting
                met_bins = met_grid[0,:] #extracting
                met_bins = np.mean(met_bins, axis=1)[::-1] #inverting

                alpha_bins = alpha_grid[0, 0, :] #extracting
                alpha_bins = alpha_bins[::-1] #inverting

            else:
                if custom_emiles or stellar_library == 'xshooter':
                    #retrieving age and metallicity grids
                    age_grid = sps.get_full_age_grid()
                    met_grid = sps.get_full_metal_grid()
                    age_bins = age_grid[:,0] #extracting
                    age_bins = age_bins[::-1] #inverting
                    met_bins = met_grid[0,:] #extracting
                    met_bins = met_bins[::-1] #inverting
                else:
                    age_bins = sps_data_ppxf.get_age_grid()[::-1] #extracting and inverting
                    met_bins = sps_data_ppxf.get_metal_grid()[::-1] #extracting and inverting

                mass_weights_age_bin = np.sum(mass_weights, axis=1)[::-1]
                light_weights_age_bin = np.sum(light_weights, axis=1)[::-1]

                mass_weights_met_bin= np.sum(mass_weights, axis=0)[::-1]
                light_weights_met_bin= np.sum(light_weights, axis=0)[::-1]


            if lg_age:
                age_bins = np.log10(age_bins) + 9

            cumulative_mass = np.cumsum(mass_weights_age_bin)
            cumulative_light = np.cumsum(light_weights_age_bin)

            t50_age, t80_age, t50_cosmic, t80_cosmic = calculate_t50_t80_cosmic(age_bins, cumulative_mass, redshift, lg_age)

            print ('')
            print(f"--- Stellar population times ---")
            print(f"t50 (stellar age):  {t50_age:.2f} Gyr ago")
            print(f"t80 (stellar age):  {t80_age:.2f} Gyr ago")
            print(f"--- Cosmic times since Big Bang ---")
            print(f"t50 (cosmic time):  {t50_cosmic:.2f} Gyr")
            print(f"t80 (cosmic time):  {t80_cosmic:.2f} Gyr")
            print('')

        except AssertionError:
            print ('The selected template does not cover the wavelength range you want to fit')
            kinematics=info_pop=info_pop_mass= mass_light= errors= bestfit_flux= bestfit_wave= bestfit_gas_flux=residual= chi_square=age_err=met_err=alpha_err=mass_age_err=mass_met_err=mass_alpha_err=emission_corrected_flux, age_bins, light_weights_age_bin, mass_weights_age_bin, cumulative_mass, light_weights_age_std, mass_weights_age_std, cumulative_light_std, cumulative_mass_std, snr, light_weights, mass_weights, t50_age, t80_age, t50_cosmic, t80_cosmic = 0

#################### WITH GAS #########################

    if fit_components == 'with_gas':

        print ('Fitting with at least one gas component')
        try:
            tie_balmer=tied_balmer
            limit_doublets=False

            #retrieving the emission lines in the wavelength range
            gas_templates, gas_names, line_wave = emission_lines(
            sps.ln_lam_temp, lam_range_gal, FWHM_gal,
            tie_balmer=tie_balmer, limit_doublets=limit_doublets)

            if tie_balmer:
                dust_correction_gas = True
                print ('With tied Balmer lines, I activate the gas dust correction for you')

            templates = np.column_stack([stars_templates, gas_templates])
            vel = c*np.log(1 + z)
            start = [vel, sigma_guess]
            n_temps = stars_templates.shape[1]

            # grouping the emission lines: 1) balmer, 2) forbidden, 3) others
            n_forbidden = np.sum(["[" in a for a in gas_names])
            if not tie_balmer:
                n_balmer = np.sum(["(" in a for a in gas_names])
            else:
                n_balmer = np.sum(["Balmer" in a for a in gas_names])
                print ('Tied Balmer lines')

            n_others = np.sum(["-" in a for a in gas_names])


            #looking for the existence of at least one line of each group in the selected spectral window
            if n_forbidden !=0 and n_balmer !=0 and n_others !=0:
                ##### THREE GAS COMPONETS
                gas = True
                print('Balmer, forbidden and other lines')
                component = [0]*n_temps + [1]*n_balmer + [2]*n_forbidden +[3]*n_others
                gas_component = np.array(component) > 0
                moments = [4, 2, 2, 2]
                start = [start, start, start, start]

            if n_forbidden !=0 and n_balmer !=0 and n_others == 0:
                #####
                gas = True
                print ('Forbidden and Balmer lines')
                component = [0]*n_temps + [1]*n_balmer + [2]*n_forbidden
                gas_component = np.array(component) > 0
                moments = [4, 2, 2]
                start = [start, start, start]

            if n_forbidden !=0 and n_balmer == 0 and n_others !=0:
                #####
                gas = True
                print ('Forbidden and other lines')
                component = [0]*n_temps + [1]*n_others + [2]*n_forbidden
                gas_component = np.array(component) > 0
                moments = [4, 2, 2]
                start = [start, start, start]

            if n_forbidden !=0 and n_balmer == 0 and n_others ==0:
                #######
                gas = True
                print ('Only forbidden lines')
                component = [0]*n_temps + [1]*n_forbidden
                gas_component = np.array(component) > 0
                moments = [4, 2]
                start = [start, start]

            if n_forbidden ==0 and n_balmer != 0 and n_others ==0:
                ######
                gas = True
                print('Only balmer lines')
                component = [0]*n_temps + [1]*n_balmer
                gas_component = np.array(component) > 0
                moments = [4, 2]
                start = [start, start]

            if n_forbidden ==0 and n_balmer != 0 and n_others !=0:
                #######
                gas = True
                print ('Balmer and other lines')
                component = [0]*n_temps + [1]*n_balmer [2]*n_forbidden
                gas_component = np.array(component) > 0
                moments = [4, 2, 2]
                start = [start, start, start]

            if n_forbidden ==0 and n_balmer == 0 and n_others !=0:
                ########
                gas = True
                print ('Only other lines')
                component = [0]*n_temps + [1]*n_others
                gas_component = np.array(component) > 0
                moments = [4, 2]
                start = [start, start]

            if n_forbidden ==0 and n_balmer == 0 and n_others ==0:
                ########### NO GAS COMPONENT
                gas = False
                print ('No gas lines found')
                # check_gas_cond = 0
                component = [0]*n_temps
                gas_component = np.array(component) > 0
                moments = 4
                start = start

            t = clock()


            #define the dust components, if activated
            if dust_correction_stars or dust_correction_gas:
                if (dust_correction_stars and dust_correction_gas) and gas:
                    print('Considering dust for stars and gas')
                    dust_gas = {"start": [0.1], "bounds": [[0, 8]], "component": gas_component}
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_gas, dust_stars]
                if (dust_correction_stars and dust_correction_gas) and not gas:
                    print('You only have stars, considering only dust for the stellar component')
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]
                if not dust_correction_stars and dust_correction_gas and not gas:
                    print('You do not have gas to correct for dust')
                    dust = None
                if not dust_correction_stars and dust_correction_gas and gas:
                    print ('Considering dust for gas')
                    dust_gas = {"start": [0.1], "bounds": [[0, 8]], "component": gas_component}
                    dust = [dust_gas]
                if dust_correction_stars and not dust_correction_gas:
                    print('Considering dust for the stellar component')
                    dust_stars = {"start": [0.1, -0.1], "bounds": [[0, 4], [-1, 0.4]], "component": ~gas_component}
                    dust = [dust_stars]

            else:
                dust = None


            #routine to find automatically the best parameters for ppxf (noise and regul_err)
            if best_param or best_noise_estimate:
                print('')
                print ('Running ppxf in silent mode to find the best noise level...')
                try_regularization = 0

                if gas:
                    pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                        moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                        lam=wave, lam_temp=sps.lam_temp,
                        regul=try_regularization, reg_dim=reg_dim,
                        component=component, gas_component=gas_component,
                        gas_names=gas_names, dust=dust, quiet = True)

                else:
                    pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                        moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                        lam=wave, lam_temp=sps.lam_temp,
                        regul=regularization, reg_dim=reg_dim,
                        component=component, dust = dust, quiet = True)
                nonregul_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                best_noise = np.full_like(galaxy, noise*mt.sqrt(pp.chi2))
                noise = best_noise

                print ('Best noise: ', round(best_noise[0],5))

                if not best_param:
                    print ('Now fitting with this noise level...')
                    print('')

            if best_param:
                #now finding the best regul_err
                max_iter = 10 #maximum iteration in order to find the best regul err
                desired_deltachi_square = round(np.sqrt(2*galaxy.size),2)
                target_deltachi_square = round(desired_deltachi_square*frac_chi, 2) #the real delta chi is a fracion of the desired one
                epsilon_chi = 0.1*target_deltachi_square # if the deltachi2 found will be up to 10% smaller than the desired delta chi2, I will accept the parameters.
                min_meaningful_regul = 0.30/n_temps #empirical value from test and errors.
                print ('Maximum delta chi2: ',desired_deltachi_square)
                print ('Trying to reach target delta chi2: ',target_deltachi_square)
                current_deltachi_square = 0 #nonregul_deltachi_square


                min_regul_err, max_regul_err = 0, 0.2 # min regul err = 0 and max likely 0.05

                #starting from the regul_err guess, if it's reasonable
                if regul_err < max_regul_err:
                    max_regul_err = regul_err

                print('')
                print ('Running iteratively ppxf in silent mode to find the best regul err...')

                #this is the regul_err you entered in the GUI
                input_regul_err = regul_err

                #finding the best regul_err with the bisection algorithm
                for k in range(max_iter):
                    print('Trying regul error: ',regul_err)

                    if regul_err < min_meaningful_regul:
                        regul_err = round(min_meaningful_regul, 3)
                        print ('')
                        print ('WARNING: your spectra are too noisy for a proper regul err estimation')
                        print ('Minimum accettable regul err ', regul_err, ' reached. Using this regardless the delta chi2 value.')
                        print('')
                        regularization = 1/regul_err
                        break

                    #with gas
                    if gas:
                        pp = ppxf(templates, galaxy, best_noise, velscale, start, goodpixels = goodpix,
                            moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                            lam=wave, lam_temp=sps.lam_temp,
                            regul=1/regul_err, reg_dim=reg_dim,
                            component=component, gas_component=gas_component,
                            gas_names=gas_names, dust=dust, quiet = True)

                        current_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                        print(f"Current Delta Chi^2: {(pp.chi2 - 1)*galaxy.size:#.4g}")
                        print(f"Desired Delta Chi^2: {np.sqrt(2*galaxy.size):#.4g}")
                        print('Target delta Chi^2: ', target_deltachi_square)
                        print('')

                    #in case I did not find gas lines
                    else:
                        pp = ppxf(templates, galaxy, best_noise, velscale, start, goodpixels = goodpix,
                            moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                            lam=wave, lam_temp=sps.lam_temp,
                            regul=1/regul_err, reg_dim=reg_dim,
                            component=component, dust=dust, quiet = True)
                        current_deltachi_square = round((pp.chi2 - 1)*galaxy.size, 2)
                        print(f"Current Delta Chi^2: {(pp.chi2 - 1)*galaxy.size:#.4g}")
                        print(f"Desired Delta Chi^2: {np.sqrt(2*galaxy.size):#.4g}")
                        print('')

                    #Checking if I reached the good value according th the tolerance epsilon_chi, and only if the current deltachi is smaller or equal to the derired, not greater.
                    if abs(target_deltachi_square - current_deltachi_square) < epsilon_chi:
                        print ('Best Regul. err found!', round(regul_err,3))
                        print('Now running ppxf with noise: ', round(best_noise[0],5), 'and Regul. err: ', round(regul_err,3))
                        print('')
                        regularization = 1/regul_err
                        break

                    #simple bisection method
                    elif current_deltachi_square > target_deltachi_square:
                        min_regul_err = regul_err
                    else:
                        max_regul_err = regul_err

                    #splitting the regul err interval and trying a new value
                    regul_err = round((min_regul_err + max_regul_err) / 2, 5)

                    if k == max_iter-1:
                        print ('Convergence not reached, using the input regul err')
                        regularization = 1/input_regul_err

                    #In case the regul err is too small, I adjust the search range to include greater values
                    if k == 1:
                        if regul_err == input_regul_err:
                            print ('The regul err you entered is too small. I will guess a better value for you')
                            max_regul_err = 0.2
                            min_regul_err = regul_err
                            regul_err = max_regul_err


            #finally fitting
            if gas:
                pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=sps.lam_temp,
                    regul=regularization, reg_dim=reg_dim,
                    component=component, gas_component=gas_component,
                    gas_names=gas_names, dust=dust)
            else:
                pp = ppxf(templates, galaxy, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=sps.lam_temp,
                    regul=regularization, reg_dim=reg_dim,
                    component=component, dust = dust)

                    #setting up the result parameters
            light_weights = pp.weights[~gas_component]
            light_weights = light_weights.reshape(reg_dim)
            mass_weights = light_weights/sps.flux #converting to mass weigths
            #Normalizing
            light_weights /= light_weights.sum() # Normalize to light fractions
            mass_weights /= mass_weights.sum()              # Normalize to mass fractions

# NOTE: Following what states Cappellari (in sps_util.py), please be aware that:
# "One can use the output attribute ``.flux`` to convert light-normalized
        # weights into mass weights, without repeating the ``ppxf`` fit.
        # However, when using regularization in ``ppxf`` the results will not
        # be identical. In fact, enforcing smoothness to the light-weights is
        # not quite the same as enforcing it to the mass-weights."


            # Retrieving the mean weighted age, metallicity, and alpha values (if available).
            # For the embedded pPXF libraries I need to extract the data from auxiliary functions, since I cannot modify the sps.util function.
            if custom_emiles or stellar_library in ['sMILES', 'xshooter']:
                print('\nLuminosity weighted stellar populations:')
                info_pop = sps.mean_age_metal(light_weights, lg_age, lg_met)
                print('\nMass weighted stellar populations:')
                info_pop_mass = sps.mean_age_metal(mass_weights, lg_age, lg_met)
                mass_light = 0  # No photometry info available
            else:
                sps_data_ppxf = template.SPSLibWrapper(
                    filename, velscale, fwhm_gal=FWHM_gal, age_range=[min_age_range, max_age_range],
                    lam_range=lam_range_temp, metal_range=[min_met_range, max_met_range],
                    norm_range=[5070, 5950], norm_type='mean'
                )
                print('\nLuminosity weighted stellar populations:')
                info_pop = sps_data_ppxf.mean_age_metal(light_weights, lg_age, lg_met)
                print('\nMass weighted stellar populations:')
                info_pop_mass = sps_data_ppxf.mean_age_metal(mass_weights, lg_age, lg_met)
                mass_light = sps.mass_to_light(mass_weights, band="v")


            # Printing output infos
            print(f"\nCurrent Delta Chi^2: {(pp.chi2 - 1) * galaxy.size:#.4g}")
            print(f"Desired Delta Chi^2: {np.sqrt(2 * galaxy.size):#.4g}")
            print(f"Chi^2: {pp.chi2:#.4g}")
            print(f"Elapsed time in pPXF: {clock() - t:.2f}")

            # Extracting the output parameters
            kinematics = pp.sol
            bestfit_flux = pp.bestfit
            bestfit_wave = wave
            bestfit_gas_flux = pp.gas_bestfit
            chi_square = pp.chi2
            residual = galaxy - bestfit_flux
            snr = 1/np.std(residual)
            errors = pp.error[0]*np.sqrt(pp.chi2)
            try:
                emission_corrected_flux = galaxy - pp.gas_bestfit
            except TypeError:
                emission_corrected_flux = galaxy

            print ('S/N of the spectrum:', round(snr))

            # Adjusting weights and building the SFH plot
            if stellar_library == 'sMILES' and not custom_emiles:
                reduced_mass_weights = np.sum(mass_weights, axis=2)
                mass_weights_age_bin = np.sum(reduced_mass_weights, axis=1)[::-1]
                mass_weights_met_bin = np.sum(reduced_mass_weights, axis=0)[::-1]

                reduced_light_weights = np.sum(light_weights, axis=2)
                light_weights_age_bin = np.sum(reduced_light_weights, axis=1)[::-1]
                light_weights_met_bin = np.sum(reduced_light_weights, axis=0)[::-1]

                #retrieving age and metallicity grids
                age_grid = sps.get_full_age_grid()
                met_grid = sps.get_full_metal_grid()
                alpha_grid = sps.get_full_alpha_grid()
                age_bins = age_grid[:,0] #extracting
                age_bins = np.mean(age_bins, axis=1)[::-1] #inverting
                met_bins = met_grid[0,:] #extracting
                met_bins = np.mean(met_bins, axis=1)[::-1] #inverting

                alpha_bins = alpha_grid[0, 0, :] #extracting
                alpha_bins = alpha_bins[::-1] #inverting

            else:
                if custom_emiles or stellar_library == 'xshooter':
                    #retrieving age and metallicity grids
                    age_grid = sps.get_full_age_grid()
                    met_grid = sps.get_full_metal_grid()
                    age_bins = age_grid[:,0] #extracting
                    age_bins = age_bins[::-1] #inverting
                    met_bins = met_grid[0,:] #extracting
                    met_bins = met_bins[::-1] #inverting
                else:
                    age_bins = sps_data_ppxf.get_age_grid()[::-1] #extracting and inverting
                    met_bins = sps_data_ppxf.get_metal_grid()[::-1] #extracting and inverting

                mass_weights_age_bin = np.sum(mass_weights, axis=1)[::-1]
                light_weights_age_bin = np.sum(light_weights, axis=1)[::-1]

                mass_weights_met_bin= np.sum(mass_weights, axis=0)[::-1]
                light_weights_met_bin= np.sum(light_weights, axis=0)[::-1]


            if lg_age:
                age_bins = np.log10(age_bins) + 9

            cumulative_mass = np.cumsum(mass_weights_age_bin)
            cumulative_light = np.cumsum(light_weights_age_bin)

            # Calculating t50 and t80
            t50_age, t80_age, t50_cosmic, t80_cosmic = calculate_t50_t80_cosmic(age_bins, cumulative_mass, redshift, lg_age)

            print ('')
            print(f"--- Stellar population times ---")
            print(f"t50 (stellar age):  {t50_age:.2f} Gyr ago")
            print(f"t80 (stellar age):  {t80_age:.2f} Gyr ago")

            print(f"--- Cosmic times since Big Bang ---")
            print(f"t50 (cosmic time):  {t50_cosmic:.2f} Gyr")
            print(f"t80 (cosmic time):  {t80_cosmic:.2f} Gyr")
            print('')

        except AssertionError:
            print ('The selected template does not cover the wavelength range you want to fit')
            kinematics=info_pop=info_pop_mass= mass_light= errors= bestfit_flux= bestfit_wave= bestfit_gas_flux=residual= chi_square=age_err=met_err=alpha_err=mass_age_err=mass_met_err=mass_alpha_err=emission_corrected_flux, age_bins, light_weights_age_bin, mass_weights_age_bin, cumulative_mass, light_weights_age_std, mass_weights_age_std, cumulative_light_std, cumulative_mass_std, snr, light_weights, mass_weights, t50_age, t80_age, t50_cosmic, t80_cosmic = 0


    #Doing plots and errors for both cases (gas and no gas)
    if with_plots or save_plot:

        # Creating figure and grid
        fig = plt.figure(figsize=(13, 7))
        gs = gridspec.GridSpec(2, 2, height_ratios=[1.5, 1.7])


        #*********** 1) First plot: fit of the spectrum across all the columns ***********
        ax1 = fig.add_subplot(gs[0, :])
        plt.sca(ax1)
        pp.plot()
        plt.tight_layout()


        #*********** 2) Second plot: light weights map ***********
        ax2 = fig.add_subplot(gs[1, 0])
        mean_lum_age = info_pop[0]
        mean_lum_met = info_pop[1]
        plt.sca(ax2)

        #For the embedded pPXF SSP, I need to call my external function, since I cannot modify any of the pPXF files
        if not custom_emiles and stellar_library != 'sMILES' and stellar_library != 'xshooter':
            sps_data_ppxf.plot(light_weights, lg_age, cmap='BuPu')
        else:
            template.plot_weights(light_weights, age_grid, met_grid, lg_age, cmap='BuPu')

        #Considering log or linear age grid
        if lg_age:
            plt.title(f"Luminosity fraction   lg<Age> = {mean_lum_age:.3g} dex, <[M/H]> = {mean_lum_met:.2g} dex", fontsize=11)
        else:
            plt.title(f"Luminosity fraction   <Age> = {mean_lum_age:.3g} Gyr, <[M/H]> = {mean_lum_met:.2g} dex", fontsize=11)
        plt.plot(mean_lum_age, mean_lum_met, 'ro')


        #*********** 3) Third plot: mass weights map ***********
        ax3 = fig.add_subplot(gs[1, 1])
        mean_mass_age = info_pop_mass[0]
        mean_mass_met = info_pop_mass[1]
        plt.sca(ax3)

        #For the embedded pPXF SSP, I need to call my external function, since I cannot modify any of the pPXF files
        if not custom_emiles and stellar_library != 'sMILES' and stellar_library != 'xshooter':
            sps_data_ppxf.plot(mass_weights, lg_age, cmap='BuPu')
        else:
            template.plot_weights(mass_weights, age_grid, met_grid, lg_age, cmap='BuPu')

        #Considering log or linear age grid
        if lg_age:
            plt.title(f"Mass fraction   lg<Age> = {mean_mass_age:.3g} dex, <[M/H]> = {mean_mass_met:.2g} dex", fontsize=11)
        else:
            plt.title(f"Mass fraction   <Age> = {mean_mass_age:.3g} Gyr, <[M/H]> = {mean_mass_met:.2g} dex", fontsize=11)

        plt.tight_layout()


        # Creating new figure with SFH data
        fig2 = plt.figure(figsize=(13, 7))
        gs2 = gridspec.GridSpec(3, 2, height_ratios=[1.5, 1.5, 1.5])

        # light SFH
        ax4 = fig2.add_subplot(gs2[0, 0])
        plt.sca(ax4)
        plt.plot(age_bins, light_weights_age_bin, lw=2, color='black')
        ax4.set_ylim(bottom=0)
        ax4.set_xlim(left=np.min(age_bins))
        ax4.set_xlim(right=np.max(age_bins))

        if lg_age:
            plt.xlabel("lg Age (dex)", fontsize=11)
        else:
            plt.xlabel("Age (Gyr)", fontsize=11)
        plt.ylabel("Fractional luminosity", fontsize=11)
        plt.title('Luminosity weighted', fontsize=10)

        # mass SFH
        ax5 = fig2.add_subplot(gs2[0, 1])
        plt.sca(ax5)
        plt.plot(age_bins, mass_weights_age_bin, lw=2, color='black')
        ax5.set_ylim(bottom=0)
        ax5.set_xlim(left=np.min(age_bins))
        ax5.set_xlim(right=np.max(age_bins))

        if lg_age:
            plt.xlabel("lg Age (dex)", fontsize=11)
        else:
            plt.xlabel("Age (Gyr)", fontsize=11)
        plt.ylabel("Fractional mass", fontsize=11)
        plt.title('Mass weighted', fontsize=10)

        # cumulative luminosity
        ax6 = fig2.add_subplot(gs2[1, 0])
        plt.sca(ax6)
        plt.plot(age_bins, cumulative_light, lw=2, color='black')
        ax6.set_ylim(bottom=0)
        ax6.set_xlim(left=np.min(age_bins))
        ax6.set_xlim(right=np.max(age_bins))

        if lg_age:
            plt.xlabel("lg Age (dex)", fontsize=11)
        else:
            plt.xlabel("Age (Gyr)", fontsize=11)
        plt.ylabel("Cumulative luminosity", fontsize=11)

        # cumulative mass SFH
        ax7 = fig2.add_subplot(gs2[1, 1])
        plt.sca(ax7)
        plt.plot(age_bins, cumulative_mass, lw=2, color='black')
        ax7.set_ylim(bottom=0)
        ax7.set_xlim(left=np.min(age_bins))
        ax7.set_xlim(right=np.max(age_bins))

        if lg_age:
            plt.xlabel("lg Age (dex)", fontsize=11)
        else:
            plt.xlabel("Age (Gyr)", fontsize=11)
        plt.ylabel("Cumulative mass", fontsize=11)

        # light met
        ax8 = fig2.add_subplot(gs2[2, 0])
        plt.sca(ax8)
        plt.plot(met_bins, light_weights_met_bin, lw=2, color='black')
        ax8.set_ylim(bottom=0)
        ax8.set_xlim(left=np.min(met_bins))
        ax8.set_xlim(right=np.max(met_bins))
        plt.xlabel("[M/H] (dex)", fontsize=11)
        plt.ylabel("Fractional luminosity", fontsize=11)

        # light met
        ax9 = fig2.add_subplot(gs2[2, 1])
        plt.sca(ax9)
        plt.plot(met_bins, mass_weights_met_bin, lw=2, color='black')
        ax9.set_ylim(bottom=0)
        ax9.set_xlim(left=np.min(met_bins))
        ax9.set_xlim(right=np.max(met_bins))
        plt.xlabel("[M/H] (dex)", fontsize=11)
        plt.ylabel("Fractional mass", fontsize=11)


        plt.tight_layout()


        if save_plot:
            fig.savefig(result_plot_dir + '/SFH_weights_' + spec_name + '.png', format='png', dpi=300)
            fig2.savefig(result_plot_dir + '/SFH_history_' + spec_name + '.png', format='png', dpi=300)
            plt.close(fig)
            plt.close(fig2)
        else:
            plt.show()
            plt.close('all')


        #In case of sMILES SSPs, I show also the [alpha/Fe]-[M/H] plot in another window
        if stellar_library == 'sMILES' and not custom_emiles:
            plt.figure(figsize=(12, 4))
            plt.subplot(121)
            template.plot_alpha_weights(light_weights, alpha_grid, met_grid, cmap='BuPu', title = 'Luminosity fraction')
            plt.plot(info_pop[1], info_pop[2], 'ro')

            plt.subplot(122)
            template.plot_alpha_weights(mass_weights, alpha_grid, met_grid, cmap='BuPu', title = 'Mass fraction')

            if save_plot:
                plt.savefig(result_plot_dir + '/'+ 'pop_pop_alpha_weights_'+ spec_name + '.png', format='png', dpi=300)
                plt.close()
            else:
                plt.show()
                plt.close()


    #UNCERTAINTIES WITH BOOTSTRAP!
    if with_errors:
        print('Estimating the uncertainties with bootstrapping')
        print('')
        bestfit0 = pp.bestfit.copy()
        resid = galaxy - bestfit0
        start = pp.sol.copy()
        np.random.seed(123)

        weights_array = np.empty((nrand, pp.weights.size))
        age_dist = []
        met_dist = []
        alpha_dist = []
        mass_age_dist = []
        mass_met_dist = []
        mass_alpha_dist = []

        mass_weights_age_bin_dist = []
        light_weights_age_bin_dist = []
        cumulative_mass_dist = []
        cumulative_light_dist = []

        for j in range(nrand):
            galaxy1 = bootstrap_residuals(bestfit0, resid)

            t = clock() #starting the clock

            #finally fitting
            if gas:
                pp = ppxf(templates, galaxy1, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=sps.lam_temp, regul =5,
                    reg_dim=reg_dim,
                    component=component, gas_component=gas_component,
                    gas_names=gas_names, dust=dust, quiet =1)

            else:
                pp = ppxf(templates, galaxy1, noise, velscale, start, goodpixels = goodpix,
                    moments=moments, degree=additive_degree, mdegree=multiplicative_degree,
                    lam=wave, lam_temp=sps.lam_temp, regul =5,
                    reg_dim=reg_dim,
                    component=component, dust = dust, quiet =1)


            print(f"{j + 1}/{nrand}: Elapsed time in pPXF: {clock() - t:.2f} s")

            #setting up the result parameters
            light_weights_err = pp.weights[~gas_component]
            light_weights_err = light_weights_err.reshape(reg_dim)
            light_weights_err /= light_weights_err.sum()

            mass_weights_err = light_weights_err/sps.flux
            mass_weights_err /= mass_weights_err.sum()              # Normalize to mass fractions

            if custom_emiles or stellar_library in ['sMILES', 'xshooter']:
                info_pop_err = sps.mean_age_metal(light_weights_err, lg_age, lg_met)
                info_pop_mass_err = sps.mean_age_metal(mass_weights_err, lg_age, lg_met)
                mass_light_err = 0
            else:
                info_pop_err = sps_data_ppxf.mean_age_metal(light_weights_err, lg_age, lg_met)
                info_pop_mass_err = sps_data_ppxf.mean_age_metal(mass_weights_err, lg_age, lg_met)
                mass_light_err = sps.mass_to_light(mass_weights_err, band="v")


            if stellar_library == 'sMILES' and not custom_emiles:
                alpha_dist.append(info_pop_err[2])
                mass_alpha_dist.append(info_pop_mass_err[2])

                reduced_mass_weights_err = np.sum(mass_weights_err, axis=2)
                mass_weights_age_bin_err = np.sum(reduced_mass_weights_err, axis=1)[::-1]
                # mass_weights_met_bin_err = np.sum(reduced_mass_weights, axis=0)[::-1]

                reduced_light_weights_err = np.sum(light_weights_err, axis=2)
                light_weights_age_bin_err = np.sum(reduced_light_weights_err, axis=1)[::-1]
                # light_weights_met_bin_err = np.sum(reduced_light_weights, axis=0)[::-1]

                mass_weights_age_bin_dist.append(mass_weights_age_bin_err)
                light_weights_age_bin_dist.append(light_weights_age_bin_err)



            else:
                mass_weights_age_bin_err = np.sum(mass_weights_err, axis=1)[::-1]
                light_weights_age_bin_err = np.sum(light_weights_err, axis=1)[::-1]

                mass_weights_age_bin_dist.append(mass_weights_age_bin_err)
                light_weights_age_bin_dist.append(light_weights_age_bin_err)

            cumulative_mass_err = np.cumsum(mass_weights_age_bin_err)
            cumulative_light_err = np.cumsum(light_weights_age_bin_err)

            cumulative_mass_dist.append(cumulative_mass_err)
            cumulative_light_dist.append(cumulative_light_err)

            age_dist.append(info_pop_err[0])
            met_dist.append(info_pop_err[1])
            mass_age_dist.append(info_pop_mass_err[0])
            mass_met_dist.append(info_pop_mass_err[1])




        # ---------- CONVERT BOOTSTRAP RESULTS TO ARRAYS ----------
        age_dist = np.array(age_dist)  # shape (nrand, N_age)
        met_dist = np.array(met_dist)
        mass_age_dist = np.array(mass_age_dist)
        mass_met_dist = np.array(mass_met_dist)

        # calculating the standard deviation
        age_err = np.std(age_dist)
        met_err = np.std(met_dist)
        mass_age_err = np.std(mass_age_dist)
        mass_met_err = np.std(mass_met_dist)


        # for the sMILES models I also have the alpha/Fe to consider
        if stellar_library == 'sMILES' and not custom_emiles:

            alpha_dist = np.array(alpha_dist)
            mass_alpha_dist = np.array(mass_alpha_dist)
            alpha_err = np.std(alpha_dist)
            mass_alpha_err = np.std(mass_alpha_dist)

        else:
            alpha_err = 0
            mass_alpha_err = 0


        # ---------- CONVERT BOOTSTRAP RESULTS TO ARRAYS ----------
        mass_weights_age_bin_dist = np.array(mass_weights_age_bin_dist)  # shape (nrand, N_age)
        light_weights_age_bin_dist = np.array(light_weights_age_bin_dist)
        cumulative_mass_dist = np.array(cumulative_mass_dist)
        cumulative_light_dist = np.array(cumulative_light_dist)

        # ---------- CALCOLO MEDIA E DEVIAZIONE STANDARD ----------
        # mass_weights_age_mean = np.mean(mass_weights_age_bin_dist, axis=0)
        mass_weights_age_std = np.std(mass_weights_age_bin_dist, axis=0)

        # light_weights_age_mean = np.mean(light_weights_age_bin_dist, axis=0)
        light_weights_age_std = np.std(light_weights_age_bin_dist, axis=0)

        # cumulative_mass_mean = np.mean(cumulative_mass_dist, axis=0)
        cumulative_mass_std = np.std(cumulative_mass_dist, axis=0)

        # cumulative_light_mean = np.mean(cumulative_light_dist, axis=0)
        cumulative_light_std = np.std(cumulative_light_dist, axis=0)

        print('')
        print(f"Error luminosity age: ({age_err:.4g})")
        print(f"Error luminosity met (dex)): ({met_err:.4g})")
        print(f"Error mass age: ({mass_age_err:.4g})")
        print(f"Error mass met (dex)): ({mass_met_err:.4g})")
        if stellar_library == 'sMILES' and not custom_emiles:
            print(f"Error luminosity alpha/Fe (dex): ({alpha_err:.4g})")
            print(f"Error mass alpha/Fe (dex): ({mass_alpha_err:.4g})")



    plt.close()

    return kinematics, info_pop, info_pop_mass, mass_light, errors, galaxy, bestfit_flux, bestfit_wave, bestfit_gas_flux, residual, chi_square, age_err, met_err, alpha_err, mass_age_err, mass_met_err, mass_alpha_err, emission_corrected_flux, age_bins, light_weights_age_bin, mass_weights_age_bin, cumulative_mass, light_weights_age_std, mass_weights_age_std, cumulative_light_std, cumulative_mass_std, snr, light_weights, mass_weights, t50_age, t80_age, t50_cosmic, t80_cosmic




#*****************************************************************************************************
# 10) Function to calculate t50 and t80 formation times from the SFH calculated by pPXF.
def calculate_t50_t80_cosmic(age_array, mass_cumulative_array, redshift, lg_age):
    """
    Calculate t50 and t80 (age-based and cosmic-time) from cumulative mass SFH.

    Parameters
    ----------
    age_array : array-like
        Stellar population ages in Gyr (increasing or decreasing).
    mass_cumulative_array : array-like
        Cumulative mass fraction (should go from 0 to 1).
    redshift : float
        Redshift of the galaxy.

    Returns
    -------
    t50_age : float
        Age of the stellar population when 50% of the mass formed [Gyr ago].
    t80_age : float
        Age of the stellar population when 80% of the mass formed [Gyr ago].
    t50_cosmic : float
        Time since Big Bang when 50% of the mass formed [Gyr].
    t80_cosmic : float
        Time since Big Bang when 80% of the mass formed [Gyr].
    """

    if lg_age:
        age_array = 10**np.array(age_array)/1e9

    # Ensure inputs are increasing in time (from youngest to oldest)
    if age_array[0] > age_array[-1]:
        age_array = age_array[::-1]
        mass_cumulative_array = mass_cumulative_array[::-1]

    # Interpolation function: cumulative mass -> age
    interp_func = interp1d(mass_cumulative_array, age_array, bounds_error=False, fill_value="extrapolate")

    # Get ages corresponding to 50% and 80% of mass formed
    t50_age = float(interp_func(0.5))  # Gyr ago
    t80_age = float(interp_func(0.8))

    # Age of the universe at given redshift
    t_universe_at_z = cosmo.age(redshift).value  # Gyr

    # Convert to cosmic time
    t50_cosmic = t_universe_at_z - t50_age
    t80_cosmic = t_universe_at_z - t80_age

    # Warning in case the spectra loaded are already been restframe corrected. In this case, the t50 and t80 cosmig times ages are not reliable, unless you are analysing very close (e.g. Andromeda) galaxies.
    if redshift == 0:
        print ('WARNING: Your spectra are likely restframe corrected. t50_cosmic and t80_cosmic values are NOT accurate')

    return t50_age, t80_age, t50_cosmic, t80_cosmic





#*****************************************************************************************************
# 11) Modified emission line list from the ppxf_util.py of the ppxf package.
def emission_lines(ln_lam_temp, lam_range_gal, FWHM_gal, pixel=True,
                   tie_balmer=False, limit_doublets=False, vacuum=False, wave_galaxy = None):
    """
    Generates an array of Gaussian emission lines to be used as gas templates in PPXF.

    Daniele Gasparri:
    Added the 'wave_galaxy' array, which is the galaxy wavelength array, needed to compute the FWHM_gal values in the gas
    emission lines when the FWHM_gal is not constant (i.e. when we are working with spectra with
    a fixed resolving power R. Needed for stars and gas kinematics task when selecting 'Spec. constant R resolution:'.)

    ****************************************************************************
    ADDITIONAL LINES CAN BE ADDED BY EDITING THE CODE OF THIS PROCEDURE, WHICH
    IS MEANT AS A TEMPLATE TO BE COPIED AND MODIFIED BY THE USERS AS NEEDED.
    ****************************************************************************


    Output Parameters
    -----------------

    emission_lines: ndarray
        Array of dimensions ``[ln_lam_temp.size, line_wave.size]`` containing
        the gas templates, one per array column.

    line_names: ndarray
        Array of strings with the name of each line, or group of lines'

    line_wave: ndarray
        Central wavelength of the lines, one for each gas template'

    """
    #        Balmer:     H10       H9         H8        Heps    Hdelta    Hgamma    Hbeta     Halpha
    balmer = np.array([3798.983, 3836.479, 3890.158, 3971.202, 4102.899, 4341.691, 4862.691, 6564.632])  # vacuum wavelengths

    if tie_balmer:

        # Balmer decrement for Case B recombination (T=1e4 K, ne=100 cm^-3)
        # from Storey & Hummer (1995) https://ui.adsabs.harvard.edu/abs/1995MNRAS.272...41S
        # In electronic form https://cdsarc.u-strasbg.fr/viz-bin/Cat?VI/64
        # See Table B.7 of Dopita & Sutherland 2003 https://www.amazon.com/dp/3540433627
        # Also see Table 4.2 of Osterbrock & Ferland 2006 https://www.amazon.co.uk/dp/1891389343/
        wave = balmer
        if not vacuum:
            wave = util.vac_to_air(wave)

        #if FWHM_gal is an array, I need to extract the FWHM values corresponding to the emission lines of the gas template
        if isinstance(FWHM_gal, np.ndarray):
            FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel)
        else:
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel)

        ratios = np.array([0.0530, 0.0731, 0.105, 0.159, 0.259, 0.468, 1, 2.86])
        ratios *= wave[-2]/wave  # Account for varying log-sampled pixel size in Angstrom
        emission_lines = gauss @ ratios
        line_names = ['Balmer']
        w = (lam_range_gal[0] < wave) & (wave < lam_range_gal[1])
        line_wave = np.mean(wave[w]) if np.any(w) else np.mean(wave)

    else:

        line_wave = balmer
        if not vacuum:
            line_wave = util.vac_to_air(line_wave)
        line_names = ['(H10)', '(H9)', '(H8)', '(Heps)', '(Hdelta)', '(Hgamma)', '(Hbeta)', '(Halpha)']

        #if FWHM_gal is an array, I need to extract the FWHM values corresponding to the emission lines of the gas template
        if isinstance(FWHM_gal, np.ndarray):
            FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in line_wave])
            emission_lines = util.gaussian(ln_lam_temp, line_wave, FWHM_gal_line, pixel)
        else:
            emission_lines = util.gaussian(ln_lam_temp, line_wave, FWHM_gal, pixel)


    if limit_doublets:

        # The line ratio of this doublet lam3727/lam3729 is constrained by
        # atomic physics to lie in the range 0.28--1.47 (e.g. fig.5.8 of
        # Osterbrock & Ferland 2006 https://www.amazon.co.uk/dp/1891389343/).
        # We model this doublet as a linear combination of two doublets with the
        # maximum and minimum ratios, to limit the ratio to the desired range.
        #       -----[OII]-----
        wave = [3727.092, 3729.875]    # vacuum wavelengths
        if not vacuum:
            wave = util.vac_to_air(wave)
        names = ['[OII]3726_d1', '[OII]3726_d2']

        if isinstance(FWHM_gal, np.ndarray):
            FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel)
        else:
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel)

        doublets = gauss @ [[1, 1], [0.28, 1.47]]  # produces *two* doublets
        emission_lines = np.column_stack([emission_lines, doublets])
        line_names = np.append(line_names, names)
        line_wave = np.append(line_wave, wave)

        # The line ratio of this doublet lam6717/lam6731 is constrained by
        # atomic physics to lie in the range 0.44--1.43 (e.g. fig.5.8 of
        # Osterbrock & Ferland 2006 https://www.amazon.co.uk/dp/1891389343/).
        # We model this doublet as a linear combination of two doublets with the
        # maximum and minimum ratios, to limit the ratio to the desired range.
        #        -----[SII]-----
        wave = [6718.294, 6732.674]    # vacuum wavelengths
        if not vacuum:
            wave = util.vac_to_air(wave)
        names = ['[SII]6731_d1', '[SII]6731_d2']

        #if FWHM_gal is an array, I need to extract the FWHM values corresponding to the emission lines of the gas template
        if isinstance(FWHM_gal, np.ndarray):
            FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel)
        else:
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel)

        doublets = gauss @ [[0.44, 1.43], [1, 1]]  # produces *two* doublets
        emission_lines = np.column_stack([emission_lines, doublets])
        line_names = np.append(line_names, names)
        line_wave = np.append(line_wave, wave)

    else:

        # Here the two doublets are free to have any ratio
        #         -----[OII]-----     -----[SII]-----
        # wave = [3727.092, 3729.875, 6718.294, 6732.674]  # vacuum wavelengths
        wave = [3727.092, 3729.875, 5198.4, 5201.35, 6718.294, 6732.674]  # vacuum wavelengths with NI "empirical"
        # wave = [3727.092, 3729.875, 5196.45, 5198.94, 6718.294, 6732.674] #right NI wavelengths from the emission file of GIST
        if not vacuum:
            wave = util.vac_to_air(wave)
        # names = ['[OII]3726', '[OII]3729', '[SII]6716', '[SII]6731']
        names = ['[OII]3726', '[OII]3729', '[NI]5196', '[NI]5198', '[SII]6716', '[SII]6731']

        #if FWHM_gal is an array, I need to extract the FWHM values corresponding to the emission lines of the gas template
        if isinstance(FWHM_gal, np.ndarray):
            FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel)
        else:
            gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel)

        emission_lines = np.column_stack([emission_lines, gauss])
        line_names = np.append(line_names, names)
        line_wave = np.append(line_wave, wave)

    # Here the lines are free to have any ratio
    #       -----[NeIII]-----    HeII      HeI
    wave = [3968.59, 3869.86, 4687.015, 5877.243]  # vacuum wavelengths
    if not vacuum:
        wave = util.vac_to_air(wave)
    names = ['[NeIII]3968', '[NeIII]3869', '-HeII4687-', '-HeI5876-']

    if isinstance(FWHM_gal, np.ndarray):
        FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
        gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel)
    else:
        gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel)

    emission_lines = np.column_stack([emission_lines, gauss])
    line_names = np.append(line_names, names)
    line_wave = np.append(line_wave, wave)

    # NIR H lines
    #       paeps      pad      pab
    wave = [10052.1, 10941.1, 12821.6]  # vacuum wavelengths
    if not vacuum:
        wave = util.vac_to_air(wave)
    names = ['-PaEps-', '-Pad-', '-Pab-']

    if isinstance(FWHM_gal, np.ndarray):
        FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
        gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel)
    else:
        gauss = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel)

    emission_lines = np.column_stack([emission_lines, gauss])
    line_names = np.append(line_names, names)
    line_wave = np.append(line_wave, wave)



    ######### Doublets with fixed ratios #########

    # To keep the flux ratio of a doublet fixed, we place the two lines in a single template
    #        -----[OIII]-----
    wave = [4960.295, 5008.240]    # vacuum wavelengths
    if not vacuum:
        wave = util.vac_to_air(wave)


    if isinstance(FWHM_gal, np.ndarray):
        FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
        doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel) @ [0.33, 1]
    else:
        doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel) @ [0.33, 1]



    # doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel) @ [0.33, 1]
    emission_lines = np.column_stack([emission_lines, doublet])
    line_names = np.append(line_names, '[OIII]5007_d')  # single template for this doublet
    line_wave = np.append(line_wave, wave[1])

    # To keep the flux ratio of a doublet fixed, we place the two lines in a single template
    #        -----[OI]-----
    wave = [6302.040, 6365.535]    # vacuum wavelengths
    if not vacuum:
        wave = util.vac_to_air(wave)



    if isinstance(FWHM_gal, np.ndarray):
        FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
        doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel) @ [1, 0.33]
    else:
        doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel) @ [1, 0.33]



    # doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel) @ [1, 0.33]
    emission_lines = np.column_stack([emission_lines, doublet])
    line_names = np.append(line_names, '[OI]6300_d')  # single template for this doublet
    line_wave = np.append(line_wave, wave[0])

    # To keep the flux ratio of a doublet fixed, we place the two lines in a single template
    #       -----[NII]-----
    wave = [6549.860, 6585.271]    # air wavelengths
    if not vacuum:
        wave = util.vac_to_air(wave)



    if isinstance(FWHM_gal, np.ndarray):
        FWHM_gal_line = np.array([FWHM_gal[find_nearest(wave_galaxy, lw)] for lw in wave])
        doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal_line, pixel) @ [0.33, 1]
    else:
        doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel) @ [0.33, 1]


    # doublet = util.gaussian(ln_lam_temp, wave, FWHM_gal, pixel) @ [0.33, 1]
    emission_lines = np.column_stack([emission_lines, doublet])
    line_names = np.append(line_names, '[NII]6583_d')  # single template for this doublet
    line_wave = np.append(line_wave, wave[1])

    # Only include lines falling within the estimated fitted wavelength range.
    #
    w = (lam_range_gal[0] < line_wave) & (line_wave < lam_range_gal[1])
    emission_lines = emission_lines[:, w]
    line_names = line_names[w]
    line_wave = line_wave[w]

    print('Emission lines included in gas templates:')
    print(line_names)

    return emission_lines, line_names, line_wave




#*****************************************************************************************************
# 12) stellar populations with LICK and ssp models

def lick_pop(ssp_lick_indices, ssp_lick_indices_err, ssp_model_name, interp_model):


    """
     This function calculates the properties of the stellar populations of
     galaxies via interpolation of the Lick/IDS indices Hbeta-[MgFe]' and Fem - Mgb
     using the Lick/IDS indices measured in a galaxy spectrum and the Lick/IDS indices
     measured for the following SSP models: Thomas2010 (published in Thomas et al. 2011),
     Xshooter SSP library (XSL) of Verro et al. 2022, MILES and sMILES models, all with Salpeter IMF.
     The interpolation between the measured and model Lick/IDS indices is carried out in two ways:
     1) Linear n-dimensional interpolation using the griddata function and 2) via
     Gaussian Process Regression (GPR) machine learning based model. This latter model gives
     generally better and much faster results. The learning models as well as the Lick/IDS indices measured
     for the SSP models used have been calculated with SPAN and are stored in the system_files subdirectory.
     Input: array of the Lick/IDS indices used for interpolation and measured from the galaxy spectrum,
            array of the uncertainties of the same indices, string SSP model name, string interpolation
            model to use for interpolation.
     Output: float interpolated age (in Gyr), float interpolated metallicity (dex), float
             interpolated alpha/Fe (where available, dex), float error in age, float error
             in metallicity, float error in alpha/Fe (if available).
    """


    #loading the Lick/IDS indices for the selected SSP model
    ssp_models_folder = 'system_files/'
    ssp_model_file = ssp_models_folder + ssp_model_name + '_lick.txt'
    ssp_model_file = os.path.join(BASE_DIR, ssp_model_file )

    #loading the model
    ssp_lick = np.loadtxt(ssp_model_file, delimiter=' ')

    #loading the model data in sigle arrays
    age_teo, met_teo, alpha_teo, hb_teo, mg2_teo, mgb_teo, fe5270_teo, fe5335_teo, fem_teo, mgfe_teo = ssp_lick.T

    #extracting single indices and the uncertanties
    Hbeta = ssp_lick_indices[0]
    MgFe = ssp_lick_indices[1]
    Fem = ssp_lick_indices[2]
    Mgb = ssp_lick_indices[3]

    Hbetae = ssp_lick_indices_err[0]
    MgFee = ssp_lick_indices_err[1]
    Feme = ssp_lick_indices_err[2]
    Mgbe = ssp_lick_indices_err[3]


    if ssp_model_name == 'Thomas2010' or ssp_model_name == 'miles' or ssp_model_name == 'smiles':

        #interpolate
        print('')
        print('Interpolating the values...')
        values = np.column_stack((age_teo, met_teo, alpha_teo))
        lick_indices_ml = np.array([[Hbeta, MgFe, Fem, Mgb]])
        if interp_model == 'griddata':
            #interpolation with griddata
            print('With griddata function')

            results = griddata((hb_teo, mgfe_teo, fem_teo, mgb_teo), values, lick_indices_ml, method='linear')
            age_oss = results[:, 0]
            met_oss = results[:, 1]
            alpha_oss = results[:, 2]

            age_interp = age_oss[0]
            met_interp = met_oss[0]
            alpha_interp = alpha_oss[0]

            #Uncertainties
            print('')
            print('Calculating the uncertainties...')
            sim_number = 10

            #define the arrays containing normal fluctuations of the EW of the indices with respect to their errors
            Hbeta_sim_array = np.random.normal(loc=Hbeta, scale=Hbetae, size=sim_number)
            MgFe_sim_array = np.random.normal(loc=MgFe, scale=MgFee, size=sim_number)
            Fem_sim_array = np.random.normal(loc=Fem, scale=Feme, size=sim_number)
            Mgb_sim_array = np.random.normal(loc=Mgb, scale=Mgbe, size=sim_number)

            #preparing the array of the stellar population simulated parameters
            age_sim = []
            met_sim = []
            alpha_sim = []

            #doing the simulation
            for g in range (sim_number):

                #points to interpolate
                points_for_param_sim = np.column_stack((Hbeta_sim_array[g], MgFe_sim_array[g], Fem_sim_array[g], Mgb_sim_array[g]))

                # Interpolate
                age_sim.append(griddata((hb_teo, mgfe_teo, fem_teo, mgb_teo), age_teo, points_for_param_sim, method='linear'))
                met_sim.append(griddata((hb_teo, mgfe_teo, fem_teo, mgb_teo), met_teo, points_for_param_sim, method='linear'))
                alpha_sim.append(griddata((hb_teo, mgfe_teo, fem_teo, mgb_teo), alpha_teo, points_for_param_sim, method='linear'))

            #remove the nan
            age_sim = [value for value in age_sim if not np.isnan(value)]
            met_sim = [value for value in met_sim if not np.isnan(value)]
            alpha_sim = [value for value in alpha_sim if not np.isnan(value)]

            #finally calculating the std and associate that to the error in age, met and alpha
            err_age = np.std(age_sim)
            err_met = np.std(met_sim)
            err_alpha = np.std(alpha_sim)


        if interp_model == 'GPR':
            # TEST INTERPOLATION WITH MACHINE LEARNING
            # File names for the trained models
            model_age_file = os.path.join(BASE_DIR, "system_files", ssp_model_name + "_gpr_age_model.pkl" )
            model_met_file = os.path.join(BASE_DIR, "system_files", ssp_model_name + "_gpr_met_model.pkl" )
            model_alpha_file = os.path.join(BASE_DIR, "system_files", ssp_model_name + "_gpr_alpha_model.pkl" )

            # Kernel with initial parameters
            print('With Gaussian Process Regression (GPR)')
            kernel = C(1.0, (1e-4, 4e1)) * RBF(1.0, (1e-4, 4e1))

            #better kernel for age
            kernel_age = C(1.0, (1e-4, 1e2)) * Matern(length_scale=1.0, length_scale_bounds=(1e-4, 1e2), nu=1.5)

            # Function to traing and save the model
            def train_and_save_model(X_train, y_train, kernel, filename, alpha):
                gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, alpha=alpha)
                gpr.fit(X_train, y_train)
                joblib.dump(gpr, filename)
                return gpr

            # Load of train the model, if not already saved to the disc
            if os.path.exists(model_age_file) and os.path.exists(model_met_file) and os.path.exists(model_alpha_file):
                print('Loading trained models...')
                gpr_age = joblib.load(model_age_file)
                gpr_met = joblib.load(model_met_file)
                gpr_alpha = joblib.load(model_alpha_file)
            else:
                print('Training models...')
                X_train = np.column_stack((hb_teo, mgfe_teo, fem_teo, mgb_teo))
                gpr_age = train_and_save_model(X_train, age_teo, kernel_age, model_age_file, Hbetae)
                gpr_met = train_and_save_model(X_train, met_teo, kernel, model_met_file, MgFee)
                gpr_alpha = train_and_save_model(X_train, alpha_teo, kernel, model_alpha_file, Feme)

            # Interpolation and uncertainties with the trained model
            print('Now interpolating...')
            age_interp, err_age = gpr_age.predict(lick_indices_ml, return_std=True)
            met_interp, err_met = gpr_met.predict(lick_indices_ml, return_std=True)
            alpha_interp, err_alpha = gpr_alpha.predict(lick_indices_ml, return_std=True)

            age_interp = age_interp[0]
            met_interp = met_interp[0]
            alpha_interp = alpha_interp[0]
            err_age = err_age[0]
            err_met = err_met[0]
            err_alpha = err_alpha[0]


        if interp_model == 'MCMC':
            print("Estimating with MCMC (classic: Age,Z from Hβ–[MgFe]' + α from Mgb–<Fe>; diagonal Σ)...")
            
            # ------------------------------- Observables (Å) --------------------------------
            # Order: [Hβ, [MgFe]', <Fe>, Mgb]
            obs  = np.array([Hbeta,  MgFe,  Fem,  Mgb],  dtype=float)
            errs = np.array([Hbetae, MgFee, Feme, Mgbe], dtype=float)

            # ---------------------- Fast per-index range gate (skip MCMC) --------------------
            idx_mins = np.array([
                float(np.nanmin(hb_teo)),
                float(np.nanmin(mgfe_teo)),   # [MgFe]'
                float(np.nanmin(fem_teo)),
                float(np.nanmin(mgb_teo)),
            ])
            idx_maxs = np.array([
                float(np.nanmax(hb_teo)),
                float(np.nanmax(mgfe_teo)),
                float(np.nanmax(fem_teo)),
                float(np.nanmax(mgb_teo)),
            ])
            span = idx_maxs - idx_mins

            k_sigma  = 3.0
            frac_pad = 0.02
            pad = np.maximum(k_sigma * errs, frac_pad * np.maximum(span, 1e-12))

            inside_all = np.all((obs >= idx_mins - pad) & (obs <= idx_maxs + pad))
            if not inside_all:
                age_interp = met_interp = alpha_interp = np.nan
                err_age = err_met = err_alpha = np.nan
                print(f"MCMC: indices outside model ranges (with {k_sigma}σ/{int(frac_pad*100)}% pad) -> NaN; skipping MCMC.")
            else:
                # -------------------- FAIL-FAST: convex hull via griddata(linear) --------------------
                # If griddata(linear) returns NaN, the point is outside the convex hull -> skip MCMC
                def _safe_isfinite(v):
                    v = np.asarray(v, dtype=float)
                    return np.all(np.isfinite(v))

                values  = np.column_stack((age_teo, met_teo, alpha_teo))            # (N,3)
                points4 = np.column_stack((hb_teo, mgfe_teo, fem_teo, mgb_teo))     # (N,4)
                qpt     = np.array([[Hbeta, MgFe, Fem, Mgb]], dtype=float)          # (1,4)

                res_gd = None
                try:
                    res_gd = griddata(points4, values, qpt, method='linear')
                except Exception:
                    res_gd = None

                if (res_gd is None) or (not _safe_isfinite(res_gd)):
                    # Hard skip: outside convex hull -> return NaNs
                    age_interp = met_interp = alpha_interp = np.nan
                    err_age = err_met = err_alpha = np.nan
                    print("MCMC: griddata(linear) -> NaN (outside convex hull). Returning NaNs; skipping MCMC.")
                else:
                    # ---------------------------- Domain & scaling (log age) ----------------------------
                    age_min_lin, age_max_lin = float(np.nanmin(age_teo)),   float(np.nanmax(age_teo))
                    zh_min,      zh_max      = float(np.nanmin(met_teo)),   float(np.nanmax(met_teo))
                    alpha_min,   alpha_max   = float(np.nanmin(alpha_teo)), float(np.nanmax(alpha_teo))

                    log_age_teo = np.log10(np.asarray(age_teo, dtype=float))
                    age_min_log, age_max_log = float(np.nanmin(log_age_teo)), float(np.nanmax(log_age_teo))

                    def _scale_params(loga, z, al):
                        """Scale (logAge, Z/H, α/Fe) independently to [0,1]."""
                        sa  = (loga - age_min_log) / max(age_max_log - age_min_log, 1e-12)
                        sz  = (z    - zh_min)      / max(zh_max - zh_min,           1e-12)
                        sal = (al   - alpha_min)   / max(alpha_max - alpha_min,     1e-12)
                        return sa, sz, sal

                    points_scaled = np.column_stack(_scale_params(log_age_teo, met_teo, alpha_teo))

                    # ---------------------------- Strict interpolators (hull-safe) -----------------------
                    interp_Hb    = LinearNDInterpolator(points_scaled, np.asarray(hb_teo,    dtype=float))
                    interp_MgFeP = LinearNDInterpolator(points_scaled, np.asarray(mgfe_teo,  dtype=float))  # [MgFe]'
                    interp_Fem   = LinearNDInterpolator(points_scaled, np.asarray(fem_teo,   dtype=float))
                    interp_Mgb   = LinearNDInterpolator(points_scaled, np.asarray(mgb_teo,   dtype=float))

                    def _eval_model_indices_full(age_lin, zh, alpha):
                        """
                        Return model vector [Hβ, [MgFe]', <Fe>, Mgb] (Å) at (Age[Gyr], Z/H, α/Fe).
                        Returns NaNs if outside the convex hull (interpolators are strict).
                        """
                        if not np.isfinite(age_lin) or age_lin <= 0:
                            return np.array([np.nan, np.nan, np.nan, np.nan], dtype=float)
                        loga = np.log10(age_lin)
                        sa  = (loga - age_min_log) / (age_max_log - age_min_log + 1e-12)
                        sz  = (zh   - zh_min)      / (zh_max - zh_min + 1e-12)
                        sal = (alpha - alpha_min)  / (alpha_max - alpha_min + 1e-12)
                        Xs = np.array([sa, sz, sal], dtype=float)

                        hb   = interp_Hb(Xs)
                        mgfp = interp_MgFeP(Xs)   # theoretical [MgFe]' from grid
                        fem  = interp_Fem(Xs)
                        mgb  = interp_Mgb(Xs)

                        vals = np.array([hb, mgfp, fem, mgb], dtype=float)
                        return vals if np.all(np.isfinite(vals)) else np.array([np.nan, np.nan, np.nan, np.nan], dtype=float)

                    # ----------------------------- Observational covariance Σ -----------------------------
                    # Diagonal Σ with a small calibration floor to absorb Lick zero-point
                    sigma_cal = np.array([0.00, 0.04, 0.05, 0.05], dtype=float)  # [Hb, [MgFe]', <Fe>, Mgb]
                    sigma = np.sqrt(errs**2 + sigma_cal**2)

                    # Per-index weights (w>1 => più peso / varianza effettiva minore)
                    w = np.array([1.00, 1.45, 0.90, 1.15], dtype=float)  # Hb, [MgFe]', <Fe>, Mgb
                    sigma_eff = sigma / w

                    Sigma = np.diag(sigma_eff**2).astype(float)
                    tiny = max(3e-6, 1e-6 * float(np.nanmedian(sigma_eff)))**2
                    for i in range(4):
                        Sigma[i, i] += tiny

                    var_eps = (1e-6 * float(np.nanmedian(errs)))**2   # minimal numeric floor

                    # ----------------------------- Helpers (robust shapes/dtypes) -------------------------
                    def _as_vec4(x):
                        """Return a 1D float vector of length 4 (truncate/pad if needed)."""
                        v = np.asarray(x, dtype=float).reshape(-1)
                        if v.size >= 4:
                            return v[:4]
                        out = np.full(4, np.nan, dtype=float)
                        out[:v.size] = v
                        return out

                    def _mvnorm_loglike(resid_in, Sigma_base):
                        """
                        Multivariate normal log-like N(0, Σ) with fixed diagonal Σ (classic chi²).
                        """
                        r = _as_vec4(resid_in)
                        if not np.all(np.isfinite(r)):
                            return -np.inf

                        S = np.asarray(Sigma_base, dtype=float)
                        if S.shape != (4, 4):
                            S = S.reshape(4, 4)
                        for i in range(4):
                            S[i, i] += var_eps

                        try:
                            L = np.linalg.cholesky(S)
                            Linv = np.linalg.inv(L)
                            S_inv = Linv.T @ Linv
                            logdet = 2.0 * np.sum(np.log(np.diag(L)))
                        except np.linalg.LinAlgError:
                            S_inv = np.linalg.pinv(S, rcond=1e-10)
                            sign, logdet = np.linalg.slogdet(S)
                            if sign <= 0:
                                det_safe = np.linalg.det(S)
                                logdet = np.log(max(det_safe, 1e-300))

                        quad = float(np.dot(r, S_inv @ r))
                        k = 4
                        return -0.5 * (quad + logdet + k * np.log(2.0 * np.pi))

                    # ========================== STEP 1 (FORZATO): (Age,Z) = GRIDDATA ==========================
                    # Abbiamo già 'res_gd' valido qui sopra (linear). Usiamolo come seed/àncora:
                    x0 = res_gd[0]  # [age, Z/H, alpha] dal griddata linear

                    # *********** FORZA L’ÀNCORA = GRIDDATA ***********
                    loga_hat = np.log10(float(np.clip(x0[0], age_min_lin, age_max_lin)))
                    zh_hat   = float(np.clip(x0[1], zh_min, zh_max))

                    # incertezze minime (prior widths)
                    sig_loga = 0.06
                    sig_zh   = 0.04
                    sig_loga_eff = max(sig_loga, 0.05)
                    sig_zh_eff   = max(sig_zh,   0.03)

                    # ================= Alpha prior (1D fit on Mgb & <Fe> at fixed (loga_hat, zh_hat)) =================
                    USE_ALPHA_PRIOR = True
                    try:
                        from scipy.optimize import least_squares

                        def _model_Mgb_Fem(loga, zh, alpha):
                            sa  = (loga - age_min_log) / (age_max_log - age_min_log + 1e-12)
                            sz  = (zh   - zh_min)      / (zh_max - zh_min + 1e-12)
                            sal = (alpha - alpha_min)  / (alpha_max - alpha_min + 1e-12)
                            Xs = np.array([sa, sz, sal], dtype=float)
                            return float(interp_Mgb(Xs)), float(interp_Fem(Xs))

                        def _resid_alpha(a):
                            mgb_m, fem_m = _model_Mgb_Fem(loga_hat, zh_hat, a[0])
                            r_mgb = (Mgb - mgb_m) / np.sqrt(Sigma[3,3])
                            r_fem = (Fem - fem_m) / np.sqrt(Sigma[2,2])
                            return np.array([r_mgb, r_fem], dtype=float)

                        a0 = float(np.clip(x0[2], alpha_min, alpha_max))
                        ls_a = least_squares(_resid_alpha, x0=np.array([a0], float),
                                            bounds=([alpha_min],[alpha_max]), method='trf', max_nfev=150)
                        alpha_hat = float(ls_a.x[0]) if ls_a.success and np.isfinite(ls_a.x[0]) else a0

                        try:
                            J = ls_a.jac
                            JTJ = J.T @ J
                            var_a = float(1.0 / JTJ) if np.isfinite(JTJ).all() else 0.0144  # 0.12^2
                            sig_alpha = float(np.sqrt(max(var_a, 0.0144)))
                        except Exception:
                            sig_alpha = 0.12
                    except Exception:
                        alpha_hat = float(np.clip(x0[2], alpha_min, alpha_max))
                        sig_alpha = 0.12

                    # ========================== STEP 2: MCMC with informative prior ==========================

                    def log_prior(theta):
                        age, zh, alpha = theta
                        if not (age_min_lin <= age <= age_max_lin): return -np.inf
                        if not (zh_min      <= zh  <= zh_max):      return -np.inf
                        if not (alpha_min   <= alpha <= alpha_max): return -np.inf
                        loga = np.log10(age)
                        lp_age = -0.5*((loga - loga_hat)/sig_loga_eff)**2 - np.log(sig_loga_eff*np.sqrt(2*np.pi))
                        lp_zh  = -0.5*((zh   - zh_hat  )/sig_zh_eff  )**2 - np.log(sig_zh_eff  *np.sqrt(2*np.pi))
                        lp_alpha = 0.0
                        if USE_ALPHA_PRIOR:
                            lp_alpha = -0.5*((alpha - alpha_hat)/sig_alpha)**2 - np.log(sig_alpha*np.sqrt(2*np.pi))
                        return lp_age + lp_zh + lp_alpha

                    def log_likelihood(theta):
                        age, zh, alpha = theta
                        mod = _eval_model_indices_full(age, zh, alpha)
                        if np.any(~np.isfinite(mod)): return -np.inf
                        resid = _as_vec4(obs - mod)
                        return _mvnorm_loglike(resid, Sigma)

                    def log_posterior(theta):
                        lp = log_prior(theta)
                        if not np.isfinite(lp): return -np.inf
                        ll = log_likelihood(theta)
                        if not np.isfinite(ll): return -np.inf
                        return lp + ll

                    # MAP initialisation (full 3D, but anchored)
                    bounds = [(age_min_lin, age_max_lin), (zh_min, zh_max), (alpha_min, alpha_max)]
                    def _chi2(theta):
                        ll = log_likelihood(theta)
                        return 1e9 if not np.isfinite(ll) else -2.0*ll

                    x0_full = np.array([10**loga_hat, zh_hat, float(np.clip(x0[2], alpha_min, alpha_max))], dtype=float)
                    try:
                        res = minimize(_chi2, x0=x0_full, bounds=bounds, method='L-BFGS-B')
                        theta_map = res.x
                    except Exception:
                        theta_map = x0_full

                    # Reparameterised MCMC in (logAge, Z/H, α)
                    def _reflect_in_bounds(val, lo, hi):
                        rng = hi - lo
                        if rng <= 0: return lo
                        t = (val - lo) % (2.0 * rng)
                        return lo + (t if t <= rng else 2.0 * rng - t)

                    def _jitter_in_bounds(centre, lo, hi, frac=0.05):
                        sig = frac * max(1e-6, abs(centre))
                        val = np.random.normal(centre, sig)
                        return _reflect_in_bounds(val, lo, hi)

                    def _log_prior_prime(theta_prime):
                        loga, zh, alpha = theta_prime
                        if not (age_min_log <= loga <= age_max_log): return -np.inf
                        if not (zh_min <= zh <= zh_max):             return -np.inf
                        if not (alpha_min <= alpha <= alpha_max):    return -np.inf
                        lp_age = -0.5*((loga - loga_hat)/sig_loga_eff)**2 - np.log(sig_loga_eff*np.sqrt(2*np.pi))
                        lp_zh  = -0.5*((zh   - zh_hat  )/sig_zh_eff  )**2 - np.log(sig_zh_eff  *np.sqrt(2*np.pi))
                        lp_alpha = 0.0
                        if USE_ALPHA_PRIOR:
                            lp_alpha = -0.5*((alpha - alpha_hat)/sig_alpha)**2 - np.log(sig_alpha*np.sqrt(2*np.pi))
                        return lp_age + lp_zh + lp_alpha

                    def _log_likelihood_prime(theta_prime):
                        loga, zh, alpha = theta_prime
                        age_lin = 10.0**loga
                        mod = _eval_model_indices_full(age_lin, zh, alpha)
                        if np.any(~np.isfinite(mod)): return -np.inf
                        resid = _as_vec4(obs - mod)
                        return _mvnorm_loglike(resid, Sigma)

                    def _log_post_prime(theta_prime):
                        lp = _log_prior_prime(theta_prime)
                        if not np.isfinite(lp): return -np.inf
                        ll = _log_likelihood_prime(theta_prime)
                        if not np.isfinite(ll): return -np.inf
                        return lp + ll

                    theta_map_prime = np.array([np.log10(theta_map[0]), theta_map[1], theta_map[2]], dtype=float)

                    # Walker init: half around (loga_hat, zh_hat, seed α), half around MAP
                    n_walkers = 48
                    ndim = 3

                    centre1 = np.array([loga_hat, zh_hat, np.clip(x0[2], alpha_min, alpha_max)], dtype=float)
                    centre2 = theta_map_prime.copy()

                    def _jitter_centre(c, lows, highs, frac):
                        out = np.empty_like(c)
                        for i in range(3):
                            sig = frac[i] * max(1e-6, abs(c[i]))
                            val = np.random.normal(c[i], sig)
                            out[i] = _reflect_in_bounds(val, lows[i], highs[i])
                        return out

                    frac1 = np.array([0.03, 0.05, 0.06])  # tighter around age-Z anchor
                    frac2 = np.array([0.05, 0.07, 0.07])  # a bit wider around MAP

                    half = n_walkers // 2
                    initial_pos_prime = []
                    for _ in range(half):
                        initial_pos_prime.append(_jitter_centre(centre1,
                                            np.array([age_min_log, zh_min, alpha_min]),
                                            np.array([age_max_log, zh_max, alpha_max]), frac1))
                    for _ in range(n_walkers - half):
                        initial_pos_prime.append(_jitter_centre(centre2,
                                            np.array([age_min_log, zh_min, alpha_min]),
                                            np.array([age_max_log, zh_max, alpha_max]), frac2))
                    initial_pos_prime = np.asarray(initial_pos_prime, dtype=float)

                    move = emcee.moves.StretchMove(a=1.8)

                    # ------------------------------- Chain length control -------------------------------------
                    use_fixed_steps   = True
                    fixed_total_steps = 3000
                    warm_steps        = 600
                    chunk_steps       = 1000
                    max_steps         = 30000
                    conv_tol          = 0.05

                    try:
                        with mp.get_context("spawn").Pool() as pool:
                            sampler = emcee.EnsembleSampler(n_walkers, ndim, _log_post_prime, moves=[move], pool=pool)
                            sampler.run_mcmc(initial_pos_prime, warm_steps, progress=False)
                    except Exception:
                        sampler = emcee.EnsembleSampler(n_walkers, ndim, _log_post_prime, moves=[move])
                        sampler.run_mcmc(initial_pos_prime, warm_steps, progress=False)

                    steps_done = warm_steps
                    tau = None

                    def _estimate_tau(s):
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", category=AutocorrWarning)
                            return float(np.max(s.get_autocorr_time(quiet=True)))

                    if use_fixed_steps:
                        extra = max(0, fixed_total_steps - steps_done)
                        if extra > 0:
                            sampler.run_mcmc(None, extra, progress=False)
                        try:
                            tau = _estimate_tau(sampler)
                        except Exception:
                            tau = None
                    else:
                        prev_tau = None
                        while steps_done < max_steps:
                            sampler.run_mcmc(None, chunk_steps, progress=False)
                            steps_done += chunk_steps
                            try:
                                tau_curr = _estimate_tau(sampler)
                            except Exception:
                                continue
                            stable = (prev_tau is not None) and (abs(tau_curr - prev_tau) / max(tau_curr, 1e-12) <= conv_tol)
                            long_enough = (steps_done >= 150.0 * tau_curr)
                            prev_tau = tau_curr
                            tau = tau_curr
                            if stable and long_enough:
                                break

                    # ------------------------------------- Burn / thin ----------------------------------------
                    if tau is not None and np.isfinite(tau) and tau > 0:
                        burn = int(3 * tau)
                        thin = max(1, int(0.5 * tau))
                    else:
                        burn, thin = 300, 2

                    chain_prime = sampler.get_chain(discard=burn, thin=thin, flat=True)

                    # ------------------------------------ Summaries -------------------------------------------
                    if chain_prime.size == 0 or not np.all(np.isfinite(chain_prime)):
                        age_interp = met_interp = alpha_interp = np.nan
                        err_age = err_met = err_alpha = np.nan
                        print('MCMC: no valid posterior samples after adaptive run -> returning NaN.')
                    else:
                        def q16_50_84(a): return np.percentile(a, [16, 50, 84])

                        q_logage = q16_50_84(chain_prime[:, 0])
                        q_age_lin = 10.0**q_logage
                        age_med, age_lo, age_hi = q_age_lin[1], q_age_lin[0], q_age_lin[2]

                        q_zh = q16_50_84(chain_prime[:, 1])
                        q_al = q16_50_84(chain_prime[:, 2])

                        age_interp   = float(age_med)
                        met_interp   = float(q_zh[1])
                        alpha_interp = float(q_al[1])

                        err_age   = float(max(age_med - age_lo,  age_hi - age_med, 1e-9))
                        err_met   = float(max(q_zh[1] - q_zh[0], q_zh[2] - q_zh[1], 1e-9))
                        err_alpha = float(max(q_al[1] - q_al[0], q_al[2] - q_al[1], 1e-9))


    #the same thing for xshooter or any model without alpha enhancment
    if ssp_model_name == 'xshooter':
        print('')
        print('Interpolating the values...')

        #interpolate
        print('')
        print('Interpolating the values...')
        values = np.column_stack((age_teo, met_teo))

        #interpolation with griddata
        print('Only with griddata function')
        lick_indices_ml = np.array([[Hbeta, MgFe]])
        results = griddata((hb_teo, mgfe_teo), values, lick_indices_ml, method='linear')
        age_oss = results[:, 0]
        met_oss = results[:, 1]
        age_interp = age_oss[0]
        met_interp = met_oss[0]
        alpha_interp = 0

        #Uncertainties
        print('')
        print('Calculating the uncertainties...')

        sim_number = 30

        #define the arrays containing normal fluctuations of the EW of the indices with respect to their errors
        Hbeta_sim_array = np.random.normal(loc=Hbeta, scale=Hbetae, size=sim_number)
        MgFe_sim_array = np.random.normal(loc=MgFe, scale=MgFee, size=sim_number)


        #preparing the array of the stellar population simulated parameters
        age_sim = []
        met_sim = []

        #doing the simulation
        for g in range (sim_number):

            #points to interpolate
            points_for_param_sim = np.column_stack((Hbeta_sim_array[g], MgFe_sim_array[g]))

            # Interpolate
            age_sim.append(griddata((hb_teo, mgfe_teo), age_teo, points_for_param_sim, method='linear'))
            met_sim.append(griddata((hb_teo, mgfe_teo), met_teo, points_for_param_sim, method='linear'))


        #remove the nan
        age_sim = [value for value in age_sim if not np.isnan(value)]
        met_sim = [value for value in met_sim if not np.isnan(value)]


        #finally calculating the std and associates it to the error in age, met and alpha
        err_age = np.std(age_sim)
        err_met = np.std(met_sim)

        err_alpha = 0

    return age_interp, met_interp, alpha_interp, err_age, err_met, err_alpha




    #**********************plotting**************************

def lick_grids(ssp_model_name, ssp_lick_indices, ssp_lick_indices_err, age, show_plot, save_plot, spectra_list_name, result_plot_dir):

    """
     This function plots the measured values of the Hbeta-[MgFe]' and Fem-Mgb indices for the galaxy spectrum
     into the index grid of the selected SSP models.
     Input: string SSP model name, array of the Lick/IDS indices used for interpolation and measured from the galaxy spectrum,
            array of the uncertainties of the same indices, float mean luminosity age estimated via interpolation
            with the SSP models for the n spectra or value for the single spectrum,
            bool whether show (True) or not (False) the plot, bool whether to ssave (True) or not (False) the plot
            in a png high resolution image, string name of the spectra to plot, or the single spectrum.
     Output: A matplot window or a PNG image with the model grids and the data point(s).

    """


    # if with_plots or save_plots:
    ssp_models_folder = 'system_files/'
    ssp_model_file = ssp_models_folder + ssp_model_name + '_lick.txt'
    ssp_model_file = os.path.join(BASE_DIR, ssp_model_file )

    #extracting single indices and the uncertanties
    Hbeta = ssp_lick_indices[:,0]
    MgFe = ssp_lick_indices[:,1]
    Fem = ssp_lick_indices[:,2]
    Mgb = ssp_lick_indices[:,3]

    Hbetae = ssp_lick_indices_err[:,0]
    MgFee = ssp_lick_indices_err[:,1]
    Feme = ssp_lick_indices_err[:,2]
    Mgbe = ssp_lick_indices_err[:,3]

    if ssp_model_name == 'Thomas2010':
        data = np.genfromtxt(os.path.join(BASE_DIR, ssp_model_file), delimiter=' ', skip_header=True)
        met_values = [-1.35, -0.33, 0, 0.35, 0.67]
        age_values = [0.6, 0.8, 1, 2, 4, 10, 15]
        alpha_values = [-0.3, 0, 0.3, 0.5]

    if ssp_model_name == 'xshooter':
        data = np.genfromtxt(os.path.join(BASE_DIR, "system_files", "xshooter_lick_plot.txt"), delimiter=' ', skip_header=True)
        met_values = [-1.2, -0.8, -0.4, 0, 0.1, 0.2]
        age_values = [0.79, 1, 2, 3.98, 6.31, 10, 15.85]
        alpha_values = [0]

    if ssp_model_name == 'miles':
        data = np.genfromtxt(os.path.join(BASE_DIR, "system_files", "miles_lick_plot.txt"), delimiter=' ', skip_header=True)
        met_values = [-0.96, -0.66, -0.35, 0.06, 0.26, 0.4]
        age_values = [0.6, 0.8, 1., 2., 4., 10., 14.]
        alpha_values = [0, 0.4]

    if ssp_model_name == 'smiles':
        data = np.genfromtxt(os.path.join(BASE_DIR, "system_files", "smiles_lick_plot.txt"), delimiter=' ', skip_header=True)
        met_values = [-0.96, -0.66, -0.35, 0.06, 0.26]
        age_values = [0.6, 0.8, 1., 2., 4., 10., 14.]
        alpha_values = [-0.2, 0, 0.2, 0.4, 0.6]


    age_values = np.array(age_values)
    met_values = np.array(met_values)

    #round to the closest value. Useful for the mgb-fem grid which strongly depends on age, so I need to fix that
    age_closest_alpha_plot = min(age_values, key=lambda x: abs(x - age))

    plt.figure(figsize=(10, 6))

    # age
    plt.subplot(1, 2, 1)

    alpha_value_grid = 0. # fixing a solar alpha enhancment for the mgfe-hbeta plot


    if ssp_model_name == 'Thomas2010':

        for i in range(len(age_values)):
            age_idx = np.where((data[:, 0] == age_values[i]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[age_idx, 9], data[age_idx, 3], color='black', linewidth=-1)
            plt.text(data[age_idx[4], 9] + 0.1, data[age_idx[4], 3] + 0., f'{age_values[i]} Gyr', fontsize=10, color='darkgrey')


        # met
        for h in range(len(met_values)):
            met_idx = np.where((data[:, 1] == met_values[h]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[met_idx, 9], data[met_idx, 3], color='black', linewidth=1)
            plt.text(data[met_idx[15], 9] - 0.1, data[met_idx[15], 3] - 0.25, f'{met_values[h]}', fontsize=10, color='darkgray')
            if h == 0:
                plt.text(data[met_idx[15], 9] - 0.7, data[met_idx[15], 3] - 0.25, f'[Fe/H]=', fontsize=10, color='darkgray')

        plt.xlabel("[MgFe]' (\u00c5)", fontsize=14)
        plt.ylabel('H\u03B2 (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))
        plt.xlim(0.4, 5.80)
        plt.ylim(0.7, 5.3)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(MgFe, Hbeta, color='red', s = 16)
        plt.errorbar(MgFe, Hbeta, xerr=MgFee, yerr=Hbetae, linestyle='None', ecolor = 'black', capsize=2)

        # alpha values, second plot
        plt.subplot(1, 2, 2)
        for i in range(len(alpha_values)):
            alpha_idx = np.where((data[:, 2] == alpha_values[i]) & (data[:, 0] == age_closest_alpha_plot))[0]
            plt.plot(data[alpha_idx, 5], data[alpha_idx, 8], color='black', linewidth=-1)
            plt.text(data[alpha_idx[4], 5] - 0.5, data[alpha_idx[4], 8] + 0.05, f' [\u03B1/Fe]={alpha_values[i]}', fontsize=10,
                    color='darkgray')

        # #minor ticks
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))

        plt.yticks(np.arange(1, 6), fontsize=14)
        plt.xlabel('Mgb (\u00c5)', fontsize=14)
        plt.ylabel('<Fe> (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.xlim(0.4, 6.5)
        plt.ylim(0.7, 5.3)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(Mgb, Fem, color='red', s = 16)
        plt.errorbar(Mgb, Fem, xerr=Mgbe, yerr=Feme, linestyle='None', ecolor = 'black', capsize=2)

        plt.tight_layout()

        if show_plot:
            plt.show()
            plt.close()
        if save_plot:
            # result_plot_dir = 'results/plots'
            # os.makedirs(result_plot_dir, exist_ok=True)
            model_grids_file = result_plot_dir + '/'+ 'index_grids_' + spectra_list_name + '.png'
            plt.savefig(model_grids_file, format='png', dpi=300) #I must save a png image because the eps file does not reproduce well the grids. Don't know why...
            print ('Index-index diagrams for SSP models and data points saved in: ', model_grids_file)
            plt.close()






    if ssp_model_name == 'xshooter':
        for i in range(len(age_values)):
            age_idx = np.where((data[:, 0] == age_values[i]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[age_idx, 9], data[age_idx, 3], color='black', linewidth=-1)
            plt.text(data[age_idx[4], 9] + 0.25, data[age_idx[4], 3] - 0., f'{age_values[i]} Gyr', fontsize=10, color='darkgrey')


        # met
        for h in range(len(met_values)):
            met_idx = np.where((data[:, 1] == met_values[h]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[met_idx, 9], data[met_idx, 3], color='black', linewidth=1)

            if h == 0:
                plt.text(data[met_idx[25], 9] - 0.6, data[met_idx[25], 3] - 0.2, f'[Fe/H]=', fontsize=10, color='darkgray')
                plt.text(data[met_idx[25], 9] -0.1 , data[met_idx[25], 3] - 0.2, f'{met_values[h]}', fontsize=10, color='darkgray')

            elif h == (len(met_values)-2):
                plt.text(data[met_idx[25], 9] +0 , data[met_idx[25], 3] - 0.2, f'{met_values[h]}', fontsize=10, color='darkgray')

            elif h == (len(met_values)-1):
                plt.text(data[met_idx[25], 9] +0.1 , data[met_idx[25], 3] - 0.2, f'{met_values[h]}', fontsize=10, color='darkgray')
            else:
                plt.text(data[met_idx[25], 9] - 0.1, data[met_idx[25], 3] - 0.2, f'{met_values[h]}', fontsize=10, color='darkgray')


        plt.xlabel("[MgFe]' (\u00c5)", fontsize=14)
        plt.ylabel('H\u03B2 (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))
        plt.xlim(0.5, 4.8)
        plt.ylim(1.2, 8)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(MgFe, Hbeta, color='red', s = 16)
        plt.errorbar(MgFe, Hbeta, xerr=MgFee, yerr=Hbetae, linestyle='None', ecolor = 'black', capsize=2)

        # alpha values, second plot
        plt.subplot(1, 2, 2)
        for i in range(len(alpha_values)):
            alpha_idx = np.where((data[:, 2] == alpha_values[i]) & (data[:, 0] == age_closest_alpha_plot))[0]
            plt.plot(data[alpha_idx, 5], data[alpha_idx, 8], color='black', linewidth=-1)
            plt.text(data[alpha_idx[4], 5] - 0.5, data[alpha_idx[4], 8] + 0.05, f' [\u03B1/Fe]={alpha_values[i]}', fontsize=10,
                    color='darkgray')

        #minor ticks
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))

        plt.yticks(np.arange(1, 6), fontsize=14)
        plt.xlabel('Mgb (\u00c5)', fontsize=14)
        plt.ylabel('<Fe> (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.xlim(0.4, 6.5)
        plt.ylim(0.7, 5.3)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(Mgb, Fem, color='black', s = 16)
        plt.errorbar(Mgb, Fem, xerr=Mgbe, yerr=Feme, linestyle='None', ecolor = 'black', capsize=2)

        plt.tight_layout()

        if show_plot:
            plt.show()
            plt.close()
        if save_plot:
            # result_plot_dir = 'results/plots'
            # os.makedirs(result_plot_dir, exist_ok=True)
            model_grids_file = result_plot_dir + '/'+ 'index_grids_' + spectra_list_name + '.png'
            plt.savefig(model_grids_file, format='png', dpi=300) #I must save a png image because the eps file does not reproduce well the grids. Don't know why...
            print ('Index-index diagrams for SSP models and data points saved in: ', model_grids_file)
            plt.close()



    if ssp_model_name == 'miles':
        for i in range(len(age_values)):
            age_idx = np.where((data[:, 0] == age_values[i]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[age_idx, 9], data[age_idx, 3], color='black', linewidth=-1)
            plt.text(data[age_idx[4], 9] + 0.4, data[age_idx[4], 3] - 0.1, f'{age_values[i]} Gyr', fontsize=10, color='darkgrey')


        # met
        for h in range(len(met_values)):
            met_idx = np.where((data[:, 1] == met_values[h]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[met_idx, 9], data[met_idx, 3], color='black', linewidth=1)

            if h == 0:
                plt.text(data[met_idx[35], 9] - 0.7, data[met_idx[35], 3] - 0.7, f'[Fe/H]=', fontsize=10, color='darkgray')
                plt.text(data[met_idx[35], 9] -0.2 , data[met_idx[35], 3] - 0.7, f'{met_values[h]}', fontsize=10, color='darkgray')
            elif h == (len(met_values)-2):
                plt.text(data[met_idx[35], 9] -0.1 , data[met_idx[35], 3] - 0.25, f'{met_values[h]}', fontsize=10, color='darkgray')

            elif h == (len(met_values)-1):
                plt.text(data[met_idx[35], 9] +0.1 , data[met_idx[35], 3] - 0.2, f'{met_values[h]}', fontsize=10, color='darkgray')
            else:
                plt.text(data[met_idx[35], 9] - 0.1, data[met_idx[35], 3] - 0.2, f'{met_values[h]}', fontsize=10, color='darkgray')


        plt.xlabel("[MgFe]' (\u00c5)", fontsize=14)
        plt.ylabel('H\u03B2 (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))
        plt.xlim(0.5, 5)
        plt.ylim(1.2, 6.3)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(MgFe, Hbeta, color='red', s = 16)
        plt.errorbar(MgFe, Hbeta, xerr=MgFee, yerr=Hbetae, linestyle='None', ecolor = 'black', capsize=2)

        # alpha values, second plot
        plt.subplot(1, 2, 2)
        for i in range(len(alpha_values)):
            alpha_idx = np.where((data[:, 2] == alpha_values[i]) & (data[:, 0] == age_closest_alpha_plot))[0]
            plt.plot(data[alpha_idx, 5], data[alpha_idx, 8], color='black', linewidth=-1)
            plt.text(data[alpha_idx[4], 5] - 0.5, data[alpha_idx[4], 8] + 0.05, f' [\u03B1/Fe]={alpha_values[i]}', fontsize=10,
                    color='darkgray')

        # minor ticks
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))

        plt.yticks(np.arange(1, 6), fontsize=14)
        plt.xlabel('Mgb (\u00c5)', fontsize=14)
        plt.ylabel('<Fe> (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.xlim(1, 6.5)
        plt.ylim(1.1, 5.3)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(Mgb, Fem, color='black', s = 16)
        plt.errorbar(Mgb, Fem, xerr=Mgbe, yerr=Feme, linestyle='None', ecolor = 'black', capsize=2)

        plt.tight_layout()

        if show_plot:
            plt.show()
            plt.close()
        if save_plot:
            # result_plot_dir = 'results/plots'
            # os.makedirs(result_plot_dir, exist_ok=True)
            model_grids_file = result_plot_dir + '/'+ 'index_grids_' + spectra_list_name + '.png'
            plt.savefig(model_grids_file, format='png', dpi=300) #I must save a png image because the eps file does not reproduce well the grids. Don't know why...
            print ('Index-index diagrams for SSP models and data points saved in: ', model_grids_file)
            plt.close()



    if ssp_model_name == 'smiles':

        for i in range(len(age_values)):
            age_idx = np.where((data[:, 0] == age_values[i]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[age_idx, 9], data[age_idx, 3], color='black', linewidth=-1)
            plt.text(data[age_idx[4], 9] + 0.1, data[age_idx[4], 3] + 0., f'{age_values[i]} Gyr', fontsize=10, color='darkgrey')


        # met
        for h in range(len(met_values)):
            met_idx = np.where((data[:, 1] == met_values[h]) & (data[:, 2] == alpha_value_grid))[0]
            plt.plot(data[met_idx, 9], data[met_idx, 3], color='black', linewidth=1)

            if h == 0:
                plt.text(data[met_idx[36], 9] - 0.7, data[met_idx[36], 3] - 0.75, f'[Fe/H]=', fontsize=10, color='darkgray')
                plt.text(data[met_idx[36], 9] -0.2 , data[met_idx[35], 3] - 0.75, f'{met_values[h]}', fontsize=10, color='darkgray')
            else:
                plt.text(data[met_idx[36], 9] - 0.1, data[met_idx[36], 3] - 0.25, f'{met_values[h]}', fontsize=10, color='darkgray')

        plt.xlabel("[MgFe]' (\u00c5)", fontsize=14)
        plt.ylabel('H\u03B2 (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))
        plt.xlim(0.6, 4.6)
        plt.ylim(1.2, 6.2)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(MgFe, Hbeta, color='red', s = 16)
        plt.errorbar(MgFe, Hbeta, xerr=MgFee, yerr=Hbetae, linestyle='None', ecolor = 'black', capsize=2)

        # alpha values, second plot
        plt.subplot(1, 2, 2)
        for i in range(len(alpha_values)):
            alpha_idx = np.where((data[:, 2] == alpha_values[i]) & (data[:, 0] == age_closest_alpha_plot))[0]
            plt.plot(data[alpha_idx, 5], data[alpha_idx, 8], color='black', linewidth=-1)
            plt.text(data[alpha_idx[4], 5] - 0.5, data[alpha_idx[4], 8] + 0.05, f' [\u03B1/Fe]={alpha_values[i]}', fontsize=10,
                    color='darkgray')

        # #minor ticks
        plt.minorticks_on()
        plt.gca().yaxis.set_minor_locator(MultipleLocator(0.2))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(0.25))

        plt.yticks(np.arange(1, 6), fontsize=14)
        plt.xlabel('Mgb (\u00c5)', fontsize=14)
        plt.ylabel('<Fe> (\u00c5)', fontsize=14)
        plt.tick_params(axis='both', which='both', direction='in', left=True, right=True, top=True, bottom=True)
        plt.xlim(0.4, 6.5)
        plt.ylim(0.7, 5.3)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        #plotting the value
        plt.scatter(Mgb, Fem, color='black', s = 16)
        plt.errorbar(Mgb, Fem, xerr=Mgbe, yerr=Feme, linestyle='None', ecolor = 'black', capsize=2)

        plt.tight_layout()

        if show_plot:
            plt.show()
            plt.close()
        if save_plot:
            # result_plot_dir = 'results/plots'
            # os.makedirs(result_plot_dir, exist_ok=True)
            model_grids_file = result_plot_dir + '/'+ 'index_grids_' + spectra_list_name + '.png'
            plt.savefig(model_grids_file, format='png', dpi=300) #I must save a png image because the eps file does not reproduce well the grids. Don't know why...
            print ('Index-index diagrams for SSP models and data points saved in: ', model_grids_file)
            plt.close()


#wild bootstrap function for uncertainties for ppxf populations by Cappellari
def bootstrap_residuals(model, resid, wild=True):
    """
    https://en.wikipedia.org/wiki/Bootstrapping_(statistics)#Resampling_residuals
    https://en.wikipedia.org/wiki/Bootstrapping_(statistics)#Wild_bootstrap

    Davidson & Flachaire (2008) eq.(12) gives the recommended form
    of the wild bootstrapping probability used here.

    https://doi.org/10.1016/j.jeconom.2008.08.003

    :param spec: model (e.g. best fitting spectrum)
    :param res: residuals (best_fit - observed)
    :param wild: use wild bootstrap to allow for variable errors
    :return: new model with bootstrapped residuals

    """
    if wild:    # Wild Bootstrapping: generates -resid or resid with prob=1/2
        eps = resid*(2*np.random.randint(2, size=resid.size) - 1)
    else:       # Standard Bootstrapping: random selection with repetition
        eps = np.random.choice(resid, size=resid.size)

    return model + eps



# simple function to find the nearest FWHM_gal value corresponding to the emission line funcion, in case of kinematics with gas and variable FWHM_gal (i.e. constant resolving power R).
def find_nearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx



# Find a specific SSP template for ppxf kinematics module when you use the two fit stellar components
def pick_ssp_template(desired_age, desired_metal, ages, metals, templates):
    """
    Find the nearest SSP template to the age and metallicity values provided by
    the user for the stellar and gas kinematics task when the two stellar component fit is
    activated.
    Return (model, i_closest, j_closest)
        where model is the spectral template in pPXF standard (n_wave,)
    """
    # If the age grid is in log10:
    # i_closest = np.argmin(np.abs(np.log10(ages) - np.log10(desired_age)))

    # If the age are linear (Gyr) values:
    i_closest = np.argmin(np.abs(ages - desired_age))
    j_closest = np.argmin(np.abs(metals - desired_metal))

    # Retrieving the nearest age and metallicity values for the SSP models
    best_age   = ages[i_closest]
    best_metal = metals[j_closest]

    # Retrieving the corresponding template
    model = templates[:, i_closest, j_closest]

    # Checking if the difference between the desired age and metallicity values is large:
    age_diff   = abs(best_age - desired_age)
    metal_diff = abs(best_metal - desired_metal)
    age_threshold   = 0.1   # adjust the value if needed
    metal_threshold = 0.06  # adjust the value if needed

    if age_diff > age_threshold or metal_diff > metal_threshold:
        msg = (
            f"WARNING: Not found a template for age={desired_age}Gyr, [M/H]={desired_metal}. "
            f"Selected the nearest template with age={best_age:.2f}Gyr, [M/H]={best_metal:.2f}."
        )
        print(msg)

    return model, i_closest, j_closest



# Function to download the pPXF SSP models accounting also for the SSL certificate problem arising with some MacOS distributions
def download_file(url, dest_path):
    """Download a file using SSL context compatible with macOS"""
    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(url, context=context) as response, open(dest_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)



# Function to define the goodpixels for pPXF kinematics, both for emission lines and user mask
def build_goodpixels_with_mask(ln_lam1, lam_range_temp, redshift, redshift_0, mask_ranges=None, user_mask = False, use_emission_mask=True):
    """
    Returns an array of goodpixels for pPXF, combining optional emission-line masking
    and optional user-defined masking.

    Parameters
    ----------
    ln_lam1 : array_like
        Natural log of wavelength grid (output of log-rebinning).
    lam_range_temp : list or array
        Wavelength range of the template [start, end] in Angstrom.
    redshift : float
        Redshift of the galaxy.
    mask_ranges : list of tuples, optional
        List of (start, end) wavelength intervals to mask (in Angstrom, observed frame).
    redshift_0 : float
        Cosmological redshift according to pPXF nomenclature
    use_emission_mask : bool
        If True, applies automatic masking of emission lines via determine_goodpixels().

    Returns
    -------
    final_goodpix : ndarray
        Array of indices of good pixels to use in pPXF.
    """

    n_pixels = len(ln_lam1)

    # Step 1: emission-line masking or use all pixels
    if use_emission_mask:
        goodpix = util.determine_goodpixels(ln_lam1, lam_range_temp, redshift)
    else:
        goodpix = np.arange(n_pixels)

    # Step 2: user-defined masking
    if mask_ranges is not None and len(mask_ranges) > 0 and user_mask:
        wave_log = np.exp(ln_lam1)
        user_mask_log = np.zeros(n_pixels, dtype=bool)

        # Shift ranges to rest-frame if needed
        corrected_mask_ranges = [(start / (1 + redshift_0), end / (1 + redshift_0)) for start, end in mask_ranges]

        for start, end in corrected_mask_ranges:
            user_mask_log |= (wave_log >= start) & (wave_log <= end)

        # Get indices to exclude
        badpix = np.where(user_mask_log)[0]

        # Remove user-masked pixels from current goodpix
        final_goodpix = np.array([i for i in goodpix if i not in badpix])
    else:
        final_goodpix = goodpix

    return final_goodpix


def build_stellar_blocks_gui(templates, age_values, met_values, mode="all", n_components=1, custom_selections=None, normalise=True):
    """
    Build stellar template blocks for multi-component kinematics, robust to 3D grids.

    Returns
    -------
    blocks : list of [n_wave, n_temp_i]
    stars_templates : [n_wave, sum_i n_temp_i]
    component_vector : [sum_i n_temp_i]  values in {0,...,n_components-1}
    """
    # 1) Coerce to 2D and get age/met aligned with columns
    T2, age_flat, met_flat, n_met = _coerce_templates_to_2d(templates, age_values, met_values)
    n_wave, n_temp = T2.shape

    blocks = []
    comp_vec = []

    def _range_mask(age_range, met_range):
        m = np.ones(n_temp, dtype=bool)
        if age_range is not None:
            amin, amax = age_range
            m &= (age_flat >= amin) & (age_flat <= amax)
        if met_range is not None:
            zmin, zmax = met_range
            m &= (met_flat >= zmin) & (met_flat <= zmax)
        return m

    if mode == "all":
        b0 = T2
        b1 = T2
        blocks = [b0, b1]
        comp_vec = [np.zeros(b0.shape[1], dtype=int), np.ones (b1.shape[1], dtype=int)]

    elif mode == "old_young" and n_components == 2:
        mask_old   = _range_mask((5.0, np.inf), None)
        mask_young = _range_mask((0.0, 5.0),     None)
        b0 = T2[:, mask_old]
        b1 = T2[:, mask_young]
        blocks = [b0, b1]
        comp_vec = [np.zeros(b0.shape[1], dtype=int),
                    np.ones (b1.shape[1], dtype=int)]

    elif mode == "metal_rich_poor" and n_components == 2:
        mask_rich = _range_mask(None, (0.0,  np.inf))
        mask_poor = _range_mask(None, (-np.inf, 0.0))
        b0 = T2[:, mask_rich]
        b1 = T2[:, mask_poor]
        blocks = [b0, b1]
        comp_vec = [np.zeros(b0.shape[1], dtype=int),
                    np.ones (b1.shape[1], dtype=int)]

    elif mode == "custom" and custom_selections is not None:
        for icomp, sel in enumerate(custom_selections):
            if sel.get("custom_idx") is not None:
                # custom_idx as list of (i_age, j_met)
                idx_pairs = sel["custom_idx"]
                if n_met is None:
                    raise ValueError("custom_idx requires grid info (n_met).")
                flat_idx = [i * n_met + j for (i, j) in idx_pairs]
                mask = np.zeros(n_temp, dtype=bool)
                mask[flat_idx] = True
            else:
                mask = _range_mask(sel.get("age_range"), sel.get("met_range"))

            block = T2[:, mask]
            blocks.append(block)
            comp_vec.append(np.full(block.shape[1], icomp, dtype=int))

    else:
        raise ValueError(f"Unsupported mode='{mode}' / n_components={n_components}")

    # 3) Concatenate and normalize
    stars_templates = np.hstack(blocks) if len(blocks) > 1 else blocks[0]
    component_vector = np.hstack(comp_vec) if len(comp_vec) > 1 else comp_vec[0]

    if normalise:
        med = np.median(stars_templates, axis=0)
        med[med == 0] = 1.0
        stars_templates = stars_templates / med

    # 4) Checks
    assert stars_templates.ndim == 2, "stars_templates must be 2D"
    assert component_vector.ndim == 1, "component_vector must be 1D"
    assert stars_templates.shape[1] == component_vector.size, \
        "component_vector length must match number of template columns"

    return blocks, stars_templates, component_vector


def _coerce_templates_to_2d(templates, ages, metals):
    """
    Ensure templates is [n_wave, n_temp] and return aligned age/met arrays
    of length n_temp. Accepts:
      - 3D [n_wave, n_age, n_met]
      - 2D [n_wave, n_temp]  (in questo caso cerca di ricostruire age/met flat)
    """
    tmpl = np.asarray(templates)
    if tmpl.ndim == 3:
        n_wave, n_age, n_met = tmpl.shape
        # Flatten: col index = i_age * n_met + j_met  (row-major/'C')
        T2 = tmpl.reshape(n_wave, n_age * n_met)
        age_flat = np.repeat(ages, n_met)    # [a0,a0,...,a1,a1,...]
        met_flat = np.tile(metals, n_age)    # [m0,m1,...,m_last, m0, m1,...]
        return T2, age_flat, met_flat, n_met
    elif tmpl.ndim == 2:
        # Best effort: if already 2D, we try to infer age/met per col only if lengths match.
        # Otherwise, we just return placeholders to avoid breaking; selections by range will fail.
        n_wave, n_temp = tmpl.shape
        # Try to guess grid if lengths multiply correctly
        n_age = len(ages)
        n_met = len(metals)
        if n_age * n_met == n_temp:
            age_flat = np.repeat(ages, n_met)
            met_flat = np.tile(metals, n_age)
            return tmpl, age_flat, met_flat, n_met
        else:
            # Fallback: no aligned age/met (range selection non funzionerà su 2D non-grid)
            return tmpl, None, None, None
    else:
        raise ValueError("templates must be 2D or 3D")


def extract_stellar_components_from_matrix(pp, component, stars_templates, gas_templates=None, additive_degree=0):
    """
    Extracts the two stellar components (comp=0 and comp=1) directly from pp.matrix.

    Parameters
    ----------
    pp : pPXF object after the fit.
    component : array of kinematic component labels for ALL templates used in the fit
                (only the first n_stars, i.e. the stellar ones, are used here).
    stars_templates : array [n_pix_temp, n_stars] used to build the 'templates'
                      (only needed to infer n_stars).
    gas_templates : array [n_pix_temp, n_gas] if gas templates were used, otherwise None.
    additive_degree : integer, degree used for additive polynomials in the fit.
                      Number of additive columns = degree + 1 if degree >= 0, else 0.

    Returns
    -------
    spec_comp0, spec_comp1 : arrays [n_pix_gal]
        Best-fit spectra of each stellar component on the same grid as pp.bestfit.
    """

    # 1) Determine the number of additive polynomial columns
    # n_add = (additive_degree + 1) if (additive_degree is not None and additive_degree >= 0) else 0 # additive_degree +1 or not???
    n_add = (additive_degree) if (additive_degree is not None and additive_degree >= 0) else 0

    # 2) Determine how many stellar and gas templates were used
    n_stars = stars_templates.shape[1]
    n_gas   = 0 if gas_templates is None else gas_templates.shape[1]
    n_templ_total = n_stars + n_gas

    # 3) Extract the template block from the pPXF design matrix
    #    pp.matrix has shape [n_pix_gal, n_add + n_templ_total (+ n_sky if used)]
    #    Each column already includes LOSVD convolution, multiplicative polynomials,
    #    and dust effects (if applied in the fit).
    A_temp = pp.matrix[:, n_add : n_add + n_templ_total]

    # 4) Extract the linear weights of the templates
    w = np.asarray(pp.weights).ravel()
    w_stars = w[:n_stars]  # first n_stars correspond to the stellar templates
    # w_gas   = w[n_stars : n_stars + n_gas]  # uncomment if you need the gas part

    # 5) Select only the stellar template block
    A_stars = A_temp[:, :n_stars]

    # 6) Identify the two stellar components based on the 'component' vector
    comp_stars = np.asarray(component[:n_stars], int)
    idx0 = np.where(comp_stars == 0)[0]
    idx1 = np.where(comp_stars == 1)[0]

    
    # 7) Reconstruct the individual stellar components on the galaxy wavelength grid
    #    If a component is missing, create a zero array of the same length as pp.bestfit.
    spec_comp0 = A_stars[:, idx0] @ w_stars[idx0] if idx0.size > 0 else np.zeros(pp.bestfit.shape, dtype=float)
    spec_comp1 = A_stars[:, idx1] @ w_stars[idx1] if idx1.size > 0 else np.zeros(pp.bestfit.shape, dtype=float)

    # I don't know why, but IF using both additive and multiplicative polynomials, I need to divide the extracted two components for the multiplicative polynomials, otherwise thet have a very distorted continuum. Maybe a small bug in pPXF matrix??
    M = getattr(pp, "mpoly", None)
    spec_comp0 = spec_comp0 / M if M is not None and n_add >0 else spec_comp0
    spec_comp1 = spec_comp1 / M if M is not None and n_add >0 else spec_comp1


    return spec_comp0, spec_comp1
#********************** END OF SPECTRA ANALYSIS FUNCTIONS *********************************
#******************************************************************************************

