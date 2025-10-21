###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import pytest

from LbAPCommon.linting.bk_paths import InvalidBKQueryError, validate_bk_query

EXAMPLE_PATH_1 = "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"


@pytest.mark.parametrize(
    "path",
    [
        EXAMPLE_PATH_1,
        "/LHCb/Collision15/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco15a/Stripping24r1/90000000/MDST.DST",
        "/LHCb/Collision23/Beam6800GeV-VeloClosed-MagDown-Excl-UT/Real Data/Sprucing23/90000000/CHARM.DST",
        "/LHCb/Collision22/Beam6800GeV-VeloClosed-MagDown-Excl-UT/Real Data/HLT201/98100000/FULL.RAW",
    ],
)
def test_good(path):
    assert validate_bk_query(path)


def test_suggestion():
    with pytest.raises(InvalidBKQueryError) as e:
        validate_bk_query(
            "/MC/2018/24142001/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/ALLSTREAMS.DST"
        )
    assert "The provided BK query is not valid" in str(e)
    assert EXAMPLE_PATH_1 in str(e)


@pytest.mark.parametrize(
    "path",
    [
        "/MC/2018/xxxxx/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/ALLSTREAMS.DST",
        "/LHCb/Collision23/Beam6800GeV-VeloClosed-MagDown-Excl-UT/Real Data/90000000/RAW",
        "/LHCb/Collision22/Beam6800GeV-VeloClosed-MagDown-Excl-MU-UT/Real Data/98100000/RAW",
        "/LHCb/Collision22/Beam6800GeV-VeloClosed-MagDown-Excl-MU-UT/Real Data/95100000/RAW",
        "/LHCb/Collision22/Beam6800GeV-MagUp-MagDown-Excl-UT/Real Data/94000000/RAW",
    ],
)
def test_invalid(path):
    with pytest.raises(InvalidBKQueryError) as e:
        validate_bk_query(path)
    assert "The provided BK query is not valid" in str(e)
