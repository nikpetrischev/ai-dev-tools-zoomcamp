from django.db import models
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES: list[tuple[str, str]] = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    title: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField(blank=True, null=True)
    status: models.CharField = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    priority: models.IntegerField = models.IntegerField(default=0)
    due_date: models.DateTimeField = models.DateTimeField(blank=True, null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering: list[str] = ['-priority', 'due_date']
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs) -> None:
        """Save the task instance"""
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """Delete the task instance"""
        return super().delete(*args, **kwargs)
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
    
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == 'completed'
