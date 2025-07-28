from motor.motor_asyncio import AsyncIOMotorClient

from store.core.config import settings


class MongoClient:
    def __init__(self) -> None:
        self.client: "AsyncIOMotorClient" = AsyncIOMotorClient(  # type: ignore
            settings.DATABASE_URL, uuidRepresentation="standard"
        )

    def get(self) -> "AsyncIOMotorClient":  # type: ignore
        return self.client


db_client = MongoClient()
