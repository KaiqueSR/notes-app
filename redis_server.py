import os
from redis import Redis
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("REDIS_HOST")
port = os.getenv("REDIS_PORT")
redisDb = os.getenv("REDIS_DB")

redis = Redis(host=host, port=port, db=redisDb)
