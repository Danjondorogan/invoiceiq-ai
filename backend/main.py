from fastapi import FastAPI

app = FastAPI(
    title="InvoiceIQ API",
    version="1.0.0",
    description="AI Powered Invoice Verification Platform"
)

@app.get("/")
def home():
    return {
        "project": "InvoiceIQ",
        "status": "running",
        "version": "1.0.0"
    }