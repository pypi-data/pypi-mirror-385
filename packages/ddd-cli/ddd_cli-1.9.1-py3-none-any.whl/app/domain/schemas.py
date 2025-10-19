
from pydantic import BaseModel, HttpUrl

class FileData(BaseModel):
    file_name: str
    url: str  
