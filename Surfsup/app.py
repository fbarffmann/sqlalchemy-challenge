# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station

# reflect the tables
Base.metadata.create_all(engine)

# Save references to each table
measurement = Base.metadata.tables["measurement"]
station = Base.metadata.tables["station"]

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#################################################
# Flask Routes
#################################################

#Establishing Welcome page route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station"
    )

#Establishing Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session=Session(bind=engine)
    # Starting from the most recent data point in the database. 
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    one_year_ago = latest_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Create a dictionary to capture precip_data
    precip_dict = {}
    for date, prcp in precip_data:
        precip_dict[date]=prcp

    return jsonify(precip_dict)

if __name__ == '__main__':
    app.run(debug=True)




