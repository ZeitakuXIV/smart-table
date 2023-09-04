from datetime import datetime, date, time
from pytz import timezone
from django.db import models
from smart_table.models import CustomUser

class Presence(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time_in = models.DateTimeField()
    time_out = models.DateTimeField()

    class Meta:
        db_table = 'presences'

    def __str__(self):
        return f"Presence #{self.id} - {self.user.name}"

# Get the Jakarta timezone
jakarta_timezone = timezone('Asia/Jakarta')

# Get the current date and time in Jakarta timezone
now_jakarta = datetime.now(jakarta_timezone)

# Get the beginning of the current day in Jakarta timezone
start_of_day_jakarta = now_jakarta.replace(hour=0, minute=0, second=0, microsecond=0)

# Query the Presence model to get today's data based on time_in
todays_data = Presence.objects.filter(time_in__range=(start_of_day_jakarta, now_jakarta))

for presence in todays_data:
    print(presence.time_in, presence.time_out, presence.user.name)