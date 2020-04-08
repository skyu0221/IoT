# Occupancy Monitoring System in Smart Building

Please deploy the `backend server` and `synthetic data generator` separately to two different server.

You can find our `backend server` on http://3.133.122.194:8000, and `synthetic data generator` on https://pacific-temple-42851.herokuapp.com/

## Architecture

![Architecture](/architecture.png)

## Report

Our first draft of the report is available [here](/Report-Draft.pdf).

## Demo

[Click for video (University login required)](https://drive.google.com/open?id=1NfoVn2cnpcxLPgdQ5m2riQiNsxhwE5CV)

## Important files in the `synthetic data generator`
+ `synthetic-data-generator/proj/urls.py`: Contains all API settings
+ `synthetic-data-generator/hello/data_generator.py`: Contains the code that generate the synthetic data for the location of each person in a day and sensor data in second granularity
+ `synthetic-data-generator/hello/views.py`: Contains all functions that process the requests

## Important files in the `frontend gui`
+ `frontend-gui/main.py`: Main file for whole gui program
+ `frontend-gui/lpanel.py`: Contains all UI elements for left panel
+ `frontend-gui/rpanel.py`: Contains all UI elements for right panel

## Important files in the `backend server`
+ The scripts used for registering a new user: `backend-server/scripts/register_user_client.py`
+ The scripts used for on-permise cameras: `backend-server/scripts/camera_client.py`
+ Other files under the `backend-server/scripts/` directory are used for fetching data from sensor devices
+ We follow the common Django practice to put all the files related to our app in `backend-server/sensors/` and their names are self-explained.
+ The database scheme is auto-generated with Django data model, so the scheme can be checked from `backend-server/sensors/models.py `.
