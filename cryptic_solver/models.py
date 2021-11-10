from django.db import models

class Puzzle(models.Model):
    grid_json = models.JSONField()


# Create your models here.

