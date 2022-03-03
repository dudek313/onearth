#!/usr/bin/env python3

# Copyright (c) 2002-2016, California Institute of Technology.
# All rights reserved.  Based on Government Sponsored Research under contracts NAS7-1407 and/or NAS7-03001.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#   3. Neither the name of the California Institute of Technology (Caltech), its operating division the Jet Propulsion Laboratory (JPL),
#      the National Aeronautics and Space Administration (NASA), nor the names of its contributors may be used to
#      endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE CALIFORNIA INSTITUTE OF TECHNOLOGY BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Tests for oe_sync_s3_configs.py and oe_sync_s3_idx.py
#

import subprocess
import sys
import unittest2 as unittest
import xmlrunner
from optparse import OptionParser
from math import isclose


# Handles parsing the raw output of twmsbox2wmts.py and wmts2twmsbox.py
def parse_twms_wmts_output(output):
    lines = output.split('\n')
    result_dict = {}
    unexpected_lines = ""
    for line in lines[:-1]: # last line is whitespace
        if "EPSG" in line:
            result_dict["EPSG"] = line.split(':')[1]
        elif "Scale Denominator" in line:
            result_dict["Scale Denominator"] = line.split(': ')[1]
        elif "Top Left BBOX" in line:
            result_dict["Top Left BBOX"] = line.split(': ')[1]
        elif "Request BBOX" in line:
            result_dict["Request BBOX"] = line.split(': ')[1]
        elif "TILECOL" in line:
            result_dict["TILECOL"] = line.split('=')[1]
        elif "TILEROW" in line:
            result_dict["TILEROW"] = line.split('=')[1]
        elif "tilesize" in line:
            result_dict["tilesize"] = line.split(': ')[1]
        else: # parse error, something is there that shouldn't be
            unexpected_lines += line + '\n'
    return result_dict, unexpected_lines
        

# Handles comparing two strings representing bounding boxes
# For example: comparing "-81.0000000000,36.0000000000,-72.0000000000,45.0000000000"
# to "-81,36,-72,45", which is the same box
def compare_bbox_str(req_bbox, twmsbox):
    # convert both strings into numerical values for comparison
    req_bbox_lst = list(map(lambda x: float(x), req_bbox.split(',')))
    twmsbox_lst = list(map(lambda x: float(x), twmsbox.split(',')))
    if req_bbox_lst == twmsbox_lst:
        return True, ""
    else:
        fail_str = "Expected values: {0}\nActual values: {1}\n".format(','.join(map(str, twmsbox_lst)),
                                                                      ','.join(map(str, req_bbox_lst)))
        return False, fail_str


class TestTWMSboxWMTSConvert(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        return   
    
    # Tests converting from a Tiled WMS box to WMTS tile and back to a Tiled WMS box
    # using first `twmsbox2wmts.py` and then `wmts2twmsbox.py`.
    # Runs `wmts2twmsbox.py` with Scale Denominator, TILECOL, and TILEROW as input.
    def test_twmsbox2wmts2twmsbox_scale_denom(self):
        twmsbox = "-81,36,-72,45"
        fail_str = ""
        
        twms_cmd = "python3 /home/oe2/onearth/src/scripts/twmsbox2wmts.py -b {0}".format(twmsbox)
        wmts_output = subprocess.check_output(twms_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        # parse the result to use as input for wmts2twmsbox.py
        wmts_dict, unexpected_lines = parse_twms_wmts_output(wmts_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in twmsbox2wmts.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        wmts_cmd = "python3 /home/oe2/onearth/src/scripts/wmts2twmsbox.py -e {0} -s {1} -c {2} -r {3}".format(wmts_dict['EPSG'],
                                                                                                              wmts_dict['Scale Denominator'],
                                                                                                              wmts_dict['TILECOL'],
                                                                                                              wmts_dict['TILEROW'])
        twms_output = subprocess.check_output(wmts_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        twms_dict, unexpected_lines = parse_twms_wmts_output(twms_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in wmts2twmsbox.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        test_result, fail_str = compare_bbox_str(twms_dict["Request BBOX"], twmsbox)
        fail_str = "`wmts2twmsbox.py` did not return the correct twmsbox values.\n" + fail_str
        self.assertTrue(test_result, fail_str)


    # Tests converting from a Tiled WMS box to WMTS tile and back to a Tiled WMS box
    # using first `twmsbox2wmts.py` and then `wmts2twmsbox.py`.
    # Runs `wmts2twmsbox.py` with Top Left BBOX, TILECOL, and TILEROW as input.
    def test_twmsbox2wmts2twmsbox_top_left_bbox(self):
        twmsbox = "-81,36,-72,45"
        fail_str = ""
        
        twms_cmd = "python3 /home/oe2/onearth/src/scripts/twmsbox2wmts.py -b {0}".format(twmsbox)
        wmts_output = subprocess.check_output(twms_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        # parse the result to use as input for wmts2twmsbox.py
        wmts_dict, unexpected_lines = parse_twms_wmts_output(wmts_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in twmsbox2wmts.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        wmts_cmd = "python3 /home/oe2/onearth/src/scripts/wmts2twmsbox.py -e {0} -t {1} -c {2} -r {3}".format(wmts_dict['EPSG'],
                                                                                                              wmts_dict['Top Left BBOX'],
                                                                                                              wmts_dict['TILECOL'],
                                                                                                              wmts_dict['TILEROW'])
        twms_output = subprocess.check_output(wmts_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        twms_dict, unexpected_lines = parse_twms_wmts_output(twms_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in wmts2twmsbox.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)
        
        test_result, fail_str = compare_bbox_str(twms_dict["Request BBOX"], twmsbox)
        fail_str = "`wmts2twmsbox.py` did not return the correct twmsbox values.\n" + fail_str
        self.assertTrue(test_result, fail_str)

    # Tests converting from a WMTS tile to Tiled WMS box and back to a WMTS box
    # using first `wmts2twmsbox.py` and then `twmsbox2wmts.py`.
    # Runs `wmts2twmsbox.py` with Scale Denominator, TILECOL, and TILEROW as input.
    def test_wmts2twmsbox2wmts_scale_denom(self):
        wmts_input = {
            "Scale Denominator": "6988528.300359",
            "TILECOL": "11",
            "TILEROW": "5"
            }
        fail_str = ""

        wmts_cmd = "python3 /home/oe2/onearth/src/scripts/wmts2twmsbox.py -s {0} -c {1} -r {2}".format(wmts_input['Scale Denominator'],
                                                                                                       wmts_input['TILECOL'],
                                                                                                       wmts_input['TILEROW'])
                                                                                                       
        twms_output = subprocess.check_output(wmts_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        # parse the result to use as input for twmsbox2wmts.py
        twms_dict, unexpected_lines = parse_twms_wmts_output(twms_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in wmts2twmsbox.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        twms_cmd = "python3 /home/oe2/onearth/src/scripts/twmsbox2wmts.py -b {}".format(twms_dict["Request BBOX"])
        wmts_output = subprocess.check_output(twms_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        wmts_dict, unexpected_lines = parse_twms_wmts_output(wmts_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in twmsbox2wmts.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        # check if the original input values were returned
        test_result = True
        # use isclose because the values may be rounded differently (6988528.300359 vs 6988528.3003589983)
        if not isclose(float(wmts_input["Scale Denominator"]),float(wmts_dict["Scale Denominator"])):
            test_result = False
            fail_str += "`twmsbox2wmts.py` returned {0} for Scale Denominator when it should have returned {1}\n".format(wmts_dict["Scale Denominator"],
                                                                                                             wmts_input["Scale Denominator"])
        if wmts_input["TILECOL"] != wmts_dict["TILECOL"]:
            test_result = False
            fail_str += "`twmsbox2wmts.py` returned {0} for TILECOL when it should have returned {1}\n".format(wmts_dict["TILECOL"],
                                                                                                             wmts_input["TILECOL"])
        if wmts_input["TILEROW"] != wmts_dict["TILEROW"]:
            test_result = False
            fail_str += "`twmsbox2wmts.py` returned {0} for TILEROW when it should have returned {1}\n".format(wmts_dict["TILEROW"],
                                                                                                             wmts_input["TILEROW"])
        self.assertTrue(test_result, fail_str)

    # Tests converting from a WMTS tile to Tiled WMS box and back to a WMTS box
    # using first `wmts2twmsbox.py` and then `twmsbox2wmts.py`.
    # Runs `wmts2twmsbox.py` with Top Left BBOX, TILECOL, and TILEROW as input.
    def test_wmts2twmsbox2wmts_top_left_bbox(self):
        wmts_input = {
            "Top Left BBOX": "-180,81,-171,90",
            "TILECOL": "11",
            "TILEROW": "5"
            }
        fail_str = ""

        wmts_cmd = "python3 /home/oe2/onearth/src/scripts/wmts2twmsbox.py -t {0} -c {1} -r {2}".format(wmts_input['Top Left BBOX'],
                                                                                                       wmts_input['TILECOL'],
                                                                                                       wmts_input['TILEROW'])
                                                                                                       
        twms_output = subprocess.check_output(wmts_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        # parse the result to use as input for twmsbox2wmts.py
        twms_dict, unexpected_lines = parse_twms_wmts_output(twms_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in wmts2twmsbox.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        twms_cmd = "python3 /home/oe2/onearth/src/scripts/twmsbox2wmts.py -b {}".format(twms_dict["Request BBOX"])
        wmts_output = subprocess.check_output(twms_cmd, shell=True, stderr=subprocess.PIPE).decode("utf-8")
        wmts_dict, unexpected_lines = parse_twms_wmts_output(wmts_output)

        if unexpected_lines != "":
            fail_str += "ERROR: Unexpected line(s) in twmsbox2wmts.py output:\n{}".format(unexpected_lines)
            self.fail(fail_str)

        # check if the original input values were returned
        test_result, fail_str = compare_bbox_str(wmts_input["Top Left BBOX"], wmts_dict["Top Left BBOX"])
        fail_str = "`twmsbox2wmts.py` did not return the correct Top Left BBOX values.\n" + fail_str
        if wmts_input["TILECOL"] != wmts_dict["TILECOL"]:
            test_result = False
            fail_str += "`twmsbox2wmts.py` returned {0} for TILECOL when it should have returned {1}\n".format(wmts_dict["TILECOL"],
                                                                                                             wmts_input["TILECOL"])
        if wmts_input["TILEROW"] != wmts_dict["TILEROW"]:
            test_result = False
            fail_str += "`twmsbox2wmts.py` returned {0} for TILEROW when it should have returned {1}\n".format(wmts_dict["TILEROW"],
                                                                                                             wmts_input["TILEROW"])
        self.assertTrue(test_result, fail_str)

    @classmethod
    def tearDown(self):
        return
    
    @classmethod
    def tearDownClass(self):
        return
        
if __name__ == '__main__':
    # Parse options before running tests
    parser = OptionParser()
    parser.add_option(
        '-o',
        '--output',
        action='store',
        type='string',
        dest='outfile',
        default='test_twmsbox_wmts_convert_results.xml',
        help='Specify XML output file (default is test_twmsbox_wmts_convert_results.xml')
    parser.add_option(
        '-s',
        '--start_server',
        action='store_true',
        dest='start_server',
        help='Load test configuration into Apache and quit (for debugging)')
    (options, args) = parser.parse_args()

    # --start_server option runs the test Apache setup, then quits.
    if options.start_server:
        TestTWMSboxWMTSConvert.setUpClass()
        sys.exit(
            'Apache has been loaded with the test configuration. No tests run.'
        )

    # Have to delete the arguments as they confuse unittest
    del sys.argv[1:]

    with open(options.outfile, 'wb') as f:
        print('\nStoring test results in "{0}"'.format(options.outfile))
        unittest.main(testRunner=xmlrunner.XMLTestRunner(output=f))