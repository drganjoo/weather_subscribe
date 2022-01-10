import typing as t

from weather_alerts.services.subscriptionservice import CityAlert

class AlertService:
    """A dummy service to simulate sending out a notification"""
    def __init__(self):
        pass

    def has_notified(self, email: str):
        """Some code will go here to check that the user is not notified
        more than once in a day OR till the alert is resolved etc."""
        return False

    def notify(self, email: str, alarmed_cities : t.List[CityAlert]):
        """Send notification about the alarmed cities. But do not send
        multiple notifications of a city in a day (or whatever the update period
        would be)"""
        if not self.has_notified(email):
            self.send_email(email, alarmed_cities)

    def send_email(self, email: str, alarmed_cities : t.List[CityAlert]):
        # todo: code to send email
        pass