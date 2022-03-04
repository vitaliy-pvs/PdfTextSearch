from django.db import models


class Drawing(models.Model):
    path = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    text = models.TextField()
    article = models.CharField(max_length=255, default="")
    true_name = models.CharField(max_length=255, default="")
    true_text = models.TextField(default="")
    applicability = models.TextField(default="")
    structure = models.TextField(default="")
    incoming = models.TextField(default="")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "drawing"
