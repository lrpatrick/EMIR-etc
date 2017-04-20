	<meta charset="UTF-8">
	<title>EMIR ETC 1.0.4</title>

	<link type="text/css" rel="stylesheet"  href="style.css" />

	<script type='text/javascript' src="jquery.tools.min.js"></script>

	<script>

		function chSelect(id, value) {
			var elems = document.querySelectorAll("[data-group='" + id + "']");


			for (var i=0; i < elems.length; i++) {
				elems[i].style.display = (elems[i].getAttribute('data-value') != value) ? 'none' : 'block';
			}
		}

		function filterLineCenter(name,filter, val) {

			MIN    = 0;
			CENTER = 1;
			MAX    = 2;

			var lineCenterData = [];

			lineCenterData['photo_filter'] = [];
			lineCenterData['photo_filter']['Y']        = [0.95, 1.03, 1.10];
			lineCenterData['photo_filter']['J']        = [1.13, 1.31, 1.39];
			lineCenterData['photo_filter']['H']        = [1.42, 1.73, 1.86];
			lineCenterData['photo_filter']['Ks']       = [1.90, 2.26, 2.40];
			lineCenterData['photo_filter']['F123M']    = [1.18, 1.23, 1.28];
			lineCenterData['photo_filter']['FeII']     = [1.632, 1.647, 1.662];
			lineCenterData['photo_filter']['BrG']      = [2.125, 2.175, 2.225];
			lineCenterData['photo_filter']['H2(1-0)']  = [2.110, 2.125, 2.141];
			lineCenterData['photo_filter']['H2(2-1)']  = [2.235, 2.249, 2.264];

			lineCenterData['spec_grism'] = [];
			lineCenterData['spec_grism']['J']          = [1.17, 1.25, 1.33];
			lineCenterData['spec_grism']['H']          = [1.51, 1.65, 1.76];
			lineCenterData['spec_grism']['K']          = [2.05, 2.35, 2.43];
			lineCenterData['spec_grism']['YJ']         = [0.899, 1.115, 1.331];
			lineCenterData['spec_grism']['HK']         = [1.454, 2.214, 2.428];

			var lineCenter = document.getElementById('line_center')
			if (lineCenter) {
				lineCenter.min = lineCenterData[name][filter][MIN];
				lineCenter.max = lineCenterData[name][filter][MAX];
				lineCenter.value = (val != null) ? val : lineCenterData[name][filter][CENTER];
				lineCenter.step = 0.001;
			}

			var lineCenterUnit = document.getElementById('unit_line_center')
			if (lineCenterUnit) {
				lineCenterUnit.innerHTML  = "microns [" + lineCenterData[name][filter][MIN];
				lineCenterUnit.innerHTML += " - " + lineCenterData[name][filter][MAX] + "]";
				lineCenterUnit.innerHTML += " (c:" + lineCenterData[name][filter][CENTER] + ")";
			}

		}


	</script>

