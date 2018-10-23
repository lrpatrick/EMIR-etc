#!/usr/bin/env python
"""
Created:
Author: ???
Date: ???
Description: (LRP)
EMIR ETC python main script. These routines consists of an underlying python
script to claculate exposure times for EMIR Photometry and Spectroscopy with
a wrapper (also in python) to make the scripts usable online

The underlying python script was written by Carlos Gonzalez-Fernandez
(cambridge) and the wrapper was written by Matteo Miluzio (ESAC)

v2.0.10 22-10-2018
    Bug fix in spectroscopy range (split loops for spec. and phot. )


v1.0.9 27-04-2018
    Fix bug to add a dependence on the input magnitude for 'Model file' when
    'normal_flux' is used as units

v1.0.8 14-04-2017
    Standard structure for all filter files
    Improved standardisation of etc_modules
    Added addtional output for spectroscopy
    Corrected bugs that distored S/N estimate
    Added new sky emission and transmission files at below 1.0um

v1.0.7 20-03-2017
    Used standard structure for (some) filter files
    (others need to be implemented)
    Correct a bug regarding the median values of the S/N

v.1.0.6 27-01-2017
    Updated the previous change to the resolution element calculation.
    More updates of code standardisation (still not complete!)

v.1.0.5 09-12-2016
    In this file, updated the way the resolution element is calculated in
    getSpecSton

v.1.0.4 08-12-2016
    Major updates of code standardisation
    Merged with ETC from Marc Balcells
    Much more ouput for spec. mode

v.1.0.3 05-12-2016
    Included fix for using 'Model file' that now does not depend upon the
    input magnitude
    Added F123M filter at request of Marc Balcels
    Updated 07-12-2016 to correct F123M transmission

TODO: Make better naming choices for variables
Work out where the slowest parts of this code are

Author: LRP lpatrick@iac.es
Date: 28-11-2016
Description:
Updated to correct the output exposure times in output xml file and figures
Updated to add the Y filter as an option in photometry
Added version numer as v1.0

"""
import numpy as np
import sys
import xml.etree.ElementTree as ET
from optparse import OptionParser

import emir_guy
import etc_config as con
import etc_modules as mod
from etc_classes import SpecCurve

import matplotlib
matplotlib.use('Agg')  # Do we actually need agg?
import matplotlib.pylab as plt

description = ">> Exposure Time Calculator for EMIR. Contact Lee Patrick"
usage = "%prog [options]"

version = '2.0.10'

if len(sys.argv) == 1:
    print(help)
    sys.exit()
parser = OptionParser(usage=usage, description=description)
parser.add_option("-d", "--directory", dest="directory",
                  default='', help='Path of the xml file \n  [%default]')
option, args = parser.parse_args()


class EmirGui:
    """GUI for the ETC"""

    def __init__(self):
        """Initialise"""
        # When the application is loaded, all the fixed elements of the system
        # (optics, etc.) plus the sky curves are loaded
        global ff
        config_files = con.get_config()
        # Changed to 80000 by LRP on 04-04-2017
        self.ldo_hr = (8000 + np.arange(100001)*0.2)*1e-4

        # Fixed elements of the system

        qe = SpecCurve(config_files['qe'])
        optics = SpecCurve(config_files['optics'])
        tel = SpecCurve(config_files['telescope'])

        # Addition from MCB's ETC by LRP
        self.qe_hr = qe.interpolate(self.ldo_hr)
        self.optics_hr = optics.interpolate(self.ldo_hr)
        self.tel_hr = tel.interpolate(self.ldo_hr)
        self.tel_trans = self.qe_hr*self.optics_hr*self.tel_hr
        # End addition

        try:
            ff = emir_guy.readxml(args[0] + '.xml')
        except:
            print("ERROR opening XML file")
            exit()

        emir_guy.load(self)
        emir_guy.check_inputs(ff, args[0])

        # Vega spectrum for normalizations

        self.vega = SpecCurve(config_files['vega']).interpolate(self.ldo_hr)

        # Functions for options:
        if ff['operation'] == 'Photometry':
            self.doPhotometry()
        elif ff['operation'] == 'Spectroscopy':
            self.doSpectroscopy()

    def doPhotometry(self):
        """Photometry initialisations"""
        self.mode_oper = 'ph'
        # Convert magnidutes into Vega system (if appropriate)
        if ff['system'] == 'AB':
            conv_ab = mod.mag_convert(ff['photo_filter'])
            # conv_ab = 0.1
            ff['magnitude'] = float(ff['magnitude']) - conv_ab

        # Obtaining configuration parameters from GUI
        self.mag = float(ff['magnitude'])
        self.seeing = float(ff['seeing'])
        self.airmass = float(ff['airmass'])
        self.sky_t, self.sky_e = mod.interpolatesky(self.airmass, self.ldo_hr)
        self.filtname = ff['photo_filter']

        self.buildObj()
        # We have to break the texp into its bits
        temp = ff['photo_exp_time'].split('-')
        if len(temp) == 1:
            # This creates a one length array, so that len(texp) doesn't crash
            self.texp = np.array([float(temp[0])])
            self.timerange = 'Single'
        else:
            tmin = float(temp[0])
            tmax = float(temp[1])
            self.texp = tmin + (tmax - tmin)*np.arange(10)/9.
            self.timerange = 'Range'

        # Number of frames
        self.nobj = float(ff['photo_nf_obj'])
        self.nsky = float(ff['photo_nf_sky'])

        # Filter transmission curve
        self.filt = con.get_filter(self.filtname)
        self.filt_hr = self.filt.interpolate(self.ldo_hr)

        self.filt_hr = self.filt.interpolate(self.ldo_hr)
        # Addition from MCB's ETC by LRP
        self.efftotal_hr = self.tel_hr*self.optics_hr*self.filt_hr*self.qe_hr

        # Calling the function that calculates the STON
        ston, signal_obj, signal_sky, saturated,\
            params, fl_obj, fl_sky = self.getPhotSton(self.texp,
                                                      self.nobj,
                                                      self.nsky)

        if self.timerange == 'Range':
            # self.printResults(self.texp,ston,saturated)
            self.printXML(signal_obj, signal_sky,
                          ston, saturated, **params)
            lineObjects = plt.plot(self.texp*self.nobj, ston)
            plt.legend(iter(lineObjects),
                       ('1.2*seeing', '2.0*seeing', 'Per pixel'),
                       loc=2)
            plt.xlabel('Exposure time (seconds)')
            if ff['source_type'] == 'Point':
                plt.ylabel('S/N')
            if ff['source_type'] == 'Extended':
                plt.ylabel('S/N per pixel')
            # import pdb; pdb.set_trace()

            plt.savefig(args[0] + '_fig.png')
        else:
            self.printXML(signal_obj, signal_sky,
                          ston, saturated, **params)
            # TODO: Create some meaniningful graphic output!
            # Create some figures:
            plt.figure(1, figsize=(15., 10.))
            # plt.subplot(321)
            # plt.plot(self.ldo_hr, fl_obj, color='b', label='Obj. spectrum')
            # plt.xlim(self.ldo_hr[0], self.ldo_hr[-1])
            # plt.xlabel('Wavelength (micron)')
            # plt.ylabel('Souce counts ADU/pixel')
            plt.subplot(322)
            plt.plot(self.ldo_hr, self.qe_hr, '-r', label='Det')
            plt.plot(self.ldo_hr, self.filt_hr, '-c', label='Filter')
            plt.plot(self.ldo_hr, self.optics_hr, '-b', label='Optics')
            plt.plot(self.ldo_hr, self.tel_hr, '--b', label='Tel')
            plt.plot(self.ldo_hr, self.efftotal_hr, '-k', label='Qtot')
            plt.xlim(self.ldo_hr[0], self.ldo_hr[-1])
            plt.legend(bbox_to_anchor=(1.3, 1.05))
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('efficiency / band')
            # plt.subplot(323)
            # plt.plot(self.ldo_hr, fl_sky, color='r', label='Sky spectrum')
            # plt.xlim(self.ldo_hr[0], self.ldo_hr[-1])
            # plt.xlabel('Wavelength (micron)')
            # plt.ylabel('Sky counts ADU/pixel')
            # plt.subplot(324)
            # plt.plot(self.ldo_hr, self.sky_e, color='r', label='Sky spectrum')
            # plt.xlim(self.ldo_hr[0], self.ldo_hr[-1])
            # plt.xlabel('Wavelength (micron)')
            # plt.ylabel('Sky counts ADU/pixel')
            plt.savefig(args[0] + '_photo.png')

    def doSpectroscopy(self):
        """Spectroscopy initialisations"""
        self.mode_oper = 'sp'
        # Convert magnidutes into Vega system (if appropriate)
        self.grismname = ff['spec_grism']
        if ff['system'] == 'AB':
            conv_ab = mod.mag_convert(self.grismname)
            ff['magnitude'] = float(ff['magnitude']) - conv_ab

        # Obtaining configuration parameters from GUI
        self.mag = float(ff['magnitude'])
        self.seeing = float(ff['seeing'])
        self.airmass = float(ff['airmass'])
        self.slitwidth = float(ff['spec_slit_width'])
        self.sloss = mod.slitpercent(self.seeing, self.slitwidth)

        self.sky_t, self.sky_e = mod.interpolatesky(self.airmass, self.ldo_hr)
        self.buildObj()

        #    We have to break the texp into its bits
        temp = ff['spec_exp_time'].split('-')
        if len(temp) == 1:
            # This creates a one length array, so that len(texp) does't crash
            self.texp = np.array([float(temp[0])])
            self.timerange = 'Single'
        else:
            tmin = float(temp[0])
            tmax = float(temp[1])
            self.texp = tmin + (tmax - tmin)*np.arange(10)/9.
            self.timerange = 'Range'

        # Number of frames
        self.nobj = float(ff['spec_nf_obj'])
        self.nsky = float(ff['spec_nf_sky'])

        # The filter transmission curve
        #
        self.specres, self.grism, self.filt = con.get_grism(self.grismname)
        self.filt_hr = self.filt.interpolate(self.ldo_hr)
        self.grism_hr = self.grism.interpolate(self.ldo_hr)
        self.disp_trans = self.filt_hr*self.grism_hr
        # Addition from MCB's ETC by LRP
        self.efftotal_hr = self.tel_hr*self.optics_hr*self.filt_hr*\
            self.grism_hr*self.qe_hr
        #
        #    Calling the function that calculates the STON
        #

        if self.timerange == 'Single':
            ston, src_cnts, sky_cnts, sp,\
                saturated, params = self.getSpecSton(self.texp, self.nobj,
                                                     self.nsky)
            if ff['template'] == 'Emission line':
                # np.argmax(ston) then get the signal from the pixels surrounding the max
                # idx_sn = np.argmax(ston)
                # num_pix = np.int(np.round(self.res_ele/self.dpx))
                # idx_res_ele = [np.arange(idx_sn - num_pix/2, idx_sn + num_pix/2, 1)]
                # ston_inresele = ston[idx_res_ele] -- this step is the problem
                # ston_resele = np.sum(ston_inresele)

                # ston_resele = np.max(ston)*self.res_ele/self.dpx
                self.printXML([np.max(src_cnts)],
                              [np.median(sky_cnts[np.nonzero(sky_cnts)])],
                              [np.max(ston)],
                              saturated, **params)
            else:
                # ston_resele = np.median(ston[np.nonzero(ston)])*self.res_ele/self.dpx
                self.printXML([np.median(src_cnts[np.nonzero(src_cnts)])],
                              [np.median(sky_cnts[np.nonzero(sky_cnts)])],
                              [np.median(ston[np.nonzero(ston)])],
                              saturated, **params)

            # Create some figures:
            plt.figure(1, figsize=(15., 10.))
            plt.subplot(321)
            plt.plot(self.ldo_px, ston, color='b')
            med_spec = np.median(ston[np.nonzero(ston)])
            x_med = np.linspace(self.ldo_px[0], self.ldo_px[-1])
            plt.plot(x_med, np.linspace(med_spec, med_spec), color='r')
            plt.xlim(self.ldo_px[0], self.ldo_px[-1])
            plt.xlabel('Wavelength (micron)')
            if ff['source_type'] == 'Point':
                plt.ylabel('S/N')
            if ff['source_type'] == 'Extended':
                plt.ylabel('S/N per pixel')

            plt.subplot(323)
            plt.plot(self.ldo_px, src_cnts)
            plt.plot(self.ldo_px, sky_cnts)
            plt.xlim(self.ldo_px[0], self.ldo_px[-1])
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('Source ADU/pixel')

            plt.subplot(325)
            plt.plot(self.ldo_px, sp)
            plt.xlim(self.ldo_px[0], self.ldo_px[-1])
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('Normalized src flux')

            plt.subplot(322)
            plt.plot(self.ldo_hr, self.qe_hr, '-r', label='Det')
            plt.plot(self.ldo_hr, self.grism_hr, '--c', label='Grism')
            plt.plot(self.ldo_hr, self.filt_hr, '-c', label='Filter')
            plt.plot(self.ldo_hr, self.optics_hr, '-b', label='Optics')
            plt.plot(self.ldo_hr, self.tel_hr, '--b', label='Tel')
            plt.plot(self.ldo_hr, self.efftotal_hr, '-k', label='Qtot')
            plt.xlim(self.ldo_px[0], self.ldo_px[-1])
            plt.legend(bbox_to_anchor=(1.3, 1.05))
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('efficiency / band')

            plt.subplot(324)
            plt.plot(self.ldo_hr, self.efftotal_hr, '-k', label='Qtot')
            plt.xlim(self.ldo_px[0], self.ldo_px[-1])
            plt.legend(bbox_to_anchor=(1.3, 1.05))
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('Eff Tel to Det')

            plt.subplot(326)
            plt.plot(self.ldo_hr, self.qe_hr, '-r', label='Det')
            plt.plot(self.ldo_hr, self.grism_hr, '--c', label='Grism')
            plt.plot(self.ldo_hr, self.filt_hr, '-c', label='Filter')
            plt.plot(self.ldo_hr, self.optics_hr, '-b', label='Optics')
            plt.plot(self.ldo_hr, self.tel_hr, '--b', label='Tel')
            plt.plot(self.ldo_hr, self.efftotal_hr, '-k', label='Qtot')
            plt.legend(bbox_to_anchor=(1.3, 1.05))
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('Efficiency full EMIR range')
            # End of figures

        if self.timerange == 'Range':

            ston = np.zeros_like(self.texp)
            saturated = np.zeros_like(self.texp)
            src_med_cnts = np.zeros_like(self.texp)
            sky_med_cnts = np.zeros_like(self.texp)
            for i in range(len(self.texp)):
                temp, src_cnts, sky_cnts, sp, satur, params\
                    = self.getSpecSton(self.texp[i], self.nobj, self.nsky)
                ston[i] = np.median(temp[np.nonzero(temp)])
                saturated[i] = satur
                src_med_cnts[i] = np.median(src_cnts[np.nonzero(src_cnts)])
                sky_med_cnts[i] = np.median(sky_cnts[np.nonzero(sky_cnts)])
            self.printXML(src_med_cnts, sky_med_cnts,
                          ston, saturated, **params)
            # self.printXML(src_cnts,sky_cnts,ston,saturated,params)

            # temp, src_cnts, sky_cnts, sp, temp2, params\
            #    = self.getSpecSton(self.texp[i], self.nobj, self.nsky)
            # Additional figure for an inputed range of exposure times
            plt.figure(1)
            plt.subplot(211)
            plt.plot(self.ldo_px, temp)
            plt.xlabel('Wavelength (micron)')
            if ff['source_type'] == 'Point':
                plt.ylabel('S/N at texp = {0:.1f}'.format(self.texp[-1]))
            if ff['source_type'] == 'Extended':
                plt.ylabel('S/N per pixel at texp = {0:.1f}'
                           .format(self.texp[-1]))

            plt.subplot(212)
            plt.plot(self.ldo_px, sp)
            plt.xlabel('Wavelength (micron)')
            plt.ylabel('Normalized src flux')
        plt.savefig(args[0]+'_fig.png')

    def getSpecSton(self, texp=1, nobj=1, nsky=1):
        """
        For Spectroscopy Get SignaltoNoise (Ston):
        1.- Calculate the wavelengths visible in the detector

        2.- Scale object & sky with Vega. Note: the per angstrom dependence
        of the SED is removed later, when the ldo per pixel is calculated

        3.- Convolve the object and sky SEDs with the proper resolution
        Delta(lambda) is evaluated at the central wavelength
        In case of an emission line, there is no need to re-normalize

        4.- Interpolate SEDs over the observed wavelengths

        5.- Estimate the Signal to Noise (STON)
        """
        params = con.get_params()

        # 1. Calculate visible wavelengths

        # import pdb; pdb.set_trace()
        self.mag_sky = con.get_skymag(self.grismname, ff['season'])
        self.cenwl = (self.ldo_hr*self.disp_trans).sum()/(self.disp_trans).sum()
        self.dpx = (self.cenwl/self.specres)/3.
        self.res_ele = self.dpx*(self.slitwidth/(params['scale']))
        self.ldo_px = (np.arange(2048) - 1024)*self.dpx + self.cenwl

        # CGF 02/12/16
        # if ff['template'] == 'Emission line':
        #    no = self.obj*params['area']
        # elif (ff['template'] == 'Model file') & \
        #        (self.obj_units != 'normal_photon'):
        no = self.obj*params['area']
        if self.grismname == 'YJ' or self.grismname == 'HK':
            self.gname_b, self.gname_r = self.grismname[0], self.grismname[1]
            # Split spectra into two parts depending on the grism:
            split = {'YJ': 1.1500, 'HK': 1.9000}
            # Filters:
            filt_b = self.filt_hr*(self.ldo_hr < split[self.grismname])
            filt_r = self.filt_hr*(self.ldo_hr >= split[self.grismname])

            # 2. Scale object and sky with Vega
            # Third statement added by LRP 24-04-2018
            # Object
            if (ff['template'] == 'Black body') |\
               (ff['template'] == 'Model library') |\
               ((ff['template'] == 'Model file') &
                    (self.obj_units == 'normal_photon')):
                no = (10**(-1*self.mag/2.5))*\
                    mod.vega(self.obj, self.vega, filt_r)*params['area']

            # Sky
            ns_b = 10**(-con.get_skymag(self.gname_b, ff['season'])/2.5)*\
                mod.vega(self.sky_e, self.vega, filt_b)*params['area']
            ns_r = 10**(-con.get_skymag(self.gname_r, ff['season'])/2.5)*\
                mod.vega(self.sky_e, self.vega, filt_r)*params['area']

            # 3. Convolve with input resolution (sky)
            sp_sky_config_b = ns_b*texp*(self.disp_trans*self.tel_trans)
            sp_sky_con_b = mod.convolres(self.ldo_hr, sp_sky_config_b,
                                         self.res_ele)

            sp_sky_config_r = ns_r*texp*(self.disp_trans*self.tel_trans)
            sp_sky_con_r = mod.convolres(self.ldo_hr, sp_sky_config_r,
                                         self.res_ele)
            sp_sky_con = (sp_sky_con_b + sp_sky_con_r) / 2.

        else:
            # 2. Scale object and sky with Vega
            if (ff['template'] == 'Black body') |\
               (ff['template'] == 'Model library') |\
               ((ff['template'] == 'Model file') &
                    (self.obj_units == 'normal_photon')):
                no = (10**(-1*self.mag/2.5))*\
                    mod.vega(self.obj, self.vega, self.filt_hr)*params['area']

            ns = (10**(-1*self.mag_sky/2.5))*\
                mod.vega(self.sky_e, self.vega, self.filt_hr)*params['area']

            # 3. Convolve with input resolution (sky)
            sp_sky_config = ns*texp*(self.disp_trans*self.tel_trans)
            sp_sky_con = mod.convolres(self.ldo_hr, sp_sky_config,
                                       self.res_ele)

        # 4. Interpolate over observed wavelengths (sky)
        sp_sky = self.dpx*mod.spec_int(self.ldo_hr,
                                       sp_sky_con*params['scale']**2,
                                       self.ldo_px)
        # 3. Convolve with input resolution (object)
        # Object spectrum scaled by the configuration and transmission
        sp_obj_config = no*(texp*self.sloss)*\
                           (self.disp_trans*self.tel_trans*self.sky_t)
        sp_obj_con = mod.convolres(self.ldo_hr, sp_obj_config, self.res_ele)

        if ff['source_type'] == 'Point':
            # 4. Interpolate over observed wavelengths (object)
            sp_obj = self.dpx*mod.spec_int(self.ldo_hr, sp_obj_con, self.ldo_px)
            im_spec = np.zeros((len(sp_obj), 100))
            im_sky = np.zeros((len(sp_obj), 100))
            total_noise = np.zeros((len(sp_obj), 100))

            # No sky frame implies that reduction is as good
            # as taking one single sky frame

            if nsky == 0:
                nsky_t = 1
            else:
                nsky_t = nsky

            for i in range(len(sp_obj)):
                im_spec[i, :] = mod.getspread(sp_obj[i], self.seeing, 0) + sp_sky[i]
                im_sky[i, :] = sp_sky[i]

                spec_noise = mod.getnoise(im_spec[i, :], texp)/np.sqrt(nobj)
                sky_noise = mod.getnoise(im_sky[i, :], texp)/np.sqrt(nsky_t)
                total_noise[i, :] = np.sqrt(spec_noise**2 + sky_noise**2)

            r = np.abs(np.arange(100) - 50)
            # Receta de Peter
            ind = np.where(r <= 1.2*self.seeing/2./params['scale'])[0]

            # 5. S/N calculation signal-to-noise
            ston_sp = (im_spec - im_sky)[:, ind].sum(axis=1)/\
                np.sqrt((total_noise[:, ind]**2).sum(axis=1))
            satur = mod.checkforsaturation(im_spec[:, ind])
            # Calculate original spectrum for display
            con_0 = mod.convolres(self.ldo_hr, self.sloss*texp*no, self.dpx)
            sp_0 = mod.spec_int(self.ldo_hr, con_0, self.ldo_px)*self.dpx

        elif ff['source_type'] == 'Extended':
            # 4. Interpolate over observed wavelengths (object)
            sp_obj = self.dpx*mod.spec_int(self.ldo_hr,
                                           sp_obj_con*params['scale']**2,
                                           self.ldo_px)
            im_noise = np.sqrt((mod.getnoise(sp_obj + sp_sky, texp)/
                                np.sqrt(nobj))**2 +
                               (mod.getnoise(sp_sky, texp)/np.sqrt(nsky))**2)

            satur = mod.checkforsaturation(sp_obj + sp_sky)

            # 5. S/N calculation signal-to-noise
            ston_sp = sp_obj/im_noise
            # Calculate original spectrum for display
            con_0 = mod.convolres(self.ldo_hr, self.sloss*texp*no, self.dpx)
            sp_0 = self.dpx*mod.spec_int(self.ldo_hr, con_0*params['scale']**2,
                                         self.ldo_px)

        obj_cnts = sp_obj/params['gain']
        sky_cnts = sp_sky/params['gain']

        return ston_sp, obj_cnts, sky_cnts, sp_0/sp_0.max(), satur, params

    def getPhotSton(self, texp=1, nobj=1, nsky=1):
        """
        For Photometry Get SignaltoNoise (Ston):
        1.- Scale object & sky with Vega

        2.- Calculate total fluxes through passbands.

        3.- Synthethic image generation

        4.- Calcualte Signal-to-noise
        """
        params = con.get_params()
        self.mag_sky = con.get_skymag(self.filtname, ff['season'])
        # ston = np.zeros_like(texp)
        satur = np.zeros_like(texp)
        # Added by LRP from MBC's ETC
        ston = np.zeros((np.shape(texp)[0], 3))
        signal_obj = np.zeros((np.shape(texp)[0], 3))
        signal_sky = np.zeros((np.shape(texp)[0], 3))
        step = float(self.ldo_hr[1] - self.ldo_hr[0])
        #    1.- Scale object & sky with Vega
        # CGF 02/12/16

        if ff['template'] == 'Emission line':
            no = self.obj*params['area']*step
        elif (ff['template'] == 'Model file') & \
                (self.obj_units != 'normal_photon'):
            no = self.obj*params['area']*step
        else:
            no = (10**(-1*self.mag/2.5))\
                *mod.vega(self.obj, self.vega, self.filt_hr)\
                *params['area']*step

        # Sky:
        sky_e_vega = mod.vega(self.sky_e, self.vega, self.filt_hr)
        ns = (10**(-1*self.mag_sky/2.5))*sky_e_vega*params['area']*step

        #  2.- Calculate total fluxes through passbands.
        #  The filter appears here and in step 1 because there is used
        #  to calculate the flux under it in order to normalize the
        #  spectra with Vega. Here is used to calculate total fluxes.
        sp_obj = no*self.filt_hr*self.tel_trans*self.sky_t
        sp_sky = ns*self.filt_hr*self.tel_trans

        fl_obj = texp*sp_obj.sum()
        fl_sky = texp*sp_sky.sum()*params['scale']**2

        # In case of point-like source, we need to estimate the aperture
        # to properly account for the effect of the RON and sky.
        # In the case of extended sources, the estimated values are per pixel

        # Implement the reality factor
        rfact = mod.reality_factor(self.filtname)
        if ff['source_type'] == 'Point':
            # 3.- Synthethic image generation
            # An "image" of radii values from the center is used to see how
            # many pixels fall inside the seeing ring.

            im_r = np.zeros((100, 100))
            x = np.arange(100)
            for i in range(0, 100):
                im_r[i, ] = np.sqrt((float(i) - 50.0)**2 + (x - 50.0)**2)

            # From Peter: a good guesstimate of the aperture is 1.2*seeing

            ind = np.where(im_r <= (1.2*self.seeing / 2.) / params['scale'])
            ind2 = np.where(im_r <= (2.0*self.seeing / 2.) / params['scale'])

            # 4.- Calcualte Signal-to-noise

            for i in range(len(texp)):
                im_obj = mod.getspread(fl_obj[i], self.seeing, 1) + fl_sky[i]
                im_sky = np.zeros_like(im_obj) + fl_sky[i]
                im_obj = im_obj / rfact
                im_sky = im_sky / rfact
                # print (rfact,(im_obj.max()+im_sky.min())/params['gain']\
                #    /texp[i],im_sky.min()/params['gain']/texp[i])

                if nsky == 0:
                    # For no sky frames is assumed that the reduction
                    # is as good as taking a single sky frame.
                    sky_noise = mod.getnoise(im_sky, texp[i])
                else:
                    sky_noise = mod.getnoise(im_sky, texp[i]) / np.sqrt(nsky)

                obj_noise = mod.getnoise(im_obj, texp[i]) / np.sqrt(nobj)
                total_noise = np.sqrt(sky_noise**2 + obj_noise**2)
                ston[i][0] = (im_obj - im_sky)[ind].sum()\
                    / np.sqrt((total_noise[ind]**2).sum())
                ston[i][1] = (im_obj - im_sky)[ind2].sum()\
                    / np.sqrt((total_noise[ind2]**2).sum())
                ston[i][2] = (im_obj.max() - im_sky.min())/total_noise.max()
                satur[i] = mod.checkforsaturation(im_obj)

                # Added by LRP from MBC's ETC
                # MBC added 2016-11-28
                # total counts from source and sky in aperture
                # Updated by LRP in 06-2017
                signal_obj[i][0] = (im_obj - im_sky)[ind].sum() / params['gain']
                signal_sky[i][0] = im_sky[ind].sum() / params['gain']
                signal_obj[i][1] = (im_obj - im_sky)[ind2].sum() / params['gain']
                signal_sky[i][1] = im_sky[ind2].sum() / params['gain']
                signal_obj[i][2] = im_obj.max()/params['gain']/texp[i]
                signal_sky[i][2] = im_sky.min()/params['gain']/texp[i]

        elif ff['source_type'] == 'Extended':
            # For an extended sources calculate the flux per pixel
            fl_obj = fl_obj*params['scale']**2
            for i in range(len(texp)):
                im_obj = np.ones(1)*(fl_obj[i] + fl_sky[i])
                im_sky = np.ones(1)*fl_sky[i]
                im_obj = im_obj / rfact
                im_sky = im_sky / rfact

                if nsky == 0:
                    # For no sky frames is assumed that the reduction
                    # is as good as taking a single sky frame.
                    sky_noise = mod.getnoise(im_sky, texp[i])
                else:
                    sky_noise = mod.getnoise(im_sky, texp[i])/ np.sqrt(nsky)
                obj_noise = mod.getnoise(im_obj, texp[i])/ np.sqrt(nobj)
                total_noise = np.sqrt(sky_noise**2 + obj_noise**2)
                ston[i][0] = (im_obj - im_sky) / total_noise
                ston[i][1] = (im_obj - im_sky) / total_noise
                ston[i][2] = (im_obj - im_sky) / total_noise
                satur[i] = mod.checkforsaturation(im_obj)
                # Added by LRP from MBC's ETC
                # MBC added 2016-11-28
                signal_obj[i][0] = (im_obj - im_sky).sum() / params['gain']
                signal_sky[i][0] = im_sky.sum() / params['gain']
                signal_obj[i][1] = (im_obj - im_sky).sum() / params['gain']
                signal_sky[i][1] = im_sky.sum() / params['gain']
                signal_obj[i][2] = im_obj.max()/params['gain']/texp[i]
                signal_sky[i][2] = im_sky.min()/params['gain']/texp[i]
        return ston, signal_obj, signal_sky, satur, params, sp_obj, sp_sky

    def buildObj(self):
        """Build the SED from the input parameters"""
        # CGF 05/12/16
        # Default catchall so that the units are always defined
        self.obj_units = 'normal_photon'
        if ff['template'] == 'Model library':
            # CGF 05/12/16
            temp_curve = SpecCurve('libs/' + self.available[ff['model']])
            self.obj = temp_curve.interpolate(self.ldo_hr)
            self.obj_units = temp_curve.unity
        elif ff['template'] == 'Black body':
            self.bbteff = float(ff['body_temp'])
            self.obj = mod.bbody(self.ldo_hr, self.bbteff)
            # CGF 05/12/16
            self.obj_units = 'normal_photon'
        elif ff['template'] == 'Model file':
            # User loaded model
            # CGF 02/12/16
            temp_curve = SpecCurve(ff['model_file'])
            self.obj = temp_curve.interpolate(self.ldo_hr)
            self.obj_units = temp_curve.unity
        elif ff['template'] == 'Emission line':
            # LRP: I don't understand this temp buisness
            # ... Why do we have 3 loops that seem to do nothing???
            # It seems to think we can have multiple emission line inputs but
            # the php wrapper doesn't support this.
            #
            # The input can be several lines separated by commas
            #
            temp = ff['line_center'].split(',')
            self.lcenter = []
            for i in temp:
                self.lcenter.append(float(i))
            temp = ff['line_fwhm'].split(',')
            self.lwidth = []
            for i in temp:
                self.lwidth.append(float(i)*1e-4)
            temp = ff['line_peakf'].split(',')
            self.lflux = []
            for i in temp:
                self.lflux.append(float(i)*1e-16)

            # In case the number of inputs is different in any section

            n_valid = np.min([len(self.lcenter), len(self.lwidth),
                             len(self.lflux)])
            self.lcenter = self.lcenter[0:n_valid]
            self.lwidth = self.lwidth[0:n_valid]
            self.lflux = self.lflux[0:n_valid]
            self.obj = np.zeros_like(self.ldo_hr)
            for i in range(len(self.lflux)):
                self.obj += mod.emline(self.ldo_hr, self.lcenter[i],
                                       self.lwidth[i], self.lflux[i])
            ###################################################################
            # CGF 05/12/16
            self.obj_units = 'photon/s/m2/micron'
            # mod.emline outputs in photon/s/m2/micron

    def printXML(self, signal_obj, signal_sky, ston, satur, **params):
        """
        A function to create the output XML files
        Updated to inlucde more output by LRP 08-12-2016
        Mainly taken from Marc Balcells' version of the ETC

        Would this would be quicker if we just had a few already built xml
        templates and the code just filled in the appropriate template instead
        of generating it each time?

        TODO: remodel this function, the format is confusing and needs a large
        number of ifs
        """
        # Some redefinitions to make life easier
        o = ET.Element("output")
        se = ET.SubElement

        se(o, "fig").text = args[0] + "_fig.png"
        se(o, "text").text = "<h2>EMIR-ETC Version {}</h2>".format(version)
        se(o, "text").text = "<b>Source</b>"

        if ff['operation'] == 'Photometry':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;{0:s} Source (Vega Mag) = {1:.2f} {2}".\
                format(ff['source_type'], self.mag, self.filtname)
        elif self.grismname == 'YJ' or self.grismname == 'HK':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;{0:s} Source (Vega Mag) = {1:.2f} {2}".\
                format(ff['source_type'], self.mag, self.gname_r)
        else:
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;{0:s} Source (Vega Mag) = {1:.2f} {2}".\
                format(ff['source_type'], self.mag, self.grismname)

        if ff['template'] == 'Model library':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Template: Model library"
            se(o, "text").text= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Spectral Type: {0:s}".format(ff['model'])
        elif ff['template'] == 'Black body':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Template: Black Body"
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Temperature = {0:.1f} K".format(float(ff['body_temp']))
        elif ff['template'] == 'Emission line':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Template: Emission Line"
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Center = {0:s}, FWHM = {1:s}, Total line flux = {2:s}"\
                .format(ff['line_center'], ff['line_fwhm'], ff['line_peakf'])
        elif ff['template'] == 'Model file':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Template: Model file"
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Model file = {0:s}".format(ff['model_file'])

        se(o, "text").text = "<b>Observation</b>"
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Operation: {0:s}".format(ff['operation'])
        if self.timerange == 'Range':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Exposure times = {0:8.1f} - {1:8.1f}".format(self.texp[0], self.texp[-1])
        else:
            se(o, "text").text = "Exposure time = {0:8.1f}".format(self.texp[0])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Number of exposures: Object {0:d}, Sky {1:d}".format(int(self.nobj), int(self.nsky))

        se(o, "text").text = "<b>Observing Conditions</b>"
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Airmass = {0:.2f}".format(self.airmass)
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Seeing = {0:.2f} arcsec FWHM".format(self.seeing)
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Sky brightness = {0:.2f} Vega mag/arcsec<sup>2</sup>".format(self.mag_sky)

        se(o, "text").text = "<b>Telescope and Instrument </b>"
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Telescope collecting area = {0:.1f} m<sup>2</sup>".format(params['area'])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Spatial scale = {0:.4f} arcsec/pix ".format(params['scale'])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Readout noise = {0:.1f} e<sup>-</sup> ".format(params['RON'])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Dark current = {0:.2f} ADU/hour".format(3600*params['DC']/params['gain'])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Well depth = {0:.1f} e<sup>-</sup>".format(params['well'])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Gain = {0:.2f} e<sup>-</sup>/ADU".format(params['gain'])
        se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Effective gain = {0:.2f} ".format(params['gain']*self.nobj)
        if ff['operation'] == 'Photometry':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Filter: <b>{0:s}</b>".format(self.filtname)
        else:       # Spectroscopy
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Grism: <b>{0:s}</b>".format(self.grismname)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Wavelength coverage = {0:.2f} - {1:.2f} &mu;".format(self.ldo_px[0],self.ldo_px[-1])
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Central wavelength = {0:.4f} ".format(self.cenwl)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Dispersion = {0:.2f} &Aring;/pix".format(self.dpx*1e4)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Resolution element = {0:.2f} &Aring or {1:.2f} px"\
                .format(self.res_ele*1e4, self.res_ele/self.dpx)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Slit width = {0:.2f} arcsec".format(self.slitwidth)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;In-slit fraction = {0:.4f} ".format(self.sloss)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Nominal Spectral resolution = {0:.4f}".format(self.specres)
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Achieved Spectral resolution = {0:.4f}".format(self.cenwl/self.res_ele)

        se(o, "text").text = "<b>Results</b>"

        tabletext = ""
        if self.timerange != 'Range':
            se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;For {0:d} exposure(s) of {1:.1f} s: ".format(int(self.nobj), self.texp[0])
            if ff['operation'] =='Spectroscopy':
                if ff['template'] == 'Emission line':
                    px_res_ele = max(1, np.sqrt(self.lwidth[0]/self.dpx))
                    se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Maximum counts from object {0:.1f}, median from sky: {1:.1f}"\
                        .format(signal_obj[0], signal_sky[0])
                    se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Maximum S/N per FWHM = {0:.1f}".format(ston[0]*px_res_ele)
                else:
                    px_res_ele = max(1, np.sqrt(self.slitwidth/params['scale']))
                    se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Median counts per res. element: from object = {0:.1f}, from sky = {1:.1f}"\
                        .format(signal_obj[0]*px_res_ele, signal_sky[0]*px_res_ele)
                    se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Median S/N per res. element = {0:.1f}".format(ston[0]*px_res_ele)
                    se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Median S/N per pixel = {0:.1f}".format(ston[0])
            else:  # Photometry
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;S/N Calculations:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Per Pixel:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Maximum object counts per pixel per second: "\
                    " = {0:.1f}".format(signal_obj[0][2])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Median sky counts per pixel per second: "\
                    " = {0:.1f}".format(signal_sky[0][2])

                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;S/N Calculations:"
                ap1, ap2 = 1.2, 2.0
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Per Aperture:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Aperture 1:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;diameter = {0}*seeing = "\
                    "{1:.2f} arcsecs or {2:.2f} pixels"\
                    .format(ap1, ap1*self.seeing, ap1*self.seeing / params['scale'])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total counts in aperture: "\
                    "from object = {0:.1f}, from sky = {1:.1f}"\
                    .format(signal_obj[0][0], signal_sky[0][0])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Aperture 2:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;diameter = {0}*seeing = "\
                    "{1:.2f} arcsecs or {2:.2f} pixels"\
                    .format(ap2, ap2*self.seeing, ap2*self.seeing / params['scale'])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total counts in aperture: "\
                    "from object = {0:.1f}, from sky = {1:.1f}"\
                    .format(signal_obj[0][1], signal_sky[0][1])

                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;S/N Estimates:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Maximum S/N per pixel = {0:.1f}".format(ston[0][2])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Final S/N per 1.2*seeing aperture = {0:.1f}".format(ston[0][0])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Final S/N per 2.0*seeing aperture = {0:.1f}".format(ston[0][1])

            if satur:
                se(o, "warning").text = "<font color=\"red\"><b>WARNING:For time {0:.1f} s some pixels are saturated</b></font>".format(self.texp[0])

        else:  # Range of texp
            if ff['operation']=='Spectroscopy':
                if ff['template'] == 'Emission line':
                    tabletext += '\n\tFor the selected time range, the S/N per FWHM are:'
                else:
                    tabletext += '\n\tFor the selected time range, the S/N per pixel are:'
                tabletext += '\n\t________________________________________'
                tabletext += '\n\t    t(s)\tS/N(pp)\tSaturation?'
                tabletext += '\n\t________________________________________'

                for i in range(10):
                        flags = 'No'
                        if satur[i]:
                            flags = 'Yes'
                        tabletext += '\n\t{0:8.1f}\t{1:8.1f}\t'\
                            .format(self.texp[i]*self.nobj, ston[i]) + flags

            else:  # Photometry
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;S/N Calculations:"
                ap1, ap2 = 1.2, 2.0
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;An example for {0:d} exposure(s) of {1:.1f} s: ".format(int(self.nobj), self.texp[0])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Per Pixel:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Maximum object counts per pixel per second: "\
                    " = {0:.1f}".format(signal_obj[0][2])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Median sky counts per pixel per second: "\
                    " = {0:.1f}".format(signal_sky[0][2])

                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Per Aperture:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Aperture 1:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;diameter = {0}*seeing = "\
                    "{1:.2f} arcsecs or {2:.2f} pixels"\
                    .format(ap1, ap1*self.seeing, ap1*self.seeing / params['scale'])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total counts in aperture: "\
                    "from object = {0:.1f}, from sky = {1:.1f}"\
                    .format(signal_obj[0][0], signal_sky[0][0])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;Aperture 2:"
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;diameter = {0}*seeing = "\
                    "{1:.2f} arcsecs or {2:.2f} pixels"\
                    .format(ap2, ap2*self.seeing, ap2*self.seeing / params['scale'])
                se(o, "text").text = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total counts in aperture: "\
                    "from object = {0:.1f}, from sky = {1:.1f}"\
                    .format(signal_obj[0][1], signal_sky[0][1])

                tabletext += '\n\tFor the selected time range, the S/N estimates are:'.format(1.2)
                tabletext += '\n\t____________________________________________________________________________________'
                tabletext += '\n\t    t (s)\t  S/N<sub>pp</sub>\t\tS/N<sub>1.2*FWHM</sub>\t S/N<sub>2.0*FWHM</sub>\tSaturation?'
                tabletext += '\n\t____________________________________________________________________________________'

                for i in range(10):
                    flags = 'No'
                    if satur[i]:
                        flags = 'Yes'
                    tabletext += '\n\t{0:8.1f}\t{1:8.1f}\t{2:8.1f}\t{3:8.1f}\t'\
                        .format(self.texp[i]*self.nobj, ston[i][2], ston[i][0], ston[i][1]) + flags

        tabletext += "\n"
        se(o, "table").text = tabletext
        emir_guy.indent(o)
        tree = ET.ElementTree(o)
        tree.write(args[0] + "_out.xml")


try:
    EmirGui()
except SystemExit:
    pass
except:
    emir_guy.generic_error(args[0])
exit()
