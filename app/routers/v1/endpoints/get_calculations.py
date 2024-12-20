import math
from fastapi import APIRouter, Request, HTTPException
from app.configs.reference import COEFFICIENTS, population_data
from app.middleware.exception import exception_message
import logging


router = APIRouter()

uvicorn_logger = logging.getLogger('uvicorn.error')
system_logger = logging.getLogger('custom.error')


def get_ibw_abw(gender, height, weight):
    try:
        value = float(height.split(" ")[0])
        ht_unit = str(height.split(" ")[1])

        if ht_unit == "cm":
            # Convert height from cm to inches
            ht = value / 2.54

        elif ht_unit == "in":
            ht = value
        
        else:
            ht = value

        # Calculate IBW based on gender
        if gender.lower() == 'male':
            ibw = 50 + 2.3 * max(0, ht - 60)  # 5 feet = 60 inches
            
        elif gender.lower() == 'female':
            ibw = 45.5 + 2.3 * max(0, ht - 60)
            
        else:
            raise ValueError("Gender must be 'male' or 'female'.")
        
        # Calculate ABW based on weight
        wt_value = float(weight.split(" ")[0])
        wt_unit = str(weight.split(" ")[1])

        if wt_value > ibw: 
            abw = ibw + 0.4 * (wt_value - ibw)
            abw = str(wt_value) + " " + wt_unit

        else:
            # If actual weight is not greater than IBW
            abw = weight
        
        ibw = str(round(ibw,1)) + " " + wt_unit

    except:
        ibw = "Not available due to missing required data"
        abw = "Not available due to missing required data"

    return ibw, abw


def get_crcl(age, weight, gender, height, creatinine):

    try:
        wt = float(weight.split(" ")[0])
        ht = float(height.split(" ")[0])
        cr = float(creatinine.split(" ")[0])


        # Calculate BMI
        ht = ht / 100
        bmi = wt / (ht ** 2)

        # Calculate CrCl using actual weight
        actual_crcl = (140 - age) * wt * (0.85 if gender.lower() == 'female' else 1) / (72 * cr)

        # Determine which weight to use for the adjusted CrCl calculation
        ibw = float(get_ibw_abw(gender, height, weight)[0].split(" ")[0])
        abw = float(get_ibw_abw(gender, height, weight)[1].split(" ")[0])

        if bmi < 18.5:  # Underweight
            abw = wt
            bmi_category = "Underweight"
            method = "actual weight"
            
        elif 18.5 <= bmi < 25:  # Normal weight
            abw = ibw
            bmi_category = "Normal weight"
            method = "ideal body weight"
            
        else:  # Overweight/Obese
            abw = ibw + 0.4 * (wt - ibw)
            bmi_category = "Overweight / obese"
            method = "adjusted body weight"

        # Calculate CrCl using adjusted weight
        adjusted_crcl = (140 - age) * abw * (0.85 if gender.lower() == 'female' else 1) / (72 * cr)
        
        # Format Output
        unit = "mg/mL"
        actual_crcl = str(round(actual_crcl,2)) + " " + unit
        adjusted_crcl = str(round(adjusted_crcl, 2))  + " " + unit

    except:
        actual_crcl = "Not available due to missing required data"
        adjusted_crcl = "Not available due to missing required data"
        bmi_category = ""
        method = ""

    return actual_crcl, adjusted_crcl, bmi_category, method


def get_ost_index(weight, age, gender):
    try:
        wt = float(weight.split(" ")[0])
        age = float(age)

        # Calculate OST Index, truncated to integer
        ost_index = int((wt - age) * 0.2)

        # Determine risk based on gender-specific criteria
        if gender.lower() == 'female':
            risk = "Low" if ost_index > 1 else "Intermediate" if -3 <= ost_index <= 1 else "High"
        elif gender.lower() == 'male':
            risk = "Low" if ost_index > 3 else "Intermediate" if -1 <= ost_index <= 3 else "High"
        else:
            raise ValueError("Invalid gender. Please specify 'female' or 'male'.")
        
        ost_index = str(ost_index) + " points"
    
    except:
        ost_index = "Not available due to missing required data"
        risk = "Not available due to missing required data"

    return ost_index, risk


def get_mets_ir(glucose, tg, weight, height, hdl):
    """
    Calculate the METS-IR using the given formula, directly using weight and height to compute BMI,
    and provide an interpretation based on the METS-IR value.

    Parameters:
    glucose (float): Fasting glucose in mg/dL
    triglycerides (float): Triglyceride concentration in mg/dL
    weight (float): Weight in kilograms
    height (float): Height in centimeters
    hdl_cholesterol (float): High-density lipoprotein cholesterol in mg/dL

    Returns:
    tuple: The METS-IR value and its interpretation regarding T2D risk
    """
    try:
        wt = float(weight.split(" ")[0])
        ht = float(height.split(" ")[0])
        tg = float(tg.split(" ")[0])
        hdl = float(hdl.split(" ")[0])
        glucose = float(glucose.split(" ")[0])

        # Calculate BMI
        bmi = wt / ((ht / 100) ** 2)

        numerator = math.log((2 * glucose) + tg) * bmi
        denominator = math.log(hdl)

        mets_ir = numerator / denominator

        # Interpretation based on METS-IR value
        if mets_ir <= 50.39:
            risk_interpretation = "Low"
        else:
            risk_interpretation = "High"
        
        mets_ir = str(int(mets_ir))
    
    except:
        mets_ir = "Not available due to missing required data"
        risk_interpretation = "Not available due to missing required data"

    return mets_ir, risk_interpretation


def _determine_population_group(race: str, gender: str) -> str:
    """
    Determine the population group based on race and gender.
    Returns:
        str or None: The population group, or None if the race or gender cannot be determined.
    """
    is_african = False
    is_female = False

    # Determine race
    if "black" in race.lower():
        is_african = True
    elif "white" in race.lower():
        is_african = False
    else:
        is_african = False

    # Determine gender
    if gender.lower() == "female":
        is_female = True
    elif gender.lower() == "male":
        is_female = False
    else:
        print("Cannot determine gender")
        return None

    # Map the race and gender to a population group
    population_groups = {
        (False, True): "White & Women",
        (False, False): "White & Men",
        (True, True): "African American & Women",
        (True, False): "African American & Men"
    }
    group = population_groups.get((is_african, is_female))

    return group


def _calculate_ln_values(race: str, gender: str, age: int, cholesterol, hdl, sbp, has_diabetes, is_smoking , is_treating_htn):

    group = _determine_population_group(race, gender)
    
    coefficients = COEFFICIENTS.get(group)

    ln_age = math.log(age)
    ln_cholesterol = math.log(cholesterol)
    ln_hdl = math.log(hdl)
    ln_sbp = math.log(sbp)

    # Calculate each value
    value1 = coefficients['Ln Age (y)'] * ln_age
    
    if coefficients.get('Ln Age, Squared') is not None:
        value2 = coefficients.get('Ln Age, Squared', 0) * (ln_age ** 2)
    else:
        value2 = 0
    value3 = coefficients['Ln Total Cholesterol (mg/dL)'] * ln_cholesterol

    if coefficients.get('Ln Age x Ln Total Cholesterol') is not None:
        value4 = coefficients['Ln Age x Ln Total Cholesterol'] * (ln_age * ln_cholesterol)
    else:
        value4 = 0

    value5 = coefficients['Ln HDL-C (mg/dL)'] * ln_hdl

    if coefficients.get('Ln Age x Ln HDL-C') is not None:
        value6 = coefficients['Ln Age x Ln HDL-C'] * (ln_age * ln_hdl)
    else:
        value6 = 0

    if is_treating_htn:
        value7 = coefficients['Ln Treated Systolic BP (mmHg)'] * ln_sbp
        value8 = coefficients.get('Ln Age x Ln Treated Systolic BP', 0) * (ln_age * ln_sbp)
    else:
        value7 = coefficients['Ln Untreated Systolic BP (mmHg)'] * ln_sbp
        value8 = coefficients.get('Ln Age x Ln Untreated Systolic BP', 0) * (ln_age * ln_sbp)

    value9 = coefficients['Current Smoker (1=Yes, 0=No)'] * (1 if is_smoking else 0)

    if coefficients.get('Ln Age x Current Smoker') is not None:
        value10 = coefficients['Ln Age x Current Smoker'] * (ln_age * (1 if is_smoking else 0))
    else:
        value10 = 0

    value11 = coefficients['Diabetes (1=Yes, 0=No)'] * (1 if has_diabetes else 0)
    
    return {
        "value1": value1,
        "value2": value2,
        "value3": value3,
        "value4": value4,
        "value5": value5,
        "value6": value6,
        "value7": value7,
        "value8": value8,
        "value9": value9,
        "value10": value10,
        "value11": value11
    }


def _get_mean_coefficient_value(group):
    group_data = population_data.get(group)
    if group_data:
        mean_coefficient_value = group_data["mean_coefficient_value"]
        return mean_coefficient_value
    else:
        return None

    
def _get_baseline_survival(group):
    group_data = population_data.get(group)
    if group_data:     
        baseline_survival = group_data["baseline_survival"]
        return baseline_survival
    else:
        return None
    

def _calculate_ascvd_risk(value_sum: float, mean_coefficient_value: float, baseline_survival: float) -> float:
    """
    Calculates the 10-year risk of a first hard ASCVD event.

    Args:
        individual_sum: The sum of "Coefficient x Value" for the individual.
        mean_coefficient_value: The mean of "Coefficient x Value" for the race and sex group.
        baseline_survival: The baseline survival rate at 10 years.
    Returns:
        The 10-year risk of a first hard ASCVD event as a percentage, or None if
        input is invalid.
    """
    exponent = value_sum - mean_coefficient_value
    
    risk = 1 - (baseline_survival ** math.exp(exponent))
    
    return risk * 100  # Convert to percentage