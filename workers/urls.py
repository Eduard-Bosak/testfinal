# ========================================
# КОММЕНТАРИЙ ДЛЯ СТУДЕНТКИ:
# Это файл с URL-маршрутами для приложения workers
# Здесь определяются адреса страниц
# ========================================
from django.urls import path

from .views import detail, home, list

# ВАЖНО: app_name нужен для использования {% url 'workers:home' %} в шаблонах
app_name = 'workers'

urlpatterns = [
    # Главная страница (К3, К4)
    path('', home, name='home'),
    
    # Список всех сотрудников с пагинацией (К5)
    path('list/', list, name='list'),
    
    # Детальная страница сотрудника (К6)
    path('person/<int:pk>/', detail, name='detail'),
]

