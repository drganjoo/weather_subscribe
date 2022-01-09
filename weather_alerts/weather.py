import typing as t
from flask import Flask,Blueprint, request
from sqlalchemy.exc import IntegrityError
from .database import db_session
from .commontypes import FormField, FormFieldValues
from .common import get_fields
from .models.subscription import Subscription
from .models.subscriber import Subscriber
from .exceptions import AlreadyExistsException

bp = Blueprint('weather', __name__, url_prefix='/weather')

# list of valid_cities that we have seen in the past, in case of
# a new city we will first check with the downstreeam service
# to make sure the city is valid
city_cache = []

@bp.route('/register', methods=['POST'])
def register():
    fields : FormFieldValues = get_fields(request, [
        FormField('email', 'email', True),
        FormField('city', 'city', True),
        FormField('maxTemperature', 'maximum temperature', True),
        ])

    email, city, temperature = fields['email'], fields['city'], fields['maxTemperature']

    if city not in city_cache:
        city_cache.append(fields['email'])

    subscription = Subscription(email, city, temperature)
    db_session.add(subscription)
    try:
        db_session.commit()
        return {
            "result" : "success",
            "id" : subscription.id
        }
    except IntegrityError as ue:
        raise AlreadyExistsException(f"Email addreess {email} is already registered")

def register_routes(app: Flask):
    app.register_blueprint(bp)


        # if not username:
        #     error = 'Username is required.'
        # elif not password:
        #     error = 'Password is required.'

        # if error is None:
        #     try:
        #         db.execute(
        #             "INSERT INTO user (username, password) VALUES (?, ?)",
        #             (username, generate_password_hash(password)),
        #         )
        #         db.commit()
        #     except db.IntegrityError:
        #         error = f"User {username} is already registered."
        #     else:
        #         return redirect(url_for("auth.login"))

        # flash(error)
