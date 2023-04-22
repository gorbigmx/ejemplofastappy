from fastapi import FastAPI
from fastapi import Form

app = FastAPI()

@app.post("/contact")
async def contact(subject: str = Form(), msg: str = Form()):
    return {
        "subject": subject,
        "message": msg
    }