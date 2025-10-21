# CovetPy ORM Relationships Guide

**Complete guide to relationship handling in CovetPy ORM**

Version: 1.0.0
Last Updated: 2025-01-11

---

## Table of Contents

1. [Introduction](#introduction)
2. [ForeignKey (Many-to-One)](#foreignkey-many-to-one)
3. [OneToOneField](#onetoonefield)
4. [ManyToManyField](#manytomanyfield)
5. [Generic Foreign Keys](#generic-foreign-keys)
6. [Self-Referential Relationships](#self-referential-relationships)
7. [Polymorphic Models](#polymorphic-models)
8. [Cascade Behaviors](#cascade-behaviors)
9. [Performance Optimization](#performance-optimization)
10. [Best Practices](#best-practices)

---

## Introduction

CovetPy ORM provides a comprehensive relationship system that is Django-compatible and production-ready. All relationship types support:

- **Lazy loading**: Related objects load on first access
- **Eager loading**: Use `select_related()` and `prefetch_related()`
- **Reverse relations**: Access relationships from both sides
- **Cascade behaviors**: Control what happens on deletion
- **Type safety**: Full type hints and validation

### Quick Reference

| Relationship Type | Use Case | Example |
|------------------|----------|---------|
| ForeignKey | Many-to-One | Many books → one author |
| OneToOneField | One-to-One | User → Profile |
| ManyToManyField | Many-to-Many | Posts ↔ Tags |
| GenericForeignKey | Polymorphic | Comments on any model |
| Self-referential | Hierarchies | Category tree |

---

## ForeignKey (Many-to-One)

**Definition**: Creates a many-to-one relationship. Multiple objects can reference the same related object.

### Basic Usage

```python
from covet.database.orm import Model
from covet.database.orm.fields import CharField
from covet.database.orm.relationships import ForeignKey, CASCADE

class Author(Model):
    name = CharField(max_length=100)

class Book(Model):
    title = CharField(max_length=200)
    author = ForeignKey(Author, on_delete=CASCADE, related_name='books')

# Usage
author = await Author.create(name='Alice')
book = await Book.create(title='Python Guide', author=author)

# Forward access
author = await book.author
print(author.name)  # 'Alice'

# Reverse access
books = await author.books.all()
```

### Parameters

- **`to`**: Related model class or string name
- **`on_delete`**: Cascade behavior (CASCADE, PROTECT, SET_NULL, etc.)
- **`related_name`**: Name for reverse relation (default: `<model>_set`)
- **`related_query_name`**: Name for filtering through reverse relation
- **`to_field`**: Field to reference (default: primary key)
- **`db_constraint`**: Create database FK constraint (default: True)
- **`nullable`**: Allow NULL values (default: True)

### On Delete Behaviors

```python
# CASCADE: Delete books when author deleted
author = ForeignKey(Author, on_delete=CASCADE)

# PROTECT: Prevent deletion if books exist
author = ForeignKey(Author, on_delete=PROTECT)

# SET_NULL: Set to NULL (requires nullable=True)
author = ForeignKey(Author, on_delete=SET_NULL, nullable=True)

# SET_DEFAULT: Set to default value
author = ForeignKey(Author, on_delete=SET_DEFAULT, default=1)

# DO_NOTHING: No action (may cause DB errors)
author = ForeignKey(Author, on_delete=DO_NOTHING)
```

### Reverse Relations

```python
# Access all books by author
books = await author.books.all()

# Filter reverse relation
recent_books = await author.books.filter(published_year=2024)

# Count
book_count = await author.books.count()

# Create through reverse relation
new_book = await author.books.create(title='New Book')
```

---

## OneToOneField

**Definition**: Similar to ForeignKey but ensures uniqueness – each object can only be related to one other object.

### Basic Usage

```python
class User(Model):
    username = CharField(max_length=100)

class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    bio = TextField()

# Usage
user = await User.create(username='alice')
profile = await Profile.create(user=user, bio='Developer')

# Forward access
user = await profile.user

# Reverse access (single object, not QuerySet)
profile = await user.profile
```

### Key Differences from ForeignKey

1. **Unique constraint**: Automatically adds UNIQUE constraint
2. **Reverse access**: Returns single object, not manager
3. **Use case**: 1:1 relationships (User ↔ Profile)

---

## ManyToManyField

**Definition**: Creates a many-to-many relationship using an intermediate table. Multiple objects can be related to multiple other objects.

### Basic Usage

```python
class Post(Model):
    title = CharField(max_length=200)
    tags = ManyToManyField('Tag', related_name='posts')

class Tag(Model):
    name = CharField(max_length=50)

# Usage
post = await Post.create(title='Python Tips')
tag1 = await Tag.create(name='Python')
tag2 = await Tag.create(name='Programming')

# Add tags
await post.tags.add(tag1, tag2)

# Remove tag
await post.tags.remove(tag1)

# Clear all
await post.tags.clear()

# Set to specific list
await post.tags.set([tag1, tag2])

# Get all tags
tags = await post.tags.all()

# Reverse access
posts = await tag1.posts.all()
```

### Manager Methods

| Method | Description |
|--------|-------------|
| `add(*objs)` | Add objects to relationship |
| `remove(*objs)` | Remove objects from relationship |
| `clear()` | Remove all relationships |
| `set(objs)` | Replace all relationships |
| `create(**kwargs)` | Create and add object |
| `all()` | Get all related objects |
| `filter(**kwargs)` | Filter related objects |
| `count()` | Count related objects |

### Through Models

Custom intermediate table with extra fields:

```python
class Membership(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    group = ForeignKey(Group, on_delete=CASCADE)
    date_joined = DateTimeField(auto_now_add=True)
    role = CharField(max_length=50)

class Group(Model):
    name = CharField(max_length=100)
    members = ManyToManyField(
        User,
        through=Membership,
        through_fields=('group', 'user'),
        related_name='groups'
    )

# Add with through defaults
await group.members.add(user, through_defaults={'role': 'admin'})

# Access through model
membership = await Membership.objects.get(user=user, group=group)
print(membership.role)  # 'admin'
```

### Symmetric Relationships

For self-referential M2M where relationship is symmetric (e.g., friends):

```python
class User(Model):
    username = CharField(max_length=100)
    friends = ManyToManyField('self', symmetrical=True)

# Add friend (automatically adds reverse)
await alice.friends.add(bob)

# Both have each other as friends
alice_friends = await alice.friends.all()  # includes bob
bob_friends = await bob.friends.all()      # includes alice
```

---

## Generic Foreign Keys

**Definition**: Allows relationships to any model type using ContentType framework.

### Basic Usage

```python
from covet.database.orm.relationships import GenericForeignKey, GenericRelation, ContentType

class Comment(Model):
    content_type_id = IntegerField()
    object_id = IntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = TextField()

class Post(Model):
    title = CharField(max_length=200)
    comments = GenericRelation(Comment)

class Photo(Model):
    caption = CharField(max_length=200)
    comments = GenericRelation(Comment)

# Usage - comments can attach to any model
post = await Post.create(title='My Post')
photo = await Photo.create(caption='Sunset')

comment1 = await Comment.create(
    content_object=post,
    text='Great post!'
)

comment2 = await Comment.create(
    content_object=photo,
    text='Beautiful photo!'
)

# Access generic FK
content = await comment1.content_object  # Returns Post instance
content = await comment2.content_object  # Returns Photo instance

# Reverse access
post_comments = await post.comments.all()
photo_comments = await photo.comments.all()
```

### ContentType Framework

```python
# Get ContentType for model
ct = ContentType.get_for_model(Post)

# Use in queries
comments = await Comment.objects.filter(content_type_id=ct.id)
```

### Prefetch Optimization

```python
from covet.database.orm.relationships import GenericPrefetch

# Prefetch to avoid N+1 queries
comments = await Comment.objects.all()
await GenericPrefetch.prefetch_generic_fk(comments, 'content_object')

# Now no additional queries
for comment in comments:
    print(comment.content_object.title)  # Cached
```

---

## Self-Referential Relationships

**Definition**: Models that reference themselves, useful for hierarchies and trees.

### Tree Structures

```python
class Category(Model, TreeNode):
    name = CharField(max_length=100)
    parent = ForeignKey(
        'self',
        on_delete=SET_NULL,
        nullable=True,
        related_name='children'
    )

# Usage
electronics = await Category.create(name='Electronics')
computers = await Category.create(name='Computers', parent=electronics)
laptops = await Category.create(name='Laptops', parent=computers)

# Navigate tree
parent = await laptops.get_parent()           # computers
ancestors = await laptops.get_ancestors()     # [computers, electronics]
descendants = await electronics.get_descendants()  # [computers, laptops]
siblings = await computers.get_siblings()
depth = await laptops.get_depth()             # 2

# Get all root nodes
roots = await Category.get_root_nodes()
```

### Tree Methods (TreeNode Mixin)

| Method | Description |
|--------|-------------|
| `get_parent()` | Get parent node |
| `get_children()` | Get direct children |
| `get_ancestors()` | Get all ancestors |
| `get_descendants()` | Get all descendants recursively |
| `get_siblings()` | Get sibling nodes |
| `get_depth()` | Get depth in tree (root = 0) |
| `is_root()` | Check if root node |
| `is_leaf()` | Check if leaf node |
| `get_root()` | Get root of tree |

### Nested Set Pattern

For read-heavy trees, use nested sets:

```python
class Category(Model, NestedSetNode):
    name = CharField(max_length=100)
    lft = IntegerField()
    rgt = IntegerField()
    tree_id = IntegerField()
    level = IntegerField()

# More efficient queries
descendants = await category.get_descendants()  # Single query
ancestors = await category.get_ancestors()      # Single query
```

---

## Polymorphic Models

**Definition**: Model inheritance with three strategies.

### 1. Abstract Base Classes

No table for base class, each child has complete schema:

```python
class Animal(Model):
    name = CharField(max_length=100)
    age = IntegerField()

    class Meta:
        abstract = True  # No table created

class Dog(Animal):
    breed = CharField(max_length=50)
    # Has name, age, breed fields

class Cat(Animal):
    indoor = BooleanField()
    # Has name, age, indoor fields
```

**Pros**: No joins, simple queries
**Cons**: Can't query across types, schema duplication

### 2. Single Table Inheritance (STI)

All models in one table with discriminator:

```python
class Vehicle(Model):
    model_name = CharField(max_length=100)
    year = IntegerField()

    class Meta:
        polymorphic_on = 'vehicle_type'
        polymorphic_identity = 'vehicle'

class Car(Vehicle):
    num_doors = IntegerField()

    class Meta:
        polymorphic_identity = 'car'

class Motorcycle(Vehicle):
    has_sidecar = BooleanField()

    class Meta:
        polymorphic_identity = 'motorcycle'

# Usage
car = await Car.create(model_name='Tesla Model 3', year=2024, num_doors=4)
# Creates entry in vehicles table with vehicle_type='car'

# Query specific type
cars = await Car.objects.all()  # Automatically filters vehicle_type='car'
```

**Pros**: Fast queries, can query across types
**Cons**: Sparse tables (many NULLs), wide tables

### 3. Multi-Table Inheritance (MTI)

Each model gets own table, joined via FK:

```python
class Person(Model):
    name = CharField(max_length=100)
    email = EmailField()

    class Meta:
        inheritance = 'multi_table'

class Employee(Person):
    employee_id = CharField(max_length=20)
    department = CharField(max_length=50)
    # Has name, email, employee_id, department

class Customer(Person):
    customer_since = DateTimeField()
    loyalty_points = IntegerField()
    # Has name, email, customer_since, loyalty_points

# Usage
employee = await Employee.create(
    name='Alice',
    email='alice@example.com',
    employee_id='EMP001',
    department='Engineering'
)
# Creates entries in both person and employee tables
```

**Pros**: Clean schema, no NULLs
**Cons**: Requires joins, more tables

### 4. Proxy Models

Alternative interface to existing model:

```python
class Person(Model):
    name = CharField(max_length=100)
    age = IntegerField()

class Adult(Person):
    class Meta:
        proxy = True  # Same table as Person

    @classmethod
    async def get_adults(cls):
        return await cls.objects.filter(age__gte=18)

# Same table, different interface
adults = await Adult.get_adults()
```

---

## Cascade Behaviors

Control what happens when referenced object is deleted.

### CASCADE

Delete related objects:

```python
author = ForeignKey(Author, on_delete=CASCADE)

# When author deleted, all books deleted too
await author.delete()
```

### PROTECT

Prevent deletion if related objects exist:

```python
from covet.database.orm.relationships.cascades import ProtectedError

book = ForeignKey(Book, on_delete=PROTECT)

# Raises ProtectedError if reviews exist
await book.delete()  # Error if has reviews
```

### SET_NULL

Set FK to NULL:

```python
author = ForeignKey(Author, on_delete=SET_NULL, nullable=True)

# When author deleted, book.author_id becomes NULL
await author.delete()
```

### SET_DEFAULT

Set FK to default value:

```python
author = ForeignKey(Author, on_delete=SET_DEFAULT, default=1)

# When author deleted, book.author_id set to 1
await author.delete()
```

### SET(...)

Set to specific value:

```python
from covet.database.orm.relationships import SET

def get_default_author():
    return Author.objects.get(name='Default Author')

author = ForeignKey(Author, on_delete=SET(get_default_author))
```

### RESTRICT

Similar to PROTECT but checked before cascades:

```python
author = ForeignKey(Author, on_delete=RESTRICT)
```

### DO_NOTHING

No action (may cause database errors):

```python
author = ForeignKey(Author, on_delete=DO_NOTHING)
```

---

## Performance Optimization

### 1. Select Related (Forward FK/OneToOne)

Optimize forward foreign key access with JOIN:

```python
# Bad - N+1 queries
books = await Book.objects.all()
for book in books:
    print((await book.author).name)  # Separate query each time

# Good - Single query with JOIN
books = await Book.objects.select_related('author')
for book in books:
    print(book.author.name)  # No additional queries
```

### 2. Prefetch Related (Reverse FK/M2M)

Optimize reverse relations and M2M:

```python
# Bad - N+1 queries
authors = await Author.objects.all()
for author in authors:
    books = await author.books.all()  # Separate query

# Good - Two queries total
authors = await Author.objects.prefetch_related('books')
for author in authors:
    books = await author.books.all()  # Cached
```

### 3. Bulk Operations

Use bulk operations for multiple objects:

```python
# Bad
for tag in tags:
    await post.tags.add(tag)

# Good
await post.tags.add(*tags)
```

### 4. Only/Defer

Load only needed fields:

```python
# Only load specific fields
books = await Book.objects.only('title', 'author_id')

# Defer (exclude) fields
books = await Book.objects.defer('description')
```

---

## Best Practices

### 1. Always Use related_name

Makes reverse access clear:

```python
# Good
author = ForeignKey(Author, related_name='books')
# Access: author.books.all()

# Bad - uses default
author = ForeignKey(Author)
# Access: author.book_set.all()  # Less clear
```

### 2. Choose Right on_delete

Think about business logic:

```python
# Delete books when author deleted
author = ForeignKey(Author, on_delete=CASCADE)

# Keep book but clear author
author = ForeignKey(Author, on_delete=SET_NULL, nullable=True)

# Prevent deletion if books exist
author = ForeignKey(Author, on_delete=PROTECT)
```

### 3. Use Through Models When Needed

If you need extra data on M2M relationship:

```python
# Good - can track date_joined, role
members = ManyToManyField(User, through=Membership)

# Bad - no way to store when/how user joined
members = ManyToManyField(User)
```

### 4. Index Foreign Keys

ForeignKey fields are auto-indexed, but verify:

```python
author = ForeignKey(Author, db_index=True)  # Default
```

### 5. Use Prefetch for Performance

Always prefetch in list views:

```python
# API list endpoint
authors = await Author.objects.prefetch_related('books')
return [
    {
        'name': author.name,
        'books': [book.title for book in await author.books.all()]
    }
    for author in authors
]
```

### 6. Be Careful with Circular References

Can cause infinite loops:

```python
class A(Model):
    b = ForeignKey('B', on_delete=CASCADE)

class B(Model):
    a = ForeignKey(A, on_delete=CASCADE)  # Circular!

# Deleting A tries to delete B, which tries to delete A...
```

Solution: Use SET_NULL or DO_NOTHING for one side.

### 7. Test Cascade Behaviors

Always test deletion in your test suite:

```python
async def test_author_deletion_cascades():
    author = await Author.create(name='Test')
    book = await Book.create(title='Test Book', author=author)

    await author.delete()

    # Verify cascade
    books = await Book.objects.all()
    assert len(books) == 0
```

---

## Common Patterns

### Blog Application

```python
class User(Model):
    username = CharField(max_length=100)

class Post(Model):
    title = CharField(max_length=200)
    author = ForeignKey(User, on_delete=CASCADE, related_name='posts')
    tags = ManyToManyField('Tag', related_name='posts')

class Comment(Model):
    post = ForeignKey(Post, on_delete=CASCADE, related_name='comments')
    author = ForeignKey(User, on_delete=CASCADE, related_name='comments')
    text = TextField()

class Tag(Model):
    name = CharField(max_length=50, unique=True)
```

### E-Commerce

```python
class Category(Model):
    name = CharField(max_length=100)
    parent = ForeignKey('self', on_delete=SET_NULL, nullable=True)

class Product(Model):
    name = CharField(max_length=200)
    category = ForeignKey(Category, on_delete=PROTECT)
    price = DecimalField(max_digits=10, decimal_places=2)

class Order(Model):
    user = ForeignKey(User, on_delete=PROTECT)
    created_at = DateTimeField(auto_now_add=True)

class OrderItem(Model):
    order = ForeignKey(Order, on_delete=CASCADE, related_name='items')
    product = ForeignKey(Product, on_delete=PROTECT)
    quantity = IntegerField()
```

---

## Troubleshooting

### N+1 Query Problem

**Problem**: Making separate query for each object

```python
# This creates N+1 queries
for author in await Author.objects.all():
    print(await author.books.all())
```

**Solution**: Use prefetch_related

```python
for author in await Author.objects.prefetch_related('books'):
    print(await author.books.all())  # Cached
```

### Circular Import

**Problem**: Models in different files referencing each other

**Solution**: Use string references

```python
# models/post.py
class Post(Model):
    author = ForeignKey('User', on_delete=CASCADE)  # String reference

# models/user.py
class User(Model):
    name = CharField(max_length=100)
```

### Missing Reverse Accessor

**Problem**: Can't access reverse relation

**Solution**: Add related_name

```python
author = ForeignKey(Author, related_name='books')
# Now can use: author.books.all()
```

---

## API Reference

### ForeignKey

```python
ForeignKey(
    to: Union[Type[Model], str],
    on_delete: Union[str, Type],
    related_name: Optional[str] = None,
    related_query_name: Optional[str] = None,
    to_field: Optional[str] = None,
    db_constraint: bool = True,
    **kwargs
)
```

### ManyToManyField

```python
ManyToManyField(
    to: Union[Type[Model], str],
    through: Optional[Union[Type[Model], str]] = None,
    through_fields: Optional[Tuple[str, str]] = None,
    related_name: Optional[str] = None,
    db_table: Optional[str] = None,
    symmetrical: Optional[bool] = None,
    **kwargs
)
```

### GenericForeignKey

```python
GenericForeignKey(
    ct_field: str = 'content_type',
    fk_field: str = 'object_id',
    for_concrete_model: bool = True
)
```

---

## Conclusion

CovetPy ORM provides a complete, production-ready relationship system with:

- ✅ Django-compatible API
- ✅ Full async support
- ✅ Advanced features (generic FKs, polymorphism)
- ✅ Performance optimization tools
- ✅ Comprehensive error handling

For more information:
- [API Documentation](../api/orm.md)
- [Performance Guide](./PERFORMANCE_GUIDE.md)
- [Examples](../../examples/orm/)

---

**Questions?** Check our [FAQ](./FAQ.md) or open an issue on GitHub.
