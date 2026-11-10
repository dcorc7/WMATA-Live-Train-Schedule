from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from app.config import settings

# Initialize FastAPI app
app = FastAPI()

# Mount static files (CSS/JS) and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_board(request: Request):
    headers = {"api_key": settings.WMATA_API_KEY}
    trains = []
    station_name = settings.STATION_CODE
    error_message = None

    try:
        async with httpx.AsyncClient() as client:
            # Initiate WMATA api response
            response = await client.get(settings.WMATA_URL, headers=headers, timeout=10.0)

            # Check if response is healthy
            if response.status_code == 200:
                # Get response json data
                data = response.json()

                # Return list of train data
                all_trains = data.get("Trains", [])
                
                # Get the station name
                if all_trains:
                    station_name = all_trains[0].get("LocationName", station_name)

                # Filter out ghost trains (Line: "No")
                trains = [t for t in data.get("Trains", []) if t.get("Line") != "No"][:5]

            # Print message if the response is unhealthy
            else:
                error_message = f"WMATA API returned status {response.status_code}"

    # Throw exception if the API can't be communicated with
    except Exception as e:
        import traceback

        # Print exact error from response
        print("--- DETAILED ERROR LOG ---")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        traceback.print_exc()
        print("--------------------------")
        error_message = f"Network Error: {type(e).__name__}"
        error_message = "Could not connect to transit network."

    # Return data in a specific format for the frontend
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "trains": trains, 
            "station_name": station_name,
            "error": error_message
        }
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host='127.0.0.1', port=5000, reload=True)
