from fastapi import FastAPI
from fastapi import Request

import logging 

logger = logging.getLogger('uvicorn.error')
                   
logger.info("Tester application has started")

app = FastAPI()

@app.get('/')
async def root():
    logger.info("Hit root URL.")
    return {"message": "testing out building dockerised images"}



@app.post('/volumes/')
async def save_data(request: Request):
    payload = await request.json()
    
    logger.info(f"Hitting saving data to presistent volumes.\n{payload}")
    data =payload['message']
    with open('./data/testing.txt', "a+") as file:
        file.write(data + "\n")
                
    return {"message": "Data has been written to presistent volume"}

    

@app.get('/healthy')
async def liveness():
    logger.info("Livenesss health check made")
    return {"message": "The server is alive and functioning as expected"}

