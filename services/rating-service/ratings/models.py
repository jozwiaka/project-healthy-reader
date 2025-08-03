from django.db import models

class Rating(models.Model):
    user_id = models.BigIntegerField()
    isbn = models.CharField(max_length=13)
    rating = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'ratings'
        unique_together = ('user_id', 'isbn')
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['isbn']),
        ]

    def __str__(self):
        return f"Rating(user_id={self.user_id}, isbn={self.isbn}, rating={self.rating})"
