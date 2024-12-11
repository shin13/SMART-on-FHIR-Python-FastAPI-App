import requests
import uvicorn
import httpx
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from oauthlib.oauth2 import WebApplicationClient

from app.configs.config import basicSettings, credentialSettings
from app.routers.v1.base import router_v1
from app.middleware.exception import exception_message


app = FastAPI(
    version=basicSettings.VERSION,
    titie="Smart on FHIR App"
)

client = WebApplicationClient(credentialSettings.CLIENT_ID)
cookie = {}

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
templates = Jinja2Templates(directory="templates")

# 靜態文件配置
@app.get("/templates/{filename:path}")
async def serve_static(filename: str):
    return RedirectResponse(url=f"/templates/{filename}")


### 1. 啟動應用的端點
@app.get("/")
@app.post("/")
async def index(launch: str = "", iss: str = ""):
    if iss != credentialSettings.BASE_URL:
        raise HTTPException(status_code=400, detail=f"ISS link is {iss}, but the app's registered link is {credentialSettings.BASE_URL}")

    cookie["launch_token"] = launch
    return RedirectResponse(url="/authorize")  # 重定向到授權端點


### 2. Retrieve metadata or SMART configuration
# https://hl7.org/fhir/smart-app-launch/app-launch.html#retrieve-well-knownsmart-configuration
# https://fhir.epic.com/Documentation?docId=oauth2&section=Embedded-Oauth2-Launch_Conformance-Statement
smart_config_url = f"{credentialSettings.BASE_URL}/.well-known/smart-configuration"
response = requests.get(smart_config_url, headers={"Accept": "application/fhir+json"}).json()
authorization_uri = response["authorization_endpoint"]
token_uri = response["token_endpoint"]


### 3. 授權端點
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


### 4. 回調端點
# https://hl7.org/fhir/smart-app-launch/app-launch.html#obtain-access-token
# https://fhir.epic.com/Documentation?docId=oauth2&section=Standalone-Oauth2-Launch_Access-Token-Request
# Note: This implementation does not use a client secret, so this is a "public client"
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

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_uri, data={
                'grant_type': 'authorization_code',
                'code': request.query_params.get("code"),
                "authorization_response": request.url,
                'redirect_uri': credentialSettings.REDIRECT_URI,
                'client_id': credentialSettings.CLIENT_ID,
                "include_client_id": True,  # This is another SMART-specific aspect, in case of a public client
            })
            token_response.raise_for_status()
            cookie["token"] = token_response.json()
            tokens = cookie["token"]

            print("TOKENS: ")
            print(tokens)

            return RedirectResponse(url="/render_data")  # 重定向到數據渲染端點

    except Exception as e:
        return {"error": f"An error occurred when obtaining an access token: {e}"}

### 5. 完成授權流程
@app.get("/render_data", response_class=HTMLResponse)
async def render_data(request: Request):
    # 中略過數據提取邏輯，假設我們已經獲取了某些數據
    sample_data = {
        "Name": "John Doe",
        "Gender": "Male",
        "Height": "180 cm",
        "Weight": "75 kg",
        "BMI": "23.1",
    }

    # 使用 Jinja2 渲染模板
    return templates.TemplateResponse("render_data.html", {"request": request, "data": sample_data})


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=4201,
        workers=5,
        reload=True,
    )