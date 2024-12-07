from fastapi import FastAPI
import logging 

logger = logging.getLogger('uvicorn.error')
                   
logger.info("Tester application has started")

app = FastAPI()

@app.get('/')
async def root():
    logger.info("Hit root URL.")
    return {"message": "testing out building dockerised images"}

