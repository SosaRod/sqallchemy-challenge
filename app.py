# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine to connect to SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

# Initialize Flask app
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define homepage route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start_end/<start>/<end>"
    )

# Define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    precip_dict = {date: prcp for date, prcp in precip_data}
    return jsonify(precip_dict)

# Define stations route
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    station_list = [station[0] for station in stations]
    return jsonify(station_list)

# Define temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station).group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]
    
    temp_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago).all()

    temp_dict = {date: tobs for date, tobs in temp_data}
    return jsonify(temp_dict)

# Define start date route
@app.route("/api/v1.0/start/<start>")
def start_date(start):
    temp_stats = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    return jsonify(temp_stats)

# Define start-end date range route
@app.route("/api/v1.0/start_end/<start>/<end>")
def start_end_date(start, end):
    temp_stats = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    return jsonify(temp_stats)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

