from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from test_letter_generator import router as letter_router

app = FastAPI(title="Consent Letter Generator - Test Backend")

app.include_router(letter_router, prefix="/test", tags=["Patient Letter Tester"])


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
