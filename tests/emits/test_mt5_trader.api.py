from fastapi import FastAPI
app = FastAPI()

@app.get('/tick')
def get_tick():
    # Exec ->L->OnTick
    return {"data": []}
