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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<<start>><br/>"
        f"/api/v1.0/<<start>>/<<end>>"
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
    # Close session
    session.close()

    # Create a dictionary to capture precip_data
    precip_dict = {}
    for date, prcp in precip_data:
        precip_dict[date]=prcp

    return jsonify(precip_dict)

#Establishing Station route
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session=Session(bind=engine)
    #Retrieve station data
    station_data=session.query(Station.name).all()
    # Close session
    session.close()

    # Create a list of stations
    station_list = []
    for name in station_data:
        station_list.append(name[0])

    return jsonify(station_list)

#Establishing Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    #Create our session (link) from Python to the DB
    session=Session(bind=engine)
    # List the stations and their counts in descending order.
    active_stations = (
    session.query(Measurement.station, func.count(Measurement.id))
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.id).desc())
    .all()
    )
    # Determine most active station ID
    most_active_station = active_stations[0][0]
    # Starting from the most recent data point in the database for most active station
    latest_date = session.query(Measurement.date).filter(Measurement.station == most_active_station).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    one_year_ago = latest_date - dt.timedelta(days=365)    
    # Gets the past year of observations for most active station
    temp_data = (
    session.query(Measurement.date, Measurement.tobs)
    .filter(Measurement.station == most_active_station)
    .filter(Measurement.date >= one_year_ago)
    .all()
    )
    # Close session
    session.close()
    # Convert temp_data into a list of dictionaries
    temp_list = []
    for date, tobs in temp_data:
        temp_dict={}
        temp_dict[date]=tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)
    
#Establishing [Start] route
@app.route("/api/v1.0/<start>")
def start(startdate):
    #Create our session (link) from Python to the DB
    session=Session(bind=engine)
    #Convert start date from string to datetime
    latest_date = dt.datetime.strptime(startdate, '%Y-%m-%d')
    
    # Close session
    session.close()

    return latest_date.strftime("%Y %m")

if __name__ == '__main__':
    app.run(debug=True)
