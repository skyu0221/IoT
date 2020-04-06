# Occupancy Monitoring System in Smart Building

Please deploy the `backend server` and `synthetic data generator` separately to two different server.

## Important files in the `synthetic data generator`
+ `synthetic-data-generator/proj/urls.py`: Contains all API settings
+ `synthetic-data-generator/hello/data_generator.py`: Contains the code that generate the synthetic data for the location of each person in a day and sensor data in second granularity
+ `synthetic-data-generator/hello/views.py`: Contains all functions that process the requests
