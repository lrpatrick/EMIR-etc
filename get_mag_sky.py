"""
Author: LRP
Date: 16-04-2017
Description:
Calculate the sky magnitude for a given filter and calibate this to observed
values from the INT

ING values implmented so far:
  J      H       K
16.6    14.4    12.5

From the NOT webpages:

"Estimated near IR sky brightness
J=15-16, H=13-14, K=12-13"

From the TNG-NICS webpages:
"
1um     Js       J       H       K'       K
16.5    15.5    15.5    14.0    13.2    12.6

Unsolved questions:

-- what about the YJ-band and F123M-band?
-- Where do the measured ING values come from? Someone mentioned a techninal
   note, but I can't find this.


How to use this script:

In section 4, you must select which 'newfilt' you would like to calculate the
skymag for (HK is done automatically).

Along with your 'newfilt' you must select what filter will be used for the
normalisation ('normfilt')

Then you should be able to run the script no bother!

"""

import numpy as np
import astropy.io.ascii as at
import astropy.io.fits as pyfits
from scipy.interpolate import InterpolatedUnivariateSpline as inter
#
# 1.- Read Vega spectrum
#
vega=at.read('libs/vega_rieke08.dat', data_start=8, names=['ldo', 'fl'])
# This is in microns so no change:
vega_ldo=np.array(vega['ldo'])
# this is w/m2/nm, so to put in photon/s/m^2/micron:
vega_flux=np.array(vega['fl'])*1e3*5.034118201E+18*vega_ldo
#
# 2.- Read sky spectrum
#
sky = pyfits.open('sky/skytable.fits')
sky_ldo = sky[1].data.field('lam')
sky_flux = sky[1].data.field('flux')

sky_new = pyfits.open('sky/skytable_10_new.fits')
sky_ldo_new = sky_new[1].data.field('lam')
sky_flux_new = sky_new[1].data.field('flux')
# sky=at.read('sky/sky_rad_10.txt',data_start=3,names=['ldo','fl'])
# # this is nm, so to micron:
# sky_ldo=np.array(sky['ldo'])*1e-3
# # this is already in photon/s/m^2/micron/arcsec
# sky_flux=np.array(sky['fl'])
#
# 3.- Now the filters we know the mag for
#
mag_sky={'Y': 18.0, 'J': 16.6, 'H': 14.4, 'Ks': 12.5}

y_filt=at.read('filters/Y_trans.dat', data_start=3, names=['ldo', 'tr'])
j_filt=at.read('filters/J_trans.dat', data_start=3, names=['ldo', 'tr'])
h_filt=at.read('filters/H_trans.dat', data_start=3, names=['ldo', 'tr'])
ks_filt=at.read('filters/Kshort_trans.dat', data_start=3, names=['ldo', 'tr'])
# ks_filt=at.read('filters/K-spec_trans.dat', data_start=3, names=['ldo', 'tr'])
filt_ldo = {'Y': np.array(y_filt['ldo']),
            'J': np.array(j_filt['ldo']),
            'H': np.array(h_filt['ldo']),
            'Ks': np.array(ks_filt['ldo'])}
filt_tr = {'Y': np.array(y_filt['tr']),
           'J': np.array(j_filt['tr']),
           'H': np.array(h_filt['tr']),
           'Ks': np.array(ks_filt['tr'])}
#
# 4.- The filters for which we don't know the mag
#
hk_filt=at.read('filters/HK_paco.dat', data_start=3, names=['ldo', 'tr'])
filt_ldo['HK']=np.array(hk_filt['ldo'])
filt_tr['HK']=np.array(hk_filt['tr'])

yj_filt=at.read('filters/YJ_smooth_trans.dat', data_start=3, names=['ldo', 'tr'])
filt_ldo['YJ']=np.array(yj_filt['ldo'])
filt_tr['YJ']=np.array(yj_filt['tr'])

# J-band
# normfilt = 'J'
# newfilt = 'Y'
# newfilt = 'YJ'
# newfilt = 'F123M'
# filt_file=at.read('filters/J_trans.dat',data_start=3,names=['ldo','tr'])
# filt_file=at.read('filters/Y_trans.dat',data_start=3,names=['ldo','tr'])
# filt_file=at.read('filters/F123M_trans.dat',data_start=3,names=['ldo','tr'])
# filt_file=at.read('filters/YJ_smooth_trans.dat', data_start=3, names=['ldo', 'tr'])

# H-band
# normfilt = 'H'
# newfilt = 'H'
# newfilt = 'FeII'
# filt_file=at.read('filters/H_trans.dat',data_start=3,names=['ldo','tr'])
# filt_file=at.read('filters/FeII_trans.dat',data_start=3,names=['ldo','tr'])

# K-band
normfilt = 'K'
# newfilt = 'K'
# newfilt = 'BrG'
# newfilt = 'H2_10'
newfilt = 'H2_21'
# filt_file=at.read('filters/Kshort_trans.dat',data_start=3,names=['ldo','tr'])
# filt_file=at.read('filters/BrG_trans.dat',data_start=3,names=['ldo','tr'])
# filt_file = at.read('filters/H2_10_trans.dat', data_start=3, names=['ldo', 'tr'])
filt_file=at.read('filters/H2_21_trans.dat',data_start=3,names=['ldo','tr'])


filt_ldo[newfilt]=np.array(filt_file['ldo'])
filt_tr[newfilt]=np.array(filt_file['tr'])

#
# 5.- Now we need to interplate everything to a reasonable
# resolution in wvl, to make the integrals smoother
#
fine_ldo = np.arange(8000, 27500, 2)*1e-4
# Vega
f = inter(vega_ldo, vega_flux)
vega_flux_fine = f(fine_ldo)
# Sky
f = inter(sky_ldo, sky_flux)
sky_flux_fine = f(fine_ldo)
# filters
fy = inter(filt_ldo['Y'], filt_tr['Y'])
fj = inter(filt_ldo['J'], filt_tr['J'])
fh = inter(filt_ldo['H'], filt_tr['H'])
fk = inter(filt_ldo['Ks'], filt_tr['Ks'])
fhk = inter(filt_ldo['HK'], filt_tr['HK'])
fyj = inter(filt_ldo['YJ'], filt_tr['YJ'])
fbrg = inter(filt_ldo[newfilt], filt_tr[newfilt])

filt_tr_fine = {'Y': fy(fine_ldo).clip(0, 1),
                'J': fj(fine_ldo).clip(0, 1),
                'H': fh(fine_ldo).clip(0, 1),
                'Ks': fk(fine_ldo).clip(0, 1)}

filt_tr_fine['HK'] = fhk(fine_ldo).clip(0, 1)
filt_tr_fine['YJ'] = fyj(fine_ldo).clip(0, 1)
filt_tr_fine[newfilt] = fbrg(fine_ldo).clip(0, 1)

#
# 6.- Now the integrals. Filters filter photons, so we need
# to go from photon/s/m^2/micron to ph/s, but the mirror size
# is the same for sky and vega, so I skip it, and the sky mags
# are per arcsec, so I forget that too


def sum_flux(flux, wvl, filt_profile):
    return np.sum(flux*wvl*filt_profile*(wvl[1] - wvl[0]))

v_int_y = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine['Y'])
sky_int_y = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine['Y'])
v_int_j = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine['J'])
sky_int_j = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine['J'])

v_int_h = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine['H'])
sky_int_h = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine['H'])

v_int_k = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine['Ks'])
sky_int_k = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine['Ks'])

# HK & YJ
v_int_hk = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine['HK'])
sky_int_hk = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine['HK'])
v_int_yj = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine['YJ'])
sky_int_yj = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine['YJ'])
# New filter
v_int_newfilt = sum_flux(vega_flux_fine, fine_ldo, filt_tr_fine[newfilt])
sky_int_newfilt = sum_flux(sky_flux_fine, fine_ldo, filt_tr_fine[newfilt])

print('Vega integral in {0} = {1}'
      .format(newfilt, v_int_newfilt))
print('Sky integral in {0} = {1}'
      .format(newfilt, sky_int_newfilt))
print('Ratio of fluxes (sky/vega) {}'.format(sky_int_newfilt/v_int_newfilt))
#
# Now the normalization factors
#
factors = {'Y': (10**(-1*mag_sky['Y']/2.5))*(v_int_y/sky_int_y),
           'J': (10**(-1*mag_sky['J']/2.5))*(v_int_j/sky_int_j),
           'H': (10**(-1*mag_sky['H']/2.5))*(v_int_h/sky_int_h),
           'K': (10**(-1*mag_sky['Ks']/2.5))*(v_int_k/sky_int_k)}
# j_norm=(10**(-1*mag_sky['J']/2.5))*(v_int_j/sky_int_j)
# h_norm=(10**(-1*mag_sky['H']/2.5))*(v_int_h/sky_int_h)
# k_norm=(10**(-1*mag_sky['Ks']/2.5))*(v_int_k/sky_int_k)
# print('normal_1, 2 (K, H) = {0}, {1}'.format(k_norm, h_norm))
#
# And we calculate the magnitude for the HK filter
#
mag_1 = -2.5*np.log10(sky_int_hk*factors['K']/v_int_hk)
mag_2 = -2.5*np.log10(sky_int_hk*factors['H']/v_int_hk)
mag_yj_y = -2.5*np.log10(sky_int_yj*factors['Y']/v_int_yj)
mag_yj_j = -2.5*np.log10(sky_int_yj*factors['J']/v_int_yj)
mag_newfilt = -2.5*np.log10(sky_int_newfilt*factors[normfilt]/v_int_newfilt)
#
# Results
#
print('Integrated magnitudes in JHK for comparison:')
print('Mag in Y-band {}'.format(-2.5*np.log10(sky_int_y/v_int_y)))
print('Mag in J-band {}'.format(-2.5*np.log10(sky_int_j/v_int_j)))
print('Mag in H-band {}'.format(-2.5*np.log10(sky_int_h/v_int_h)))
print('Mag in Ks-band {}\n'.format(-2.5*np.log10(sky_int_k/v_int_k)))

print('Mag in HK normalized to Ks: {0:.2f}'.format(mag_1))
print('Mag in HK normalized to H: {0:.2f}'.format(mag_2))
print('Mag in YJ normalized to Y: {0:.2f}'.format(mag_yj_y))
print('Mag in YJ normalized to J: {0:.2f}'.format(mag_yj_j))
print('Mag in {0} normalized to {1}: {2:.2f}'
      .format(newfilt, normfilt, mag_newfilt))
