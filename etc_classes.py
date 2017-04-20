"""
Author: XXX (CG probably)
Date: XXX
Description (LRP): the SpecCurve class for the etc_gui.py

"""
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as Inter
from scipy import polyval
from scipy import polyfit

from etc_modules import getdata


class SpecCurve(object):
    """
    Class for spectral curves
    This is an envelope for all transmission
    and emission curves to be used
    """

    def __init__(self, data_file):
        """Initialise"""
        super(SpecCurve, self).__init__()
        temp = getdata(data_file)
        self.unitx0 = temp['unit_x']
        self.unity0 = temp['unit_y']
        self.wvl0 = temp['wvl']
        self.fl0 = temp['fl']
        #
        #    This handles unit conversion for the wavelengths
        #    everything gets transformed into microns
        #
        if self.unitx0 == 'ang':
            self.wvl = temp['wvl']/1e4
            self.unitx = 'micron'
        elif self.unitx0 == 'nm':
            self.wvl = temp['wvl']/1e3
            self.unitx = 'micron'
        else:
            self.wvl = temp['wvl']
            self.unitx = self.unitx0
        #
        # This handles unit conversion for the fluxes.
        # Percentages get transformed to unitary ratios.
        # Fluxes get transformed into photons/s/m2/micron/arc2
        # or photons/s/m2/micron for point sources
        #
        # Normalized fluxed (this is, normalized to a given point
        # or value, not continuum-normalized) can be in photons
        # (normal_photon) or in energy (normal_flux). The latter
        # gets transformed into the former
        #
        # Sometimes throughput measures of filters have negative values
        # that might be problematic when interpolating
        if self.unity0 == 'percent':
            self.fl = (temp['fl']/100.).clip(0)
            self.unity = 'perone'
        elif self.unity0 == 'perone':
            self.fl = (temp['fl']).clip(0)
            self.unity = 'perone'
        elif self.unity0 == 'W/m2/nm':
            fl_t = temp['fl']*1e3  # to W/m^2/um
            fl_t = fl_t*5.034118201E+18*self.wvl  # to phot/s/m^2/micron
            self.fl = fl_t
            self.unity = 'photon/s/m2/micron'
        elif self.unity0 == 'W/m2/micron':
            fl_t = temp['fl']*5.034118201E+18*self.wvl  # to phot/s/m^2/micron
            self.fl = fl_t
            self.unity = 'photon/s/m2/micron'
        elif self.unity0 == 'photon/s/m2/micron/arcsec2':
            self.fl = temp['fl']
            self.unity = 'photon/s/m2/micron/arcsec2'
        elif self.unity0 == 'photon/s/m2/nm/arcsec2':
            self.fl = temp['fl']*1e3
            self.unity = 'photon/s/m2/micron/arcsec2'
        elif self.unity0 == 'normal_flux':
            self.fl = temp['fl']*self.wvl
            self.unity = 'normal_photon'
        else:
            self.fl = temp['fl']
            self.unity = self.unity0

    def interpolate(self, wvl):
        """
        Interpolation to a given wvl array. Returned values
        are clipped to 0, and if it is a transmission curve, also to ones.

        Order=1 used, as larger orders produce weird effects around corners.
        """
        if self.unity == 'perone':
            inter_func = Inter(self.wvl, self.fl, k=1)
            result = inter_func(wvl).clip(0, 1)
        else:
            inter_func = Inter(self.wvl, self.fl, k=1)
            result = inter_func(wvl).clip(0)

        # To avoid weird extrapolations, a lineal fit to the
        # extreme points of the original curve is used

        ind_i = np.where(wvl <= self.wvl.min())[0]
        ind_f = np.where(wvl >= self.wvl.max())[0]
        # MB 2016-10-30 make nel integer to avoid deprecation warning
        nel = int(np.clip(0.1*len(self.wvl), 3, 20))

        if len(ind_i) >= 1:
            cof = polyfit(self.wvl[0:nel], self.fl[0:nel], 1)
            #
            # This makes the transition smooth, if not there is a break as
            # linfit is evaluated not only at the last point and the coordinate
            # at the origin of the fit makes the extrapolated curve jump
            #
            temp = polyval(cof, wvl[ind_i])
            result[ind_i] = (temp + (self.fl[0] - temp[-1])).clip(0)

        if len(ind_f) >= 1:
            cof = polyfit(self.wvl[-1*nel:], self.fl[-1*nel:], 1)
            temp = polyval(cof, wvl[ind_f])
            # temp2 = polyval(cof, self.wvl[-1])
            result[ind_f] = (temp + (self.fl[-1] - temp[0])).clip(0)

        return result
