"""
Author: XXX (probably CG)
Date: XXX
Description (LRP): functions to setup the configuration of the ETC


Updated:
Author: LRP
Date: 14-04-2017
Description: Added dictionary of skymag values
All obsolete filters moved to LRP's local directory

Author: LRP
Date: 16-03-2017
Description: Updated config files

Author: LRP
Date: 08-12-2016
Description: Updated config files

Author: LRP
Date: 28-11-2016
Description: Including the Y filter

"""


def get_config(filt='Ks', grism='K'):
    """Load files for each component"""
    # Fixed elements
    # Updated by LRP from MBC's ETC
    telescope_file = 'components/GTC_m1m2m3.dat'
    optics_file = 'components/EMIR_coll_cam_peri.dat'
    qe_file = 'components/HAWAII_QE_EMIR.dat'

    # SED templates
    vega_file = 'libs/vegfluxtot.dat'
    return {'telescope': telescope_file, 'optics': optics_file,
            'qe': qe_file, 'vega': vega_file}


def get_models():
    """
    Give the model <-> filename as a dictionary. It adds
    the order so that in the menu they appear nice.
    """
    temp = open('libs/models.txt')
    mod = temp.readlines()
    temp.close()
    models = {}
    order = []
    for i in mod:
        temp = i.split()
        if len(temp) > 2:
            models[temp[2]] = temp[1]
            order.append(temp[2])
    return models, order


def get_filter(filt='Ks'):
    """Get the proper filter and returns it as a speccurve object"""
    from etc_classes import SpecCurve

    # Broad Band Photometry:
    if (filt == 'Y'):
        filter_file = 'filters/Y_trans.dat'
    elif (filt == 'J'):
        filter_file = 'filters/J_trans.dat'
    elif (filt == 'H'):
        filter_file = 'filters/H_trans.dat'
    elif (filt == 'Ks'):
        filter_file = 'filters/Kshort_trans.dat'

    # Narrow band photometry:
    elif (filt == 'FeII'):
        filter_file = 'filters/FeII_trans.dat'
    elif (filt == 'FeII_cont'):
        filter_file = 'filters/FeII_cont_trans.dat'
    elif (filt == 'BrG'):
        filter_file = 'filters/BrG_trans.dat'
    elif (filt == 'BrG_cont'):
        filter_file = 'filters/BrG_cont_trans.dat'
    elif (filt == 'H2(1-0)'):  # Added LRP 16-03-2017
        filter_file = 'filters/H2_10_trans.dat'
    elif (filt == 'H2(2-1)'):  # Added LRP 16-03-2017
        filter_file = 'filters/H2_21_trans.dat'

    # Medium band:
    elif (filt == 'F123M'):
        filter_file = 'filters/F123M_trans.dat'

    # Spectroscopic filters
    elif (filt == 'Kspec'):
        filter_file = 'filters/K-spec_trans.dat'
    elif (filt == 'YJ'):
        filter_file = 'filters/YJ_smooth_trans.dat'
    elif (filt == 'HK'):
        filter_file = 'filters/HK_paco.dat'

    return SpecCurve(filter_file)


def get_grism(grism='K'):
    """
    Get the proper grism and returns it as a
    speccurve object, along with the associated filter

    MBC 2016-10-29 increase 'res' values so spectral dispersion is as
    measured in commissioning (Nicolas lambda cal with sky lines)
    NB the safer way is to get 'res' from commissioning data,
    and adjust the number of pixels per resolution element where required.
    """
    from etc_classes import SpecCurve

    if (grism == 'K'):
        grism_file = 'grisms/grism_k.dat'
        filter_curve = get_filter('Kspec')
        res = 4000.*1.067485  # up by 6.7485%
    elif (grism == 'H'):
        grism_file = 'grisms/grism_h.dat'
        filter_curve = get_filter('H')
        res = 4250.*1.052066  # up by 5.2%
    elif (grism == 'J'):
        grism_file = 'grisms/grism_j.dat'
        filter_curve = get_filter('J')
        res = 5000.*1.085924  # up by 8.5924%

    # Low Resolution Grisms:

    elif (grism == 'YJ'):
        grism_file = 'grisms/grism_yj.dat'
        filter_curve = get_filter('YJ')
        res = 987.
    elif (grism == 'HK'):
        grism_file = 'grisms/grism_hk.dat'
        filter_curve = get_filter('HK')
        res = 987.
    return res, SpecCurve(grism_file), filter_curve


def get_skymag(filt):
    """
    Return the sky magnitude appropriate for the filter
    J, H and K values are emprical values from La Palma technical note #115
    http://www.ing.iac.es/Astronomy/observing/conditions/skybr/skybr.html
    Note: Value for K quote on document is typo, should be 12.5 not 12.0

    All other filters are calibrated to these measurements.
    Calculated using the get_mag_sky.py routine (author: GCF)

    ING values implmented so far:
     Y       J      H        K
    18.0   16.6    14.4    12.5

    From the NOT webpages:

    "Estimated near IR sky brightness
    J=15-16, H=13-14, K=12-13"

    From the TNG-NICS webpages:
    "
    1um     Js       J       H       K'       K
    16.5    15.5    15.5    14.0    13.2    12.6
    "
    """
    skymag_dict = {
        # Broad band filters:
        "Y": 18.0, "J": 16.6, "H": 14.4, "Ks": 12.5,
        # Spectroscopic filters:
        "YJ": 16.3, "HK": 13.7, "K": 12.5,
        # Narrow band filters:
        "FeII": 12.5, "FeII_cont": 12.5, "BrG": 15.4, "BrG_cont": 15.4,
        "H2(1-0)": 13.3, "H2(2-1)": 12.0,
        # Medium band filters:
        "F123M": 17.0}
    return skymag_dict[filt]


def get_params():
    """
    Load the fixed parameters of the system (RON, DC, Seeing, etc.)
    Values are taken for Vr=0.7, OFF=14
    """
    # Telescope
    # Taking into account baffling pi*(0.5*10.4)**2
    collector_area = 73.  # m2
    # Paco cambio 22/09/16
    # Updated by LRP 12-12-2016 from Marc's version
    scale = 0.1922        # arcsec/px
    # Detector
    # Paco cambio 22/09/16
    # Updated by LRP 12-12-2016 from Marc's version
    dark_current = 0.25   # e-/s/px
    readout_noise = 15.0  # e-/px
    well_depth = 166981   # e-
    gain = 3.33           # e-/ADU

    return {'DC': dark_current, 'RON': readout_noise, 'gain': gain,
            'well': well_depth, 'area': collector_area, 'scale': scale}
