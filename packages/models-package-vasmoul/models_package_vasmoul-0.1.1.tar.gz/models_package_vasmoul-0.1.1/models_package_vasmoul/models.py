from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models import Sum, F

# Create the Project model
class Project(models.Model):

    # Possible health values for a project
    HEALTH_CHOICES = [
       # Healthy
       ('green', 'Green'),
       # Minor issues
       ('yellow', 'Yellow'),
       # At risk
       ('red', 'Red'),
    ]

    # Possible health statuses for a project
    STATUS_CHOICES = [
       # Not started
       ('not_started', 'Not started'),
       # In progress
       ('in_progress', 'In progress'),
       # On hold
       ('on_hold', 'On hold'),
       # Completed
       ('completed', 'Completed'),
       # Cancelled
       ('cancelled', 'Cancelled'),
    ]

    # Attributes of the Project
    
    # Title
    title = models.CharField(max_length=255)
    
    # Short Description
    short_description = models.TextField(blank=True)
    
    # Project Owner
    owner = models.CharField(max_length=150)

    # Last updated date
    last_updated = models.DateTimeField(auto_now=True)

    # Progress (0.00%-100.00%)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Tags
    tags = models.JSONField(default=list, blank=True)

    # Health
    health = models.CharField(max_length=10, choices=HEALTH_CHOICES, default='green')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    # Soft delete for recover
    deleted = models.BooleanField(default=False)

    # Optimistic concurrency safeguard (version)
    version = models.IntegerField(default=1)

    # This field stores the full-text search vector
    search_vector = SearchVectorField(null=True)
    
    # Created a GIN (Generalized Inverted Index) on the search_vector.
    # This improves performance of PostgreSQL full-text search queries
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
                   ]

    def __str__(self):
        # Return the string representation of the Project (its title)
        return self.title
    
    # Update project's progress based on the progress of its milestones
    def update_progress(self):
        milestones = self.milestones.all()
        total_weight = milestones.aggregate(total=Sum('weight'))['total'] or 0
        if total_weight == 0:
            self.progress = 0
        else:
            weighted_progress = milestones.aggregate(
                total=Sum(F('progress') * F('weight'))
            )['total'] or 0
            self.progress = round(weighted_progress / total_weight, 2)
        self.save(update_fields=['progress', 'last_updated'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
 
# Create the Milestone model
class Milestone(models.Model):
    
    # Relation with Project model
    # Each milestone belongs to one project - ForeignKey to Project models
    project = models.ForeignKey('Project', related_name='milestones', on_delete=models.CASCADE)

    # Attributes of the Milestone

    # Title
    title = models.CharField(max_length=255)
    
    # Description
    description = models.TextField(blank=True)

    # Due date
    due_date = models.DateField(null=True, blank=True)

    # Progress (0.00%-100.00%)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Weight
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    def __str__(self):
        # Return the project's and Milestone's titles
        return f"{self.project.title} - {self.title}"
    
# Create the TeamRoster model
class TeamRoster(models.Model):

    # Possible health values for a project
    ROLE_CHOICES = [
        # Project Manager
        ('pm', 'Project Manager'),
        # Developer
        ('dev', 'Developer'),
        # QA
        ('qa', 'QA'),
        # Other
        ('other', 'Other'),
    ]

    # Relation with Project model
    # One team member can be in multiple projects - Many-to-many to Project models
    projects = models.ManyToManyField('Project', related_name='team')

    # Attributes of the TeamRoster

    # Name
    name = models.CharField(max_length=150)

    # Role
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='other')

    # Capacity Percent
    capacity_percent = models.DecimalField(max_digits=5, decimal_places=2, default=100)

    def __str__(self):
        # Return the name and role of the team member
        return f"{self.name} ({self.role})"
    
# Create the RecentActivityEvent model
class RecentActivityEvent(models.Model):

    # Relation with Project model
    # Each activity event corresponds to one project - ForeignKey to Project models
    project = models.ForeignKey('Project', related_name='events', on_delete=models.CASCADE)

    # Attributes of the RecentActivityEvent
    
    # Who performed the event
    created_by = models.CharField(max_length=150, blank=True)

    # Description of the event
    description = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return the title of the project, the description of the event, who created and when
        return f"[{self.project.title}] {self.description} by {self.created_by} at {self.created_at}"