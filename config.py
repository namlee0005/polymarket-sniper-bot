from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = "placeholder"
    MONGODB_URI: str = "mongodb://mongo:27017/polymarket_sniper"
    POLYGONSCAN_API_KEY: str = ""
    X_BEARER_TOKEN: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
