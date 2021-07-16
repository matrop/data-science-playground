import sqlalchemy
import pandas as pd

def get_con():
    """Get a connection object for the Postgres database
    """
    return sqlalchemy.create_engine('postgresql://maurice:maurice@localhost/mydatabase').connect()
