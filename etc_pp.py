# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:55:30 2017

@author: fgl
"""
import numpy as np
import astropy.io.ascii as at
import astropy.io.fits as pyfits
from scipy.interpolate import InterpolatedUnivariateSpline as inter

def scale_to_vega(obj, vega, filt):
    """
    Take a given normalized spectrum, that must be in photons
    and normalizes it to have zero magnitude under given filter
    """
    vega_photons = (vega*filt).sum()
    obj_photons = (obj*filt).sum()
    return obj*vega_photons/obj_photons

def convolres(ldo, fl, res_el):
    """
    Convolves the given spectra at config resolution.
    The resolution element is assumed to be the FWHM
    """
    sigma = (res_el/(ldo[1] - ldo[0]))/2.354  # Sigma in pixels, res el taken to be FWHM
    x = np.arange(sigma*10) - sigma*5         # Vector large enough, centered
    kernel = np.exp(-0.5*(x/sigma)**2)

    # Pad at the sides to avoid windowing
    # MB 2016-10-30 make window_len integer to avoid deprecation warning
    window_len = int(np.round(sigma))
    s = np.r_[fl[window_len - 1:0:-1], fl, fl[-1:-window_len:-1]]
    y = np.convolve(kernel/kernel.sum(), s, mode='same')

    return y[len(fl[window_len - 1:0:-1]):len(y) - len(fl[-1:-window_len:-1])]

def spec_interpolate(wvl0, fl0, wvl1):
    """Interpolation to a given wvl array."""
    from scipy.interpolate import InterpolatedUnivariateSpline as inter
  
    inter_func = inter(wvl0, fl0, k=3)
    result = inter_func(wvl1).clip(0)
    return result


ldo_hr_blue = np.arange(12000, 18998, 2)*1e-4
ldo_hr_red = np.arange(19000, 27000, 2)*1e-4
mag_sky = {'H': 14.4, 'Ks': 12.5}

vega=at.read('libs/vegflux_std.dat',data_start=3,names=['ldo','fl'])
# This is in microns so no change:
vega_ldo=np.array(vega['ldo'])
# this is already in photon/s/m^2/micron/arcsec
vega_flux=np.array(vega['fl'])
f=inter(vega_ldo,vega_flux)
vega_flux_blue=f(ldo_hr_blue)
vega_flux_red=f(ldo_hr_red)

# sky=at.read('sky_rad_10.txt',data_start=3,names=['ldo','fl'])
# # this is nm, so to micron:
# sky_ldo=np.array(sky['ldo'])*1e-3
# # this is already in photon/s/m^2/micron/arcsec
# sky_flux=np.array(sky['fl'])
sky = pyfits.open('sky/skytable_10.fits')
sky_ldo = sky[1].data.field('lam')
sky_flux = sky[1].data.field('flux')
f=inter(sky_ldo,sky_flux)
sky_flux_blue=f(ldo_hr_blue)
sky_flux_red=f(ldo_hr_red)

temp=at.read('filters/HK_trans.dat',data_start=3,names=['ldo','tr'])
filt_ldo=np.array(temp['ldo'])
# in per one
filt_tr=np.array(temp['tr'])
f=inter(filt_ldo,filt_tr)
filt_tr_blue=f(ldo_hr_blue).clip(0,1)
filt_tr_red=f(ldo_hr_red).clip(0,1)

ns_blue = (10**(-1*mag_sky['H']/2.5))*\
    scale_to_vega(sky_flux_blue, vega_flux_blue, filt_tr_blue)

ns_red = (10**(-1*mag_sky['Ks']/2.5))*\
    scale_to_vega(sky_flux_red, vega_flux_red, filt_tr_red)


cenwl = 1.9
specres = 987.
texp = 3600.
delta_px = (cenwl/specres)/3.
res_element = 27.5e-4
loss=0.8
scale=0.1922
area = 73.  # m2
ldo_px = (np.arange(2048) - 1024)*delta_px + cenwl

#    3.- Convolve the SEDs with the proper resolution
#        Delta(lambda) is evaluated at the central wavelength

con_sky_blue = convolres(ldo_hr_blue,texp*loss*(ns_blue*filt_tr_blue*0.4*0.2),
    res_element)*area
con_sky_red = convolres(ldo_hr_red,texp*loss*(ns_red*filt_tr_red*0.4*0.2),
    res_element)*area

sp_sky_blue = delta_px*spec_interpolate(ldo_hr_blue,
    con_sky_blue*scale**2,ldo_px)
sp_sky_red = delta_px*spec_interpolate(ldo_hr_red,
    con_sky_red*scale**2,ldo_px)
sp_sky = sp_sky_blue + sp_sky_red
