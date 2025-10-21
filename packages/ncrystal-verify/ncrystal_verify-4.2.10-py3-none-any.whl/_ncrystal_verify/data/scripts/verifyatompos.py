#!/usr/bin/env python3

################################################################################
##                                                                            ##
##  This file is part of NCrystal (see https://mctools.github.io/ncrystal/)   ##
##                                                                            ##
##  Copyright 2015-2025 NCrystal developers                                   ##
##                                                                            ##
##  Licensed under the Apache License, Version 2.0 (the "License");           ##
##  you may not use this file except in compliance with the License.          ##
##  You may obtain a copy of the License at                                   ##
##                                                                            ##
##      http://www.apache.org/licenses/LICENSE-2.0                            ##
##                                                                            ##
##  Unless required by applicable law or agreed to in writing, software       ##
##  distributed under the License is distributed on an "AS IS" BASIS,         ##
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  ##
##  See the License for the specific language governing permissions and       ##
##  limitations under the License.                                            ##
##                                                                            ##
################################################################################

# NEEDS: numpy ase

import NCrystal as NC
import NCrystal.cli as nc_cli
from NCTestUtils.common import ensure_error
import shlex

def test_cli( args ):
    if isinstance(args,str):
        args = shlex.split(args)
    hr=f"============= CLI >>{shlex.join(args)}<< ===================="
    print(hr)
    nc_cli.run('verifyatompos',*args)
    print('='*len(hr))

def main():
    test_cli(['-h'])
    #with ensure_error(NC.NCFileNotFound,
    data = """NCMAT v1
@CELL
    lengths 4.04958 4.04958 4.04958
    angles 90. 90. 90.
@ATOMPOSITIONS
    Al 0. 0.5 0.5
    Al 0. 0. 0.
    Al 0.5 0.5 0.
    Al 0.5 0. 0.5
@DEBYETEMPERATURE
    Al   410.3542
"""
    data_perturbed_1em5 = """NCMAT v1
@CELL
    lengths 4.04958 4.04958 4.04958
    angles 90. 90. 90.
@ATOMPOSITIONS
    Al 0. 0.5 0.5
    Al 0. 0. 0.
    Al 0.5 0.49999 0.
    Al 0.5 0. 0.5
@DEBYETEMPERATURE
    Al   410.3542
"""
    data_perturbed_1em8 = """NCMAT v1
@CELL
    lengths 4.04958 4.04958 4.04958
    angles 90. 90. 90.
@ATOMPOSITIONS
    Al 0. 0.5 0.5
    Al 0. 0. 0.
    Al 0.5 0.49999999 0.
    Al 0.5 0. 0.5
@DEBYETEMPERATURE
    Al   410.3542
"""
    NC.registerInMemoryFileData('Al_nosg.ncmat',data)
    NC.registerInMemoryFileData('Al.ncmat',data+'@SPACEGROUP\n    225\n')
    NC.registerInMemoryFileData('Al_perturbed5.ncmat',data_perturbed_1em5+'@SPACEGROUP\n    225\n')
    NC.registerInMemoryFileData('Al_perturbed8.ncmat',data_perturbed_1em8+'@SPACEGROUP\n    225\n')
    test_cli('Al.ncmat')
    with ensure_error(RuntimeError,
                      'Not applicable: Material does not have unit'
                      ' cell structure info'):
        test_cli('Al_nosg.ncmat')
    test_cli('Al_perturbed8.ncmat')

    issuemsg = ( 'Problems detected in list of atom positions! Most likely'
                 ' this is a real problem, but you can also check with '
                 '(enter spacegroup 225): '
                 'https://www.cryst.ehu.es/cryst/get_wp.html')

    with ensure_error(RuntimeError,issuemsg):
        test_cli('Al_perturbed5.ncmat')
    test_cli('Al_perturbed5.ncmat --eps=1e-4')
    with ensure_error(RuntimeError,issuemsg):
        test_cli('Al_perturbed8.ncmat --eps=1e-10')
    test_cli('Al.ncmat --wyckoff')
    test_cli('MgAl2O4_sg227_MAS.ncmat --wyckoff')
    test_cli('MgAl2O4_sg227_MAS.ncmat --wyckoff --quiet')
    test_cli('MgAl2O4_sg227_MAS.ncmat --quiet')


if __name__ == '__main__':
    main()
