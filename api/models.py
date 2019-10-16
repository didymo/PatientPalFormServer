from django.db import models

class DeployedSurvey(models.Model):
    name = models.JSONField(type=dict)
    id = models.JSONField(type=dict)
