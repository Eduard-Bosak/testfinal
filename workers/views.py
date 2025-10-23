# ========================================
# ИСПРАВЛЕНО: Убраны дублирующие импорты, добавлены нужные
# ========================================
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Person


def home(request):
    template_name = "HomeWork/index.html"
    total_employees = Person.objects.count()
    recent_employees = Person.objects.all().order_by("-employment_date")[:4]
    context = {
        "total_employees": total_employees,  # Общее количество
        "recent_employees": recent_employees,  # 4 последних сотрудника
    }
    return render(request, template_name, context)


def list(request):
    template_name = "HomeWork/personal.html"
    all_employees = Person.objects.all().order_by("-employment_date")
    paginator = Paginator(all_employees, 10)  # 10 записей на странице
    page_number = request.GET.get("page")  # Получаем номер страницы из URL
    page_obj = paginator.get_page(page_number)  # Получаем объекты для текущей страницы
    context = {"page_obj": page_obj}
    return render(request, template_name, context)


# ========================================
# ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О СОТРУДНИКЕ (К6 - требование ТЗ)
# ========================================
@login_required
def detail(request, pk):
    template_name = "HomeWork/detail.html"
    person = get_object_or_404(Person.objects.select_related("desk"), pk=pk)
    context = {"person": person}
    return render(request, template_name, context)
