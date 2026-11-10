import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Create class for WMATA API configuration
class Settings:
    WMATA_API_KEY: str = os.getenv("WMATA_API_KEY", "")
    STATION_CODE: str = os.getenv("STATION_CODE", "A06")
    WMATA_BASE_URL: str = "https://api.wmata.com"

    @property
    def WMATA_URL(self) -> str:
        return f"{self.WMATA_BASE_URL}/StationPrediction.svc/json/GetPrediction/{self.STATION_CODE}"

settings = Settings()
