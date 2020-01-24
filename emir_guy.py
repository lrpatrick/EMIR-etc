"""
Author: XXX
Date: XXX
Description: (LRP)

This file deals with the XML opertations of the ETC


Update:
Author: LRP (lpatrick@iac.es)
Date: 28-11-2016
Description:

"""

import os.path
import xml.etree.ElementTree as ET


def readxml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    dati = {}
    for child in root:
        for country in child:
            dati[country.tag] = country.text
    return dati


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return

def errorxml(elem, text):
    ET.SubElement(elem, "error").text = text
    return


def check_inputs(ff, fname):
    output = ET.Element('output')

    error = False

    if ff['template'] != 'Emission line':
        (val1, val2) = (None, None)
    elif ff['operation'] == 'Photometry':

        # These affect the emission line templates
        # All of these values should be from the GTC webpages
        # Since I don't know, I'm going to gess that it is supposed to be the
        # edges of the filter. From the webpages (28-11-2016) this is:

        if ff['photo_filter'] == 'Y':  # added by LRP 28-11-2016
            (val1, val2) = (0.965, 1.097)  # added by LRP 28-11-2016
        elif ff['photo_filter'] == 'J':
            (val1, val2) = (1.126, 1.397)
        elif ff['photo_filter'] == 'H':
            (val1, val2) = (1.420, 1.861)
        elif ff['photo_filter'] == 'Ks':
            (val1, val2) = (1.902, 2.400)
        elif ff['photo_filter'] == 'FeII':
            (val1, val2) = (1.606, 1.670)
        elif ff['photo_filter'] == 'FeII_cont':
            (val1, val2) = (1.660, 1.760)  # Added by LRP 16-05-2017
        elif ff['photo_filter'] == 'BrG':
            (val1, val2) = (2.125, 2.225)  # changed by LRP 09-12-2016
        elif ff['photo_filter'] == 'BrG_cont':
            (val1, val2) = (2.080, 2.180)  # changed by LRP 16-05-2017
        elif ff['photo_filter'] == 'F123M':
            (val1, val2) = (1.110, 1.228)  # Added by LRP 09-12-2016
        elif ff['photo_filter'] == 'H2(1-0)':
            (val1, val2) = (2.110, 2.141)  # Added by LRP 16-03-2017
        elif ff['photo_filter'] == 'H2(2-1)':
            (val1, val2) = (2.235, 2.264)  # Added by LRP 16-03-2017
    elif ff['operation'] == 'Spectroscopy':
        if ff['spec_grism'] == 'J':
            (val1, val2) = (1.168, 1.338)
        elif ff['spec_grism'] == 'H':
            (val1, val2) = (1.512, 1.759)
        elif ff['spec_grism'] == 'K':
            (val1, val2) = (2.048, 2.429)
        elif ff['spec_grism'] == 'YJ':
            (val1, val2) = (0.899, 1.331)
        elif ff['spec_grism'] == 'HK':
            (val1, val2) = (1.454, 2.405)
        elif ff['spec_grism'] == 'K_Y':
            (val1, val2) = (0.96, 1.09)

    NAME = 0
    TITLE = 1
    TYPE = 2
    TEMPL = 3
    OPER = 4
    MIN = 5
    MAX = 6
    VALUES = 3
    DATA_INPUT = [
        ['magnitude', 'Magnitude', 'float', None, None, 0, None],
        ['system', 'System', 'select', ['Vega', 'AB']],
        ['season', 'Season', 'select', ['Summer', 'Winter']],
        ['source_type', 'Source Type', 'select', ['Extended', 'Point']],
        ['template', 'Spectral Template', 'select',
            ['Model library', 'Black body', 'Emission line', 'Model file']],
        ['model', 'Model', 'select',
            ['b0i', 'b1i', 'b3i', 'b5i', 'b8i',
             'a0i', 'a2i',
             'f0i', 'f5i', 'f8i',
             'g0i', 'g2i', 'g5i', 'g8i',
             'k2i', 'k3i', 'k4i',
             'm2i',
             'o8iii',
             'b3iii', 'b5iii', 'b9iii',
             'a0iii', 'a3iii', 'a5iii', 'a7iii',
             'f0iii', 'f2iii', 'f5iii',
             'g0iii', 'g5iii', 'g8iii',
             'k0iii', 'k1iii', 'k2iii', 'k3iii', 'k4iii', 'k5iii',
             'm0iii', 'm1iii', 'm2iii', 'm3iii', 'm4iii', 'm5iii',
             'm6iii', 'm7iii', 'm8iii', 'm9iii', 'm10iii',
             'o5v', 'o9v',
             'b0v', 'b1v', 'b3v', 'b8v', 'b9v',
             'a0v', 'a2v', 'a3v', 'a5v', 'a7v',
             'f0v', 'f2v', 'f5v', 'f6v', 'f8v',
             'g0v', 'g2v', 'g5v', 'g8v',
             'k0v', 'k2v', 'k3v', 'k4v', 'k5v', 'k7v',
             'm0v', 'm1v', 'm2.5v', 'm2v', 'm3v', 'm4v', 'm5v', 'm6v']],
        ['body_temp', 'Body temperature', 'float',
         'Black body', None, 0, None],
        ['line_center', 'Line center', 'float', 'Emission line', None,
         val1, val2],
        ['line_fwhm', 'Line FWHM', 'float', 'Emission line', None, 0, None],
        ['line_peakf', 'Line peak flux', 'float', 'Emission line',
         None, 0, None],
        ['airmass', 'Airmass', 'float', None, None, 1.0, 2.0],
        ['seeing', 'Seeing', 'float', None, None, 0, None],
        ['operation', 'Operation', 'select', ['Photometry',
         'Spectroscopy']],
        ['photo_exp_time', 'Exp. time', 'range', None, 'Photometry', 0, None],
        ['photo_nf_obj', '#Frames:obj', 'float', None, 'Photometry', 0, None],
        ['photo_nf_sky', '#Frames:sky', 'float', None, 'Photometry', 0, None],
        # ['nf_sky', '#Frames:sky', 'float', None, 'Photometry', 0, None],
        ['photo_filter', 'Filter', 'select',
            ['Y', 'J', 'H', 'Ks',
             'BrG', 'BrG_cont', 'FeII', 'FeII_cont', 'H2(1-0)', 'H2(2-1)',
             'F123M']],
        ['spec_slit_width', 'Slit Width', 'float', None, 'Spectroscopy',
         0, None],
        ['spec_grism', 'Grism', 'select', ['J', 'H', 'K', 'YJ', 'HK', 'K_Y']],
        ['spec_exp_time', 'Exp. time', 'range', None, 'Spectroscopy', 0, None],
        ['spec_nf_obj', '#Frames:obj', 'float', None, 'Spectroscopy', 0, None],
        # ['nf_sky', '#Frames:sky', 'float', None, 'Spectroscopy', 0, None],
        ['spec_nf_sky', '#Frames:sky', 'float', None, 'Spectroscopy', 0, None],
    ]

    for elems in DATA_INPUT:
        if elems[TYPE] != 'select' and (not elems[TEMPL] is None
                and ff['template'] != elems[TEMPL] or not elems[OPER]
                is None and ff['operation'] != elems[OPER]):

            # This field is not needed for the present template/operation

            continue

        val = ff[elems[NAME]]

    # Check Type

        if elems[TYPE] == 'float' or elems[TYPE] == 'range' and not '-' in val:
            try:
                float(val)
            except:
                errorxml(output, 'Value of ' + elems[TITLE] + ' is not a valid number')
                error = True
                continue

      # Check range

            if elems[MIN] is not None and float(val) \
                < float(elems[MIN]) or elems[MAX] is not None \
                and float(val) > float(elems[MAX]):

          # print elems[MIN], elems[MAX], val

                errorxml(output, 'Value of ' + elems[TITLE]
                         + ' is out of range [' + str(elems[MIN]) + ', '
                          + str(elems[MAX]) + ']')
                error = True
        elif elems[TYPE] == 'select':

            if not val in elems[VALUES]:
                errorxml(output, 'Value of ' + elems[TITLE]
                         + ' is not one of the elements in the list')
                error = True
        elif elems[TYPE] == 'range':

            rval = val.split('-')


            if len(rval) != 2:
                errorxml(output, 'Value of ' + elems[TITLE]
                         + ' is not a valid range ')
                error = True
                continue

            try:
                float(rval[0])
                float(rval[1])
            except:
                errorxml(output, 'Value(s) of ' + elems[TITLE]
                         + ' are not valid numbers')
                error = True
                continue

            if float(rval[0]) > float(rval[1]):
                errorxml(output, 'Min value of ' + elems[TITLE]
                         + ' is greater than max value')
                error = True
        else:

            errorxml(output, 'Value of ' + elems[TITLE]
                     + 'has not a valid type')
            error = True

    if error:
        indent(output)
        tree = ET.ElementTree(output)
        tree.write(fname + '_out.xml')
        exit()

    return

def model_error(model, fname):
    output = ET.Element("output")
    if not os.path.isfile(model):
        errorxml(output, "No file found")
    else:
        errorxml(output, "There is something wrong. Error triggered: emir_guy.model_error Please, check that all input data are correct. See <a href=\"http://www.iac.es/proyecto/emir/pages/observing-with-emir/observing-tools.php\" target=\"_blank\">here</a> for more info. If the problem remains unsolved, please contact Lee Patrick (lpatrick [at] iac es).")
    indent(output)
    tree = ET.ElementTree(output)
    tree.write(fname+"_out.xml")
    exit()
    return


def generic_error(fname):
    output = ET.Element("output")
    errorxml(output, "Unexpected error. Please, check that all input data are correct. If the problem remains unsolved and you believe you have spotted a bug, please contact Lee Patrick (lpatrick [at] iac es).")
    indent(output)
    tree = ET.ElementTree(output)
    tree.write(fname+"_out.xml")
    exit()
    return
