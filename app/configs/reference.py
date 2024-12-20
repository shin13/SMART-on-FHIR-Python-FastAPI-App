### 6. Calculate ASCVD Risk Using User's Input
# 定義人群類別與每項變因的計算常數
COEFFICIENTS = {
    "White & Women": {
        "Ln Age (y)": -29.799,
        "Ln Age, Squared": 4.884,
        "Ln Total Cholesterol (mg/dL)": 13.540,
        "Ln Age x Ln Total Cholesterol": -3.114,
        "Ln HDL-C (mg/dL)": -13.578,
        "Ln Age x Ln HDL-C": 3.149,
        "Ln Treated Systolic BP (mmHg)": 2.019,
        "Ln Age x Ln Treated Systolic BP": 0,
        "Ln Untreated Systolic BP (mmHg)": 1.957,
        "Ln Age x Ln Untreated Systolic BP": 0,
        "Current Smoker (1=Yes, 0=No)": 7.574,
        "Ln Age x Current Smoker": -1.665,
        "Diabetes (1=Yes, 0=No)": 0.661,
    },
    "White & Men": {
        "Ln Age (y)": 12.344,
        "Ln Age, Squared": 0,
        "Ln Total Cholesterol (mg/dL)": 11.853,
        "Ln Age x Ln Total Cholesterol": -2.664,
        "Ln HDL-C (mg/dL)": -7.990,
        "Ln Age x Ln HDL-C": 1.769,
        "Ln Treated Systolic BP (mmHg)": 1.797,
        "Ln Age x Ln Treated Systolic BP": 0,
        "Ln Untreated Systolic BP (mmHg)": 1.764,
        "Ln Age x Ln Untreated Systolic BP": 0,
        "Current Smoker (1=Yes, 0=No)": 7.837,
        "Ln Age x Current Smoker": -1.795,
        "Diabetes (1=Yes, 0=No)": 0.658,
    },
    "African American & Women": {
        "Ln Age (y)": 17.114,
        "Ln Age, Squared": 0,
        "Ln Total Cholesterol (mg/dL)": 0.940,
        "Ln Age x Ln Total Cholesterol": 0,
        "Ln HDL-C (mg/dL)": -18.920,
        "Ln Age x Ln HDL-C": 4.475,
        "Ln Treated Systolic BP (mmHg)": 29.291,
        "Ln Age x Ln Treated Systolic BP": -6.432,
        "Ln Untreated Systolic BP (mmHg)": 27.820,
        "Ln Age x Ln Untreated Systolic BP": -6.087,
        "Current Smoker (1=Yes, 0=No)": 0.691,
        "Ln Age x Current Smoker": 0,
        "Diabetes (1=Yes, 0=No)": 0.874,
    },
    "African American & Men": {
        "Ln Age (y)": 2.469,
        "Ln Age, Squared": 0,
        "Ln Total Cholesterol (mg/dL)": 0.302,
        "Ln Age x Ln Total Cholesterol": 0,
        "Ln HDL-C (mg/dL)": -0.307,
        "Ln Age x Ln HDL-C": 0,
        "Ln Treated Systolic BP (mmHg)": 1.916,
        "Ln Age x Ln Treated Systolic BP": 0,
        "Ln Untreated Systolic BP (mmHg)": 1.809,
        "Ln Age x Ln Untreated Systolic BP": 0,
        "Current Smoker (1=Yes, 0=No)": 0.549,
        "Ln Age x Current Smoker": 0,
        "Diabetes (1=Yes, 0=No)": 0.645,
    },
}

# 定義人群類別與對照表的關係
population_data = {
    "White & Women": {
        "mean_coefficient_value": -29.18,
        "baseline_survival": 0.9665
    },
    "White & Men": {
        "mean_coefficient_value": 61.18,
        "baseline_survival": 0.9144
    },
    "African American & Women": {
        "mean_coefficient_value": 86.61,
        "baseline_survival": 0.9533
    },
    "African American & Men": {
        "mean_coefficient_value": 19.54,
        "baseline_survival": 0.8954
    }
}