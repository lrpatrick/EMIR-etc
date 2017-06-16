"""
Author: XXX (probably CG)
Date: XXX
Description (LRP): Different functions for the etc_gui.py script

Updated:
Author: LRP
Date: 28-11-2016 and 12-12-2016
"""

import numpy as np
from etc_config import get_params
from scipy.interpolate import InterpolatedUnivariateSpline as Inter
import astropy.io.fits as pyfits


def bbody(wvl, teff):
    """Compute bb radiation for wavelength in microns and t in kelvin"""
    h = 6.62606957E-34  # J.s
    c = 299792458       # m/s
    k = 1.3806488E-23   # J/K

    freq = c/(wvl*1e-6)

    # From J/s/Hz to W/m2/Hz there is a constant that depends on the distance
    # to the source and the solif angle, as this will be normalized with Vega,
    # it is not necessary.
    # J/s/Hz=W/m2/Hz
    ibb = 2*h*(freq**3)*(c**(-2))*(np.exp((h*freq)/(k*teff)) - 1)**(-1)
    ibb = 2.99792458E+21*ibb/((wvl*1e4)**2)   # erg/cm^2/s/A
    ibb = 5.03411250E+07*ibb*(wvl*1e4)        # photon/cm^2/s/A
    return ibb


def checkforsaturation(data):
    """Check whether any element of the array is saturated"""
    param = get_params()
    return True if np.any(data >= param['well']) else False


def convolres(ldo, fl, res_el):
    """
    Convolve the inpuut spectrum to the desired resolution.
    The resolution element is assumed to be the FWHM
    """
    # Sigma in pixels, res el taken to be FWHM
    sigma = (res_el/(ldo[1] - ldo[0]))/2.354
    x = np.arange(sigma*10) - sigma*5  # Vector large enough, centered
    kernel = np.exp(-0.5*(x/sigma)**2)

    # Pad at the sides to avoid windowing
    # MB 2016-10-30 make window_len integer to avoid deprecation warning
    window_len = int(np.round(sigma))
    s = np.r_[fl[window_len - 1:0:-1], fl, fl[-1:-window_len:-1]]
    y = np.convolve(kernel/kernel.sum(), s, mode='same')
    return y[len(fl[window_len - 1:0:-1]):len(y) - len(fl[-1:-window_len:-1])]


def emline(wvl, cen, width, flx):
    """
    Compute a line profile centered at cen, with FWHM width and total flux flx
    Flux in erg/cm2/s, wvl in microns
    """
    sigma = width/2.354
    fl_t = np.exp(-0.5*((wvl - cen)/sigma)**2)

    # normalizing to the total flux and converting to erg/cm2/s/A
    fl_t = 1e-4*(flx*fl_t/fl_t.sum())/(wvl[1] - wvl[0])

    # Flux has to be translated into photon/s
    fl_t = 1e-3*fl_t                     # to W/m2/A
    fl_t = fl_t*5.034118201E+18*wvl*1e4  # to photon/s/m^2/um
    return fl_t


def getbin(wvl):
    """Get the wavelength bin"""
    wvl_bin = np.zeros_like(wvl)
    wvl_bin[0] = wvl[1] - wvl[0]
    for i in range(1, len(wvl_bin)):
        wvl_bin[i] = wvl[i] - wvl[i - 1]
    return wvl_bin


def getdata(fil=''):
    """
    Get the wavelength and transmission, flux, etc. from a file
    It stores the units of this file, that have to be the two first
    lines of the archive into two separate variables
    LRP : what units do these have to be???
    """
    arch = open(fil)
    temp = arch.readlines()
    arch.close()
    ldo = []
    fl = []
    for i in temp:
        line = i.split()
        if len(line) >= 2 and line[0][0].isdigit():
            ldo.append(float(line[0]))
            fl.append(float(line[1]))

    u1 = (temp[0].replace("\n", '')).replace("\r", '')
    u2 = (temp[1].replace("\n", '')).replace("\r", '')

    return {'unit_x': u1, 'unit_y': u2, 'wvl': np.array(ldo),
            'fl': np.array(fl)}


def getfiltwidth(wvl, filt):
    """Return the width (measured at 50% transmitance) of a filter"""
    temp = filt - 0.5
    imin = 0
    imax = len(wvl) - 1
    for i in range(1, len(wvl)):
        prod = temp[i]*temp[i - 1]
        if (prod <= 0) & (imin == 0):
            imin = i
        elif (prod <= 0):
            imax = i
    return [imin, imax]


def getnoise(image, t_exp):
    """
    Return the noise image to a given input,
    including RON, shot noise of all the signals and DC
    """
    param = get_params()
    ron = np.ones_like(image)*param['RON']               # Readout noise
    dc = np.ones_like(image)*np.sqrt(param['DC']*t_exp)  # Dark Current
    shot = np.sqrt(image)                                # Shot noise
    # Added in quad.
    noise = np.sqrt(ron**2 + dc**2 + shot**2)
    return noise


def getspread(flux=1., seeing=0.6, photo=0):
    """Spread the flux over seeing disc/profile"""
    param = get_params()
    sigma = seeing/2.354
    x_t = param['scale']*(np.arange(100) - 50)

    if photo == 1:
        # Generating 2D image of seeing as gaussian
        image = np.zeros((100, 100))
        for i in range(0, 100):
            image[i, :] = np.exp(-0.5*(x_t/sigma)**2)*\
                np.exp(-0.5*(param['scale']*float(i-50)/sigma)**2)

    if photo == 0:
        # Generating 1D image of seeing as gaussian
        image = np.exp(-0.5*(x_t/sigma)**2)

    # Normalize to total flux
    image = image*flux/image.sum()
    return image


def interpolatesky(airmass, wvl):
    """
    Interpolate sky curves with airmass and generate fit to be used by ETC
    Sky tables generated using ESO's SkyCalc tool
    Sky tables contain all parameters used
    """
    sky25 = pyfits.open('sky/skytable_25.fits')
    sky20 = pyfits.open('sky/skytable_20.fits')
    sky15 = pyfits.open('sky/skytable_15.fits')
    sky10 = pyfits.open('sky/skytable_10.fits')

    t25 = sky25[1].data.field('trans')
    t20 = sky20[1].data.field('trans')
    t15 = sky15[1].data.field('trans')
    t10 = sky10[1].data.field('trans')

    e25 = sky25[1].data.field('flux')
    e20 = sky20[1].data.field('flux')
    e15 = sky15[1].data.field('flux')
    e10 = sky10[1].data.field('flux')

    am = np.array([1.0, 1.5, 2.0, 2.5])
    wvl_ori = sky25[1].data.field('lam')

    # This should be upated to include all nominal airmass values
    if airmass == 1.0:
        t_inter = t10
        a_inter = e10
    else:
        t_inter = np.zeros(len(wvl_ori))
        a_inter = np.zeros(len(wvl_ori))
        for i in range(len(wvl_ori)):
            trans = np.array([t10[i], t15[i], t20[i], t25[i]])
            rad = np.array([e10[i], e15[i], e20[i], e25[i]])
            inter_func = Inter(am, trans, k=1)
            t_inter[i] = inter_func(airmass)
            inter_func = Inter(am, rad, k=1)
            a_inter[i] = inter_func(airmass)

    inter_func = Inter(wvl_ori, t_inter, k=1)
    trans_final = inter_func(wvl)
    inter_func = Inter(wvl_ori, a_inter, k=1)
    rad_final = inter_func(wvl)

    # import pdb; pdb.set_trace()

    return trans_final, rad_final


def mag_convert(filt):
    """
    The use of these corrections is : m_AB = m_Vega + conv_AB
    # From Roser:
    #  n       wl_eff     surface   bandpass1  conv_AB
    #              A          A          A       (mags)
    Y    1   10187.524   1021.072    642.483    0.621
    J    2   12565.214   1502.516    951.536    0.950
    H    3   16352.561   2622.795   1634.486    1.390
    Ks   4   21674.443   2919.557   1848.038    1.873
    K    5   21669.438   2917.865   1848.177    1.873
    #  n     wl_eff     surface   bandpass1  conv_AB
               A           A          A         mag
    F123M   12041.662    480.423    282.823    0.872
    FeII    16469.611    308.730    237.192    1.404
    FeII c  17140.035    286.924    220.561    1.482
    BrG     21756.217    367.331    276.122    1.883
    BrG c   21276.980    312.741    236.999    1.845
    H2(1-0) 21247.080    317.209    239.540    1.842
    H2(2-1) 22478.545    305.222    232.791    1.941
    """
    conv_ab = {
        # Broad band filters:
        'Y': 0.621, 'J': 0.950, 'H': 1.390, 'Ks': 1.873,
        # Narrow band filters:
        "FeII": 1.404, "FeII_cont": 1.482, "BrG": 1.883, "BrG_cont": 1.845,
        "H2(1-0)": 1.842, "H2(2-1)": 1.941,
        # Medium band filters:
        "F123M": 0.872,
        # Spectroscopy:
        # Low-res grisms use 'red' filter as this is what is requred as input
        'K': 1.873, 'YJ': 0.950, 'HK': 1.873}
    return conv_ab[filt]


# def reality_factor(filt):
#     """Scale the final S/N with an empirically defined reality factor"""
#     reality = {
#         # Broad band filters:
#         'Y': 1.0, 'J': 1.0, 'H': 1.0, 'Ks': 1.75,
#         # Spectroscopic filters:
#         "YJ": 1.0, "HK": 1.0, "K": 1.0,
#         # Narrow band filters:
#         "FeII": 1.0, "FeII_cont": 1.0, "BrG": 1.0, "BrG_cont": 1.0,
#         "H2(1-0)": 1.0, "H2(2-1)": 1.0,
#         # Medium band filters:
#         "F123M": 1.0}
#     return reality[filt]


def reality_factor(filt):
    """
    Scale the final S/N with an empirically defined reality factor

    FGL 13jun
    Better, scale the meas. counts with an empirically defined reality factor.
    """
    reality = {
        # Broad band filters:
        'Y': 0.21, 'J': 0.5, 'H': 0.9, 'Ks': 1.8,
        # Spectroscopic filters:
        "YJ": 1.0, "HK": 1.0, "K": 1.0,
        # Narrow band filters inherit rf values from broad band filters
        # Narrow band filters:
        "FeII": 0.9, "FeII_cont": 0.9, "BrG": 1.8, "BrG_cont": 1.8,
        "H2(1-0)": 1.8, "H2(2-1)": 1.8,
        # Medium band filters:
        "F123M": 0.5}
    return reality[filt]


def rebinwvl(wvl0, flux, wvl1):
    """Rebin a spectrum onto a coarser wavelength sampling"""
    flux1 = np.zeros_like(wvl1)
    n_el = np.zeros_like(wvl1)
    delta1 = wvl1[1] - wvl1[0]
    for i in range(len(wvl1)):
        ind = np.where((wvl0 >= wvl1[i] - 0.5*delta1) &
                       (wvl0 < wvl1[i] + 0.5*delta1))
        if len(ind) > 0:
            flux1[i] = flux[ind[0]].sum()
            n_el[i] = float(len(ind[0]))
    # Corrige que hay pixeles con 10 muestras en lugar de 9
    return flux1/n_el*n_el.mean()


def slitpercent(seeing, slitwd):
    """
    Calculate the flux lost due to the relation seeing/slit width.
    Seeing is always FWHM
    """
    sigma = seeing/2.354
    xs = np.arange(1000)/100. - 5
    ys = np.exp(-0.5*(xs/sigma)**2)
    ys = ys/ys.sum()
    # px inside the slit
    ind = np.where(np.abs(xs) <= slitwd*0.5)[0]
    perone = ys[ind].sum()
    return perone


def spec_int(wvl0, fl0, wvl1):
    """Interpolation to a given wvl array."""
    inter_func = Inter(wvl0, fl0, k=3)
    result = inter_func(wvl1).clip(0)
    return result


def vega(obj, vega, filt):
    """
    Take a given normalized spectrum, that must be in photons
    and normalizes it to have zero magnitude under given filter

    Old name: scale_to_vega
    """
    vega_photons = (vega*filt).sum()
    obj_photons = (obj*filt).sum()
    return obj*vega_photons/obj_photons
