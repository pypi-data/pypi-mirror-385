from typing import List

from pydantic import BaseModel

from mongoguard import MongoGuard

mg = MongoGuard(
    mongo_url="mongodb://localhost:27017/",
    db_name="Medusa",
    collection_name="contacts"
)

class ContactModel(BaseModel):
    id: int
    name: str
    numbers: List[str]
    uuid: str

print(mg.fetch_entries(out_model=ContactModel))
