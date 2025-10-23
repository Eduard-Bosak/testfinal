# ========================================
# ИСПРАВЛЕНО: Убраны ненужные импорты (random, symtable)
# ========================================
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# ========================================
# ИСПРАВЛЕНО: Названия констант по PEP8 должны быть в UPPER_CASE
# Исправлена опечатка: CHOISE -> CHOICE
# ========================================
CHOICE_SEX = [("male", "Мужской"), ("female", "Женский")]

# ИСПРАВЛЕНО: Исправлены опечатки fronted->frontend, beckend->backend
CHOICE_SKILLS = [
    ("frontend", "Фронтенд"),
    ("backend", "Бэкенд"),
    ("testing", "Тестирование"),
    ("project_management", "Управление проектами"),
]

CHOICE_SKILL_LEVEL = [
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
]


class Person(models.Model):

    name = models.CharField(
        "ФИО (при наличии)",
        max_length=200,
        null=True,
        help_text="Полное имя сотрудника",
    )
    sex = models.CharField("Пол", choices=CHOICE_SEX, null=True, max_length=10)
    skills = models.CharField("Навыки", choices=CHOICE_SKILLS, null=True, max_length=50)
    skill_level = models.CharField(
        "Уровень освоения навыка", choices=CHOICE_SKILL_LEVEL, max_length=2, null=True
    )
    description = models.TextField(
        "Описание",
        blank=True,
        null=True,
        help_text="Дополнительная информация о сотруднике",
    )
    is_on_main = models.BooleanField(
        "Показывать на главной",
        default=False,
        help_text="Отметьте, если сотрудник должен отображаться на главной странице",
    )
    employment_date = models.DateField(
        "Дата приёма на работу",
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
        help_text="Дата, когда сотрудник был принят на работу",
    )
    gallery = models.ImageField(
        "Фото сотрудника",
        upload_to="images/",
        null=True,
        blank=True,
        help_text="Основное фото сотрудника",
    )
    desk = models.ForeignKey(
        "Desk",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Рабочий стол",
        related_name="employees",
    )

    class Meta:
        ordering = ["-employment_date"]
        verbose_name = "IT-специалист"
        verbose_name_plural = "IT-специалисты"

    def __str__(self):

        return self.name if self.name else f"Сотрудник #{self.pk}"

    def get_work_experience_days(self):

        if self.employment_date:
            # Вычисляем разницу между сегодняшним днём и датой приёма
            delta = timezone.now().date() - self.employment_date
            return delta.days
        return 0

    def clean(self):
        """Валидатор: тестировщики и разработчики не могут сидеть рядом."""
        super().clean()

        # Проверяем только если назначен стол
        if not self.desk:
            return
        # Определяем, кто является разработчиком
        developer_skills = ["frontend", "backend"]
        is_developer = self.skills in developer_skills
        is_tester = self.skills == "testing"

        # Если сотрудник не разработчик и не тестировщик, валидация не нужна
        if not (is_developer or is_tester):
            return

        # Находим номера соседних столов
        neighbor_desk_numbers = [self.desk.number - 1, self.desk.number + 1]

        # Ищем сотрудников за соседними столами
        neighbors = Person.objects.filter(
            desk__number__in=neighbor_desk_numbers
        ).exclude(
            pk=self.pk
        )  # Исключаем самого себя

        # Проверяем каждого соседа
        for neighbor in neighbors:
            neighbor_is_developer = neighbor.skills in developer_skills
            neighbor_is_tester = neighbor.skills == "testing"

            # Если тестировщик рядом с разработчиком - ошибка!
            if (is_tester and neighbor_is_developer) or (
                is_developer and neighbor_is_tester
            ):
                raise ValidationError(
                    f"Нельзя размещать тестировщиков и разработчиков за соседними столами! "
                    f"За столом №{neighbor.desk.number} сидит {neighbor.get_skills_display()}."
                )


# ========================================
# ДОПОЛНИТЕЛЬНЫЕ МОДЕЛИ (оставлены для совместимости)
# ========================================
class Desk(models.Model):
    number = models.IntegerField(
        "Номер стола", unique=True, help_text="Уникальный номер рабочего стола"
    )

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ["number"]

    def __str__(self):
        return f"Стол №{self.number}"


class Employee(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, verbose_name="Стол")
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        verbose_name="Сотрудник",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Привязка к столу"
        verbose_name_plural = "Привязки к столам"

    def __str__(self):
        return (
            f"{self.person} - {self.desk}"
            if self.person
            else f"Стол {self.desk.number}"
        )
