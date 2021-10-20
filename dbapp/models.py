from django.db import models


class Drawing(models.Model):
    path = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "drawing"
