#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import unittest

from OHA.Diabetes import Diabetes


class DiabetesTest(unittest.TestCase):

    def test_risk_is_0(self):
        params = {'gender': 'F', 'age': 20, 'systolic': 139, 'diastolic': 89,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 0)

    def test_risk_is_2(self):
        params = {'gender': 'M', 'age': 20, 'systolic': 139, 'diastolic': 89,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 2)

    def test_risk_is_4(self):
        params = {'gender': 'M', 'age': 20, 'systolic': 139, 'diastolic': 90,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 4)

        params = {'gender': 'M', 'age': 20, 'systolic': 140, 'diastolic': 100,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 4)

        params = {'gender': 'M', 'age': 20, 'systolic': 140, 'diastolic': 89,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 4)

        params = {'gender': 'F', 'age': 42, 'systolic': 139, 'diastolic': 89,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 4)

    def test_risk_is_7(self):
        params = {'gender': 'M', 'age': 31, 'systolic': 139, 'diastolic': 90,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 7)

        params = {'gender': 'M', 'age': 31, 'systolic': 140, 'diastolic': 100,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 7)

        params = {'gender': 'M', 'age': 31, 'systolic': 140, 'diastolic': 89,
                  'weight': 50.0, 'height': 2.0, 'waist': 50.0, 'hip': 90.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 7)

    def test_risk_is_9(self):
        params = {'gender': 'F', 'age': 30, 'systolic': 145, 'diastolic': 80,
                  'weight': 70.0, 'height': 1.5, 'waist': 99.0, 'hip': 104.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 9)

    def test_risk_is_11(self):
        params = {'gender': 'M', 'age': 30, 'systolic': 145, 'diastolic': 80,
                  'weight': 70.0, 'height': 1.5, 'waist': 99.0, 'hip': 104.0}
        result = Diabetes().calculate(params)
        self.assertEqual(result['risk'], 11)
