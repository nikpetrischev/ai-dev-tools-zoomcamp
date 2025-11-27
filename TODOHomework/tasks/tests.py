from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Task
from django.test.utils import override_settings
from django.urls import path
from . import views

class TaskModelTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            priority=1
        )
    
    def test_task_creation(self):
        """Test basic task creation"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'Test Description')
        self.assertEqual(self.task.status, 'pending')
        self.assertEqual(self.task.priority, 1)
    
    def test_task_minimal_creation(self):
        """Test task creation with only title"""
        task = Task.objects.create(title='Minimal Task')
        self.assertEqual(task.title, 'Minimal Task')
        self.assertIsNone(task.description)
        self.assertEqual(task.status, 'pending')
    
    def test_task_string_representation(self):
        """Test task __str__ method"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_with_due_date(self):
        """Test task creation with due date"""
        due_date = timezone.now() + timedelta(days=5)
        task = Task.objects.create(title='Task with Due Date', due_date=due_date)
        self.assertEqual(task.due_date, due_date)
    
    def test_task_status_choices(self):
        """Test task status field"""
        self.assertIn(self.task.status, ['pending', 'in_progress', 'completed'])
        self.task.status = 'completed'
        self.task.save()
        self.assertEqual(self.task.status, 'completed')
    
    def test_task_ordering(self):
        """Test tasks are ordered by priority and due_date"""
        Task.objects.all().delete()
        task1 = Task.objects.create(title='Low Priority', priority=0)
        task2 = Task.objects.create(title='High Priority', priority=5)
        tasks = Task.objects.all()
        self.assertEqual(tasks[0].priority, 5)
        self.assertEqual(tasks[1].priority, 0)
    
    def test_task_timestamps(self):
        """Test created_at and updated_at timestamps"""
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.task1 = Task.objects.create(
            title='Task 1',
            description='Description 1',
            priority=1
        )
        self.task2 = Task.objects.create(
            title='Task 2',
            description='Description 2',
            priority=2,
            status='completed'
        )
    
    def test_task_list_view(self):
        """Test task list view displays all tasks"""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')
    
    def test_task_list_context(self):
        """Test task list view context"""
        response = self.client.get('/tasks/')
        self.assertIn('tasks', response.context)
        self.assertEqual(len(response.context['tasks']), 2)
    
    def test_task_create_get(self):
        """Test task create form GET request"""
        response = self.client.get('/tasks/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
    
    def test_task_create_post(self):
        """Test task creation POST request"""
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'priority': 3
        }
        response = self.client.post('/tasks/create/', data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/tasks/')
        self.assertTrue(Task.objects.filter(title='New Task').exists())
    
    def test_task_create_with_due_date(self):
        """Test task creation with due date"""
        due_date = (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        data = {
            'title': 'Task with Due Date',
            'description': 'Test',
            'priority': 1,
            'due_date': due_date
        }
        response = self.client.post('/tasks/create/', data)
        task = Task.objects.get(title='Task with Due Date')
        self.assertIsNotNone(task.due_date)
    
    def test_task_edit_get(self):
        """Test task edit form GET request"""
        response = self.client.get(f'/tasks/{self.task1.pk}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
        self.assertContains(response, self.task1.title)
    
    def test_task_edit_post(self):
        """Test task edit POST request"""
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'priority': 5
        }
        response = self.client.post(f'/tasks/{self.task1.pk}/edit/', data)
        self.assertRedirects(response, '/tasks/')
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Task')
        self.assertEqual(self.task1.priority, 5)
    
    def test_task_edit_nonexistent(self):
        """Test edit view with non-existent task"""
        response = self.client.get('/tasks/999/edit/')
        self.assertEqual(response.status_code, 404)
    
    def test_task_delete_get(self):
        """Test task delete confirmation page"""
        response = self.client.get(f'/tasks/{self.task1.pk}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_confirm_delete.html')
    
    def test_task_delete_post(self):
        """Test task deletion POST request"""
        task_id = self.task1.pk
        response = self.client.post(f'/tasks/{task_id}/delete/')
        self.assertRedirects(response, '/tasks/')
        self.assertFalse(Task.objects.filter(pk=task_id).exists())
    
    def test_task_delete_nonexistent(self):
        """Test delete view with non-existent task"""
        response = self.client.get('/tasks/999/delete/')
        self.assertEqual(response.status_code, 404)
    
    def test_task_mark_resolved(self):
        """Test marking task as resolved"""
        self.assertEqual(self.task1.status, 'pending')
        response = self.client.get(f'/tasks/{self.task1.pk}/resolve/')
        self.assertRedirects(response, '/tasks/')
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'completed')
    
    def test_task_mark_resolved_nonexistent(self):
        """Test mark resolved with non-existent task"""
        response = self.client.get('/tasks/999/resolve/')
        self.assertEqual(response.status_code, 404)