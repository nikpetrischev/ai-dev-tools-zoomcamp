from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import Task
from typing import Any

def home(request: HttpRequest) -> HttpResponse:
    """Render home page"""
    return render(request, 'tasks/home.html')

def task_list(request: HttpRequest) -> HttpResponse:
    """Display list of all tasks"""
    tasks: list[Task] = Task.objects.all()  # type: ignore
    context: dict[str, Any] = {'tasks': tasks}
    return render(request, 'tasks/task_list.html', context)

def task_create(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """Handle task creation (GET form / POST create)"""
    if request.method == 'POST':
        title: str = request.POST.get('title', '')
        description: str = request.POST.get('description', '')
        due_date: str | None = request.POST.get('due_date') or None
        priority: int = int(request.POST.get('priority', 0))
        
        Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority
        )
        return redirect('tasks:task_list')
    return render(request, 'tasks/task_form.html')

def task_edit(request: HttpRequest, pk: int) -> HttpResponse | HttpResponseRedirect:
    """Handle task editing (GET form / POST update)"""
    task: Task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.title = request.POST.get('title', '')
        task.description = request.POST.get('description', '')
        task.due_date = request.POST.get('due_date') or None
        task.priority = int(request.POST.get('priority', 0))
        task.save()
        return redirect('tasks:task_list')
    
    context: dict[str, Any] = {'task': task}
    return render(request, 'tasks/task_form.html', context)

def task_delete(request: HttpRequest, pk: int) -> HttpResponse | HttpResponseRedirect:
    """Handle task deletion (GET confirmation / POST delete)"""
    task: Task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.delete()
        return redirect('tasks:task_list')
    
    context: dict[str, Any] = {'task': task}
    return render(request, 'tasks/task_confirm_delete.html', context)

def task_mark_resolved(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    """Mark a task as completed"""
    task: Task = get_object_or_404(Task, pk=pk)
    task.status = 'completed'
    task.save()
    return redirect('tasks:task_list')  # type: ignore
