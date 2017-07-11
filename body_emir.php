<?php

// From http://stackoverflow.com/questions/8970913/create-a-temp-file-with-a-specific-extension-using-php

define ("DATA_DIR", "/datos/ext/proyecto/emir/pages/observing-with-emir/observing-tools/tmp_files");

function mkstemp($template) {
  #$attempts = 238328; // 62 x 62 x 62
  $MAX_TRIES = 50;
    $PATTERN   = "XXXXXX";
  $letters   = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  $length    = strlen($letters) - 1;

  if (mb_strlen($template) < strlen($PATTERN) || !strstr($template, $PATTERN))
    return FALSE;

  for ($count = 0; $count < $MAX_TRIES; ++$count) {
    $random = "";

    for ($p = 0; $p < strlen($PATTERN); $p++) {
      $random .= $letters[mt_rand(0, $length)];
    }

    $randomFile = str_replace($PATTERN, $random, $template);

    if (!($fd = @fopen($randomFile, "x+")))
      continue;

    return str_replace(".xml", "", $randomFile);
  }

  return FALSE;
}

function startsWith($haystack, $needle) {
    // search backwards starting from haystack length characters from the end
    return $needle === "" || strrpos($haystack, $needle, -strlen($haystack)) !== FALSE;
}
function endsWith($haystack, $needle) {
    // search forward starting from end minus needle length characters
    return $needle === "" || (($temp = strlen($haystack) - strlen($needle)) >= 0 && strpos($haystack, $needle, $temp) !== FALSE);
}


    // SELECT FIELDS
    $system_vals   =  array("Vega", "AB"); // Added LRP 16-05-2017
    $season_vals   =  array("Summer", "Winter"); // Added LRP 10-07-2017
    $source_type_vals   =  array("Point", "Extended");
    $model_vals         =  array("b0i", "b1i", "b3i", "b5i", "b8i", "a0i", "a2i", "f0i", "f5i", "f8i", "g0i", "g2i", "g5i", "g8i", "k2i",
                                 "k3i", "k4i", "m2i", "o8iii", "b3iii", "b5iii", "b9iii", "a0iii", "a3iii", "a5iii", "a7iii", "f0iii",
                                 "f2iii", "f5iii", "g0iii", "g5iii", "g8iii", "k0iii", "k1iii", "k2iii", "k3iii", "k4iii", "k5iii", "m0iii",
                                 "m1iii", "m2iii", "m3iii", "m4iii", "m5iii", "m6iii", "m7iii", "m8iii", "m9iii", "m10iii", "o5v", "o9v",
                                 "b0v", "b1v", "b3v", "b8v", "b9v", "a0v", "a2v", "a3v", "a5v", "a7v", "f0v", "f2v", "f5v", "f6v", "f8v",
                                 "g0v", "g2v", "g5v", "g8v", "k0v", "k2v", "k3v", "k4v", "k5v", "k7v", "m0v", "m1v", "m2.5v", "m2v", "m3v",
                               "m4v", "m5v", "m6v",);
    $template_vals      =  array("Model library", "Black body", "Emission line", "Model file");
    $filter_vals        =  array("Y", "J", "H", "Ks",
                                 "F123M", "FeII", "FeII_cont", "BrG", "BrG_cont", "H2(1-0)", "H2(2-1)"); // Y, F123M, H10, H21 Added by LRP 
    $grism_vals         =  array("J", "H", "K", "YJ", "HK", "K_Y");
    $operation_vals     =  array("Photometry", "Spectroscopy");


    // FIELDS CONFIGURATION
    // Everything you need to do to display and store (XML format) fields has to be done HERE.
    // There are different parameters depending on the field:
    //  - id: HTML name and id of each field
    //  - group: To be displayed in the correct fieldset
    //  - label: Text to be displayed near the field
    //  - type: field type: "Text", "Number", "Select", "File", "Radio", "Submit", etc.
    //  - value: default value
    //  - unit: Unit to be displayed after the field
    //  - min: in "Number", min allowed value
    //  - max: in "Number", max allowed value
    //  - step: in "Number", value will change +/- step
    //  - values: in "Select", list of values to be converted in options
    //  - dependID: in "Select", ID to be used when showing dependent fields
    //  - depend: "dependID:value" of dependency with a Select field (to be showed/hidden)
    //  - info: text to be displayed with a tooltip
    //  - url: clicking on the info icon you will be redirected to this URL

    $FIELDS = array (
        // Group 0
        'magnitude' => array('group' => 0, 'label' => 'Magnitude',
                             'type' => "Number", 'min' => '0', 'step' => '0.01',
                             'value' => "0.0", 'unit' => "" ),
        'system' => array('group' => 0, 'label' => 'System',
                          'type' => "Radio", 'values' => $system_vals,
                          'value' => "Vega",  'unit' => "",
                          'info' => 'Magnitude System'),
        'season' => array('group' => 0, 'label' => 'Season',
                          'type' => "Radio", 'values' => $season_vals,
                          'value' => "Summer",  'unit' => "",
                          'info' => 'Determines the sky magnitude brightness values (only change in K)'),
        'source_type' => array('group' => 0, 'label' => 'Source Type',
                               'type' => "Select", 'values' => $source_type_vals,
                               'value' => "Point",  'unit' => "",
                               'info' => 'Point Source: the S/N will be estimated over the whole aperture (1.2*FWHM)<br />Extended source: all the derived S/N will be per pixel', 
                               'onChange' => 'var new_unit = (this.value==\'Extended\') ? \'x10<sup>-16</sup> erg/s/cm<sup>2</sup>/arcsec<sup>2</sup>\' : \'x10<sup>-16</sup> erg/s/cm<sup>2</sup>\'; document.getElementById(\'unit_line_peakf\').innerHTML=new_unit;'),


        // Group 1
        'template'  => array('group' => 1, 'label' => 'Template',
                             'type' => "Select", 'values' => $template_vals,
                             'value' => "Black body", 'unit' => "",
                             'dependID'=>'template'),

        'model' => array('group' => 1, 'label' => 'Model',
                         'type' => "Select", 'values' => $model_vals,
                         'value' => "k2iii", 'unit' => "",
                         'info' => 'You will choose one of the preloaded models form the Pickles Stellar Library',
                         'depend' => "template:$template_vals[0]"),
        'body_temp' => array('group' => 1, 'label' => 'B. Body temperature',
                             'type' => "Number", 'value' => "10000", 
                             'unit' => "K", 'min' => 0, 'step' => '0.01',
                             'depend' => "template:$template_vals[1]"),
        'line_center' => array('group' => 1, 'label' => 'Line center',
                               'type' => "Number", 'value' => "2.26",
                               'unit' => "microns",
                               'info' => 'This value depends on the filter/grism. Reference values are available at EMIR website',
                               'url' => 'http://www.iac.es/proyecto/emir/pages/observing-with-emir/observing-tools.php',
                               'depend' => "template:$template_vals[2]"),
        'line_fwhm' => array('group' => 1, 'label' => 'Line FWHM',
                             'type' => "Text", 'value' => "1.5",
                             'unit' => "Angstrom",
                             'depend' => "template:$template_vals[2]"),
        'line_peakf' => array('group' => 1, 'label' => 'Total line flux',
                              'type' => "Text", 'value' => "1.0",
                               'unit' => "x10<sup>-16</sup> erg/s/cm<sup>2</sup>",
                               'depend' => "template:$template_vals[2]"),
        'model_file' => array('group' => 1, 'label' => 'Model file',
                              'type' => "File", 'value' => "", 'unit' => "",
                              'info' => 'You will provide your proper own SED. The format of your file is availabe at EMIR website',
                              'url' => 'http://www.iac.es/proyecto/emir/pages/observing-with-emir/observing-tools.php',
                              'depend' => "template:$template_vals[3]"),


        // Group 2
        'airmass' => array('group' => 2, 'label' => 'Airmass',
                           'type' => "Number", 'value' => "1.5", 'unit' => "",
                           'info' => 'The Airmass of the observed target. Must be between 1 and 2.',
                           'min' => 1, 'max' => 2, 'step' => 0.01),
        'seeing' => array('group' => 2, 'label' => 'Seeing',
                          'type' => "Number", 'value' => "0.8",
                          'unit' => "arcsec", 'min' => 0, 'step' => '0.01',
                          'info' => "Astronomical seeing refers to the blurring and twinkling of astronomical objects such as stars caused by turbulences",
                          'url' => 'https://en.wikipedia.org/wiki/Astronomical_seeing'),


        // Group 3
        'operation' => array('group' => 3, 'label' => 'Operation',
                             'type' => "Select", 'values' => $operation_vals,
                             'value' => "Photometry", 'unit' => "",
                             'dependID' => 'operation'),
        'photo_filter' => array('group' => 3, 'label' => 'Filter',
                                'type' => "Radio",'values' => $filter_vals, 'value' => "Ks",
                                'unit' => "", 'depend' => "operation:$operation_vals[0]",
                                'function' => "filterLineCenter"),
        'photo_exp_time'  => array('group' => 3, 'label' => 'Exp. time', 
                                   'type' => "Text", 'value' => "1-10",
                                   'unit' => "seconds",
                                   'info' => 'Single number: single calculation of the S/N for this time will be performed<br />Range: S/N will be calculated for the whole range',
                                   'depend' => "operation:$operation_vals[0]"),
        'photo_nf_obj' => array('group' => 3, 'label' => '# frames: Object',
                                'type' => "Text", 'value' => "1",'unit' => "",
                                'info' => 'Number of on and off target images',
                                'depend' => "operation:$operation_vals[0]",
                                'nobr' => 1),
        'photo_nf_sky' => array('group' => 3, 'label' => 'Sky', 'type' => "Text",
                                'value' => "1",    'unit' => "",
                                'depend' => "operation:$operation_vals[0]"),
        'spec_grism' => array('group' => 3, 'label' => 'Grism',
                              'type' => "Radio", 'values' => $grism_vals,
                              'value' => "K", 'unit' => "",
                              'depend' => "operation:$operation_vals[1]",
                              'function' => "filterLineCenter"),
        'spec_slit_width' => array('group' => 3, 'label' => 'Slit width',
                                   'type' => "Text", 'value' => "0.8",
                                   'unit' => "arcsec",
                                   'depend' => "operation:$operation_vals[1]"),
        'spec_exp_time'   => array('group' => 3, 'label' => 'Exp. time',
                                   'type' => "Text", 'value' => "100",
                                   'unit' => "seconds",
                                   'info' => 'Single number: single calculation of the S/N for this time will be performed<br />Range: S/N will be calculated for the whole range',
                                   'depend' => "operation:$operation_vals[1]"),
        'spec_nf_obj'  => array('group' => 3, 'label' => '# frames: Object',
                                'type' => "Text", 'value' => "1", 'unit' => "",
                                'info' => 'Number of on and off target images',
                                'depend' => "operation:$operation_vals[1]",
                                'nobr' => 1),
        'spec_nf_sky'  => array('group' => 3, 'label' => 'Sky', 'type' => "Text",
                                'value' => "1", 'unit' => "",
                                'depend' => "operation:$operation_vals[1]"),
        'submit'  => array('group' => 3, 'label' => 'Calculate',
                           'type' => "Submit", 'value' => "Calculate",
                           "unit" => ""),
    );


    // GROUPS fOR FIELDSETs
    $GROUPS= array("source_config" => "Source configuration", "spectral_template" => "Spectral template",
                   "observ_config" => "Observation configuration", "operation_info" => "Operation" );


    // Copy POST data to VALUES
    if (!empty($_POST)) {
        foreach ($FIELDS as $params => $data) {
            if (!in_array($data['type'], array("Submit", "File"))) {
                // Values will be sanitazed when displaying on screen / being saved to XML file
                $FIELDS[$params]['value'] = $_POST[$params];
            }
        }
    }

    $data_sent = (isset ($_POST['data_sent']) && ($_POST['data_sent'] == 'sent'));



?>


    <div id="dialog_out">
        <div id="dialog_in"><span>Processing... Please, wait &nbsp; </span>
        <img src="ajax-loader.gif" alt="Loading" /></div>
    </div>

    <div id="page">
        <div id="content_emir">
                <form enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF']; ?>#results" method="post" onsubmit="document.getElementById('dialog_out').style.display='block'; return true;">

<?php

    // Initialize
    $last_group = -1;
    $group = array_values($GROUPS);
    $group_key = array_keys($GROUPS);
    $xml = new SimpleXMLElement('<?xml version="1.0" encoding="utf-8"?><data_etc></data_etc>');
    $next_short = false;
    $depend = "";


    if (!($fname = mkstemp(DATA_DIR."/emir-XXXXXX.xml"))) {
        die ("<h2>ERROR: Out files can not be created</h2>");
    }



    // PROCESS FIELDS
    foreach ($FIELDS as $id => $field) {
        if ($last_group != $field['group']) {
            // New group
            if ($last_group != -1) {
                if ($depend != "") {
                    echo "</div> <!-- Closing4 $depend -->\n";
                    $depend = "";
                }
                echo "</fieldset>\n\n";
            }
            $num_field = 1;
            $last_group = $field['group'];

            echo "<fieldset>\n";
            echo "<h2>" . $group[$field['group']] . "</h2>\n";
            $xml_cat = $xml->addChild($group_key[$field['group']]);

        }

        // BLOQUES CON DEPENDENCIAS
        if (isset($field['depend'])) {
            if (($depend != $field['depend']) && ($depend != "")) {
                echo "</div> <!-- Closing1 $depend -->\n";
            }
            if ($depend != $field['depend']) {
                $depend = $field['depend'];
                $depend_data = explode(':', $field['depend']);
                echo "\n\n  <!-- Opening $depend -->\n  <div id=\"$depend\" class=\"hide\" data-group=\"$depend_data[0]\" data-value=\"$depend_data[1]\">\n";
            }
        }
        elseif ($depend != "") {
            echo "</div> <!-- Closing2 $depend -->\n";
            $depend = "";
        }


        if ($field['type'] == "Submit") {
            // Submit button
            echo "<div class=\"submit_button\"><input name=\"$id\" id=\"$id\" type=\"submit\" value=\"$field[label]\"  /> &nbsp; &nbsp;";
            echo "<input name=\"reset\" id=\"reset\" type=\"button\" value=\"Reset\" onclick=\"location.href='$_SERVER[PHP_SELF]';\" /></div>\n";
        }
        else {
            // Normal fields
            // Save field to XML. Get value (except FILE: tmp_name)
            //$value = (($field['type'] == "File") && isset($_FILES['model_file'])) ? $_FILES['model_file']['tmp_name'] : $field['value'];
            $value = $field['value'];
            if (($field['type'] == "File") && isset($_FILES['model_file'])) {
                $MAX_SIZE = 2 * 1024 * 1024;
                $value = "$fname.dat";
                //echo "<h3>TEST:".$_FILES['model_file']["type"]."</h3>";
                if ($_FILES['model_file']["size"] > $MAX_SIZE)
                    echo "<script>alert('ERROR: File is bigger than 2 MB');</script>\n";
                    // If file is bigger than permitted, we will NOT copy it (and then python script will print error)
                else
                   move_uploaded_file($_FILES['model_file']["tmp_name"], $value);
            }
            $xml_cat->addChild($id, htmlspecialchars(strip_tags($value)));


            // PRINT LABEL
            echo "<span class=\"field\">";
            if (($field['type'] != "Radio") && ($field['type'] != "File"))  echo "<label for=\"$id\">";
            echo "<span class=\"";
            if ($next_short) echo "short-";
            echo "label\">$field[label]";
            if (isset($field['info']) || isset($field['url'])) {
                echo " <img class=\"info\" src=\"info.png\" alt=\"i\" title=\"$field[info]";
                if (isset($field['url'])) {
                    echo " - Click this blue info icon for more info.\"";
                    echo " onclick=\"window.open('$field[url]')";
                }
                echo "\"  />";
            }

            echo ": </span>\n";
            if (($field['type'] != "Radio") && ($field['type'] != "File"))  echo "</label>";

            // INPUT TEXT
            if (($field['type'] == "Text") || ($field['type'] == "Number")) {
                echo "<input name=\"$id\" id=\"$id\" type=\"$field[type]\" data-defvalue=\"$field[value]\" value=\"$field[value]\"";
                if ($field['type'] == "Number") {
                    if (isset($field['min']))  echo " min=\"$field[min]\"";
                    if (isset($field['max']))  echo " max=\"$field[max]\"";
                    if (isset($field['step'])) echo " step=\"$field[step]\"";
                }
                echo " />\n";
            }

            // SELECT FIELD: build options
            elseif ($field['type'] == "Select") {
                echo "<select name=\"$id\" id=\"$id\"";
                if (isset($field['dependID'])) {
                    echo " onchange=\"chSelect('$field[dependID]', this.value);\"";
                }
                else if (isset($field['onChange'])) {
                    echo " onchange=\"$field[onChange]\"";
                }
                echo ">\n";
                foreach ($field['values'] as $val) {
                    echo "\t<option value=\"$val\"";
                    if ($val == $field['value']) echo " selected=\"selected\"";
                    echo ">$val</option>\n";
                }
                echo "</select>\n";
            }

            // RADIO BUTTON: build options
            elseif ($field['type'] == "Radio") {
                foreach ($field['values'] as $val) {
                    echo "\t<input type=\"radio\" name=\"$id\" value=\"$val\"";
                    if ($val == $field['value']) echo " checked=\"checked\"";
                    if (isset($field['function'])) echo " onclick=\"$field[function]('$id', this.value);\"";
                    echo "/>$val&nbsp;\n";
                }
            }

            // FILE INPUT
            elseif ($field['type'] == "File") {
                echo "<input name=\"$id\" id=\"$id\" type=\"file\" />\n";
            }

        // PRINT UNITS
        echo " <span class=\"unit\" id=\"unit_$id\">$field[unit]";
        if (isset($field['max']) || isset($field['min'])) {
            if (!isset($field['max'])) echo " [&ge; $field[min]]";
            elseif (!isset($field['min'])) echo " [&le; $field[max]]";
            else echo " [$field[min] - $field[max]]";
        }
        echo "</span>\n";

        echo "</span>";
        if (!isset($field['nobr'])) {
            $next_short = false;
            echo "<br />";
        }
        else {
            echo " &nbsp; ";
            $next_short = true;
        }
        $num_field++;
        }
    }

    // GENERATE XML
    $dom = dom_import_simplexml($xml)->ownerDocument;
    $dom->formatOutput = true;
    $xml_save = $dom->saveXML();

    if ($fxml = fopen("$fname.xml", "w+")) {
        fwrite($fxml, $xml_save);
         fclose($fxml);
    }
    else {
        die ("<h2>ERROR: Out file can not be created</h2>\n");
    }


    if ($depend != "") {
        echo "</div> <!-- Closing3 $depend -->\n";
        $depend = "";
    }

?>
                <input type="hidden" name="data_sent" id="data_sent" value="sent">
            <a name="results">
            </fieldset>

        </form>

    </div>


    </div>
    <div>


    <?php


        if ($data_sent) {
            #$cmd = "/datos/ext/proyecto/emir/pages/observing-with-emir/observing-tools/etc_gui.py $fname";
            $cmd = "(export LD_LIBRARY_PATH=/usr/pkg/python/Python-3.4.3/lib ; /usr/pkg/python/Python-3.4.3/bin/python3 ./etc_gui.py $fname)";
            exec ($cmd, $cmd_out);

            echo "<div id=\"code\">\n";
            if (file_exists($fname."_out.xml")) {
                $xml_result = simplexml_load_file($fname."_out.xml") or die("Error: Cannot create object");

                $XMLElements = ["error", "warning", "text", "table", "fig"];

                echo "</a><h1>RESULTS</h1>\n";
                foreach ($XMLElements as $elem) {
                    $outputs = $xml_result->xpath("//$elem");
                    if ($outputs) {
                        foreach ($outputs as $out) {
                            if (trim($out) == "")
                                continue;
                            if (in_array($elem, array("error", "warning", "text"))) {
                                echo "<span class=\"results_$elem\">$out</span><br />\n";
                            }
                            elseif ($elem == "table") {
                                echo "<br /><h2>Table</h2>\n";
                                echo "<pre>$out</pre>\n";
                            }
                            elseif ($elem == "fig") {
                                if (startswith($out, DATA_DIR) && endswith($out, ".png") && file_exists($out)) {
                                    $img_path = str_replace("/datos/ext/", "/", $out);
                                    echo "<br /><img src=\"$img_path\" alt=\"img\" style=\"max-width:610px;\" />\n";
                                }
                                else {
                                    echo "<li class=\"error\">Graph is not valid</h3>\n";
                                }
                            }
                        }
                    }
                }
/*
                # DEBUG
                $xml_out = $xml_result->asXML();
                echo "<pre>$xml_out</pre>\n";
                $xml_out = htmlspecialchars($xml_out);
                // Apply some syntax highlighting and remove extra spans
                $xml_out = str_replace(array("&lt;", "&gt;"), array("</span>&lt;", "&gt;<span class=\"value\">"), $xml_out);
                $xml_out = substr($xml_out, 0, -strlen('<span> class="value">'));
                $xml_out = substr($xml_out, strlen("</span>"));
                echo "<pre>$xml_out</pre>\n";
    */
            }

        echo "<br />&nbsp;\n";
        echo "</div>\n";
        }

    ?>
    </div>
<script>$("[title]").tooltip();

<?php
    // Set value for bound fields
     foreach ($FIELDS as $id => $field) {
        if (isset($field['dependID'])) {
            echo "chSelect('$field[dependID]', '$field[value]');\n";
        }
    }

    echo "filterLineCenter('spec_grism', '"   . $FIELDS['spec_grism']['value']   . "', document.getElementById('line_center').value);\n";
    echo "filterLineCenter('photo_filter', '" . $FIELDS['photo_filter']['value'] . "', document.getElementById('line_center').value);\n";


?>
</script>

