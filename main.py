import os
import json
import logging
from datetime import datetime, timedelta
import re
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# FastAPI setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Constants: Only TN Seashore Districts
DISTRICTS = [
    "Chennai", "Thiruvallur", "Chengalpattu", "Kancheepuram", "Cuddalore", "Villupuram",
    "Nagapattinam", "Mayiladuthurai", "Thanjavur", "Thoothukudi", "Ramanathapuram",
    "Tirunelveli", "Kanniyakumari"
]
STAKEHOLDERS = ["Field Officer", "Command Center", "NGO", "Senior Official"]

DISTRICT_QUERY = {
    "Chennai": "Chennai,India",
    "Thiruvallur": "Thiruvallur,India",
    "Chengalpattu": "Chengalpattu,India",
    "Kancheepuram": "Kancheepuram,India",
    "Cuddalore": "Cuddalore,India",
    "Villupuram": "Villupuram,India",
    "Nagapattinam": "Nagapattinam,India",
    "Mayiladuthurai": "Mayiladuthurai,India",
    "Thanjavur": "Thanjavur,India",
    "Thoothukudi": "Thoothukudi,India",
    "Ramanathapuram": "Ramanathapuram,India",
    "Tirunelveli": "Tirunelveli,India",
    "Kanniyakumari": "Kanniyakumari,India"
}

# Approximate bounding boxes (minLon, minLat, maxLon, maxLat) for districts (example values, adjust if needed)
DISTRICT_BBOX = {
    "Chennai": [80.20, 12.90, 80.30, 13.10],
    "Thiruvallur": [79.85, 13.00, 80.20, 13.40],
    "Chengalpattu": [79.95, 12.70, 80.25, 13.00],
    "Kancheepuram": [79.80, 12.70, 80.10, 13.00],
    "Cuddalore": [79.30, 11.70, 79.80, 12.20],
    "Villupuram": [79.20, 11.80, 79.70, 12.30],
    "Nagapattinam": [79.60, 10.70, 79.90, 11.10],
    "Mayiladuthurai": [79.60, 11.10, 79.90, 11.50],
    "Thanjavur": [79.10, 10.70, 79.60, 11.10],
    "Thoothukudi": [78.10, 8.40, 78.40, 8.80],
    "Ramanathapuram": [78.30, 9.20, 78.70, 9.60],
    "Tirunelveli": [77.50, 8.30, 77.90, 8.70],
    "Kanniyakumari": [77.20, 8.00, 77.50, 8.40]
}

# API Keys
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WEATHER_HISTORY_URL = "https://api.weatherapi.com/v1/history.json"

# Login page
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "districts": DISTRICTS,
        "stakeholders": STAKEHOLDERS
    })

# Dashboard page
@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    name: str = Form(...),
    district: str = Form(...),
    stakeholder: str = Form(...)
):
    location_query = DISTRICT_QUERY.get(district, district)
    weather_data = {}
    forecast_data = []

    if not WEATHERAPI_KEY:
        weather_data = {"error": "Weather API key not configured."}
    else:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                forecast_url = (
                    f"https://api.weatherapi.com/v1/forecast.json?"
                    f"key={WEATHERAPI_KEY}&q={location_query}&days=7&aqi=no&alerts=no"
                )
                resp = await client.get(forecast_url)
                resp.raise_for_status()
                data = resp.json()
                current = data.get("current", {})
                weather_data = {
                    "temperature": current.get("temp_c"),
                    "condition": current.get("condition", {}).get("text"),
                    "icon": current.get("condition", {}).get("icon"),
                    "humidity": current.get("humidity"),
                    "wind_kph": current.get("wind_kph"),
                }
                forecast_data = [
                    {
                        "date": day.get("date"),
                        "avg_temp": day.get("day", {}).get("avgtemp_c"),
                        "condition": day.get("day", {}).get("condition", {}).get("text"),
                        "icon": day.get("day", {}).get("condition", {}).get("icon"),
                    } for day in data.get("forecast", {}).get("forecastday", [])
                ]
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            weather_data = {"error": "Weather data unavailable."}

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "name": name,
        "district": district,
        "stakeholder": stakeholder,
        "weather": weather_data,
        "forecast": forecast_data,
        "MAPBOX_API_KEY": MAPBOX_API_KEY
    })
import re
import os
import json
import logging
import re
from datetime import datetime, timedelta

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Constants: Tamil Nadu seashore districts & stakeholders
DISTRICTS = [
    "Chennai", "Thiruvallur", "Chengalpattu", "Kancheepuram", "Cuddalore", "Villupuram",
    "Nagapattinam", "Mayiladuthurai", "Thanjavur", "Thoothukudi", "Ramanathapuram",
    "Tirunelveli", "Kanniyakumari"
]
STAKEHOLDERS = ["Field Officer", "Command Center", "NGO", "Senior Official"]

DISTRICT_QUERY = {
    "Chennai": "Chennai,India",
    "Thiruvallur": "Thiruvallur,India",
    "Chengalpattu": "Chengalpattu,India",
    "Kancheepuram": "Kancheepuram,India",
    "Cuddalore": "Cuddalore,India",
    "Villupuram": "Villupuram,India",
    "Nagapattinam": "Nagapattinam,India",
    "Mayiladuthurai": "Mayiladuthurai,India",
    "Thanjavur": "Thanjavur,India",
    "Thoothukudi": "Thoothukudi,India",
    "Ramanathapuram": "Ramanathapuram,India",
    "Tirunelveli": "Tirunelveli,India",
    "Kanniyakumari": "Kanniyakumari,India"
}

# Approximate bounding boxes (minLon, minLat, maxLon, maxLat) for districts
DISTRICT_BBOX = {
    "Chennai": [80.20, 12.90, 80.30, 13.10],
    "Thiruvallur": [79.85, 13.00, 80.20, 13.40],
    "Chengalpattu": [79.95, 12.70, 80.25, 13.00],
    "Kancheepuram": [79.80, 12.70, 80.10, 13.00],
    "Cuddalore": [79.30, 11.70, 79.80, 12.20],
    "Villupuram": [79.20, 11.80, 79.70, 12.30],
    "Nagapattinam": [79.60, 10.70, 79.90, 11.10],
    "Mayiladuthurai": [79.60, 11.10, 79.90, 11.50],
    "Thanjavur": [79.10, 10.70, 79.60, 11.10],
    "Thoothukudi": [78.10, 8.40, 78.40, 8.80],
    "Ramanathapuram": [78.30, 9.20, 78.70, 9.60],
    "Tirunelveli": [77.50, 8.30, 77.90, 8.70],
    "Kanniyakumari": [77.20, 8.00, 77.50, 8.40]
}

# API Keys from environment variables
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WEATHER_HISTORY_URL = "https://api.weatherapi.com/v1/history.json"

# Login page route
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "districts": DISTRICTS,
        "stakeholders": STAKEHOLDERS
    })

# Dashboard route
@app.post("/login", response_class=HTMLResponse)
async def login(request:Request, name: str = Form(...), phone: str = Form(...), district: str = Form(...), stakeholder: str = Form(...)):
    # Append login to logins.txt
    log_entry = f"{name},{phone}\n"
    with open("logins.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

    location_query = DISTRICT_QUERY.get(district, district)
    weather_data = {}
    forecast_data = []

    if not WEATHERAPI_KEY:
        weather_data = {"error": "Weather API key not configured."}
    else:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                forecast_url = (
                    f"https://api.weatherapi.com/v1/forecast.json?"
                    f"key={WEATHERAPI_KEY}&q={location_query}&days=7&aqi=no&alerts=no"
                )
                resp = await client.get(forecast_url)
                resp.raise_for_status()
                data = resp.json()
                current = data.get("current", {})
                weather_data = {
                    "temperature": current.get("temp_c"),
                    "condition": current.get("condition", {}).get("text"),
                    "icon": current.get("condition", {}).get("icon"),
                    "humidity": current.get("humidity"),
                    "wind_kph": current.get("wind_kph"),
                }
                forecast_data = [
                    {
                        "date": day.get("date"),
                        "avg_temp": day.get("day", {}).get("avgtemp_c"),
                        "condition": day.get("day", {}).get("condition", {}).get("text"),
                        "icon": day.get("day", {}).get("condition", {}).get("icon"),
                    } for day in data.get("forecast", {}).get("forecastday", [])
                ]
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            weather_data = {"error": "Weather data unavailable."}

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "name": name,
        "district": district,
        "stakeholder": stakeholder,
        "weather": weather_data,
        "forecast": forecast_data,
        "MAPBOX_API_KEY": MAPBOX_API_KEY
    })

# Flood risk prediction and suggestions API
@app.get("/api/flood-risk", response_class=JSONResponse)
async def get_flood_risk(district: str = "Chennai", stakeholder: str = "Field Officer"):
    logger.info(f"Flood risk request for district: {district}, stakeholder: {stakeholder}")
    location_query = DISTRICT_QUERY.get(district, district)
    district_bbox = DISTRICT_BBOX.get(district, [80.2, 13.0, 80.4, 13.2])  # fallback bbox

    if not WEATHERAPI_KEY or not OPENROUTER_API_KEY:
        logger.error("Missing API configuration.")
        return JSONResponse(status_code=500, content={"error": "Missing API configuration."})

    try:
        # Fetch last 3 days of historical weather
        historical_weather = []
        async with httpx.AsyncClient(timeout=10) as client:
            for days_ago in range(1, 4):
                date_str = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                url = f"{WEATHER_HISTORY_URL}?key={WEATHERAPI_KEY}&q={location_query}&dt={date_str}"
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                day = data.get("forecast", {}).get("forecastday", [{}])[0]
                if day:
                    historical_weather.append({
                        "date": day.get("date"),
                        "avgtemp_c": day.get("day", {}).get("avgtemp_c"),
                        "totalprecip_mm": day.get("day", {}).get("totalprecip_mm"),
                        "maxwind_kph": day.get("day", {}).get("maxwind_kph"),
                        "avghumidity": day.get("day", {}).get("avghumidity")
                    })

        # Prompt for GeoJSON flood risk prediction
        flood_prompt = f"""
You are an expert flood risk analyst with knowledge of hydrology, topography, soil types, drainage infrastructure, land use, and historical flood data.

Given the last 3 days of weather data for the {district} district in Tamil Nadu, along with your knowledge of other relevant flood risk factors (topography, soil permeability, drainage capacity, land cover, historical flood events), predict the flood risk zones in GeoJSON format.

Risk levels: High, Moderate, Low. Each feature must have:
- geometry (Polygon strictly within the bounding box coordinates {district_bbox})
- properties: risk_level

Weather data:
{json.dumps(historical_weather, indent=2)}

Return ONLY valid GeoJSON (FeatureCollection) representing flood risk zones.
"""

        # Prompt for stakeholder-specific suggestions
        suggestion_prompt = f"""
You are a disaster management advisor. Based on the flood risk levels in {district} from the recent weather data (see below), provide actionable and concise suggestions tailored for the role of a '{stakeholder}'.

Weather data:
{json.dumps(historical_weather, indent=2)}

Keep it under 5 bullet points. Be role-specific.
"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30) as client:
            # Request GeoJSON prediction
            geo_req = {
                "model": "meta-llama/llama-3-70b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that generates GeoJSON."},
                    {"role": "user", "content": flood_prompt}
                ],
                "max_tokens": 1024
            }
            geo_resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=geo_req)
            geo_resp.raise_for_status()
            geo_text = geo_resp.json()["choices"][0]["message"]["content"]
            logger.info(f"GeoJSON AI raw response: {geo_text}")

            # Extract GeoJSON from AI response
            match = re.search(r"\{[\s\S]*\}", geo_text)
            if not match:
                raise ValueError("Valid GeoJSON not found in AI response.")
            geojson = json.loads(match.group(0))

            # Request stakeholder suggestions
            suggestion_req = {
                "model": "meta-llama/llama-3-70b-instruct",
                "messages": [
                    {"role": "system", "content": "You generate stakeholder-specific flood response suggestions as bullet points."},
                    {"role": "user", "content": suggestion_prompt}
                ],
                "max_tokens": 512
            }
            sugg_resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=suggestion_req)
            sugg_resp.raise_for_status()
            suggestions_text = sugg_resp.json()["choices"][0]["message"]["content"]
            logger.info(f"Suggestions for {stakeholder} in {district}:\n{suggestions_text}")

        return JSONResponse({
            "district": district,
            "stakeholder": stakeholder,
            "geojson": geojson,
            "suggestions": suggestions_text
        })

    except Exception as e:
        logger.error(f"Error during flood risk prediction: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Failed to fetch flood risk data."})
