from django.db import models


class Book(models.Model):
    class CoverChoices(models.IntegerChoices):
        HARD = 0, "Hard"
        SOFT = 1, "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.IntegerField(choices=CoverChoices)
    inventory = models.PositiveIntegerField(unique=True)
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.inventory} {self.title}"

    @property
    def daily_fee_display(self) -> str:
        return f"{self.daily_fee}$"
