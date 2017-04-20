from xml.dom.minidom import parse, parseString
parser = parse("emir_etc.xml")
dati = dict()
#print dati


for xxx in parser.getElementsByTagName("data_etc"):
    for aaa in xxx.getElementsByTagName("source_config"):
        mag = aaa.getAttribute("magnitude")
        source = aaa.getAttribute("source_type")
    for bbb in xxx.getElementsByTagName("spectral_template"):
        template = bbb.getAttribute("template")
        BB = bbb.getAttribute("body_temp")
        line_c = bbb.getAttribute("line_center")
        line_f = bbb.getAttribute("line_fwhm")
        line_p = bbb.getAttribute("line_peakf"
    dati[xxx.getElementsByTagName] = { "": mag, "autore": source, "indirizzo": template}

print dati
