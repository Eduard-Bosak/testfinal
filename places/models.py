from django.db import models
from workers.models import Person

TABLE_CHOICES = [('Стол 1', '1'), ('Стол 2', '2'), ('Стол 3', '3'), ('Стол 4', '4'), ('Стол 5', '5'), ('Стол 6', '6'), ('Стол 7', '7'), ('Стол 8', '8'), ('Стол 9', '9')]

class Place(models.Model):
    table_number = models.CharField('Стол', choices=TABLE_CHOICES, unique=True,)
    additional_information = models.CharField('Дополнительная информация', max_length=500, blank=True, null=True,)

    class Meta:
        verbose_name = 'Все места'
        verbose_name_plural = 'Все места'
    def __str__(self):
        return self.table_number

class Job(models.Model):
    name = models.OneToOneField(Person, on_delete=models.PROTECT, null=True, blank=False)
    class Meta:
        verbose_name = 'Занятые места'
        verbose_name_plural = 'Занятые места'

