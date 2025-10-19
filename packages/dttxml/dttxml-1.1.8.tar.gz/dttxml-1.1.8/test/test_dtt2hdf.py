import pytest
import sys
import subprocess
from dttxml.dtt2bunch import dtt2bunch
from dttxml.dtt2hdf import main


def run_dtt2hdf(*args):
    try:
        main(args)
    except Exception:
        return False
    return True



@pytest.mark.xfail(reason = """
This dttxml has references and the bunch exporter currently cannot handle this.
It uses DiagAccess to combinatorically export everything, and the references are
not available through the DiagAccess interfaces
""")
def test_dtt2hdf_1(fpath_join, tpath_join, plot, pprint):
    """
    """
    # EXAMPLE 1: Dealing with a SweptSine measurement file.

    # These are the xml files we want to get our data from.
    measurement_file = fpath_join('data', '2020-01-03_H1_DARM_OLGTF_LF_SS_5to1100Hz_15min.xml')
    b = dtt2bunch(measurement_file)
    success = run_dtt2hdf(measurement_file, tpath_join('output.h5'))

    assert(success)


@pytest.mark.xfail(reason = """
This dttxml has references and the bunch exporter currently cannot handle this.
It uses DiagAccess to combinatorically export everything.  DiagAccess can't handle the way references can be incompletely stored.
For example, if a transfer function is stored, DiagAccess assumes a coherence is also stored for the same channels.
This is true for results, but not necessarily true for references.
""")
def test_dtt2hdf_2(fpath_join, tpath_join, plot, pprint):
    """
    """
    # EXAMPLE 1: Dealing with a SweptSine measurement file.

    # These are the xml files we want to get our data from.
    measurement_file = fpath_join('data', '2019-01-25_H1SUSETMX_L1_iEXC2DARM_HFDynamicsTest_40-110Hz.xml')

    b = dtt2bunch(measurement_file)
    success = run_dtt2hdf(measurement_file, tpath_join('output.h5'))

    assert(success)




#@pytest.mark.xfail(reason = """
#""")
def test_dtt2hdf_3(fpath_join, tpath_join, plot, pprint):
    """
    """
    # EXAMPLE 1: Dealing with a SweptSine measurement file.

    # These are the xml files we want to get our data from.
    measurement_file = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.xml')

    b = dtt2bunch(measurement_file)
    pprint("----------------------output dict---------------------------")
    pprint(b)
    pprint("----------------------output done---------------------------")
    success = run_dtt2hdf(measurement_file, tpath_join('output.h5'))

    assert(success)
