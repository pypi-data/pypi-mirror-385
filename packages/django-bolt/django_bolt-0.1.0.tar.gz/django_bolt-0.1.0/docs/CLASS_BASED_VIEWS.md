# Django-Bolt Class-Based Views

## Overview

Django-Bolt provides a powerful class-based view system inspired by Django REST Framework and Litestar, offering organized, reusable code for building REST APIs. Class-based views support all Django-Bolt features including authentication, guards, middleware, dependency injection, and custom actions.

**New in this version**: Unified ViewSet pattern with `api.viewset()` - a single ViewSet handles both list and detail views with automatic route generation, inspired by Litestar's Controller pattern.

## Table of Contents

- [Quick Start](#quick-start)
- [Unified ViewSet Pattern (Recommended)](#unified-viewset-pattern-recommended)
- [APIView](#apiview)
- [ViewSet](#viewset)
- [Mixins](#mixins)
- [ModelViewSet](#modelviewset)
- [Custom Actions](#custom-actions)
- [Authentication & Guards](#authentication--guards)
- [Middleware](#middleware)
- [Advanced Patterns](#advanced-patterns)

## Quick Start

```python
from django_bolt import BoltAPI, action
from django_bolt.views import APIView, ViewSet

api = BoltAPI()

# Simple APIView with decorator (recommended)
@api.view("/hello")
class HelloView(APIView):
    async def get(self, request):
        return {"message": "Hello, World!"}

# ViewSet for CRUD operations with decorator (recommended)
@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    lookup_field = 'article_id'  # Use 'article_id' instead of default 'pk'

    async def list(self, request):
        """GET /articles - List all articles"""
        return [{"id": 1, "title": "Article 1"}]

    async def retrieve(self, request, article_id: int):
        """GET /articles/{article_id} - Retrieve a single article"""
        return {"id": article_id, "title": "My Article"}

    async def create(self, request, data: dict):
        """POST /articles - Create a new article"""
        return {"id": 1, "created": True}

    async def update(self, request, article_id: int, data: dict):
        """PUT /articles/{article_id} - Update an article"""
        return {"id": article_id, "updated": True}

    async def destroy(self, request, article_id: int):
        """DELETE /articles/{article_id} - Delete an article"""
        return {"id": article_id, "deleted": True}

    # Custom action
    @action(methods=["POST"], detail=True)
    async def publish(self, request, article_id: int):
        """POST /articles/{article_id}/publish - Publish an article"""
        return {"id": article_id, "published": True}

```

## Unified ViewSet Pattern (Recommended)

**Inspired by Litestar's Controller pattern**, the unified ViewSet pattern eliminates the need for separate list and detail ViewSets. Use `api.viewset()` for automatic CRUD route generation with DRF-style action methods.

### Why Unified ViewSets?

**Before** (Old Pattern - Required 2 ViewSets):
```python
# Separate ViewSet for list operations
class UserListViewSet(ViewSet):
    async def get(self, request, limit: int = 100):
        return await User.objects.all()[:limit]

@api.view("/users")
class UserListViewSet(ViewSet):
    async def get(self, request, limit: int = 100):
        return await User.objects.all()[:limit]

# Separate ViewSet for detail operations
@api.view("/users/{user_id}")
class UserDetailViewSet(ViewSet):
    async def get(self, request, user_id: int):
        return await User.objects.aget(id=user_id)

    async def put(self, request, user_id: int, data: UserUpdate):
        # ... update logic
        pass
```

**After** (New Pattern - Single ViewSet):
```python
class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserFull
    list_serializer_class = UserMini  # Optional: different serializer for lists
    lookup_field = 'id'  # Default: 'pk'

    async def list(self, request, limit: int = 100):
        """GET /users"""
        return await User.objects.all()[:limit]

    async def retrieve(self, request, id: int):
        """GET /users/{id}"""
        return await User.objects.aget(id=id)

    async def create(self, request, data: UserCreate):
        """POST /users"""
        return await User.objects.acreate(**data.__dict__)

    async def update(self, request, id: int, data: UserUpdate):
        """PUT /users/{id}"""
        user = await User.objects.aget(id=id)
        # ... update logic
        return user

    async def partial_update(self, request, id: int, data: UserUpdate):
        """PATCH /users/{id}"""
        # ... partial update logic
        pass

    async def destroy(self, request, id: int):
        """DELETE /users/{id}"""
        user = await User.objects.aget(id=id)
        await user.adelete()
        return {"deleted": True}

# One line - automatic route generation!
@api.viewset("/users")
class UserViewSet(ViewSet):
    ...
# Auto-generates:
# GET    /users       -> list()
# POST   /users       -> create()
# GET    /users/{id}  -> retrieve()
# PUT    /users/{id}  -> update()
# PATCH  /users/{id}  -> partial_update()
# DELETE /users/{id}  -> destroy()
```

### Key Benefits

✅ **Single source of truth** - One ViewSet for all operations
✅ **DRF-style actions** - Familiar `list`, `retrieve`, `create`, `update`, `partial_update`, `destroy` methods
✅ **Automatic routes** - `api.viewset()` generates all CRUD routes
✅ **Type-driven** - Return type annotations determine serialization
✅ **Flexible serializers** - Use `list_serializer_class` for different list/detail serializers
✅ **Custom actions** - Add custom endpoints with decorators

### Standard Action Methods

The unified ViewSet recognizes these standard action methods:

| Action | HTTP Method | Route | Purpose |
|--------|-------------|-------|---------|
| `list` | GET | `/resource` | List all resources |
| `create` | POST | `/resource` | Create a new resource |
| `retrieve` | GET | `/resource/{pk}` | Get a single resource |
| `update` | PUT | `/resource/{pk}` | Full update of a resource |
| `partial_update` | PATCH | `/resource/{pk}` | Partial update of a resource |
| `destroy` | DELETE | `/resource/{pk}` | Delete a resource |

**You only implement the actions you need** - `api.viewset()` only generates routes for implemented methods.

### Complete Example

```python
from django_bolt import BoltAPI, ViewSet
from django.contrib.auth.models import User
import msgspec

api = BoltAPI()

# Define serializers
class UserFull(msgspec.Struct):
    """Full user details for detail views."""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

class UserMini(msgspec.Struct):
    """Minimal user info for list views."""
    id: int
    username: str

class UserCreate(msgspec.Struct):
    """User creation schema."""
    username: str
    email: str
    first_name: str = ""
    last_name: str = ""

class UserUpdate(msgspec.Struct):
    """User update schema."""
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None

# Unified ViewSet
@api.viewset("/users")
class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserFull          # Used for detail views
    list_serializer_class = UserMini     # Used for list views
    lookup_field = 'id'

    async def list(self, request, active: bool | None = None, limit: int = 100):
        """List users with optional filtering."""
        qs = User.objects.all()

        if active is not None:
            qs = qs.filter(is_active=active)

        qs = qs[:limit]

        users = []
        async for user in qs:
            users.append(UserMini(id=user.id, username=user.username))

        return users

    async def retrieve(self, request, id: int):
        """Retrieve a single user."""
        user = await User.objects.aget(id=id)
        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def create(self, request, data: UserCreate):
        """Create a new user."""
        user = await User.objects.acreate(
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name
        )
        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def update(self, request, id: int, data: UserUpdate):
        """Full update of a user."""
        user = await User.objects.aget(id=id)

        if data.email is not None:
            user.email = data.email
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.is_active is not None:
            user.is_active = data.is_active

        await user.asave()

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def partial_update(self, request, id: int, data: UserUpdate):
        """Partial update of a user."""
        # Same as update for this example
        return await self.update(request, id, data)

    async def destroy(self, request, id: int):
        """Delete a user."""
        user = await User.objects.aget(id=id)
        await user.adelete()
        return {"deleted": True, "user_id": id}

    # Custom actions still work!
    @api.post("/users/{id}/activate")
    async def activate(self, request, id: int):
        """Custom action: Activate a user."""
        user = await User.objects.aget(id=id)
        user.is_active = True
        await user.asave()
        return {"user_id": id, "activated": True}

    @api.get("/users/search")
    async def search(self, request, query: str):
        """Custom action: Search users."""
        users = []
        async for user in User.objects.filter(username__icontains=query)[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return {"query": query, "results": users}

```

### Customizing Serializers Per Action

Use `get_serializer_class()` to dynamically select serializers:

```python
class ArticleViewSet(ViewSet):
    serializer_class = ArticleFullSchema
    list_serializer_class = ArticleMiniSchema
    detail_serializer_class = ArticleDetailSchema

    def get_serializer_class(self, action=None):
        """Override to customize serializer per action."""
        if action == "list":
            return self.list_serializer_class
        elif action == "retrieve":
            return self.detail_serializer_class
        return self.serializer_class
```

### Custom Lookup Field

By default, detail routes use `{pk}` as the lookup parameter. Override with `lookup_field`:

```python
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSchema
    lookup_field = 'slug'  # Use slug instead of pk

    async def retrieve(self, request, slug: str):
        """Retrieve article by slug."""
        article = await self.get_object(slug=slug)
        return ArticleSchema.from_model(article)

# Generates: GET /articles/{slug}
```

### Partial Implementation (Read-Only ViewSet)

Only implement the actions you need:

```python
class ReadOnlyArticleViewSet(ViewSet):
    """Read-only ViewSet - only list and retrieve."""
    queryset = Article.objects.all()
    serializer_class = ArticleSchema

    async def list(self, request):
        """List articles."""
        articles = []
        async for article in await self.get_queryset():
            articles.append(ArticleSchema.from_model(article))
        return articles

    async def retrieve(self, request, pk: int):
        """Retrieve single article."""
        article = await self.get_object(pk)
        return ArticleSchema.from_model(article)

    # No create, update, destroy - those routes won't be registered
# Only generates:
# GET /articles       -> list()
# GET /articles/{pk}  -> retrieve()
```

### Comparison with Litestar

Django-Bolt's unified ViewSet pattern is inspired by Litestar's Controller:

**Litestar Controller:**
```python
class PersonController(Controller):
    return_dto = ReadDTO

    @get("/persons")
    def list_persons(self) -> list[Person]:
        return [person1, person2]

    @get("/persons/{id}")
    def get_person(self, id: int) -> Person:
        return person
```

**Django-Bolt ViewSet:**
```python
class PersonViewSet(ViewSet):
    serializer_class = PersonSchema

    async def list(self, request) -> list[Person]:
        return [person1, person2]

    async def retrieve(self, request, id: int) -> Person:
        return person

# Automatic route generation
```

Both patterns:
- ✅ Use a single class for list and detail views
- ✅ Automatically detect return types (`Person` vs `list[Person]`)
- ✅ Support per-action serializer overrides
- ✅ Generate routes automatically
- ✅ Support custom actions with decorators

## APIView

`APIView` is the base class for creating individual endpoint handlers. It's ideal for simple endpoints or when you need full control over the implementation.

### Basic Usage

```python
from django_bolt.views import APIView

class UserProfileView(APIView):
    async def get(self, request, user_id: int):
        """Get user profile."""
        return {
            "id": user_id,
            "username": "johndoe",
            "email": "john@example.com"
        }

    async def put(self, request, user_id: int):
        """Update user profile."""
        # Access request body via msgspec.Struct validation
        return {"id": user_id, "updated": True}

```

### Class-Level Configuration

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

class SecureView(APIView):
    # Apply to all methods in this view
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request):
        # Access auth context
        auth = request.get("auth", {})
        user_id = auth.get("user_id")
        return {"user_id": user_id, "message": "Secure data"}

    async def post(self, request):
        # Auth/guards automatically applied
        return {"created": True}
```

### Method-Level Overrides

```python
from django_bolt.auth import IsAdminUser

class MixedSecurityView(APIView):
    # Default auth for all methods
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request):
        """Public read access."""
        return {"data": "public"}

    async def post(self, request):
        """Requires admin."""
        return {"created": True}

```

## ViewSet

`ViewSet` is designed for RESTful resource management. It provides a conventional structure for CRUD operations and automatically maps HTTP methods to handler methods.

### Standard Methods

ViewSet recognizes these standard HTTP method handlers:

- `get()` - Handle GET requests (retrieve/list)
- `post()` - Handle POST requests (create)
- `put()` - Handle PUT requests (full update)
- `patch()` - Handle PATCH requests (partial update)
- `delete()` - Handle DELETE requests (destroy)
- `head()` - Handle HEAD requests (headers only)
- `options()` - Handle OPTIONS requests (metadata)

### Complete CRUD Example

```python
from django_bolt.views import ViewSet
import msgspec

class CreateArticleRequest(msgspec.Struct):
    title: str
    content: str
    author: str

class UpdateArticleRequest(msgspec.Struct):
    title: str = None
    content: str = None

class ArticleViewSet(ViewSet):
    async def get(self, request, article_id: int):
        """Retrieve a single article by ID."""
        # In real app, fetch from database
        return {
            "id": article_id,
            "title": "Django-Bolt Guide",
            "content": "...",
            "author": "John Doe"
        }

    async def post(self, request, data: CreateArticleRequest):
        """Create a new article."""
        # data is automatically validated
        # In real app, save to database
        return {
            "id": 123,
            "title": data.title,
            "content": data.content,
            "author": data.author,
            "created": True
        }

    async def put(self, request, article_id: int, data: UpdateArticleRequest):
        """Update an existing article."""
        # In real app, update in database
        return {
            "id": article_id,
            "title": data.title,
            "updated": True
        }

    async def patch(self, request, article_id: int, data: UpdateArticleRequest):
        """Partially update an article."""
        # In real app, partial update in database
        return {
            "id": article_id,
            "updated": True
        }

    async def delete(self, request, article_id: int):
        """Delete an article."""
        # In real app, delete from database
        return {"id": article_id, "deleted": True}

```

### Path Parameters

ViewSet methods automatically receive path parameters as function arguments:

```python
class CommentViewSet(ViewSet):
    async def get(self, request, post_id: int, comment_id: int):
        """Nested resource: get comment on a post."""
        return {
            "post_id": post_id,
            "comment_id": comment_id,
            "text": "Great post!"
        }

```

### Query Parameters

```python
class SearchViewSet(ViewSet):
    async def get(self, request, query: str, page: int = 1, limit: int = 10):
        """Search with pagination."""
        # Query parameters extracted from URL: ?query=django&page=2&limit=20
        return {
            "query": query,
            "page": page,
            "limit": limit,
            "results": []
        }

```

## Mixins

Mixins provide reusable functionality for common operations. They follow Django REST Framework's mixin pattern.

### Available Mixins

```python
from django_bolt.views import (
    ListMixin,      # List resources
    RetrieveMixin,  # Get single resource
    CreateMixin,    # Create resource
    UpdateMixin,    # Update resource
    DestroyMixin    # Delete resource
)
```

### Using Mixins

```python
from django_bolt.views import ViewSet, ListMixin, RetrieveMixin, CreateMixin

class ArticleViewSet(ViewSet, ListMixin, RetrieveMixin, CreateMixin):
    queryset = None  # Set to Django QuerySet for automatic ORM integration

    async def get_queryset(self):
        """Override to customize queryset."""
        # Return list of articles
        return [
            {"id": 1, "title": "First Article"},
            {"id": 2, "title": "Second Article"}
        ]

    async def get_object(self, **kwargs):
        """Override to fetch single object."""
        article_id = kwargs.get('article_id')
        return {"id": article_id, "title": "Article"}

    async def create_object(self, data):
        """Override to handle creation."""
        return {"id": 123, **data}

# Mixins provide default implementations for get/post
```

### Mixin Method Mapping

- `ListMixin` → `get()` without path params → returns list
- `RetrieveMixin` → `get()` with path params → returns single object
- `CreateMixin` → `post()` → creates new object
- `UpdateMixin` → `put()` / `patch()` → updates object
- `DestroyMixin` → `delete()` → deletes object

### Custom Mixin Example

```python
class TimestampMixin:
    """Add timestamps to responses."""

    async def add_timestamps(self, data: dict) -> dict:
        from datetime import datetime
        data['timestamp'] = datetime.utcnow().isoformat()
        return data

class ArticleViewSet(ViewSet, TimestampMixin):
    async def get(self, request, article_id: int):
        data = {"id": article_id, "title": "Article"}
        return await self.add_timestamps(data)
```

## ModelViewSet

`ModelViewSet` provides automatic CRUD operations for Django ORM models with zero boilerplate.

### Basic Usage

```python
from django.db import models
from django_bolt.views import ModelViewSet

# Django Model
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'myapp'

# ModelViewSet - automatic CRUD
class ArticleViewSet(ModelViewSet):
    model = Article
    lookup_field = 'id'  # Default: 'id'

# Automatically provides: list, retrieve, create, update, partial_update, destroy
```

### Custom QuerySet

```python
class PublishedArticleViewSet(ModelViewSet):
    model = Article

    def get_queryset(self):
        """Filter to only published articles."""
        return Article.objects.filter(status='published')
```

### Custom Lookup Field

```python
class ArticleViewSet(ModelViewSet):
    model = Article
    lookup_field = 'slug'  # Use slug instead of id

```

### Async ORM Operations

Django-Bolt supports Django's async ORM methods:

```python
class ArticleViewSet(ModelViewSet):
    model = Article

    async def get(self, request, article_id: int):
        """Custom retrieve with async ORM."""
        article = await Article.objects.aget(id=article_id)
        return {
            "id": article.id,
            "title": article.title,
            "content": article.content
        }

    async def post(self, request, data):
        """Custom create with async ORM."""
        article = await Article.objects.acreate(
            title=data.title,
            content=data.content,
            author=data.author
        )
        return {"id": article.id, "created": True}
```

### Read-Only ViewSet

```python
from django_bolt.views import ReadOnlyModelViewSet

class ArticleViewSet(ReadOnlyModelViewSet):
    model = Article

# Only provides: list (GET without params) and retrieve (GET with params)
```

## Custom Actions

Custom actions let you add non-CRUD endpoints to your ViewSet using the `@action` decorator. This is one of the most powerful features of class-based views, inspired by Django REST Framework.

**IMPORTANT**: Custom actions with `@action` decorator only work with `api.viewset()` registration. They do not work with `api.view()`.

### The @action Decorator

The `@action` decorator provides automatic path generation for custom actions based on the ViewSet's base path:

```python
from django_bolt import action

@action(methods=["POST"], detail=True)
async def activate(self, request, id: int):
    """Automatically generates: POST /users/{id}/activate"""
    pass

@action(methods=["GET"], detail=False)
async def active(self, request):
    """Automatically generates: GET /users/active"""
    pass
```

#### Parameters

- **methods** (required): List of HTTP methods (`["GET"]`, `["POST"]`, `["GET", "POST"]`, etc.)
- **detail** (required): `True` for instance-level actions (`/resource/{pk}/action`), `False` for collection-level (`/resource/action`)
- **path** (optional): Custom action name (defaults to function name)
- **auth** (optional): Override class-level authentication
- **guards** (optional): Override class-level guards
- **response_model** (optional): Response serialization model
- **status_code** (optional): HTTP status code

### Basic Custom Actions

```python
from django_bolt import BoltAPI, ViewSet, action

api = BoltAPI()

class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserFull

    async def list(self, request) -> list[UserMini]:
        """GET /users"""
        return User.objects.all()[:100]

    async def retrieve(self, request, id: int) -> UserFull:
        """GET /users/{id}"""
        return await User.objects.aget(id=id)

    # Instance-level action: POST /users/{id}/activate
    @action(methods=["POST"], detail=True)
    async def activate(self, request, id: int):
        """Activate a user account."""
        user = await User.objects.aget(id=id)
        user.is_active = True
        await user.asave()
        return {"user_id": id, "activated": True}

    # Collection-level action: GET /users/active
    @action(methods=["GET"], detail=False)
    async def active(self, request) -> list[UserMini]:
        """Get all active users."""
        return User.objects.filter(is_active=True)[:100]

    # Custom path: GET /users/search
    @action(methods=["GET"], detail=False, path="search")
    async def search_users(self, request, query: str):
        """Search users by username."""
        return User.objects.filter(username__icontains=query)[:10]

```

### Real-World Examples

#### User Account Management

```python
from django_bolt import action

class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSchema

    async def list(self, request):
        return User.objects.all()[:100]

    async def retrieve(self, request, id: int):
        return await User.objects.aget(id=id)

    @action(methods=["POST"], detail=True)
    async def activate(self, request, id: int):
        """POST /users/{id}/activate - Activate user account"""
        user = await User.objects.aget(id=id)
        user.is_active = True
        await user.asave()
        # Send activation email, etc.
        return {"id": id, "activated": True, "email_sent": True}

    @action(methods=["POST"], detail=True)
    async def deactivate(self, request, id: int):
        """POST /users/{id}/deactivate - Deactivate user account"""
        user = await User.objects.aget(id=id)
        user.is_active = False
        await user.asave()
        return {"id": id, "deactivated": True, "status": "inactive"}

    @action(methods=["POST"], detail=True, path="reset-password")
    async def reset_password(self, request, id: int):
        """POST /users/{id}/reset-password - Send password reset email"""
        user = await User.objects.aget(id=id)
        # Send reset email logic
        return {"id": id, "reset_email_sent": True}

    @action(methods=["GET"], detail=True, path="permissions")
    async def get_permissions(self, request, id: int):
        """GET /users/{id}/permissions - Get user permissions"""
        user = await User.objects.aget(id=id)
        permissions = list(user.user_permissions.values_list('codename', flat=True))
        return {"id": id, "permissions": permissions}

    @action(methods=["PUT"], detail=True, path="permissions")
    async def update_permissions(self, request, id: int, data: PermissionUpdate):
        """PUT /users/{id}/permissions - Update user permissions"""
        user = await User.objects.aget(id=id)
        # Update permissions logic
        return {"id": id, "permissions": data.permissions, "updated": True}

```

#### Document Workflow

```python
class DocumentViewSet(ViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSchema

    async def list(self, request):
        return Document.objects.all()[:100]

    async def retrieve(self, request, id: int):
        return await Document.objects.aget(id=id)

    @action(methods=["POST"], detail=True)
    async def submit(self, request, id: int):
        """POST /documents/{id}/submit - Submit document for review"""
        doc = await Document.objects.aget(id=id)
        doc.status = "submitted"
        await doc.asave()
        return {"id": id, "status": "submitted"}

    @action(methods=["POST"], detail=True)
    async def approve(self, request, id: int):
        """POST /documents/{id}/approve - Approve document"""
        doc = await Document.objects.aget(id=id)
        doc.status = "approved"
        await doc.asave()
        return {"id": id, "status": "approved"}

    @action(methods=["POST"], detail=True)
    async def reject(self, request, id: int, data: RejectRequest):
        """POST /documents/{id}/reject - Reject document with reason"""
        doc = await Document.objects.aget(id=id)
        doc.status = "rejected"
        doc.rejection_reason = data.reason
        await doc.asave()
        return {"id": id, "status": "rejected", "reason": data.reason}

    @action(methods=["POST"], detail=True)
    async def lock(self, request, id: int):
        """POST /documents/{id}/lock - Lock document for editing"""
        doc = await Document.objects.aget(id=id)
        doc.locked = True
        await doc.asave()
        return {"id": id, "locked": True}

    @action(methods=["POST"], detail=True)
    async def unlock(self, request, id: int):
        """POST /documents/{id}/unlock - Unlock document"""
        doc = await Document.objects.aget(id=id)
        doc.locked = False
        await doc.asave()
        return {"id": id, "locked": False}

```

### Multiple HTTP Methods

You can register multiple methods for the same action path:

```python
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSchema

    async def list(self, request):
        return Article.objects.all()[:100]

    # GET /articles/{id}/status
    @action(methods=["GET"], detail=True, path="status")
    async def get_status(self, request, id: int):
        """Get article publication status."""
        article = await Article.objects.aget(id=id)
        return {"is_published": article.is_published}

    # POST /articles/{id}/status
    @action(methods=["POST"], detail=True, path="status")
    async def update_status(self, request, id: int, data: StatusUpdate):
        """Update article publication status."""
        article = await Article.objects.aget(id=id)
        article.is_published = data.is_published
        await article.asave()
        return {"updated": True, "is_published": article.is_published}

```

### Custom Action Features

- **Automatic Path Generation**: Paths are auto-generated based on ViewSet base path and action name
- **Full Parameter Support**: Path params, query params, headers, cookies, body validation
- **Auth Inheritance**: Custom actions inherit class-level `auth` and `guards` unless overridden
- **Type Safety**: Full type hint support with automatic validation
- **Flexible Methods**: Support single or multiple HTTP methods per action

### Custom Action with Validation

```python
import msgspec
from django_bolt import action

class PublishRequest(msgspec.Struct):
    scheduled_time: str | None = None
    notify_subscribers: bool = True

class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()

    async def list(self, request):
        return Article.objects.all()[:100]

    @action(methods=["POST"], detail=True)
    async def publish(self, request, id: int, data: PublishRequest):
        """POST /articles/{id}/publish - Publish article with options"""
        article = await Article.objects.aget(id=id)
        article.is_published = True
        article.scheduled_time = data.scheduled_time
        await article.asave()

        if data.notify_subscribers:
            # Send notifications
            pass

        return {
            "id": id,
            "published": True,
            "scheduled": data.scheduled_time,
            "notifications_sent": data.notify_subscribers
        }

```

### Comparison: Old vs New Pattern

**Old Pattern** (No longer supported for ViewSets):
```python
# ❌ Manual path specification - repetitive and error-prone
class UserViewSet(ViewSet):
    @api.post("/users/{id}/activate")
    async def activate(self, request, id: int):
        pass
```

**New Pattern** (Recommended):
```python
# ✅ Automatic path generation - clean and maintainable
class UserViewSet(ViewSet):
    @action(methods=["POST"], detail=True)
    async def activate(self, request, id: int):
        pass

@api.viewset("/users")  # Required for @action to work
class UserViewSet(ViewSet):
    ...
```

## Authentication & Guards

Class-based views support all Django-Bolt authentication and guard features.

### Class-Level Security

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated, IsAdminUser

class SecureViewSet(ViewSet):
    # Apply to ALL methods (including custom actions)
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request, resource_id: int):
        """Protected by class-level auth."""
        auth = request.get("auth", {})
        return {
            "resource_id": resource_id,
            "user_id": auth.get("user_id")
        }

    @api.post("/resources/{resource_id}/delete")
    async def delete_action(self, request, resource_id: int):
        """Custom action - also protected by class-level auth."""
        auth = request.get("auth", {})
        return {
            "resource_id": resource_id,
            "deleted_by": auth.get("user_id")
        }

```

### Custom Action with Different Auth

```python
from django_bolt.auth import APIKeyAuthentication

class ArticleViewSet(ViewSet):
    # Default auth for standard methods
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request, article_id: int):
        """Requires JWT."""
        return {"id": article_id}

    # Custom action with different auth
    @api.post("/articles/{article_id}/webhook", auth=[APIKeyAuthentication(api_keys={"webhook-key": "system"})])
    async def webhook(self, request, article_id: int):
        """Webhook endpoint - requires API key instead of JWT."""
        return {"article_id": article_id, "processed": True}
```

### Guards with Custom Actions

```python
from django_bolt.auth import HasPermission

class DocumentViewSet(ViewSet):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request, doc_id: int):
        """Anyone authenticated can read."""
        return {"id": doc_id}

    @api.post("/documents/{doc_id}/approve", guards=[IsAdminUser()])
    async def approve(self, request, doc_id: int):
        """Only admins can approve."""
        return {"id": doc_id, "approved": True}

    @api.post("/documents/{doc_id}/publish", guards=[HasPermission("documents.publish")])
    async def publish(self, request, doc_id: int):
        """Requires specific permission."""
        return {"id": doc_id, "published": True}
```

### Accessing Auth Context

```python
class SecureViewSet(ViewSet):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request, resource_id: int):
        """Access authentication context."""
        auth = request.get("auth", {})

        # JWT auth provides:
        user_id = auth.get("user_id")
        username = auth.get("username")
        is_admin = auth.get("is_admin", False)
        is_staff = auth.get("is_staff", False)
        permissions = auth.get("permissions", [])

        return {
            "resource_id": resource_id,
            "accessed_by": user_id,
            "is_admin": is_admin
        }
```

## Middleware

Class-based views support all middleware decorators.

### CORS Middleware

```python
from django_bolt.middleware import cors

class APIViewSet(ViewSet):
    @cors(origins=["http://localhost:3000"], credentials=True)
    async def get(self, request):
        """Endpoint with CORS enabled."""
        return {"data": "accessible from localhost:3000"}

    @api.post("/api/upload")
    @cors(origins=["*"], methods=["POST"])
    async def upload(self, request):
        """Custom action with CORS."""
        return {"uploaded": True}
```

### Rate Limiting

```python
from django_bolt.middleware import rate_limit

class APIViewSet(ViewSet):
    @rate_limit(rps=100, burst=200)
    async def get(self, request):
        """Rate limited endpoint."""
        return {"data": "limited"}

    @api.post("/api/heavy")
    @rate_limit(rps=10, burst=20)
    async def heavy_operation(self, request):
        """Custom action with strict rate limit."""
        return {"processed": True}
```

### Skip Middleware

```python
from django_bolt.middleware import skip_middleware

class APIViewSet(ViewSet):
    @skip_middleware("rate_limit")
    async def get(self, request):
        """Skip rate limiting for this endpoint."""
        return {"data": "unlimited"}
```

### Multiple Middleware

```python
from django_bolt.middleware import cors, rate_limit, skip_middleware

class APIViewSet(ViewSet):
    @cors(origins=["http://localhost:3000"])
    @rate_limit(rps=50)
    async def get(self, request):
        """Multiple middleware decorators."""
        return {"data": "protected"}

    @api.post("/api/action")
    @cors(origins=["*"])
    @rate_limit(rps=10)
    async def custom_action(self, request):
        """Custom action with multiple middleware."""
        return {"action": "completed"}
```

## Advanced Patterns

### Dependency Injection

```python
from django_bolt.params import Depends

async def get_current_user(request: dict):
    """Extract user from auth context."""
    auth = request.get("auth", {})
    return {"id": auth.get("user_id"), "username": auth.get("username")}

class ProfileViewSet(ViewSet):
    async def get(self, request, current_user: dict = Depends(get_current_user)):
        """Use dependency injection."""
        return {
            "profile": current_user,
            "settings": {}
        }

    @api.put("/profile/settings")
    async def update_settings(self, request, current_user: dict = Depends(get_current_user)):
        """Custom action with dependency injection."""
        return {
            "user_id": current_user["id"],
            "settings_updated": True
        }
```

### Request Validation

```python
import msgspec

class CreateUserRequest(msgspec.Struct):
    username: str
    email: str
    password: str

class UpdateUserRequest(msgspec.Struct):
    username: str | None = None
    email: str | None = None

class UserViewSet(ViewSet):
    async def post(self, request, data: CreateUserRequest):
        """Automatic request validation."""
        # data is validated CreateUserRequest instance
        return {
            "id": 123,
            "username": data.username,
            "email": data.email
        }

    async def patch(self, request, user_id: int, data: UpdateUserRequest):
        """Partial update with validation."""
        return {
            "id": user_id,
            "updated_fields": [k for k, v in data.__dict__.items() if v is not None]
        }
```

### Response Validation

```python
import msgspec

class UserResponse(msgspec.Struct):
    id: int
    username: str
    email: str

class UserViewSet(ViewSet):
    async def get(self, request, user_id: int) -> UserResponse:
        """Response model validation."""
        return UserResponse(
            id=user_id,
            username="johndoe",
            email="john@example.com"
        )
```

### Streaming Responses

```python
from django_bolt.responses import StreamingResponse

class DataViewSet(ViewSet):
    async def get(self, request):
        """Stream large dataset."""
        async def stream_data():
            for i in range(1000):
                yield f"data: {i}\n"

        return StreamingResponse(
            stream_data(),
            media_type="text/event-stream"
        )

    @api.get("/data/export")
    async def export(self, request):
        """Custom streaming action."""
        async def export_csv():
            yield "id,name,email\n"
            for i in range(10000):
                yield f"{i},user{i},user{i}@example.com\n"

        return StreamingResponse(
            export_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users.csv"}
        )
```

### File Responses

```python
from django_bolt.responses import FileResponse

class DownloadViewSet(ViewSet):
    async def get(self, request, file_id: int):
        """Download file."""
        return FileResponse(
            f"/path/to/file/{file_id}.pdf",
            filename="document.pdf"
        )

    @api.get("/downloads/{file_id}/preview")
    async def preview(self, request, file_id: int):
        """Custom action: preview file."""
        return FileResponse(
            f"/path/to/file/{file_id}.pdf",
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )
```

### Error Handling

```python
from django_bolt.exceptions import HTTPException, NotFound, Forbidden

class ArticleViewSet(ViewSet):
    async def get(self, request, article_id: int):
        """Raise HTTP exceptions."""
        # Check if article exists
        if article_id > 1000:
            raise NotFound(detail=f"Article {article_id} not found")

        # Check permissions
        auth = request.get("auth", {})
        if not auth.get("can_read"):
            raise Forbidden(detail="You don't have permission to read this article")

        return {"id": article_id, "title": "Article"}

    @api.post("/articles/{article_id}/publish")
    async def publish(self, request, article_id: int):
        """Custom action with error handling."""
        # Custom validation
        if article_id < 1:
            raise HTTPException(
                status_code=422,
                detail="Invalid article ID",
                headers={"X-Error-Code": "INVALID_ID"}
            )

        return {"id": article_id, "published": True}
```

### Combining Everything

```python
import msgspec
from django_bolt.views import ViewSet
from django_bolt.auth import JWTAuthentication, IsAuthenticated, HasPermission
from django_bolt.middleware import cors, rate_limit
from django_bolt.params import Depends
from django_bolt.responses import StreamingResponse
from django_bolt.exceptions import NotFound, Forbidden

class ArticleRequest(msgspec.Struct):
    title: str
    content: str
    tags: list[str] = []

class ArticleResponse(msgspec.Struct):
    id: int
    title: str
    content: str
    author_id: int
    tags: list[str]

async def get_current_user(request: dict):
    auth = request.get("auth", {})
    return {"id": auth.get("user_id"), "is_admin": auth.get("is_admin", False)}

class ArticleViewSet(ViewSet):
    # Class-level security
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    @rate_limit(rps=100)
    async def get(self, request, article_id: int, current_user: dict = Depends(get_current_user)) -> ArticleResponse:
        """Retrieve article with rate limiting."""
        if article_id > 1000:
            raise NotFound(detail=f"Article {article_id} not found")

        return ArticleResponse(
            id=article_id,
            title="My Article",
            content="Content here",
            author_id=current_user["id"],
            tags=["python", "django"]
        )

    @cors(origins=["*"])
    @rate_limit(rps=50)
    async def post(self, request, data: ArticleRequest, current_user: dict = Depends(get_current_user)) -> ArticleResponse:
        """Create article with CORS and rate limiting."""
        return ArticleResponse(
            id=123,
            title=data.title,
            content=data.content,
            author_id=current_user["id"],
            tags=data.tags
        )

    @api.post("/articles/{article_id}/publish", guards=[HasPermission("articles.publish")])
    @rate_limit(rps=10)
    async def publish(self, request, article_id: int, current_user: dict = Depends(get_current_user)):
        """Custom action: publish article (admin only)."""
        if not current_user["is_admin"]:
            raise Forbidden(detail="Only admins can publish articles")

        return {
            "id": article_id,
            "published": True,
            "published_by": current_user["id"]
        }

    @api.get("/articles/{article_id}/export")
    @rate_limit(rps=5)
    async def export(self, request, article_id: int):
        """Custom action: export article as markdown."""
        async def generate_markdown():
            yield f"# Article {article_id}\n\n"
            yield "Content goes here...\n"

        return StreamingResponse(
            generate_markdown(),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=article-{article_id}.md"}
        )

```

## Best Practices

### 1. Use ViewSets for Resources

Use `ViewSet` when you're working with RESTful resources that need CRUD operations:

```python
# Good: ViewSet for resource management
class ArticleViewSet(ViewSet):
    async def get(self, request, article_id: int):
        ...
    async def post(self, request):
        ...
```

### 2. Use APIView for Single Endpoints

Use `APIView` for standalone endpoints that don't fit the CRUD pattern:

```python
# Good: APIView for specialized endpoint
class HealthCheckView(APIView):
    async def get(self, request):
        return {"status": "healthy"}
```

### 3. Use Custom Actions for Business Logic

Use custom actions for operations that don't fit standard CRUD:

```python
# Good: Custom actions for workflow operations
class OrderViewSet(ViewSet):
    @api.post("/orders/{order_id}/cancel")
    async def cancel(self, request, order_id: int):
        ...

    @api.post("/orders/{order_id}/refund")
    async def refund(self, request, order_id: int):
        ...
```

### 4. Leverage Class-Level Configuration

Set common configuration at the class level:

```python
# Good: Class-level auth/guards
class SecureViewSet(ViewSet):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]
```

### 5. Use Mixins for Reusable Logic

Create mixins for common functionality:

```python
# Good: Reusable mixin
class TimestampMixin:
    async def add_timestamp(self, data: dict) -> dict:
        data['timestamp'] = datetime.utcnow().isoformat()
        return data

class MyViewSet(ViewSet, TimestampMixin):
    ...
```

### 6. Validate Input and Output

Always use msgspec.Struct for request/response validation:

```python
# Good: Type-safe validation
class CreateRequest(msgspec.Struct):
    title: str
    content: str

class Response(msgspec.Struct):
    id: int
    title: str

async def post(self, request, data: CreateRequest) -> Response:
    ...
```

### 7. Use Dependency Injection

Leverage DI for common dependencies:

```python
# Good: Reusable dependencies
async def get_current_user(request: dict):
    ...

class ViewSet(ViewSet):
    async def get(self, request, user: dict = Depends(get_current_user)):
        ...
```

### 8. Handle Errors Explicitly

Raise appropriate HTTP exceptions:

```python
# Good: Explicit error handling
from django_bolt.exceptions import NotFound, Forbidden

async def get(self, request, article_id: int):
    if not exists(article_id):
        raise NotFound(detail=f"Article {article_id} not found")
    if not has_permission():
        raise Forbidden(detail="Access denied")
```

## Comparison with Django REST Framework

Django-Bolt class-based views are inspired by DRF but optimized for performance:

| Feature | Django REST Framework | Django-Bolt |
|---------|----------------------|-------------|
| ViewSets | ✅ | ✅ |
| Mixins | ✅ | ✅ |
| Custom Actions | ✅ `@action` decorator | ✅ `@api.post()` etc. |
| Serialization | DRF Serializers | msgspec.Struct |
| Performance | ~5-10k RPS | ~60k+ RPS |
| Async Support | Limited | Full async/await |
| Auth in Rust | ❌ | ✅ |
| Type Safety | Via type hints | Native with msgspec |

## Performance Considerations

Class-based views in Django-Bolt maintain the same high performance as function-based views:

- **Zero overhead**: Class instantiation is optimized
- **Rust-powered**: Auth, guards, and middleware run in Rust
- **Async-first**: All handlers are async by default
- **60k+ RPS**: Same performance as function-based views

## Summary

Class-based views in Django-Bolt provide:

✅ **Organized code structure** for complex APIs
✅ **Reusable mixins** for common operations
✅ **Automatic CRUD** with ModelViewSet
✅ **Custom actions** for business logic
✅ **Full feature support** - auth, guards, middleware, DI
✅ **High performance** - 60k+ RPS with Rust core
✅ **Type safety** with msgspec validation
✅ **Async-first** design

Use class-based views when you need organized, maintainable code for REST APIs with complex requirements.
