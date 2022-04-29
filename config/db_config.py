# On this module, we'll set up the database connection configuration.

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

engine = create_engine("mysql+pymysql://root@localhost:3306/db_inventory_manager")

if not database_exists(engine.url):
    create_database(engine.url)
