# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 12:17:34 2017

@author: Andre Barreto
"""

import unittest
import numpy as np
import numpy.testing as npt
from sharc.propagation.propagation_p619 import PropagationP619

class TestPropagationP619(unittest.TestCase):

    def setUp(self):
        self.p619 = PropagationP619()

    def test_specific_attenuation(self):
        temperature = 15 + 273.15 # K
        vapour_density = 7.5 # g/m**3
        pressure_hPa = 1013.25
        vapour_pressure_hPa = vapour_density * temperature / 216.7

        # compare with benchmark from ITU-R P-676-11 Figs. 1 and 2
        f_GHz_vec = [50, 60, 100, 200, 500, 1000]
        specific_att = np.zeros(len(f_GHz_vec))
        specific_att_p676_lower = [3e-1, 1e1, 4e-1, 2, 5e1, 6e2]
        specific_att_p676_upper = [5e-1, 2e1, 5e-1, 4, 7e1, 8e2]

        for index in range(len(f_GHz_vec)):
            specific_att[index] = self.p619._get_specific_attenuation(pressure_hPa,
                                                                      vapour_pressure_hPa,
                                                                      temperature,
                                                                      float(f_GHz_vec[index]) * 1000)
        npt.assert_array_less(specific_att_p676_lower, specific_att)
        npt.assert_array_less(specific_att, specific_att_p676_upper)

    def test_atmospheric_gasses_loss (self):
        # compare with benchmark from ITU-R P-619 Fig. 3
        frequency_MHz = 30000.
        sat_params = ParametersFss()
        sat_params.imt_altitude = 1000

        vapour_density_vec = [7.5, 12.5, 2.5, 5.]
        apparent_elevation_vec = [0, 10, 20, 40]

        loss_lower_vec = [10, 1, .3, .2]
        loss_upper_vec = [20, 2, .4, .3]

        for vapour_density, apparent_elevation, loss_lower, loss_upper in zip(vapour_density_vec,
                                                                              apparent_elevation_vec,
                                                                              loss_lower_vec,
                                                                              loss_upper_vec):
            sat_params.surf_water_vapour_density = vapour_density
            loss = self.p619._get_atmospheric_gasses_loss(frequency_MHz, apparent_elevation,
                                                          sat_params)
            self.assertLessEqual(loss_lower, loss)
            self.assertGreaterEqual(loss_upper, loss)


    def test_beam_spreading_attenuation(self):
        # compare with benchmark from ITU-R P-619 Fig. 7

        altitude_vec = np.array([0,1,2,3,4,6]) * 1000
        elevation_vec = [0,.5,1,2,3,5]
        att_lower_vec = [.8, .6 , .4, .2, .1, .05]
        att_upper_vec = [.9, .7, .5, .3, .2, .1]
        earth_to_space_vec = [True, False, True, False, True, False]

        for altitude, elevation, lower, upper, earth_to_space in zip(altitude_vec,
                                                                     elevation_vec,
                                                                     att_lower_vec,
                                                                     att_upper_vec,
                                                                     earth_to_space_vec):

            attenuation = self.p619._get_beam_spreading_att(elevation, altitude, earth_to_space)
            self.assertLessEqual(lower, abs(attenuation))
            self.assertGreaterEqual(upper, abs(attenuation))

            if earth_to_space:
                self.assertGreater(attenuation, 0)
            else:
                self.assertLess(attenuation, 0)

    def test_tropo_scintillation_attenuation(self):
        # compare with benchmark from ITU-R P-619 Fig. 8

        antenna_gain = 0.
        frequency_MHz = 30000.
        wet_refractivity = 42.5

        elevation_vec = np.array([5., 10., 20., 90., 35., 5., 10., 20., 35., 90.])
        percentage_gain_exceeded = np.array([.01, .1, 1, 3, 10, 90, 98, 99, 99.9, 99.99])
        attenuation_lower = [5, 1, .5, .1, .1, 1, 1, .5, .4, .3]
        attenuation_upper = [7, 2, .6, .2, .2, 2, 2, .7, .6, .5]
        sign = [-1, -1, -1, -1, -1, +1, +1, +1, +1, +1]
        attenuation = self.p619._get_tropospheric_scintillation(elevation=elevation_vec,
                                                                frequency_MHz=frequency_MHz,
                                                                antenna_gain_dB=antenna_gain,
                                                                time_ratio=percentage_gain_exceeded / 100,
                                                                wet_refractivity=wet_refractivity)

        npt.assert_array_less(attenuation_lower, np.abs(attenuation))
        npt.assert_array_less(np.abs(attenuation), attenuation_upper)

        npt.assert_array_equal(np.sign(attenuation), sign)

if __name__ == '__main__':
    unittest.main()
