import psycopg2
from datetime import datetime, timezone
from flask import Flask, request, Response, json, g

# Enter your database host, database user, database password and database name
DATABASE_HOST = 'host_name'
DATABASE_USER = 'database_user'
DATABASE_PASSWORD = 'database_password'
DATABASE_NAME = 'database_name'

# Set your server's IP address and port
IP_ADDRESS = 'ip_address'
PORT = 'port'

# Making the initial connection to the data base:
conn = psycopg2.connect(
    dbname=DATABASE_NAME,
    user=DATABASE_USER,
    host=DATABASE_HOST,
    password=DATABASE_PASSWORD
)


def convert_value(value, channel_type):
    if channel_type == 'ALARM':
        if value == 0:
            return 'OK'
        elif value == 1:
            return 'ALARM'
    else:
        return value


app = Flask(__name__)


# Set up "/measurements" endpoint, which will be receiving the data sent by Efento webhooks using POST method
@app.route('/measurements', methods=['POST'])
def respond():
    data = request.json
    record = []

    deviceSerialNumber = data['deviceSerialNumber']
    measurementPoint = data['measurementPointName']

    firstMeasurementTimestamp = datetime.strptime(data['firstMeasurementTimestamp'], "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=timezone.utc).timestamp()
    lastMeasurementTimestamp = datetime.strptime(data['lastMeasurementTimestamp'], "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=timezone.utc).timestamp()
    # Iteration in the list of measurements events received over webhook
    for measurementsEvent in data['measurementsEvents']:
        events = measurementsEvent['events']

        channelNumber = measurementsEvent['channelNumber']
        channelType = measurementsEvent['channelType']

        # Getting parameters of the first event
        period = measurementsEvent['events'][0]['period']
        value = measurementsEvent['events'][0]['value']
        status = measurementsEvent['events'][0]['status']
        timestamp = firstMeasurementTimestamp
        # Extrapolating the timestamps starting from the first measurement timestamp to the last measurement timestamp,
        # based on the measurement period
        while timestamp <= lastMeasurementTimestamp:
            # Use event parameters to create records
            if timestamp == datetime.strptime(events[0]['timestamp'], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc).timestamp():
                measurementAt = datetime.fromtimestamp(timestamp)
                record.extend([(measurementAt, deviceSerialNumber, measurementPoint, channelNumber, channelType,
                                events[0]['status'],
                                convert_value(events[0]['value'], channelType))])
                period = events[0]['period']
                timestamp = timestamp + period
                value = events[0]['value']
                status = events[0]['status']
                # Delete the event from the events array
                if len(events) != 1:
                    events.pop(0)
            # Supplement measurements record by the last event's parameters
            else:
                measurementAt = datetime.fromtimestamp(timestamp)
                record.extend(
                    [(measurementAt, deviceSerialNumber, measurementPoint, channelNumber, channelType, status,
                      convert_value(value, channelType))])
                timestamp = timestamp + period

    # Insert data received over webhook into the database
    measurements = "INSERT INTO webhooks(measured_at, serial_number, measurement_point, channel, type, status,  value) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    with conn.cursor() as cur:
        try:
            # Inserting a list of the sensor parameters and measurements to the table in PostgresSQL
            cur.executemany(measurements, record)
            conn.commit()
            cur.close()
            status_code = 201
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            status_code = 500

    return Response(status=status_code)


if __name__ == "__main__":
    # Starting the application on set IP address and port.
    app.run(host=IP_ADDRESS, port=PORT)
