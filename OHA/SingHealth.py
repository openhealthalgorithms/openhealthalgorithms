#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import json
import os

from OHA.Defaults import Defaults
from OHA.Diabetes import Diabetes
from OHA.SgFramingham import SgFramingham as SGFRE
from OHA.assessments.BMIAssessment import BMIAssessment
from OHA.assessments.BPAssessment import BPAssessment
from OHA.assessments.DiabetesAssessment import DiabetesAssessment
from OHA.assessments.DietAssessment import DietAssessment
from OHA.assessments.PhysicalActivityAssessment import PhysicalActivityAssessment
from OHA.assessments.SEABMIAssessment import SEABMIAssessment
from OHA.assessments.SmokingAssessment import SmokingAssessment
from OHA.assessments.WHRAssessment import WHRAssessment
from OHA.param_builders.diabetes_param_builder import DiabetesParamsBuilder
from OHA.param_builders.sg_framingham_param_builder import SGFraminghamParamsBuilder as SGFPB

__author__ = 'fredhersch'
__email__ = 'fred@openhealthalgorithms.org'


class SingHealth(object):
    """
        Lifestyle assessment based on SG Guidelines
    """

    @staticmethod
    def estimate_cvd_risk(age, high_risk_condition):
        # If age > assessment_age and NO high risk conditions
        assessment_age = 40

        if age < assessment_age:
            return False, "Not for CVD Risk as Age < 40"
        elif high_risk_condition["status"]:
            return False, "Has High Risk Condition"
        else:
            return True, "Continue"

    @staticmethod
    def load_messages():
        filename = 'guideline_healthassessment_content.json'
        file_path = ('%s/guideline/%s' % (
            os.path.dirname(os.path.realpath(__file__)),
            filename
        ))
        with open(file_path) as json_data:
            data = json.load(json_data)

        return data["body"]["messages"]

    @staticmethod
    def load_guidelines(guideline_key):
        filename = 'guideline_%s.json' % guideline_key
        file_path = ('%s/guideline/%s' % (
            os.path.dirname(os.path.realpath(__file__)),
            filename
        ))
        with open(file_path) as json_data:
            data = json.load(json_data)

        return data

    @staticmethod
    def check_medications(search, medications):
        for medication in medications:
            if str.upper(medication) == str.upper(search):
                return True
            else:
                return False

    @staticmethod
    def high_risk_condition_check(age, blood_pressure, conditions, high_risk_conditions):
        # Known heart disease, stroke, transient ischemic attack, DM, kidney disease (for assessment, if this has not
        #  been done)
        #  Pull this in from the configuration file
        # high_risk_conditions =
        # Return whether medical history contains any of these
        has_high_risk_condition = False
        result_code = ""

        for condition in conditions:
            if condition.upper() in high_risk_conditions:
                has_high_risk_condition = True
                result_code = "HR-0"
                # hrc_value = condition
            else:
                condition = None

        if not has_high_risk_condition:
            # check for other high risk states such as BP > 160 and age > 60 + diabetes (including newly suggested)
            # if (assessment[])
            # blood pressure [value, observation_type]
            sbp = blood_pressure['sbp'][0]
            dbp = blood_pressure['dbp'][0]

            if sbp > 200 or dbp > 120:
                # return True, "HRC-HTN", 'Severely high blood pressure. Seek emergency care immediately'
                # Very elevated
                has_high_risk_condition = True
                result_code = "HR-1"
            elif age < 40 and (sbp >= 140 or dbp >= 90):
                # High blood pressure in under 40, should be investigated for secondary hypertension
                result_code = "HR-2"

        hrc_output = {
            'status': has_high_risk_condition,
            'reason': condition,
            'code': result_code
        }

        return hrc_output

    @staticmethod
    def output_messages(section, code, output_level):
        # how do we check if this is already in memory?
        messages = SingHealth.load_messages()
        output = []

        # print("code = %s " % code)
        # output["key"] = str(code)

        if output_level == 0:
            output = messages[section][code]
        elif output_level == 1:
            output = messages[section][code][0:1]
        elif output_level == 2:
            output = messages[section][code][0:2]
        elif output_level == 3:
            output = messages[section][code][0:3]
        elif output_level == 4:
            output = messages[section][code][0:4]

        return output

    @staticmethod
    def calculate_lifestyle_assessment(params):
        output_level = 2
        ethnicities = ['malay', 'chinese', 'east-asian']

        '''
            For the Lifestyle Assessment we just want to calculate:
            params include:
                age, gender, ethnicity
                ht, wt, hip (optional), waist (optional)
                fruit, vege, carbos, protein, fats (optional)
                physical_activity
            Assess for risk factors:
                - Weight / Central Adiposity via BMI, WHR
                - Smoking and Alcohol
            Assess diet and return calorie goals
            Assess physical activity
            Generate recommendations based on the above
        '''

        demographics = params['body']['demographics']
        ethnicity = demographics['ethnicity']
        print('ethnicity is %s ' % ethnicity)

        # gender = demographics['gender']
        measurements = params['body']['measurements']
        # smoking = params['body']['smoking']
        # physical_activity = params['body']['physical_activity']
        # diet_history = params['body']['diet_history']

        if ethnicity in ethnicities:
            BMIA = SEABMIAssessment({'weight': measurements['weight'], 'height': measurements['height']})
        else:
            BMIA = BMIAssessment({'weight': measurements['weight'], 'height': measurements['height']})

        bmi = BMIA.assess()
        bmi['output'] = SingHealth.output_messages('anthro', bmi['code'], output_level)

    @staticmethod
    def calculate(params):
        assessment = {}
        output_level = 2

        print("in calculate")

        # load guidelines for SIMPLE algorithm model
        guidelines = SingHealth.load_guidelines('healthassessment')["body"]
        # Unpack some of the configurations
        # List of high risk conditions
        # Should also get the targets from here
        high_risk_conditions = guidelines["high_risk_conditions"]
        targets = guidelines["targets"]
        # print("targets = %s " % targets)

        # unpack the request, validate it and set up the params
        region = params['body']['region'] if 'region' in params['body'].keys() else Defaults.region
        demographics = params['body']['demographics']
        gender = demographics['gender']
        measurements = params['body']['measurements']
        smoking = params['body']['smoking']
        physical_activity = params['body']['physical_activity']
        diet_history = params['body']['diet_history']
        medical_history = params['body']['medical_history']
        pathology = params['body']['pathology']
        medications = params['body']['medications']

        BMIA = BMIAssessment({'weight': measurements['weight'], 'height': measurements['height']})
        bmi = BMIA.assess()
        bmi['output'] = SingHealth.output_messages('anthro', bmi['code'], output_level)

        WHRA = WHRAssessment(dict(waist=measurements['waist'], hip=measurements['hip'], gender=demographics['gender']))
        whr = WHRA.assess()
        whr['output'] = SingHealth.output_messages('anthro', whr['code'], output_level)

        SingHealth.calculate_lifestyle_assessment(params)
        SMA = SmokingAssessment({'smoking': smoking})
        smoker = SMA.assess()
        smoker['output'] = SingHealth.output_messages('smoking', smoker['code'], output_level)

        # assess diabetes status or risk
        DSA = DiabetesAssessment({
            'conditions': medical_history,
            'bsl_type': pathology['bsl']['type'],
            'bsl_units': pathology['bsl']['units'],
            'bsl_value': pathology['bsl']['value'],
        })
        diabetes_status = DSA.assess()

        # If does not have diabetes OR impaired status
        if not diabetes_status['status']:
            # calculate diabetes risk score
            diabetes_params = DiabetesParamsBuilder() \
                .gender(demographics['gender']) \
                .age(demographics['age']) \
                .waist(measurements['waist'][0]) \
                .hip(measurements['hip'][0]) \
                .height(measurements['height'][0]) \
                .weight(measurements['weight'][0]) \
                .sbp(measurements['sbp'][0]) \
                .dbp(measurements['dbp'][0]) \
                .build()
            diabetes_risk = Diabetes().calculate(diabetes_params)
            diabetes_status['risk'] = diabetes_risk['risk']
            diabetes_status['code'] = diabetes_risk['code']
        else:
            # newly diagnosed diabetes, add to existing conditions list
            conditions = medical_history['conditions']
            conditions.append('diabetes')
            medical_history['conditions'] = conditions
            diabetes_risk = None

        # unpack the messages
        # print("---- diabetes status = %s " % diabetes_status)
        diabetes_status["output"] = SingHealth.output_messages("diabetes", diabetes_status["code"], output_level)
        assessment['diabetes'] = diabetes_status

        blood_pressure = {
            'sbp': measurements['sbp'],
            'dbp': measurements['dbp']
        }

        BPA = BPAssessment({'bp': blood_pressure, 'conditions': medical_history['conditions']})
        bp_assessment = BPA.assess()
        assessment['blood_pressure'] = bp_assessment

        DTA = DietAssessment({'diet_history': diet_history, 'targets': targets})
        diet = DTA.assess()

        PAA = PhysicalActivityAssessment({
            'active_time': physical_activity,
            'targets_active_time': targets['general']['physical_activity']['active_time'],
        })
        exercise = PAA.assess()
        assessment['lifestyle'] = {
            'bmi': bmi,
            'whr': whr,
            'diet': diet,
            'exercise': exercise,
            'smoking': smoker,
        }

        age = demographics['age']
        # work out how to add in diabetes if newly diagnosed?
        has_high_risk_condition = SingHealth.high_risk_condition_check(
            demographics['age'], blood_pressure, medical_history['conditions'], high_risk_conditions
        )

        assessment['cvd_assessment'] = {
            'high_risk_condition': has_high_risk_condition
        }

        # Determine whether eligible for CVD risk assessment
        estimate_cvd_risk_calc = SingHealth().estimate_cvd_risk(age, has_high_risk_condition)
        # if not high_risk_condition[0]:
        if estimate_cvd_risk_calc[0]:
            # check if on bp_medications
            print('performing cvd risk check')
            on_bp_meds = SingHealth.check_medications('anti_hypertensive', medications)
            # print("\n--- on bp meds %s " % on_bp_meds)
            # params = FPB().gender("M").age(45).t_chol(170, 'mg/dl').hdl_chol(45, 'mg/dl').sbp(125)
            # .smoker(False).diabetic(False).bp_medication(True).build()
            cvd_params = SGFPB() \
                .gender(gender) \
                .age(age) \
                .t_chol(pathology['cholesterol']['total_chol'], pathology['cholesterol']['units']) \
                .hdl_chol(pathology['cholesterol']['hdl'], pathology['cholesterol']['units']) \
                .sbp(blood_pressure['sbp'][0]) \
                .bp_medication(on_bp_meds) \
                .smoker(smoker['smoking_calc']) \
                .diabetic(diabetes_status['status']) \
                .build()
            # print("\n---\n cvd assessment \n")
            fre_result = SGFRE().calculate(cvd_params)
            print("\n---\nFRE result %s " % fre_result)
            # print("\n---\n")

            # use the key to look up the guidelines output
            assessment['cvd_assessment']['cvd_risk_result'] = fre_result
            # assessment['cvd_assessment']['guidelines'] = guidelines['cvd_risk'][fre_result['risk_range']]

        else:
            # cvd_calc = estimate_cvd_risk_calc[1]
            assessment['cvd_assessment']['guidelines'] = guidelines['cvd_risk']['refer']

        return assessment

    @staticmethod
    def get_messages():
        return SingHealth.load_messages()

    @staticmethod
    def get_sample_params():
        return dict(
            request=dict(
                api_key="API_KEY",
                api_secret="API_SECRET",
                request_api="https://developers.openhealthalgorithms.org/algos/hearts/",
                country_code="D",
                response_type="COMPLETE"
            ),
            body=dict(
                last_assessment=dict(assessment_date="", cvd_risk="20"),
                demographics=dict(
                    gender="F", age=50, dob=["computed", "01/10/1987"], occupation="office_worker",
                    monthly_income="", ethnicity='caucasian'
                ),
                measurements=dict(
                    height=[1.5, "m"], weight=[70.0, "kg"], waist=[99.0, "cm"],
                    hip=[104.0, "cm"], sbp=[145, "sitting"], dbp=[91, "sitting"]
                ),
                smoking=dict(current=0, ex_smoker=1, quit_within_year=0),
                physical_activity="120",
                diet_history=dict(fruit=1, veg=6, rice=2, oil="olive"),
                medical_history=dict(conditions=["asthma", "tuberculosis"]),
                allergies={},
                medications=["anti_hypertensive", "statin", "antiplatelet", "bronchodilator"],
                family_history=["cvd"],
                pathology=dict(
                    bsl=dict(type="random", units="mg/dl", value=180),
                    cholesterol=dict(type="fasting", units="mg/dl", total_chol=320, hdl=100, ldl=240)
                )
            )
        )
