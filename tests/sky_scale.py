"""
Author: LRP
Date: 06-04-2017
Description:
Calculate the sky magnitude for a given filter and calibate this to the observed
values from the INT
"""
import astropy.io.fits as pyfits
import astropy.io.ascii as at
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as inter

vega_file = 'libs/vegflux_std.dat'
vega = np.genfromtxt(vega_file, skip_header=2).T


def sky_mag(filt, rad):
    """
    Calculate sky magnitude for a given filter
    This function assumes that all filter files have the following units:
    microns
    ph/s/m2/micron/arcsec2
    """
    band = np.genfromtxt(filt, skip_header=2).T
    sky = pyfits.open(rad)
    # rad = np.genfromtxt(rad, skip_header=2).T
    band_inter = inter(band[0], band[1], k=3)
    band_wvl = band_inter(sky[1].data.field('lam')).clip(0)
    # in photon/s/m^2/micron:
    bandflux = sky[1].data.field('flux')

    plt.figure()
    plt.plot(sky[1].data.field('lam'), sky[1].data.field('flux'), 'k')
    plt.plot(sky[1].data.field('lam'), bandflux, 'b')
    plt.plot(band[0], band[1]*bandflux.max(), 'r')
    plt.plot(sky[1].data.field('lam'), band_wvl*bandflux.max(), 'r')
    return sky[1].data.field('lam'), bandflux


def sky_vega(filt, vega_file):
    """
    Calculate sky magnitude for a given filter
    This function assumes that all filter files have the following units:
    microns
    ph/s/m2/micron/arcsec2

    """
    band = np.genfromtxt(filt, skip_header=2).T
    vega=at.read('libs/vega_rieke08.dat', data_start=8, names=['ldo', 'fl'])
    # This is in microns so no change:
    vega_ldo=np.array(vega['ldo'])
    # this is w/m2/nm, so to put in photon/s/m^2/micron:
    vega_flux=np.array(vega['fl'])*1e3*5.034118201E+18*vega_ldo
    band_inter = inter(band[0], band[1], k=3)
    band_wvl = band_inter(vega_ldo).clip(0)
    bandflux = vega_flux*band_wvl

    plt.figure()
    plt.plot(vega_ldo, vega_flux, 'k')
    plt.plot(vega_ldo, bandflux, 'b')
    plt.plot(band[0], band[1]*bandflux.max(), 'r')
    plt.plot(vega_ldo, band_wvl*bandflux.max(), 'r')
    return vega_ldo, bandflux

# Measured values from ING:
# K 12.5
# H 14.4
# J 16.6

# Are these values reliable?

# J-band scaling:
# xj, jflux = sky_mag('filters/J_trans.dat', 'sky/skytable_10.fits')
# jscale = np.sum(jflux)/(10**(-16.6/2.5))

# # YJ-band
# xyj, yjflux = sky_mag('filters/YJ_smooth_trans.dat', 'sky/skytable_10.fits')
# yjmag = -2.5*np.log10(np.sum(yjflux)/jscale)
# # From J scaling: YJmag = 15.1
# # Paco's number: 15.8
# # This makes sense as Paco has used a sky spectrum which stops half way in the
# # Y-band

# # Y-band:
# xy, yflux = sky_mag('filters/Y_trans.dat', 'sky/skytable_10.fits')
# ymag = -2.5*np.log10(np.sum(yflux)/jscale)

# # F123M
# xf123m, f123mflux = sky_mag('filters/F123M_trans.dat', 'sky/skytable_10.fits')
# f123mmag = -2.5*np.log10(np.sum(f123mflux)/jscale)

# H-band scaling:
xh, hflux = sky_mag('filters/H_trans.dat', 'sky/skytable_10.fits')
hscale = np.sum(hflux)/(10**(-14.4/2.5))
xhvega, hvega = sky_vega('filters/H_trans.dat', 'libs/vegflux_std.dat')
hscale = -2.5*np.log10(np.sum(hflux)/np.sum(hvega))/14.4
h_vega_integral = np.sum(hvega*xhvega*(xhvega[1] - xhvega[0]))
h_sky_integral = np.sum(hflux*xh*(xh[1] - xh[0]))
hf = (h_vega_integral/h_sky_integral)*10**(-12.5/2.5)

# # FeII:
# xfe2, fe2flux = sky_mag('filters/FeII_trans.dat', 'sky/skytable_10.fits')
# fe2mag = -2.5*np.log10(np.sum(fe2flux)/hscale)

# K-band Scaling:

xk, kflux = sky_mag('filters/K-spec_trans.dat', 'sky/skytable_10.fits')
# kscale = np.sum(kflux)/(10**(-12.5/2.5))
xkvega, kvega = sky_vega('filters/K-spec_trans.dat', 'libs/vegflux_std.dat')
# kscale = -2.5*np.log10(np.sum(kflux)/np.sum(kvega))/12.5
ks_vega_integral = np.sum(kvega*xkvega*(xkvega[1] - xkvega[0]))
ks_sky_integral = np.sum(kflux*xk*(xk[1] - xk[0]))
ksf = (ks_vega_integral/ks_sky_integral)*10**(-12.5/2.5)

# HK-band:
xhk, hkflux = sky_mag('filters/HK_paco.dat', 'sky/skytable_10.fits')
xhkvega, hkvega = sky_vega('filters/HK_paco.dat', 'libs/vegflux_std.dat')
# hkmag = -2.5*np.log10(np.sum(hkflux[np.where(xhk < 1.9)]/hscale) +
#                       np.sum(hkflux[np.where(xhk > 1.9)]/kscale))
# using vega:
# hk_vega_integral = np.trapz(hkvega_fine*fine_ldo, fine_ldo)
# hk_sky_integral = np.trapz(hkflux_fine*fine_ldo, fine_ldo)

# hk_vega_integral = np.sum(hkvega*xhkvega*(xhkvega[1] - xhkvega[0]))
# hk_sky_integral = np.sum(hkflux*xhk*(xhk[1] - xhk[0]))
# hk_mag_k = -2.5*np.log10(hk_sky_integral*ksf/hk_vega_integral)
# hk_mag_h = -2.5*np.log10(hk_sky_integral*hf/hk_vega_integral)


# hkmag = -2.5*np.log10((np.sum(hkflux[np.where(xhk < 1.9)])/np.sum(hkvega[np.where(xhkvega < 1.9)]))*ksf +
#                       (np.sum(hkflux[np.where(xhk > 1.9)]/np.sum(hkvega[np.where(xhkvega > 1.9)])))*hsf)
# From airmass = 1.0: HKmag = 11.5
# From airmass = 2.5: HKmag = 11.5
# Paco's calculation: 11.5
# Carlos' calculation: 13.3 Ks, 14.26 H
# Using Vega:
# Kspec : 13.1
#     H : 14.7
# together: 12.7

# # BrG
# xbrg, brgflux = sky_mag('filters/BrG_trans.dat', 'sky/skytable_10.fits')
# brgmag = -2.5*np.log10(np.sum(brgflux)/kscale)

# # H2(1-0)
# xh2_10, h2_10flux = sky_mag('filters/H2_10_trans.dat', 'sky/skytable_10.fits')
# h2_10mag = -2.5*np.log10(np.sum(h2_10flux)/kscale)

# # H2(2-1)
# xh2_21, h2_21flux = sky_mag('filters/H2_21_trans.dat', 'sky/skytable_10.fits')
# h2_21mag = -2.5*np.log10(np.sum(h2_21flux)/kscale)
