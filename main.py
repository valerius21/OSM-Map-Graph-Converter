import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile

from osm_processor import process_map

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(..., accept=".osm")):
    # Validate the file extension
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension != ".osm":
        raise HTTPException(status_code=422, detail="Only .osm files are allowed.")

    with tempfile.NamedTemporaryFile(delete=True, suffix=".osm") as tmp:
        shutil.copyfileobj(file.file, tmp)
        print(tmp.name)
        graph_dict = process_map(tmp.name)
    return {'filename': file.filename, 'size': len(graph_dict['edges']) * 2, 'graph': graph_dict}
