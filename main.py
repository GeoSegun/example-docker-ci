from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from a Docker image, version 2"}


@app.get("/health")
def health():
    return {"status": "ok"}
