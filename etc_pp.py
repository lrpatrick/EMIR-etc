# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:55:30 2017

@author: fgl
edited: LRP
"""
import numpy as np
import astropy.io.ascii as at
import astropy.io.fits as pyfits
# from scipy.interpolate import InterpolatedUnivariateSpline as inter

import etc_modules as mod


ldo_hr_blue = np.arange(12000, 18998, 2)*1e-4
ldo_hr_red = np.arange(19000, 27000, 2)*1e-4
mag_sky = {'H': 14.4, 'Ks': 12.5}

vega=at.read('libs/vegflux_std.dat', data_start=3, names=['ldo', 'fl'])
# This is in microns so no change:
vega_ldo=np.array(vega['ldo'])
# this is already in photon/s/m^2/micron/arcsec
vega_flux=np.array(vega['fl'])
vega_flux_blue = mod.spec_int(vega_ldo, vega_flux, ldo_hr_blue)
vega_flux_red = mod.spec_int(vega_ldo, vega_flux, ldo_hr_red)


sky = pyfits.open('sky/skytable_10.fits')
sky_ldo = sky[1].data.field('lam')
sky_flux = sky[1].data.field('flux')
sky_flux_blue = mod.spec_int(sky_ldo, sky_flux, ldo_hr_blue)
sky_flux_red = mod.spec_int(sky_ldo, sky_flux, ldo_hr_red)

temp = at.read('filters/HK_trans.dat', data_start=3, names=['ldo', 'tr'])
filt_ldo = np.array(temp['ldo'])
# in per one
filt_tr = np.array(temp['tr'])
filt_tr_blue = mod.spec_int(filt_ldo, filt_tr, ldo_hr_blue).clip(0, 1)
filt_tr_red = mod.spec_int(filt_ldo, filt_tr, ldo_hr_red).clip(0, 1)

ns_blue = (10**(-1*mag_sky['H']/2.5))*\
    mod.vega(sky_flux_blue, vega_flux_blue, filt_tr_blue)

ns_red = (10**(-1*mag_sky['Ks']/2.5))*\
    mod.vega(sky_flux_red, vega_flux_red, filt_tr_red)


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
# Factors:
# dispersion = filt_tr*grism_tr(0.4)
# optical_transmission = 0.2 ... but where has this value come from?
# additional factor of slitloss = 0.8
con_sky_blue = mod.convolres(ldo_hr_blue,
                             texp*loss*(ns_blue*filt_tr_blue*0.4*0.2),
                             res_element)*area
con_sky_red = mod.convolres(ldo_hr_red,
                            texp*loss*(ns_red*filt_tr_red*0.4*0.2),
                            res_element)*area

sp_sky_blue = delta_px*mod.spec_int(ldo_hr_blue,
                                    con_sky_blue*scale**2,
                                    ldo_px)
sp_sky_red = delta_px*mod.spec_int(ldo_hr_red,
                                   con_sky_red*scale**2,
                                   ldo_px)
sp_sky = sp_sky_blue + sp_sky_red
