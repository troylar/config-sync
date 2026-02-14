# Package Examples

**Real-world package examples for common development scenarios**

This guide provides complete, ready-to-use package examples for various technologies and workflows. Each example includes the full manifest, component files, and usage instructions.

## Table of Contents

- [Python Development](#python-development)
- [JavaScript/TypeScript](#javascripttypescript)
- [Web Frameworks](#web-frameworks)
- [Testing & Quality](#testing--quality)
- [DevOps & Deployment](#devops--deployment)
- [Multi-Language Packages](#multi-language-packages)

---

## Python Development

### Example 1: Python Best Practices

Complete Python development setup with style, testing, and type checking.

**Package structure:**
```
python-best-practices/
├── ai-config-kit-package.yaml
├── README.md
├── instructions/
│   ├── style-guide.md
│   ├── type-hints.md
│   └── testing.md
├── hooks/
│   └── pre-commit.sh
├── commands/
│   ├── test.sh
│   └── lint.sh
└── resources/
    ├── .gitignore
    └── pyproject.toml
```

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: python-best-practices
version: 1.0.0
description: Complete Python development best practices and tooling
author: Python Team
author_email: python@example.com
namespace: python/development
license: MIT
keywords: [python, best-practices, testing, type-checking]

components:
  instructions:
    - name: style-guide
      description: PEP 8 style guidelines with modern Python patterns
      file: instructions/style-guide.md
      tags: [python, style, pep8]

    - name: type-hints
      description: Type hinting best practices with mypy
      file: instructions/type-hints.md
      tags: [python, typing, mypy]

    - name: testing
      description: Testing strategies with pytest and coverage
      file: instructions/testing.md
      tags: [python, testing, pytest]

  hooks:
    - name: pre-commit
      description: Run black, ruff, and mypy before commits
      file: hooks/pre-commit.sh
      tags: [git, python, quality]

  commands:
    - name: test
      description: Run pytest with coverage reporting
      file: commands/test.sh
      tags: [testing, pytest]

    - name: lint
      description: Run ruff linter with auto-fix
      file: commands/lint.sh
      tags: [linting, code-quality]

  resources:
    - name: gitignore
      description: Python-specific .gitignore
      file: resources/.gitignore
      install_path: .gitignore
      tags: [git, python]

    - name: pyproject
      description: Standard pyproject.toml configuration
      file: resources/pyproject.toml
      install_path: pyproject.toml
      tags: [python, config]
```

**Instruction example** (`instructions/style-guide.md`):
```markdown
# Python Style Guide

Follow PEP 8 and modern Python best practices.

## Line Length

- **Maximum**: 120 characters (not 79)
- **Docstrings**: 72 characters

## Formatting

Use `black` for automatic formatting:
```bash
black .
```

## Import Order

1. Standard library
2. Third-party packages
3. Local application/library

Example:
```python
import os
from pathlib import Path

import requests
from django.conf import settings

from myapp.models import User
from myapp.utils import helper
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | `snake_case` | `user_count` |
| Functions | `snake_case` | `get_user_by_id` |
| Classes | `PascalCase` | `UserProfile` |
| Constants | `UPPER_CASE` | `MAX_CONNECTIONS` |
| Private | `_leading_underscore` | `_internal_method` |

## Type Hints

Always use type hints for function signatures:

```python
def process_users(users: list[dict], limit: int = 10) -> list[str]:
    """Process user data and return usernames."""
    return [u["name"] for u in users[:limit]]
```
```

**Hook example** (`hooks/pre-commit.sh`):
```bash
#!/usr/bin/env bash
# Pre-commit hook for Python projects

set -e

echo "Running pre-commit checks..."

# Black formatting
echo "→ Checking formatting (black)..."
if command -v black &> /dev/null; then
    black --check . || {
        echo "❌ Formatting issues found. Run 'black .' to fix."
        exit 1
    }
else
    echo "⚠️  black not installed"
fi

# Ruff linting
echo "→ Running linter (ruff)..."
if command -v ruff &> /dev/null; then
    ruff check . || {
        echo "❌ Linting issues found. Run 'ruff check --fix .' to fix."
        exit 1
    }
else
    echo "⚠️  ruff not installed"
fi

# Type checking
echo "→ Type checking (mypy)..."
if command -v mypy &> /dev/null; then
    mypy . || {
        echo "❌ Type errors found."
        exit 1
    }
else
    echo "⚠️  mypy not installed"
fi

echo "✓ All pre-commit checks passed!"
```

**Installation:**
```bash
aiconfig package install ./python-best-practices --ide claude
```

---

### Example 2: Django Development

Django-specific package with models, views, and deployment.

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: django-development
version: 2.1.0
description: Django best practices with ORM patterns and testing
author: Django Team
namespace: web-frameworks/django
license: MIT
keywords: [django, python, web, orm]

components:
  instructions:
    - name: django-models
      description: Model design patterns and best practices
      file: instructions/models.md
      tags: [django, orm, models]

    - name: django-views
      description: CBV vs FBV and view patterns
      file: instructions/views.md
      tags: [django, views]

    - name: django-testing
      description: Testing Django applications
      file: instructions/testing.md
      tags: [django, testing]

  hooks:
    - name: pre-commit
      description: Check migrations and run tests
      file: hooks/pre-commit.sh
      tags: [django, git]

  commands:
    - name: migrate
      description: Run database migrations
      file: commands/migrate.sh
      tags: [django, database]

    - name: test
      description: Run Django test suite
      file: commands/test.sh
      tags: [django, testing]

  resources:
    - name: settings-template
      description: Django settings best practices
      file: resources/settings.py
      install_path: config/settings_template.py
      tags: [django, config]
```

**Instruction example** (`instructions/models.md`):
```markdown
# Django Model Best Practices

## Model Design

### Keep Models Focused

Each model should represent one entity:

```python
# Good: Focused model
class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

# Bad: Too many responsibilities
class User(models.Model):
    # User data, settings, preferences, notifications all mixed
    ...
```

### Use Model Methods

Add business logic to models:

```python
class Order(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)

    def calculate_tax(self) -> Decimal:
        """Calculate tax amount."""
        return self.total * self.tax_rate

    def get_total_with_tax(self) -> Decimal:
        """Get total including tax."""
        return self.total + self.calculate_tax()
```

### Index Strategic Fields

Add indexes for frequently queried fields:

```python
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    published_at = models.DateTimeField(db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['published_at', 'author']),
        ]
```
```

---

## JavaScript/TypeScript

### Example 3: React Development

React best practices with TypeScript and testing.

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: react-typescript
version: 3.0.0
description: React + TypeScript development with best practices
author: Frontend Team
namespace: frontend/react
license: MIT
keywords: [react, typescript, frontend, components]

components:
  instructions:
    - name: component-patterns
      description: React component design patterns
      file: instructions/components.md
      tags: [react, components, patterns]

    - name: typescript-types
      description: TypeScript typing for React
      file: instructions/typescript.md
      tags: [react, typescript, types]

    - name: testing
      description: Testing React components with RTL
      file: instructions/testing.md
      tags: [react, testing, rtl]

  hooks:
    - name: pre-commit
      description: Run ESLint and Prettier
      file: hooks/pre-commit.sh
      tags: [git, javascript, linting]

  commands:
    - name: test
      description: Run Jest with coverage
      file: commands/test.sh
      tags: [testing, jest]

  resources:
    - name: tsconfig
      description: TypeScript configuration for React
      file: resources/tsconfig.json
      install_path: tsconfig.json
      tags: [typescript, config]

    - name: eslintrc
      description: ESLint configuration
      file: resources/.eslintrc.json
      install_path: .eslintrc.json
      tags: [linting, config]
```

**Instruction example** (`instructions/components.md`):
```markdown
# React Component Patterns

## Component Structure

### Functional Components with Hooks

Always use functional components:

```tsx
// Good: Functional component with proper typing
interface UserCardProps {
  user: User;
  onEdit: (id: string) => void;
}

export const UserCard: React.FC<UserCardProps> = ({ user, onEdit }) => {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="user-card">
      <h2>{user.name}</h2>
      <button onClick={() => onEdit(user.id)}>Edit</button>
    </div>
  );
};

// Bad: Class component (avoid)
class UserCard extends React.Component {
  ...
}
```

## State Management

### useState for Local State

```tsx
const [count, setCount] = useState(0);
const [user, setUser] = useState<User | null>(null);
```

### useReducer for Complex State

```tsx
type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset'; value: number };

const counterReducer = (state: number, action: Action): number => {
  switch (action.type) {
    case 'increment': return state + 1;
    case 'decrement': return state - 1;
    case 'reset': return action.value;
  }
};

const [count, dispatch] = useReducer(counterReducer, 0);
```
```

---

## Web Frameworks

### Example 4: FastAPI Backend

FastAPI development with async patterns and testing.

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: fastapi-backend
version: 1.5.0
description: FastAPI development with async patterns and testing
author: Backend Team
namespace: backend/fastapi
license: MIT
keywords: [fastapi, python, async, api, rest]

components:
  instructions:
    - name: api-design
      description: RESTful API design patterns
      file: instructions/api-design.md
      tags: [fastapi, rest, api]

    - name: async-patterns
      description: Async/await best practices
      file: instructions/async.md
      tags: [fastapi, async, python]

    - name: database
      description: SQLAlchemy with async support
      file: instructions/database.md
      tags: [fastapi, database, sqlalchemy]

  commands:
    - name: dev
      description: Run development server with auto-reload
      file: commands/dev.sh
      tags: [fastapi, development]

    - name: test
      description: Run pytest with async support
      file: commands/test.sh
      tags: [testing, pytest, async]
```

**Instruction example** (`instructions/api-design.md`):
```markdown
# FastAPI RESTful API Design

## Endpoint Structure

### Use Routers for Organization

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users() -> list[UserOut]:
    """List all users."""
    return await user_service.get_all()

@router.get("/{user_id}")
async def get_user(user_id: str) -> UserOut:
    """Get user by ID."""
    return await user_service.get_by_id(user_id)

@router.post("/")
async def create_user(user: UserCreate) -> UserOut:
    """Create new user."""
    return await user_service.create(user)
```

## Request/Response Models

### Use Pydantic Models

```python
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
```
```

---

## Testing & Quality

### Example 5: Testing Toolkit

Comprehensive testing setup for Python projects.

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: python-testing-toolkit
version: 1.0.0
description: Complete testing setup with pytest, coverage, and fixtures
author: QA Team
namespace: testing/python
license: MIT
keywords: [testing, pytest, coverage, tdd]

components:
  instructions:
    - name: tdd-practices
      description: Test-driven development workflow
      file: instructions/tdd.md
      tags: [testing, tdd]

    - name: pytest-patterns
      description: Pytest patterns and fixtures
      file: instructions/pytest.md
      tags: [testing, pytest]

    - name: mocking
      description: Mocking and patching strategies
      file: instructions/mocking.md
      tags: [testing, mocking]

  commands:
    - name: test
      description: Run tests with coverage
      file: commands/test.sh
      tags: [testing]

    - name: test-watch
      description: Run tests in watch mode
      file: commands/test-watch.sh
      tags: [testing, development]

  resources:
    - name: pytest-ini
      description: Pytest configuration
      file: resources/pytest.ini
      install_path: pytest.ini
      tags: [testing, config]

    - name: conftest
      description: Shared pytest fixtures
      file: resources/conftest.py
      install_path: tests/conftest.py
      tags: [testing, fixtures]
```

**Instruction example** (`instructions/tdd.md`):
```markdown
# Test-Driven Development Practices

## TDD Workflow

### Red-Green-Refactor Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green

### Example Workflow

```python
# Step 1: Red - Write failing test
def test_calculate_total_with_tax():
    cart = ShoppingCart()
    cart.add_item(Item(price=100))
    assert cart.calculate_total_with_tax(tax_rate=0.1) == 110

# Step 2: Green - Minimal implementation
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def calculate_total_with_tax(self, tax_rate):
        subtotal = sum(item.price for item in self.items)
        return subtotal * (1 + tax_rate)

# Step 3: Refactor - Improve implementation
class ShoppingCart:
    def __init__(self):
        self.items: list[Item] = []

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def get_subtotal(self) -> float:
        return sum(item.price for item in self.items)

    def calculate_total_with_tax(self, tax_rate: float) -> float:
        return self.get_subtotal() * (1 + tax_rate)
```

## Test Organization

### Arrange-Act-Assert Pattern

```python
def test_user_registration():
    # Arrange: Set up test data
    user_data = {
        "email": "test@example.com",
        "password": "secure123",
    }

    # Act: Execute the code under test
    user = User.create(user_data)

    # Assert: Verify the results
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert user.is_active is True
```
```

---

## DevOps & Deployment

### Example 6: Docker Development

Docker configuration package for development and deployment.

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: docker-development
version: 2.0.0
description: Docker development environment with best practices
author: DevOps Team
namespace: devops/docker
license: MIT
keywords: [docker, deployment, devops, containers]

components:
  instructions:
    - name: dockerfile-best-practices
      description: Writing efficient Dockerfiles
      file: instructions/dockerfile.md
      tags: [docker, deployment]

    - name: docker-compose
      description: Docker Compose for local development
      file: instructions/compose.md
      tags: [docker, development]

  commands:
    - name: build
      description: Build Docker images
      file: commands/build.sh
      tags: [docker, build]

    - name: up
      description: Start development environment
      file: commands/up.sh
      tags: [docker, development]

  resources:
    - name: dockerfile
      description: Production-ready Dockerfile
      file: resources/Dockerfile
      install_path: Dockerfile
      tags: [docker]

    - name: docker-compose
      description: Development docker-compose configuration
      file: resources/docker-compose.yml
      install_path: docker-compose.yml
      tags: [docker, development]

    - name: dockerignore
      description: Docker ignore patterns
      file: resources/.dockerignore
      install_path: .dockerignore
      tags: [docker]
```

**Resource example** (`resources/Dockerfile`):
```dockerfile
# Multi-stage Dockerfile for Python applications

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
ENV PATH=/root/.local/bin:$PATH

# Run as non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Multi-Language Packages

### Example 7: Full-Stack Development

Package combining frontend and backend best practices.

**Manifest** (`ai-config-kit-package.yaml`):
```yaml
name: fullstack-development
version: 1.0.0
description: Full-stack development with React, FastAPI, and PostgreSQL
author: Full Stack Team
namespace: fullstack/web
license: MIT
keywords: [fullstack, react, fastapi, postgresql]

components:
  instructions:
    # Frontend
    - name: react-components
      description: React component patterns
      file: instructions/frontend/components.md
      tags: [react, frontend]

    - name: state-management
      description: State management with React hooks
      file: instructions/frontend/state.md
      tags: [react, state, frontend]

    # Backend
    - name: api-design
      description: RESTful API design
      file: instructions/backend/api.md
      tags: [fastapi, api, backend]

    - name: database-patterns
      description: Database design and migrations
      file: instructions/backend/database.md
      tags: [postgresql, database, backend]

    # DevOps
    - name: deployment
      description: Deployment workflow
      file: instructions/devops/deployment.md
      tags: [devops, deployment]

  commands:
    - name: dev-frontend
      description: Start frontend development server
      file: commands/dev-frontend.sh
      tags: [frontend, development]

    - name: dev-backend
      description: Start backend development server
      file: commands/dev-backend.sh
      tags: [backend, development]

    - name: test-all
      description: Run all tests (frontend + backend)
      file: commands/test-all.sh
      tags: [testing]

  resources:
    - name: docker-compose
      description: Full development environment
      file: resources/docker-compose.yml
      install_path: docker-compose.yml
      tags: [docker, development]
```

**Command example** (`commands/test-all.sh`):
```bash
#!/usr/bin/env bash
# Run all tests (frontend + backend)

set -e

echo "Running full test suite..."

# Backend tests
echo ""
echo "=== Backend Tests ==="
cd backend
pytest --cov=. --cov-report=html --cov-report=term
cd ..

# Frontend tests
echo ""
echo "=== Frontend Tests ==="
cd frontend
npm test -- --coverage
cd ..

echo ""
echo "✓ All tests passed!"
echo "Backend coverage: backend/htmlcov/index.html"
echo "Frontend coverage: frontend/coverage/index.html"
```

---

## Usage Tips

### Installing Multiple Related Packages

```bash
# Install base package first
aiconfig package install ./python-best-practices --ide claude

# Then add framework-specific package
aiconfig package install ./django-development --ide claude
```

### Customizing After Installation

After installing a package, you can customize installed files:

```bash
# Install package
aiconfig package install ./python-best-practices --ide claude

# Customize instruction
vim .claude/rules/style-guide.md

# Note: Reinstalling with --conflict skip will preserve your changes
aiconfig package install ./python-best-practices --ide claude --conflict skip
```

### Creating Variants

Create multiple variants of a package:

```
my-packages/
├── python-minimal/       # Basic instructions only
├── python-standard/      # Instructions + hooks
└── python-complete/      # Everything
```

Users choose which variant to install:
```bash
aiconfig package install ./my-packages/python-standard --ide claude
```

---

## Related Documentation

- **[Getting Started](getting-started.md)** - Quick start guide
- **[Creating Packages](creating-packages.md)** - Build your own packages
- **[Manifest Reference](manifest-reference.md)** - Complete YAML schema
- **[CLI Reference](cli-reference.md)** - All commands and options

---

**Want to contribute your package?** Share it on [GitHub Discussions](https://github.com/troylar/devsync/discussions) or submit a PR to add it to the examples!
