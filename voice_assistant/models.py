from django.db import models

class CommandHistory(models.Model):
    command = models.CharField(max_length=255)
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.command} - {self.timestamp}"