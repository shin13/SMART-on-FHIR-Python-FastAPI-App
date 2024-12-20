import os
import sys
import logging
import typing
import uuid
import uvicorn
import json
import requests
import httpx
import asyncio
from icecream import ic

from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from oauthlib.oauth2 import WebApplicationClient

from app.configs.config import basicSettings, credentialSettings
from app.routers.v1.base import router_v1
from app.routers.v1.endpoints.get_patients import extract_patient_info
from app.routers.v1.endpoints.get_observations import extract_height, extract_weight, extract_bmi, extract_bp, extract_hdl, extract_ldl, extract_tg, extract_chol, extract_scr, extract_glucose, extract_smoking_status
from app.routers.v1.endpoints.get_calculations import get_ibw_abw, get_crcl, get_ost_index, get_mets_ir, _calculate_ln_values, _get_mean_coefficient_value, _get_baseline_survival, _determine_population_group, _calculate_ascvd_risk
from app.middleware.exception import exception_message


sys.path.append("./")

app = FastAPI(
    version=basicSettings.VERSION,
    title="Smart on FHIR App"
)

client = WebApplicationClient(credentialSettings.CLIENT_ID)
cookie = {}

uvicorn_logger = logging.getLogger('uvicorn.error')
system_logger = logging.getLogger('custom.error')

app.include_router(router_v1, prefix=basicSettings.API_PREFIX)

origins = ["http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# 啟用靜態文件
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def app_context(request: Request) -> typing.Dict[str, typing.Any]:
    return {'app': request.app}

templates = Jinja2Templates(
    directory='templates', context_processors=[app_context]
)

# 靜態文件配置
@app.get("/templates/{filename:path}")
async def serve_static(filename: str):
    return RedirectResponse(url=f"/templates/{filename}")


### 1. 啟動應用的端點
@app.get("/")
@app.post("/")
@app.get("/index.html")
@app.post("/index.html")
async def index(launch: str = "", iss: str = ""):
    if iss != credentialSettings.BASE_URL:
        raise HTTPException(status_code=400, detail=f"ISS link is {iss}, but the app's registered link is {credentialSettings.BASE_URL}")
    ic(launch)
    ic(iss)
    ic(cookie)
    cookie["launch_token"] = launch
    ic(launch)
    ic(iss)
    ic(cookie)
    return RedirectResponse(url="/authorize")  # 重定向到授權端點


### 2. Retrieve metadata or SMART configuration
# https://hl7.org/fhir/smart-app-launch/app-launch.html#retrieve-well-knownsmart-configuration
# https://fhir.epic.com/Documentation?docId=oauth2&section=Embedded-Oauth2-Launch_Conformance-Statement
smart_config_url = f"{credentialSettings.BASE_URL}/.well-known/smart-configuration"
response = requests.get(smart_config_url, headers={"Accept": "application/fhir+json"}).json()
authorization_uri = response["authorization_endpoint"]
token_uri = response["token_endpoint"]


### 3. Obtain Authorization Code
# https://hl7.org/fhir/smart-app-launch/app-launch.html#obtain-authorization-code
# https://fhir.epic.com/Documentation?docId=oauth2&section=Standalone-Oauth2-Launch_Request_Auth_Code
@app.get("/authorize")
async def authorization():
    cookie["state"] = uuid.uuid4().hex
    auth_url = client.prepare_request_uri(
    uri=authorization_uri,
    redirect_uri=credentialSettings.REDIRECT_URI,
    launch=cookie["launch_token"],  # Necessary for EHR launch
    scope=credentialSettings.SCOPES,
    state=cookie["state"],
    aud=credentialSettings.BASE_URL,  # This is a key difference between OAuth 2.0 and SMART on FHIR
    )

    return RedirectResponse(url=auth_url)  # 重定向到授權伺服器


### 4. Obtain Access Token
# https://hl7.org/fhir/smart-app-launch/app-launch.html#obtain-access-token
# https://fhir.epic.com/Documentation?docId=oauth2&section=Standalone-Oauth2-Launch_Access-Token-Request
# Note: This implementation does not use a client secret, so this is a "public client"
@app.post("/fhir-app/")
@app.get("/fhir-app/")
async def callback(request: Request):
    """
    This method will handle the callback from the authorization server.
    It will then request an access token from the token server.
    """

    try:
        # 檢查狀態
        state = request.query_params.get("state")
        if state != cookie.get("state"):
            raise HTTPException(status_code=400, detail="Invalid state parameter.")

        async with httpx.AsyncClient() as asynclient:
            token_response = await asynclient.post(token_uri, data={
                'grant_type': 'authorization_code',
                'code': request.query_params.get("code"),
                "authorization_response": request.url,
                'redirect_uri': credentialSettings.REDIRECT_URI,
                "include_client_id": True,  # This is another SMART-specific aspect, in case of a public client
            })
            token_response.raise_for_status()

            cookie["token"] = token_response.json()

            # Add token to the client object so that it can be used later
            client.parse_request_body_response(json.dumps(token_response.json()))

            return RedirectResponse(url="/render_data")  # 重定向到數據渲染端點

    except Exception as e:
        return {"error": f"An error occurred when obtaining an access token: {e}"}


@app.get("/get_records", response_model=dict)
async def get_records(request: Request):

    tokens = cookie.get("token")

    # 確保 token 是有效的
    if not tokens:
        raise HTTPException(status_code=401, detail="User not authenticated")

    patient_token = tokens['patient']

    try:
        patient_json = await get_fhir_json(patient_token, "Patient")
        patient_result = await extract_patient_info(patient_json)

        first_name = patient_result[0]
        last_name = patient_result[1]
        dob = patient_result[2]
        age = patient_result[3]
        gender = patient_result[4]
        race = patient_result[5]
        ethnicity = patient_result[6]

        # Make concurrent requests to gather data
        tasks = [
            get_fhir_json(patient_token, "Observation", category="vital-signs", code="8302-2"),  # height 0
            get_fhir_json(patient_token, "Observation", category="vital-signs", code="29463-7"),  # weight 1
            get_fhir_json(patient_token, "Observation", category="vital-signs", code="39156-5"),  # BMI 2
            get_fhir_json(patient_token, "Observation", category="vital-signs", code="55284-4"),  # BP 3
            get_fhir_json(patient_token, "Observation", category="laboratory", code="2085-9"),  # HDL 4
            get_fhir_json(patient_token, "Observation", category="laboratory", code="18262-6"),  # LDL 5
            get_fhir_json(patient_token, "Observation", category="laboratory", code="2571-8"),  # triglyceride 6
            get_fhir_json(patient_token, "Observation", category="laboratory", code="2093-3"),  # cholesterol 7
            get_fhir_json(patient_token, "Observation", category="laboratory", code="38483-4"),  # serum creatinine 8
            get_fhir_json(patient_token, "Observation", category="laboratory", code="2339-0"),  # blood glucose 9
            get_fhir_json(patient_token, "Observation", category="survey", code="72166-2"),  # smoking satus 10
        ]

        # Wait for the tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 检查是否有异常发生
        for result in results:
            if isinstance(result, Exception):
                raise HTTPException(status_code=500, detail="Error fetching data")  # 可根据需要处理异常

        height = await extract_height(results[0])
        weight = await extract_weight(results[1])
        bmi = await extract_bmi(results[2])
        sbp, dbp = await extract_bp(results[3])
        hdl = await extract_hdl (results[4])
        ldl = await extract_ldl (results[5])
        tg = await extract_tg (results[6])
        chol = await extract_chol (results[7])
        scr = await extract_scr (results[8])
        glucose = await extract_glucose (results[9])
        smoking = await extract_smoking_status (results[10])

    except Exception as e:
            return {"error": f"An error occurred when obtaining data for rendering: {exception_message(e)}"}
    
    try:
        records = {
            "Name": f"{first_name} {last_name}",
            "Gender": gender,
            "Race": race,
            "Ethnicity": ethnicity,
            "Date of Birth": dob,
            "Age": age,
            "Height": height,
            "Weight": weight,
            "BMI": bmi,
            "Systolic BP": dbp,
            "Diastolic BP": sbp,
            "HDL": hdl,
            "LDL": ldl,
            "Triglycerides": tg, 
            "Cholesterol": chol,
            "Creatinine": scr,
            "Glucose (blood sugar)": glucose,
            "Tobacco Smoking Status": smoking,
        }

        return records  # Return the records as JSON response

    except Exception as e:
        return {"error": f"An error occurred when obtaining records: {exception_message(e)}"}


@app.get("/get_calculations", response_model=dict)
async def get_calculations(request: Request):
    try:
        records_response = await get_records(request)

        if "error" in records_response:
            return templates.TemplateResponse("error.html", {"request": request, "error": records_response["error"]})

        records = records_response  # Extract the records for rendering

    except Exception as e:
        return {"error": f"An error occurred when obtaining records: {exception_message(e)}"}
    
    try:
        # Extract necessary fields from records
        gender = records["Gender"]
        height = records["Height"]  
        weight = records["Weight"]
        age = records["Age"]
        scr = records.get("Creatinine")
        glucose = records.get("Glucose (blood sugar)")
        tg = records.get("Triglycerides")
        hdl = records.get("HDL")

        # Get calculation output
        ibw = get_ibw_abw(gender, height, weight)[0]
        abw = get_ibw_abw(gender, height, weight)[1]
        actual_clcr = get_crcl(age, weight, gender, height, scr)[0]
        adjusted_clcr = get_crcl(age, weight, gender, height, scr)[1] + "  " + get_crcl(age, weight, gender, height, scr)[3]
        ost_risk = get_ost_index(weight, age, gender)[1]
        ost_index = get_ost_index(weight, age, gender)[0]
        t2d_risk = get_mets_ir(glucose, tg, weight, height, hdl)[1]
        mets_ir = get_mets_ir(glucose, tg, weight, height, hdl)[0]

        calculations = {
            "Ideal Body Weight (IBW)": ibw,
            "Adjusted Body Weight (ABW)": abw,
            "Creatinine Clearance": actual_clcr,
            "Creatinine Clearance (adjusted)": adjusted_clcr,
            "Osteoporosis Risk": ost_risk,
            "OST Index": ost_index,
            "Risk of Developing T2D (METS-IR)": t2d_risk,
            "METS-IR Value (Metabolic Score for Insulin Resistance)": mets_ir,
        }

        return calculations
    
    except Exception as e:
        return {"error": f"An error occurred when generating calculations: {exception_message(e)}"}


### 5. 完成授權流程、渲染資料
@app.get("/render_data", response_class=HTMLResponse)
async def render_data(request: Request):

    # Fetch the records using the get_records function
    records_response = await get_records(request)

    if "error" in records_response:
        return templates.TemplateResponse("error.html", {"request": request, "error": records_response["error"]})

    records = records_response

    # Fetch the calculations using the get_calculations function
    calculations_response = await get_calculations(request)

    if "error" in calculations_response:
        return templates.TemplateResponse("error.html", {"request": request, "error": calculations_response["error"]})

    calculations = calculations_response

    ic(records)
    ic(calculations)
    output = templates.TemplateResponse(name="render_data.html", context={"request": request, "data": records, "calc_data": calculations})

    return output


## [GET]: Get fhir json
@app.get("/fhir-json", tags=["Get FHIR Json"])
async def get_fhir_json(patient_token, resource_type, category=None, code=None) -> dict:
    """
     獲取 FHIR JSON 資源。

    此函數用於從 FHIR 服務器獲取特定的資源數據。它支持獲取 Patient 和 Observation 資源。

    參數:
    patient_token (str): 患者的認證令牌，例如 'bc6c8e2a-63de-4790-94af-fcab57874c21'。
    resource_type (str): FHIR 資源類型，目前只支援 'Patient' 或 'Observation'。
    category (str, optional): 觀察類別，例如 'vital-signs', 'laboratory' 或 'survey'。僅用於 Observation 資源。
    code (str, optional): 觀察的具體代碼，例如 '8302-2' 表示身高。僅用於 Observation 資源。

    返回:
    dict: 包含請求的 FHIR 資源的 JSON 數據。

    raises:
    ValueError: 如果參數無效或使用不當。
    HTTPException: 如果 API 請求失敗。
    Exception: 如果在獲取數據過程中發生其他錯誤。

    用法示例:
    fhir_json = await get_fhir_json(patient_token, "Patient")
    fhir_json = await get_fhir_json(patient_token, "Observation", "vital-signs", "8302-2")
    """
    if not patient_token:
        raise ValueError("patient_token cannot be empty")

    if resource_type not in ["Patient", "Observation"]:
        raise ValueError("resource_type must be either 'Patient' or 'Observation'")

    base_url = f"{credentialSettings.BASE_URL}/{resource_type}"
    ic(base_url)

    if resource_type == 'Observation':
        if not category and not code:
            raise ValueError("For Observation, at least one of category or code must be provided")

        params = [f"patient={patient_token}"]
        ic("ORIGINAL PARAMS", params)

        if category:
            params.append(f"category={category}")
        if code:
            params.append(f"code={code}")
        
        ic("MODIFIED PARAMS", params)

        query_string = "&".join(params) 
        ic(query_string)

        full_url = f"{base_url}?{query_string}"
    
    elif resource_type == 'Patient':
        full_url = f"{base_url}/{patient_token}"
    
    ic(full_url)

    # 添加認證令牌
    try:
        uri, headers, _ = client.add_token(
            full_url,
            headers={"Accept": "application/fhir+json"}
        )
    except Exception as e:
        ic(f"Error adding token: {exception_message(e)}")
        raise

    # 發送 HTTP 請求並獲取數據
    try:
        ic("Sending HTTP request")
        # Getting data in the way prescribed by OAuthLib package
        async with httpx.AsyncClient() as asynclient:
            # response = await asynclient.get(uri, headers=headers, data=body, timeout=10)
            response = await asynclient.get(uri, headers=headers, timeout=10)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to load patient data.")
            ic(f"Response status code: {response.status_code}")

            fhir_json = response.json()

        ic("FHIR JSON received")
        ic(fhir_json)

    except httpx.RequestError as e:
        system_logger.error(f"HTTP request failed: {exception_message(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to FHIR server: {exception_message(e)}")
    except httpx.TimeoutException:
        system_logger.error("Request to FHIR server timed out")
        raise HTTPException(status_code=504, detail="Request to FHIR server timed out")
    except json.JSONDecodeError as e:
        system_logger.error(f"Failed to decode JSON response: {exception_message(e)}")
        raise HTTPException(status_code=500, detail="Received invalid JSON from FHIR server")
    except Exception as e:
        system_logger.error(f"An unexpected error occurred: {exception_message(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exception_message(e)}")

    return fhir_json


from pydantic import BaseModel

class UserRiskInput(BaseModel):
    hasDiabetes: bool = False
    isSmoking: bool = False
    isTreatingHypertension: bool = False
    

#### 路由
## [POST] : ascvd 2013 risk
@app.post("/calculate_ascvd_risk", name="Get ASCVD 2013 Risk", description="Get ASCVD 2013 Risk in a dictionary: {'result': risk_result}")
async def calculate_ascvd_risk(request: Request, user_input: UserRiskInput):

    ic(request)
    ic(user_input)

    try:
        has_diabetes = user_input.hasDiabetes
        is_smoking = user_input.isSmoking
        is_treating_htn = user_input.isTreatingHypertension


        # 確認這些變數的類型是否正確
        if not isinstance(has_diabetes, bool) or not isinstance(is_smoking, bool) or not isinstance(is_treating_htn, bool):
            return jsonable_encoder({"error": "Invalid input data types for user risk factors."}), 400
            
        try:
            # 取得用戶的健康記錄 (可從 get_records 函數中獲得)
            records = await get_records(request)

            # 提取數據
            race = records.get("Race", "").strip()
            gender = records.get("Gender", "").strip()
            age = records.get("Age", 0)
            cholesterol = float(records.get("Cholesterol", "0").split(" ")[0])
            hdl = float(records.get("HDL", "0").split(" ")[0])
            sbp = float(records.get("Systolic BP", "0").split(" ")[0])

            # 計算 ASCVD 風險百分比
            group = _determine_population_group(race, gender)
            ln_values = _calculate_ln_values(race, gender, age, cholesterol, hdl, sbp, has_diabetes, is_smoking, is_treating_htn)
            value_sum = round(sum(ln_values.values()), 2)
            mean_coefficient_value = _get_mean_coefficient_value(group)
            baseline_survival = _get_baseline_survival(group)
            
            if mean_coefficient_value is None or baseline_survival is None:
                return {"error": "Unable to determine population group or retrieve coefficients."}, 500

            risk_percentage = _calculate_ascvd_risk(value_sum, mean_coefficient_value, baseline_survival)
            
            # 生成風險回應文本
            if risk_percentage is not None:
                risk_result = f"Risk of cardiovascular event (coronary or stroke death or non-fatal MI or stroke) in next 10 years: {risk_percentage:.1f}%"
            else:
                risk_result = "Unable to determine the risk of cardiovascular event in next 10 years."
            
            ic(risk_result)

            return jsonable_encoder({"result": risk_result})

        except Exception as e:
            # 如果在處理 JSON 請求或計算中出現錯誤，將錯誤訊息回傳給前端
            system_logger.error(f"Error during risk calculation: {exception_message(e)}")
            return jsonable_encoder({"error": f"Error during risk calculation: {exception_message(e)}"}), 500

    except Exception as e:
        # 如果在獲取記錄或健康數據時出現錯誤，回傳錯誤訊息
        return jsonable_encoder({"error": f"Server error: {exception_message(e)}"}), 500
    

if __name__ == "__main__":

    # import os
    # import logging
    
    # # This creates a secret key (needed for session to work)
    # app.secret_key = os.urandom(24)

    # # This is to allow for endpoints to be http instead of https
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # logging.basicConfig(level=logging.DEBUG)

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=4201,
        workers=5,
        reload=True,
    )