import numpy as np
from matplotlib import pyplot as plt
import dttxml
from numpy.testing import assert_allclose


def test_access_TF(fpath_join, tpath_join, plot, pprint):
    """
    Example code on how to use the following methods from measurement.py:
        - get_raw_tf
        - get_set_of_channels
        - get_raw_asd
    """
    # EXAMPLE 1: Dealing with a SweptSine measurement file.

    # These are the xml files we want to get our data from.
    data_from_dtt = np.genfromtxt(
        fpath_join('data', '2020-01-03_H1_'
                   'DARM_OLGTF_LF_SS_A_DARMIN2_B_DARMIN1_tf.txt'),
        dtype='float',
        delimiter=None
    )

    freq_from_dtt = data_from_dtt[:, 0]
    tf_from_dtt = data_from_dtt[:, 1]+1j*data_from_dtt[:, 2]

    measurement_file = fpath_join('data', '2020-01-03_H1_'
                                  'DARM_OLGTF_LF_SS_5to1100Hz_15min.xml')
    channelA = 'H1:LSC-DARM1_IN2'
    channelB = 'H1:LSC-DARM1_IN1'
    acc = dttxml.DiagAccess(measurement_file)
    tf = acc.xfer(channelB, channelA)

    # Note: For some reason, the txt file is missing one frequency.
    # This is unrelated to the coherence, at least of this TF.

    #TODO, dtt exports one less value than the xml file has available?!
    max_num = 22
    assert_allclose(freq_from_dtt[:max_num], tf.FHz[:max_num], atol=1e-4)
    assert_allclose(tf_from_dtt[:max_num], tf.xfer[:max_num], atol=1e-4)


def test_access_CSD(fpath_join, tpath_join, plot, pprint):
    """
    This is currently the most legit test
    """
    measurement_file = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.xml')
    acc = dttxml.DiagAccess(measurement_file)

    #first do an ASD
    data_from_dtt = np.genfromtxt(
        fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.txt'),
        dtype='float',
        delimiter=None
    )

    freq_from_dtt = data_from_dtt[:, 0]
    asd_from_dtt = data_from_dtt[:, 1]

    channelA = 'H1:LSC-DARM1_IN2'
    asd = acc.asd(channelA)

    assert_allclose(asd_from_dtt, asd.asd)
    assert_allclose(freq_from_dtt, asd.FHz)

    #now do COH
    data_from_dtt = np.genfromtxt(
        fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB_COH_E1_E2_12.txt'),
        dtype='float',
        delimiter=None
    )

    freq_from_dtt = data_from_dtt[:, 0]
    COH_E1_from_dtt = data_from_dtt[:, 1]
    COH_E2_from_dtt = data_from_dtt[:, 2]
    COH_12_from_dtt = data_from_dtt[:, 3]
    coh_E1 = acc.coh('H1:LSC-DARM1_EXC',  'H1:LSC-DARM1_IN1')
    coh_E2 = acc.coh('H1:LSC-DARM1_EXC',  'H1:LSC-DARM1_IN2')
    coh_12 = acc.coh('H1:LSC-DARM1_IN1',  'H1:LSC-DARM1_IN2')
    assert_allclose(freq_from_dtt, coh_E1.FHz)
    assert_allclose(COH_E1_from_dtt, coh_E1.coh)
    assert_allclose(COH_E2_from_dtt, coh_E2.coh)
    assert_allclose(COH_12_from_dtt, coh_12.coh)

    #now do CSD
    data_from_dtt = np.genfromtxt(
        fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB_CSD_E1_E2_12.txt'),
        dtype='float',
        delimiter=None
    )
    freq_from_dtt = data_from_dtt[:, 0]
    CSD_E1_from_dtt = data_from_dtt[:, 1] + 1j*data_from_dtt[:, 2]
    CSD_E2_from_dtt = data_from_dtt[:, 3] + 1j*data_from_dtt[:, 4]
    CSD_12_from_dtt = data_from_dtt[:, 5] + 1j*data_from_dtt[:, 6]
    csd_E1 = acc.csd('H1:LSC-DARM1_EXC',  'H1:LSC-DARM1_IN1')
    csd_E2 = acc.csd('H1:LSC-DARM1_EXC',  'H1:LSC-DARM1_IN2')
    csd_12 = acc.csd('H1:LSC-DARM1_IN1',  'H1:LSC-DARM1_IN2')
    assert_allclose(freq_from_dtt, csd_E1.FHz)
    assert_allclose(CSD_E1_from_dtt, csd_E1.csd)
    assert_allclose(CSD_E2_from_dtt, csd_E2.csd)
    assert_allclose(CSD_12_from_dtt, csd_12.csd)

def test_access_csd_conjugate(fpath_join, tpath_join, plot, pprint):
    """
    Check that csd(A,B) == csd(B,A).conj()
    """
    measurement_file = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB_1CSD.xml')
    acc = dttxml.DiagAccess(measurement_file)
    csd_AB = acc.csd('H1:LSC-DARM1_EXC',  'H1:LSC-DARM1_IN2')
    csd_BA = acc.csd('H1:LSC-DARM1_IN2',  'H1:LSC-DARM1_EXC')
    assert_allclose(csd_AB.csd, csd_BA.csd.conjugate())

def test_access_transfer_phase(fpath_join, tpath_join, plot, pprint):
    """
    Make sure the transfer function has the right phase when loaded from
    an ffttools result
    """
    measurement_file = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB_1CSD.xml')
    acc = dttxml.DiagAccess(measurement_file)
    xfer = acc.xfer('H1:LSC-DARM1_IN2', 'H1:LSC-DARM1_EXC')

    data_from_dtt = np.genfromtxt(
        fpath_join('data', 'transfer.txt'),
        dtype='float',
        delimiter=None
    )

    tf_from_dtt = data_from_dtt[:, 1] + 1j * data_from_dtt[:, 2]

    assert_allclose(xfer.xfer, tf_from_dtt, rtol=5e-7)


def test_access_double_fail(fpath_join, tpath_join, plot, pprint):
    """
    This test checks a single precision file to show that it does *NOT* match double precision.

    Frequencies should be 14 points from 100 Hz to 101 Hz.
    """
    measurement_file = fpath_join('data', 'doublelin-single.xml')
    acc = dttxml.DiagAccess(measurement_file)
    coh = acc.coh('X2:LSC-AA_SASY90_EXC', 'X2:LSC-AA_SASY90_OUT')
    tf = acc.xfer('X2:LSC-AA_SASY90_EXC', 'X2:LSC-AA_SASY90_OUT')

    target = np.linspace(100, 101, 14)

    # array should not perfectly match target since file data is single precision
    np.testing.assert_raises(AssertionError, np.testing.assert_array_equal, target, tf.FHz)

def test_access_double(fpath_join, tpath_join, plot, pprint):
    """
    This test checks a double precision file to show that it matches expected frequency values.

    Frequencies should be 14 points from 100 Hz to 101 Hz.
    """
    measurement_file = fpath_join('data', 'doublelin-double.xml')
    acc = dttxml.DiagAccess(measurement_file)
    coh = acc.coh('X2:LSC-AA_SASY90_EXC', 'X2:LSC-AA_SASY90_OUT')
    tf = acc.xfer('X2:LSC-AA_SASY90_EXC', 'X2:LSC-AA_SASY90_OUT')

    target = np.linspace(100, 101, 14)

    # should exactly match linspace.  If not, we have a problem with
    # the XML save file or with the linear frequency generator in DTT.
    np.testing.assert_array_equal(target, tf.FHz)