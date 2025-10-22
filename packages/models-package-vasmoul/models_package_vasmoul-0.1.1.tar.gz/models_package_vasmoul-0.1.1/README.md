# models_package_vasmoul

A reusable Django models module containing the core data models for a Project Management Dashboard application.

This package can be used in any Django project to manage projects, their milestones, team members, and events.

## Features

- `Project` model with title, description, owner, tags, progress, status, health, and deletion status.
- `Milestone` model to track project milestones and progress.
- `TeamMember` model for project team assignments.
- `Event` model to log actions related to projects.
- Easily integrated into existing Django projects.

## Installation

You can install the package from PyPI:

```bash
pip install models_package_vasmoul

# Usage
# Add the app to your Django INSTALLED_APPS:

INSTALLED_APPS = [
    ...
    'models_package_vasmoul',
]

# Run migrations
```bash
python manage.py makemigrations models_package_vasmoul
python manage.py migrate

# Usage of models
from models_package_vasmoul.models import Project, Milestone, TeamMember, Event

# Create a new project
project = Project.objects.create(
    title="Project Alpha",
    short_description="A short description",
    owner="John Doe",
    status="in_progress",
    health="green"
)

# Add a milestone
Milestone.objects.create(
    project=project,
    title="Milestone 1",
    description="Initial phase",
    due_date="2025-12-01",
    progress=50
)
