from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Store API"
    ROOT_PATH: str = "/"

    MONGO_HOST: str
    MONGO_ROOT_USER: str
    MONGO_ROOT_PASSWORD: str
    MONGO_DB_PORT: int = 27017
    MONGO_DB_NAME: str = "banco_store"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mongodb://{self.MONGO_ROOT_USER}:{self.MONGO_ROOT_PASSWORD}"
            f"@{self.MONGO_HOST}:{self.MONGO_DB_PORT}/{self.MONGO_DB_NAME}?authSource=admin"
        )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
