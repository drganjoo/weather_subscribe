# City Weather Alert System

## Background

Develop a Rest API with endpoints for weather alert subscriptions. A subscription has an email address, a location (e.g. city) and some simple weather conditions to be alerted about, (e.g. temperature less than 0 celsius).

Endpoints should be available to create/list/read/update and delete (cancel) subscriptions.

The app should regularly poll a public weather API for the city locations that have been subscribed to, check the current weather information based on the conditions and if the conditions are met send out an email alerting about it.

## How to run

### Install python modules

```
pip install -r requirements.txt
```

### Run / Create Database

```
cd devops
docker compose up
```

For first time create the database using:

```
export FLASK_APP=weather_alerts
export FLASK_ENV=production
flask init-db
```

### Run app

```
export FLASK_APP=weather_alerts
export FLASK_ENV=production
flask run
```

## Datbase Tables

### Subscriber

Holds information about a subscriber. Each email address gets a unique id in the system. `email` is a unique constraint.

|Column |          Type          | Collation | Nullable |                 Default|
|--------|------------------------|-----------|----------|-----------------------------------------|
| id     | integer                |           | not null | nextval('subscribers_id_seq'::regclass)|
| email  | character varying(255) |           | not null ||

**Note:** other fields like when was the subscriber added etc. have not been added to keep it simple

### Subscription

Alerts subscribed by a subscriber for a particular city are kept in this table. `subscriber_id` and `city` are
a unique key and one subscriber is not allowed to have multiple alerts on the same city.

|  Column       |            Type             | Collation | Nullable |                  Default|
|-------------------|-----------------------------|-----------|----------|-------------------------------------------|
| id                | integer                     |           | not null | nextval('subscriptions_id_seq'::regclass)|
| subscriber_id     | integer                     |           | not null ||
| city              | character varying(163)      |           | not null ||
| min_temperature   | double precision            |           | not null ||
|subscription_date | timestamp without time zone  |           | not null ||

Foreign-key constraints:    
    "subscriptions_subscriber_id_fkey" FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)

*Note: In order to keep it simple, other tables for city, state, country and job_runs have not been created*. `select distinct city` is used
to get distinct cities to loop over and get from weather API.

## Overall Architecture

Routes are kept separate from services and are defined under `routes/subsribe.py`. Route never talk
to the database directly.

### Services 
`SubscriptionService` allows adding, removing, updating subscriptions in the database

`WeatherService` has the code to communicate with the Weather service. It maintains a local cache of each city
and the rest of the application goes through this cache rather than going to the service for each city encountered. This
way if multiple people have same city alerts, the cached weather is used for them rather than going to the service for each of them.

`backgroundjobs.py` has the background job that is scheduled to run after every 10 minutees 

`AlertService` has dummy code that would actually notify a subscriber if the alert is active

### Exceptions

**Exceptions** are all handled inside common.py. So the routes and services can through exceptions and they will be
hadled centrally in one place. **HTTP Status Codes** are used to indicate error cases. 200 is for all successes but
anything other 200 is considered an error. Each error case will have an errorCode JSON field, which is an identifier to let the
caller know about the error case.

Custom exceptions are written out in `exceptions.py`

**Database Errors** are never sent to the client. They are written out on the console and have a unique ID. This unique ID is sent
to the client so if they would like to contact support they can do it.

|Error Code|Description|
|-|-|
|missing_fields|Some field in the input was missing|
|already_exists|Some resource already exists and cannot be duplicated|
|storage_error|Some kind of storage error has occurred|
|not_found|Some resource was not found in the system|
unknown_error|An unclassified error has ocurred|

### Lgging

A very simple console based logger is used. The idea is to use some service like **elastic** that can read from 
this and provide complete logging service.

## REST Api

### EndPoints

All endpoints take `application/json` as the content-type and return `application/json` as the response

|End Point|Method|Parameters|
|-|-|-|
|/weather/subscribe|POST| { "email": "", "city": "", "minTemperature": 0.0 }|
|/weather/subscribe|DELETE| { "email": "", "city": "" }|
|/weather/subscribe|PUT| { "email": "", "city": "", "minTemperature": 0.0 }|
|/weather/list|GET|?email=fahadzubair@gmail.com|

**health** related route has been defined BUT it is not to be consued by the outside world. The idea is to 
show that the API should have some endpoints that can be used by internal monitoring systems to check the
health of the system. Security related checks can be added to it to make sure only internal IP addreeses can 
consume these.

### Description

Routes are defined in:

- weather_alerts:    
    - routes:    
        -  health (API endpoints to test API health)   
        -  subscribe (API endpoints for subscription)      

All database related queries are kept separate from the routes and are handled by `SubscriptionService` class
defined  in `services/subscriptionservice.py`

Third party weather service is handled by `WeatherService` class defined in `services/weatherservice.py`.

Background jobs are handled by BackgroundScheduler inside `services/backgroundjobs.py`. *Note*: In a production
environemnt it would have been preferred to keep this separate and use Kafka type service to which two apps
can connect, one that monitors alerts and the other that handles notifications.

## Testing

### Manaul Testing (for QA)

`tests` folder has `api.rest` file that can be used with VSCode Rest client to be tested manually

### Automated Test Cases

```
    pytest tests/test_service.py
    pytest tests/test_weather_service.py
```

Verbose output:

```
python3 tests/test_weather_service.py
```