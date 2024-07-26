from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routes Module
import routes.oauth
import routes.account
import routes.pose

app = FastAPI()

origins = ["# Add Your Frontend Domain #"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.oauth.oauth_router, prefix="")
app.include_router(routes.account.account_router, prefix="")
app.include_router(routes.pose.pose_router, prefix="")

@app.get("/")
def read_root():
    return "OK"
