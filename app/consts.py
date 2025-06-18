ENV = "dev"

DB_CONNECTION = "mysql+aiomysql://neves:12qwaszx@mysql/achadinhos"
REDIS_HOST = "redis"

if ENV == "dev":
    DB_CONNECTION = "mysql+aiomysql://neves:12qwaszx@localhost/achadinhos"
    REDIS_HOST = "127.0.0.1"
