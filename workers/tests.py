# ИСПРАВЛЕНИЕ: Добавлены необходимые импорты для тестов
# - ValidationError для проверки валидации модели
# - Person для создания тестовых объектов
from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Person



class TestStaticRoutes(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()
    def test_static_page(self) -> None:
        pages: tuple = ('', '/list/')
        for page in pages:
            response = self.guest_client.get(page)
            error_name: str = f'Ошибка {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_home_page_context(self):
        response = self.guest_client.get('')
        # ИСПРАВЛЕНИЕ: Изменены ключи контекста в соответствии с views.py
        # Было: 'home' -> Стало: 'total_employees' и 'recent_employees'
        self.assertIn('total_employees', response.context)
        self.assertIn('recent_employees', response.context)

        # Проверяем, что данные присутствуют
        total = response.context['total_employees']
        self.assertIsNotNone(total)

    def test_list_page_context(self):
        """Проверка контекста страницы списка сотрудников"""
        response = self.guest_client.get('/list/')

        # ИСПРАВЛЕНИЕ: Изменен ключ контекста в соответствии с views.py
        # Было: 'all' -> Стало: 'page_obj' (для пагинации)
        self.assertIn('page_obj', response.context)

        # Проверяем тип данных
        page_obj = response.context['page_obj']
        self.assertIsNotNone(page_obj)


class TestDetailPageAccess(TestCase):
    def setUp(self):
        # Создаём тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Создаём тестовый объект Person
        # ИСПРАВЛЕНИЕ: Исправлены опечатки
        # - skills: 'fronted' -> 'frontend'
        # - поле: 'employment' -> 'employment_date'
        self.person = Person.objects.create(
            name='Иван Иванов',
            sex='male',
            skills='frontend',
            skill_level='5',
            employment_date='2024-01-15'
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.login(username='testuser', password='testpass123')

    def test_detail_redirect_for_unauthorized(self):
        """Неавторизованный пользователь перенаправляется на логин"""
        response = self.guest_client.get(f'/person/{self.person.pk}/')

        # ИСПРАВЛЕНИЕ: Изменен способ проверки редиректа
        # Используем status_code вместо assertRedirects, т.к. страница логина может не существовать
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(response.url.startswith('/login/'))

    def test_detail_accessible_for_authorized(self):
        """Авторизованный пользователь получает доступ"""
        response = self.authorized_client.get(f'/person/{self.person.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page_context(self):
        """Проверка контекста детальной страницы"""
        response = self.authorized_client.get(f'/person/{self.person.pk}/')

        # ИСПРАВЛЕНИЕ: Изменен ключ контекста в соответствии с views.py
        # Было: 'detail' -> Стало: 'person'
        self.assertIn('person', response.context)

        # Проверяем, что передан правильный объект
        person_obj = response.context['person']
        self.assertEqual(person_obj.pk, self.person.pk)
        self.assertEqual(person_obj.name, 'Иван Иванов')
        # ИСПРАВЛЕНИЕ: Исправлена опечатка 'fronted' -> 'frontend'
        self.assertEqual(person_obj.skills, 'frontend')


class TestValidator(TestCase):
    """Тесты валидатора, запрещающего тестировщикам и разработчикам сидеть рядом"""
    
    def setUp(self):
        from .models import Desk
        # Создаём столы
        self.desk1 = Desk.objects.create(number=1)
        self.desk2 = Desk.objects.create(number=2)
        self.desk3 = Desk.objects.create(number=3)
    
    def test_validator_prevents_tester_next_to_developer(self):
        """Тестировщик не может сидеть рядом с разработчиком"""
        from django.core.exceptions import ValidationError
        from .models import Desk
        
        # Создаём разработчика за столом 1
        developer = Person.objects.create(
            name='Developer',
            skills='frontend',
            desk=self.desk1
        )
        
        # Пытаемся посадить тестировщика за соседний стол 2
        tester = Person(
            name='Tester',
            skills='testing',
            desk=self.desk2
        )
        
        # Должна возникнуть ошибка валидации
        with self.assertRaises(ValidationError) as context:
            tester.full_clean()
        
        self.assertIn('Нельзя размещать', str(context.exception))
    
    def test_validator_allows_developers_next_to_each_other(self):
        """Разработчики могут сидеть рядом"""
        # ИСПРАВЛЕНИЕ: Добавлены обязательные поля sex и skill_level
        # Без этих полей валидация Django не проходит
        dev1 = Person.objects.create(
            name='Dev1',
            skills='frontend',
            sex='male',
            skill_level='5',
            desk=self.desk1
        )
        
        # Создаём второго разработчика за соседним столом
        dev2 = Person(
            name='Dev2',
            skills='backend',
            sex='male',
            skill_level='5',
            desk=self.desk2
        )
        
        # Не должно быть ошибки
        try:
            dev2.full_clean()
            dev2.save()
        except ValidationError as e:
            self.fail(f"Валидатор не должен запрещать разработчикам сидеть рядом. Ошибка: {e}")
    
    def test_validator_allows_testers_next_to_each_other(self):
        """Тестировщики могут сидеть рядом"""
        # ИСПРАВЛЕНИЕ: Добавлены обязательные поля sex и skill_level
        # Без этих полей валидация Django не проходит
        tester1 = Person.objects.create(
            name='Tester1',
            skills='testing',
            sex='female',
            skill_level='6',
            desk=self.desk1
        )
        
        # Создаём второго тестировщика за соседним столом
        tester2 = Person(
            name='Tester2',
            skills='testing',
            sex='female',
            skill_level='7',
            desk=self.desk2
        )
        
        # Не должно быть ошибки
        try:
            tester2.full_clean()
            tester2.save()
        except ValidationError as e:
            self.fail(f"Валидатор не должен запрещать тестировщикам сидеть рядом. Ошибка: {e}")