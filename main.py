from fastapi import Depends, FastAPI
import models
import database
import api
from fastapi.responses import FileResponse
from pathlib import Path
from auth import OAuth2PasswordBearer
import crud
import schemas
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(api.router)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/favicon.ico")
async def get_favicon():
    favicon_path = Path("path_to_your_favicon.ico")
    if favicon_path.is_file():
        return FileResponse(favicon_path, headers={"Content-Type": "image/x-icon"})
    else:
        return {"message": "Favicon not found"}, 404
       

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



