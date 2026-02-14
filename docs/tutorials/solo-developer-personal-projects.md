# Tutorial: Solo Developer - Managing Multiple Personal Projects

**Time to Complete**: 15 minutes
**Difficulty**: Beginner
**Prerequisites**:
- DevSync installed (`pip install devsync`)
- Working with 2+ projects that use different frameworks or conventions
- Using Claude Code, Cursor, Windsurf, or GitHub Copilot

## The Scenario

You're a freelance developer working on three different projects:
1. **Project A**: Django REST API with strict type hints
2. **Project B**: React TypeScript app with Jest testing
3. **Project C**: Python data science notebook with specific documentation style

Every time you switch projects, you spend 5-10 minutes reminding your AI assistant about project-specific conventions. You want your AI to instantly "know" which project you're working on.

## What You'll Learn

- How to download framework-specific instruction packages
- How to install packages to specific projects
- How to verify AI assistant configuration
- How to update packages when conventions change

## Step 1: Identify Your Needs

First, let's identify what packages would help for each project.

**Project A (Django)**: Needs Django best practices, REST API conventions, type hints
**Project B (React)**: Needs React patterns, TypeScript conventions, Jest testing
**Project C (Data Science)**: Needs notebook best practices, documentation standards

## Step 2: Discover Available Packages

Search for relevant packages (we'll create a discovery mechanism, but for now, let's assume you found these packages):

```bash
# List available packages from the community registry (future feature)
# For now, we'll use GitHub repos as package sources

# Django packages
# Example: github.com/ai-config-examples/django-rest-framework

# React packages
# Example: github.com/ai-config-examples/react-typescript

# Data Science packages
# Example: github.com/ai-config-examples/python-data-science
```

## Step 3: Set Up Project A (Django API)

Navigate to your Django project (replace with your actual project path):

```bash
# Example - replace with your actual project path
cd ~/projects/project-a-django-api
# Or: cd ~/code/my-django-project
# Or: cd /path/to/your/django/project
```

Verify you're in a git repository (DevSync works best with git projects):

```bash
git status
# Should show: On branch main
```

Create a sample Django instruction package for this tutorial:

```bash
# Create a local package for testing
mkdir -p /tmp/django-rest-package
cd /tmp/django-rest-package

# Create package manifest
cat > ai-config-kit-package.yaml << 'EOF'
name: django-rest-framework
version: 1.0.0
description: Django REST Framework best practices and conventions
author: AI Config Community
namespace: ai-config-examples/django-rest-framework
license: MIT

components:
  instructions:
    - name: django-views
      description: Django view patterns and best practices
      file: instructions/django-views.md
      tags: [django, views, api]

    - name: django-serializers
      description: DRF serializer conventions
      file: instructions/django-serializers.md
      tags: [django, serializers]

    - name: django-type-hints
      description: Python type hints for Django
      file: instructions/django-type-hints.md
      tags: [django, typing, python]

  resources:
    - name: .editorconfig
      description: EditorConfig for Django projects
      file: resources/editorconfig.txt
      install_path: .editorconfig
      checksum: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
EOF

# Create instructions directory
mkdir -p instructions

# Create django-views instruction
cat > instructions/django-views.md << 'EOF'
# Django REST Framework View Patterns

When writing Django REST Framework views, follow these conventions:

## Class-Based Views (CBV)

Always use viewsets for standard CRUD operations:

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles.

    Provides list, create, retrieve, update, and destroy actions.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        return super().get_queryset().filter(author=self.request.user)
```

## Function-Based Views (FBV)

For custom endpoints, use `@api_view` decorator:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def custom_action(request):
    """Custom endpoint for specific business logic."""
    # Implementation here
    return Response({'status': 'success'})
```

## Error Handling

Always use DRF's exception classes:

```python
from rest_framework.exceptions import ValidationError, NotFound

def validate_data(data):
    if not data.get('title'):
        raise ValidationError({'title': 'This field is required'})
```

## When helping with Django views:

1. Prefer viewsets over generic views for CRUD
2. Always include docstrings
3. Use type hints for parameters and return values
4. Implement proper permission checking
5. Filter querysets based on user context
6. Use DRF's built-in exception handling
EOF

# Create django-serializers instruction
cat > instructions/django-serializers.md << 'EOF'
# Django REST Framework Serializer Conventions

## Model Serializers

Use ModelSerializer for standard model serialization:

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model."""

    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'author']

    def validate_title(self, value: str) -> str:
        """Validate article title."""
        if len(value) < 10:
            raise serializers.ValidationError("Title must be at least 10 characters")
        return value
```

## Nested Serializers

For nested relationships:

```python
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author']

class ArticleDetailSerializer(serializers.ModelSerializer):
    """Detailed article serializer with nested comments."""

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'comments']
```

## When helping with serializers:

1. Use ModelSerializer for models
2. Add docstrings to all serializers
3. Use `validate_<field>` methods for field-level validation
4. Use `validate()` for object-level validation
5. Specify read_only_fields explicitly
6. Use type hints in validation methods
EOF

# Create django-type-hints instruction
cat > instructions/django-type-hints.md << 'EOF'
# Python Type Hints for Django Projects

Always use type hints for better code clarity and IDE support.

## Django Models

```python
from django.db import models
from django.contrib.auth.models import User
from typing import Optional

class Article(models.Model):
    """Article model with type hints."""

    title: str = models.CharField(max_length=200)
    content: str = models.TextField()
    author: User = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def get_excerpt(self, length: int = 100) -> str:
        """Get article excerpt."""
        return self.content[:length] + "..." if len(self.content) > length else self.content

    @classmethod
    def get_by_author(cls, author: User) -> models.QuerySet['Article']:
        """Get articles by author."""
        return cls.objects.filter(author=author)
```

## Django Views

```python
from django.http import HttpRequest, HttpResponse, JsonResponse
from typing import Any, Dict

def article_detail(request: HttpRequest, article_id: int) -> JsonResponse:
    """Get article details."""
    article = Article.objects.get(id=article_id)
    data: Dict[str, Any] = {
        'id': article.id,
        'title': article.title,
        'content': article.content,
    }
    return JsonResponse(data)
```

## DRF Serializers

```python
from rest_framework import serializers
from typing import Any, Dict

class ArticleSerializer(serializers.ModelSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate article data."""
        # Validation logic
        return attrs
```

## When helping with Django code:

1. Always add type hints to function parameters
2. Add return type hints to functions
3. Use `QuerySet['ModelName']` for querysets
4. Import types from `typing` module when needed
5. Use `Optional[Type]` for nullable values
EOF

# Create resources directory
mkdir -p resources
touch resources/editorconfig.txt
```

Now install the package to your Django project:

```bash
# Navigate back to your Django project
cd ~/projects/project-a-django-api  # Use your actual project path

# Install the package
aiconfig package install /tmp/django-rest-package --ide claude

# You should see output like:
# ✓ Package 'django-rest-framework' installed successfully
#
# Installed components:
#   ✓ django-views (instruction)
#   ✓ django-serializers (instruction)
#   ✓ django-type-hints (instruction)
#   ✓ .editorconfig (resource)
#
# 4/4 components installed to .claude/
```

Verify the installation:

```bash
# Check what was installed
ls -la .claude/rules/
# Should show:
# django-views.md
# django-serializers.md
# django-type-hints.md

# Check the package is tracked
cat .ai-config-kit/packages.json
```

You should see JSON like this:

```json
[
  {
    "package_name": "django-rest-framework",
    "namespace": "ai-config-examples/django-rest-framework",
    "version": "1.0.0",
    "installed_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00",
    "scope": "project",
    "components": [
      {
        "type": "instruction",
        "name": "django-views",
        "installed_path": ".claude/rules/django-views.md",
        "checksum": "sha256:...",
        "status": "installed"
      },
      {
        "type": "instruction",
        "name": "django-serializers",
        "installed_path": ".claude/rules/django-serializers.md",
        "checksum": "sha256:...",
        "status": "installed"
      },
      {
        "type": "instruction",
        "name": "django-type-hints",
        "installed_path": ".claude/rules/django-type-hints.md",
        "checksum": "sha256:...",
        "status": "installed"
      },
      {
        "type": "resource",
        "name": ".editorconfig",
        "installed_path": ".editorconfig",
        "checksum": "sha256:...",
        "status": "installed"
      }
    ],
    "status": "complete"
  }
]
```

## Step 4: Test the Configuration

Open Claude Code in your Django project and test:

```bash
# If using Claude Code CLI
claude "Create a new viewset for managing blog posts with these fields: title, content, author, published_date. Include proper permissions and filtering."
```

Claude should now:
- Use ViewSet pattern (from django-views.md)
- Include type hints (from django-type-hints.md)
- Follow serializer conventions (from django-serializers.md)
- Add proper docstrings and validation

## Step 5: Set Up Project B (React TypeScript)

Now switch to your React project (replace with your actual project path):

```bash
# Example - replace with your actual project path
cd ~/projects/project-b-react-app
```

Create a React TypeScript package:

```bash
mkdir -p /tmp/react-typescript-package
cd /tmp/react-typescript-package

# Create package manifest
cat > ai-config-kit-package.yaml << 'EOF'
name: react-typescript-testing
version: 1.0.0
description: React TypeScript patterns and Jest testing conventions
author: AI Config Community
namespace: ai-config-examples/react-typescript
license: MIT

components:
  instructions:
    - name: react-components
      description: React component patterns with TypeScript
      file: instructions/react-components.md
      tags: [react, typescript, components]

    - name: react-hooks
      description: Custom hooks conventions
      file: instructions/react-hooks.md
      tags: [react, hooks, typescript]

    - name: jest-testing
      description: Jest testing patterns for React
      file: instructions/jest-testing.md
      tags: [testing, jest, react]
EOF

mkdir -p instructions

cat > instructions/react-components.md << 'EOF'
# React TypeScript Component Patterns

## Functional Components with TypeScript

Always use typed props and proper component structure:

```typescript
import React from 'react';

interface ArticleProps {
  id: number;
  title: string;
  content: string;
  author: {
    name: string;
    email: string;
  };
  onDelete?: (id: number) => void;
}

export const Article: React.FC<ArticleProps> = ({
  id,
  title,
  content,
  author,
  onDelete
}) => {
  const handleDelete = () => {
    if (onDelete) {
      onDelete(id);
    }
  };

  return (
    <article className="article">
      <h2>{title}</h2>
      <p className="author">By {author.name}</p>
      <div>{content}</div>
      {onDelete && (
        <button onClick={handleDelete}>Delete</button>
      )}
    </article>
  );
};
```

## When creating React components:

1. Use `interface` for props (not `type`)
2. Use `React.FC<PropsType>` for functional components
3. Mark optional props with `?`
4. Destructure props in function parameters
5. Use proper event handler naming (`handle*`)
6. Export components as named exports
EOF

cat > instructions/react-hooks.md << 'EOF'
# Custom React Hooks Conventions

## Custom Hook Structure

```typescript
import { useState, useEffect } from 'react';

interface UseArticlesResult {
  articles: Article[];
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export const useArticles = (): UseArticlesResult => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/articles');
      const data = await response.json();
      setArticles(data);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  return {
    articles,
    loading,
    error,
    refetch: fetchArticles
  };
};
```

## When creating custom hooks:

1. Name hooks with `use` prefix
2. Return an object with named properties (not array)
3. Define return type interface
4. Use proper TypeScript types for all state
5. Include loading and error states for async operations
EOF

cat > instructions/jest-testing.md << 'EOF'
# Jest Testing Patterns for React

## Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Article } from './Article';

describe('Article', () => {
  const mockArticle = {
    id: 1,
    title: 'Test Article',
    content: 'Test content',
    author: {
      name: 'John Doe',
      email: 'john@example.com'
    }
  };

  it('renders article content', () => {
    render(<Article {...mockArticle} />);

    expect(screen.getByText('Test Article')).toBeInTheDocument();
    expect(screen.getByText('Test content')).toBeInTheDocument();
    expect(screen.getByText(/By John Doe/)).toBeInTheDocument();
  });

  it('calls onDelete when delete button clicked', () => {
    const handleDelete = jest.fn();
    render(<Article {...mockArticle} onDelete={handleDelete} />);

    fireEvent.click(screen.getByText('Delete'));

    expect(handleDelete).toHaveBeenCalledWith(1);
  });

  it('does not render delete button when onDelete not provided', () => {
    render(<Article {...mockArticle} />);

    expect(screen.queryByText('Delete')).not.toBeInTheDocument();
  });
});
```

## When writing tests:

1. Use `describe` blocks for grouping
2. Name tests clearly with 'it should...' pattern
3. Create mock data outside of tests
4. Use `screen.getByText` for queries
5. Test user interactions with `fireEvent`
6. Test both presence and absence of elements
EOF
```

Install to your React project:

```bash
# Navigate back to your React project
cd ~/projects/project-b-react-app  # Use your actual project path
aiconfig package install /tmp/react-typescript-package --ide cursor
```

## Step 6: Set Up Project C (Data Science)

Create a data science package:

```bash
mkdir -p /tmp/data-science-package
cd /tmp/data-science-package

cat > ai-config-kit-package.yaml << 'EOF'
name: python-data-science
version: 1.0.0
description: Python data science notebook best practices
author: AI Config Community
namespace: ai-config-examples/python-data-science
license: MIT

components:
  instructions:
    - name: notebook-structure
      description: Jupyter notebook organization
      file: instructions/notebook-structure.md
      tags: [jupyter, notebooks, data-science]

    - name: pandas-conventions
      description: Pandas code conventions
      file: instructions/pandas-conventions.md
      tags: [pandas, data-science]
EOF

mkdir -p instructions

cat > instructions/notebook-structure.md << 'EOF'
# Jupyter Notebook Structure

## Standard Notebook Organization

Every notebook should follow this structure:

### 1. Header Cell (Markdown)
```markdown
# Notebook Title

**Purpose**: Brief description of what this notebook does

**Author**: Your name
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Overview
- Data sources
- Key findings
- Dependencies
```

### 2. Imports Cell
```python
# Standard library
import os
from pathlib import Path
from typing import List, Dict

# Data manipulation
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
%matplotlib inline
sns.set_style('whitegrid')
pd.set_option('display.max_columns', None)
```

### 3. Configuration Cell
```python
# Paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")

# Constants
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
```

## When helping with notebooks:

1. Start with header describing purpose
2. Group imports logically
3. Define paths and constants upfront
4. Add markdown cells explaining each major section
5. Include visualization configuration
EOF

cat > instructions/pandas-conventions.md << 'EOF'
# Pandas Code Conventions

## DataFrames

Use descriptive variable names and type hints:

```python
import pandas as pd
from typing import List

def load_sales_data(file_path: str) -> pd.DataFrame:
    """
    Load sales data from CSV.

    Args:
        file_path: Path to CSV file

    Returns:
        DataFrame with columns: date, product, quantity, revenue
    """
    df = pd.read_csv(
        file_path,
        parse_dates=['date'],
        dtype={
            'product': 'string',
            'quantity': 'int64',
            'revenue': 'float64'
        }
    )
    return df

def calculate_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total revenue by month."""
    monthly_revenue = (
        df.groupby(df['date'].dt.to_period('M'))
        .agg({'revenue': 'sum'})
        .reset_index()
    )
    return monthly_revenue
```

## When helping with pandas:

1. Use method chaining with parentheses for readability
2. Specify dtypes in read_csv
3. Add docstrings to all data processing functions
4. Use descriptive DataFrame variable names
5. Include type hints
EOF
```

Install to your data science project:

```bash
# Navigate to your data science project
cd ~/projects/project-c-data-science  # Use your actual project path
aiconfig package install /tmp/data-science-package --ide claude
```

## Step 7: Verify All Projects

Let's verify each project is configured correctly:

```bash
# Project A (Django)
cd ~/projects/project-a-django-api
aiconfig package list
# Should show: django-rest-framework v1.0.0

# Project B (React)
cd ~/projects/project-b-react-app
aiconfig package list
# Should show: react-typescript-testing v1.0.0

# Project C (Data Science)
cd ~/projects/project-c-data-science
aiconfig package list
# Should show: python-data-science v1.0.0
```

## Step 8: Experience the Benefits

Now when you switch between projects, your AI assistant instantly has context:

**Django Project**:
```bash
cd ~/projects/project-a-django-api
# Ask: "Create a viewset for managing user profiles"
# AI knows: Use ModelViewSet, add type hints, include docstrings
```

**React Project**:
```bash
cd ~/projects/project-b-react-app
# Ask: "Create a component for displaying a list of articles"
# AI knows: Use TypeScript interfaces, React.FC, proper prop typing
```

**Data Science Project**:
```bash
cd ~/projects/project-c-data-science
# Ask: "Create a notebook to analyze monthly sales trends"
# AI knows: Proper notebook structure, pandas conventions, documentation
```

## Troubleshooting

### Issue: Package not found after installation

**Solution**: Check the .ai-config-kit directory exists:
```bash
ls -la .ai-config-kit/
# Should show: packages.json
```

### Issue: AI assistant not following instructions

**Solution**: Verify instructions were installed:
```bash
# For Claude Code
ls -la .claude/rules/

# For Cursor
ls -la .cursor/rules/
```

### Issue: Wrong IDE directory

**Solution**: Reinstall with correct `--ide` flag:
```bash
# For Claude Code
aiconfig package install <package> --ide claude

# For Cursor
aiconfig package install <package> --ide cursor

# For Windsurf
aiconfig package install <package> --ide winsurf

# For GitHub Copilot
aiconfig package install <package> --ide copilot
```

## Next Steps

- **Learn to create your own packages**: See [Creating Custom Packages](creating-custom-packages.md)
- **Share packages with your team**: See [Small Team Tutorial](small-team-shared-standards.md)
- **Update packages**: When conventions change, run `aiconfig package install <package> --force` to update

## Summary

You've successfully set up project-specific AI assistant configurations for three different projects. Now:

✅ No more repeating yourself when switching projects
✅ AI instantly knows project conventions
✅ Consistent code quality across all projects
✅ Easy to update conventions by reinstalling packages

**Time saved per project switch**: ~10 minutes
**Time saved per day** (switching 5 times): ~50 minutes
**Time saved per week**: ~4 hours
