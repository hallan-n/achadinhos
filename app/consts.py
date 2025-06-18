ENV = "dev"

DB_CONNECTION = "mysql+aiomysql://neves:12qwaszx@mysql/achadinhos"

if ENV == "dev":
    DB_CONNECTION = "mysql+aiomysql://neves:12qwaszx@localhost/achadinhos"
