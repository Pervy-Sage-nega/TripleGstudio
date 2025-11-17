from django.db import models
from django.contrib.auth.models import User
from site_diary.models import Project

class ProjectAssignment(models.Model):
    ROLE_CHOICES = [
        ('project_manager', 'Project Manager'),
        ('architect', 'Architect'),
        ('site_engineer', 'Site Engineer'),
        ('engineer', 'Engineer'),  # Added this to match assignment data
        ('foreman', 'Foreman'),
        ('supervisor', 'Supervisor'),

    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_made')
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['project', 'user', 'role']
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} - {self.project.name}"