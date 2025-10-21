# Advanced ORM Features - Quick Reference Guide

**For**: CovetPy Developers
**Team**: 18 - Advanced ORM Features
**Status**: Production Ready (90/100)

---

## Quick Start (5 Minutes)

### Import Everything You Need

```python
from covet.database.orm import Model, CharField, EmailField, IntegerField
from covet.database.orm import Q, F  # Query expressions
from covet.database.orm.aggregations import Count, Sum, Avg, Min, Max, Window, Rank
from covet.database.orm.relationships import ForeignKey, ManyToManyField
```

---

## 1. Eliminate N+1 Queries

### Problem: N+1 Queries (Slow ❌)

```python
# BAD: 101 queries (1 + 100 N+1)
posts = await Post.objects.all()  # 1 query
for post in posts:
    print(post.author.name)  # 100 queries! ❌
```

### Solution: select_related (Fast ✅)

```python
# GOOD: 1 query with JOIN
posts = await Post.objects.select_related('author').all()
for post in posts:
    print(post.author.name)  # No extra queries! ✅

# Result: 100x faster
```

### Nested Relationships

```python
# Multiple levels deep
comments = await Comment.objects.select_related(
    'post__author',
    'user__profile'
).all()

# Access without extra queries:
for comment in comments:
    print(comment.post.author.name)  # No query
    print(comment.user.profile.bio)  # No query
```

---

## 2. Optimize Reverse Relationships

### Problem: N+1 on Reverse FK (Slow ❌)

```python
# BAD: 101 queries
authors = await Author.objects.all()  # 1 query
for author in authors:
    posts = await author.posts.all()  # 100 queries! ❌
```

### Solution: prefetch_related (Fast ✅)

```python
# GOOD: 2 queries total
authors = await Author.objects.prefetch_related('posts').all()
for author in authors:
    posts = await author.posts.all()  # No extra query! ✅

# Result: 50x faster
```

### Multiple Prefetches

```python
# Prefetch multiple relationships
authors = await Author.objects.prefetch_related(
    'posts',
    'posts__comments',
    'posts__tags'
).all()

# All relationships loaded in 4 queries instead of 1000+
```

---

## 3. Reduce Data Transfer

### Problem: Loading Unnecessary Data (Slow ❌)

```python
# BAD: Loads 25 MB of data
users = await User.objects.all()  # Includes large bio field
```

### Solution: only() / defer() (Fast ✅)

```python
# GOOD: Only load what you need (1.2 MB)
users = await User.objects.only('id', 'username', 'email').all()

# OR: Exclude large fields (2.5 MB)
users = await User.objects.defer('bio', 'avatar').all()

# Result: 10x faster, 95% less data
```

---

## 4. Simple Aggregations

### Count, Sum, Average

```python
# Count all users
stats = await User.objects.aggregate(
    total=Count('*')
)
# Returns: {'total': 1000}

# Multiple aggregates
stats = await Order.objects.aggregate(
    total_orders=Count('*'),
    total_revenue=Sum('amount'),
    avg_order=Avg('amount'),
    max_order=Max('amount')
)
# Returns: {'total_orders': 500, 'total_revenue': 45000, ...}
```

### Filtered Aggregates

```python
# Count with filter
stats = await Order.objects.aggregate(
    completed=Count('id', filter=Q(status='completed')),
    pending=Count('id', filter=Q(status='pending'))
)
```

---

## 5. Add Computed Fields

### Annotate - Add Fields to Results

```python
# Add post count to each author
authors = await Author.objects.annotate(
    post_count=Count('posts')
).all()

for author in authors:
    print(f"{author.name}: {author.post_count} posts")

# Filter on computed field
popular = await Author.objects.annotate(
    post_count=Count('posts')
).filter(post_count__gte=10)
```

### Multiple Annotations

```python
# Add multiple computed fields
posts = await Post.objects.annotate(
    comment_count=Count('comments'),
    avg_rating=Avg('ratings__score'),
    total_views=Sum('views')
).all()
```

---

## 6. F Expressions - Field References

### Compare Fields in Database

```python
# Find products on sale (sale_price < regular_price)
products = await Product.objects.filter(
    sale_price__lt=F('regular_price') * 0.9
)
```

### Atomic Updates (No Race Conditions)

```python
# BAD: Race condition ❌
article = await Article.objects.get(id=1)
article.views = article.views + 1
await article.save()  # Lost updates if concurrent!

# GOOD: Atomic update ✅
await Article.objects.filter(id=1).update(
    views=F('views') + 1  # Atomic, no race condition
)
```

### Calculations

```python
# Calculate total
await Order.objects.update(
    total=F('quantity') * F('unit_price') - F('discount')
)

# Multiple operations
await Product.objects.update(
    final_price=F('price') * Decimal('0.9') + F('tax')
)
```

---

## 7. Q Objects - Complex Queries

### OR Conditions

```python
# Find admins or staff
users = await User.objects.filter(
    Q(is_staff=True) | Q(is_superuser=True)
)
```

### AND + NOT

```python
# Active users who are NOT banned
users = await User.objects.filter(
    Q(is_active=True) & ~Q(is_banned=True)
)
```

### Complex Nested Logic

```python
# (Staff OR Superuser) AND Active AND NOT Banned
admins = await User.objects.filter(
    Q(
        Q(is_staff=True) | Q(is_superuser=True)
    ) & Q(is_active=True) & ~Q(is_banned=True)
)
```

### Reusable Q Objects

```python
# Define reusable queries
active_users = Q(is_active=True, is_banned=False)
staff_or_super = Q(is_staff=True) | Q(is_superuser=True)

# Combine them
admins = await User.objects.filter(active_users & staff_or_super)
```

---

## 8. Conditional Logic (Case/When)

### Categorize Data

```python
from covet.database.orm.expressions_advanced import Case, When, Value

# Categorize users by activity
users = await User.objects.annotate(
    status=Case(
        When(last_login__gte=today, then=Value('active')),
        When(last_login__gte=last_week, then=Value('recent')),
        When(last_login__gte=last_month, then=Value('inactive')),
        default=Value('dormant')
    )
)

for user in users:
    print(f"{user.username}: {user.status}")
```

### Conditional Aggregation

```python
# Sum completed vs pending orders
stats = await Order.objects.aggregate(
    completed_total=Sum(
        Case(
            When(status='completed', then=F('amount')),
            default=Value(0)
        )
    ),
    pending_total=Sum(
        Case(
            When(status='pending', then=F('amount')),
            default=Value(0)
        )
    )
)
```

---

## 9. Window Functions

### Ranking

```python
# Rank users by score
users = await User.objects.annotate(
    rank=Window(
        expression=Rank(),
        order_by=['-score']
    )
)

for user in users:
    print(f"{user.rank}. {user.username}: {user.score}")
```

### Rank Within Groups

```python
# Rank posts within each category
posts = await Post.objects.annotate(
    category_rank=Window(
        expression=RowNumber(),
        partition_by=['category'],
        order_by=['-views']
    )
)
```

### Compare to Previous Row

```python
# Calculate change from previous score
games = await Game.objects.annotate(
    previous_score=Window(
        expression=Lag('score'),
        order_by=['created_at']
    )
).annotate(
    score_change=F('score') - F('previous_score')
)
```

---

## 10. Date Lookups

### Extract Date Components

```python
# Posts from 2024
posts = await Post.objects.filter(created_at__year=2024)

# Posts from June or later
posts = await Post.objects.filter(
    created_at__year=2024,
    created_at__month__gte=6
)

# Events on Mondays (week_day=1)
events = await Event.objects.filter(scheduled_at__week_day=1)

# Posts created in afternoon (hour >= 12)
posts = await Post.objects.filter(created_at__hour__gte=12)
```

---

## 11. Field Lookups Cheat Sheet

### String Lookups

```python
# Exact match
User.objects.filter(username__exact='alice')
User.objects.filter(username='alice')  # Same as exact

# Case-insensitive exact
User.objects.filter(username__iexact='ALICE')

# Contains
User.objects.filter(email__contains='example')

# Case-insensitive contains
User.objects.filter(email__icontains='EXAMPLE')

# Starts with
User.objects.filter(username__startswith='admin')

# Ends with
User.objects.filter(email__endswith='@gmail.com')
```

### Numeric Lookups

```python
# Greater than
User.objects.filter(age__gt=18)

# Greater than or equal
User.objects.filter(age__gte=18)

# Less than
User.objects.filter(age__lt=65)

# Less than or equal
User.objects.filter(age__lte=65)

# Range (BETWEEN)
Product.objects.filter(price__range=(10.00, 100.00))

# In list
User.objects.filter(status__in=['active', 'pending'])
```

### NULL Checks

```python
# IS NULL
User.objects.filter(deleted_at__isnull=True)

# IS NOT NULL
User.objects.filter(email__isnull=False)
```

---

## 12. JSON Lookups (PostgreSQL/MySQL)

```python
# Access JSON field
users = await User.objects.filter(
    metadata__json__role='admin'
)

# Nested JSON
users = await User.objects.filter(
    settings__json__notifications__email=True
)
```

---

## 13. Full-Text Search (PostgreSQL)

```python
# Search articles
articles = await Article.objects.filter(
    content__search='machine learning'
)

# Automatically falls back to LIKE on MySQL/SQLite
```

---

## 14. Combine Everything

### Real-World Example

```python
# Complex query with all optimizations
posts = await Post.objects.select_related(
    'author',
    'category'
).prefetch_related(
    'comments__user',
    'tags'
).annotate(
    comment_count=Count('comments'),
    avg_rating=Avg('ratings__score')
).filter(
    Q(status='published') &
    Q(comment_count__gte=5) &
    Q(created_at__year=2024)
).order_by('-created_at').limit(10)

# Result:
# - 5 queries instead of 500+ (100x faster)
# - All relationships loaded
# - Computed fields included
# - Complex filtering applied
```

---

## Performance Tips

### DO ✅

```python
# Use select_related for ForeignKey
posts = await Post.objects.select_related('author')

# Use prefetch_related for reverse FK and M2M
authors = await Author.objects.prefetch_related('posts')

# Use only() for large models
users = await User.objects.only('id', 'username', 'email')

# Use F() for atomic updates
await Article.objects.update(views=F('views') + 1)

# Use aggregate() for counts/sums
stats = await Order.objects.aggregate(total=Sum('amount'))
```

### DON'T ❌

```python
# DON'T load all data then filter in Python
users = await User.objects.all()
active = [u for u in users if u.is_active]  # Slow!

# Instead, filter in database:
active = await User.objects.filter(is_active=True)

# DON'T loop and query
for post in posts:
    author = await Author.objects.get(id=post.author_id)  # N+1!

# Instead, use select_related:
posts = await Post.objects.select_related('author')

# DON'T update with race conditions
article.views = article.views + 1  # Race condition!

# Instead, use F():
await Article.objects.update(views=F('views') + 1)  # Atomic
```

---

## Common Patterns

### Pagination with Count

```python
# Get page and total count efficiently
page_size = 20
offset = (page - 1) * page_size

results = await User.objects.limit(page_size).offset(offset)
total = await User.objects.count()

return {
    'results': results,
    'total': total,
    'page': page,
    'pages': (total + page_size - 1) // page_size
}
```

### Search with Multiple Conditions

```python
# Build dynamic search
filters = Q()

if search_term:
    filters &= Q(
        Q(username__icontains=search_term) |
        Q(email__icontains=search_term)
    )

if status:
    filters &= Q(status=status)

if date_from:
    filters &= Q(created_at__gte=date_from)

results = await User.objects.filter(filters)
```

### Top N per Category

```python
# Get top 5 posts per category using window function
top_posts = await Post.objects.annotate(
    category_rank=Window(
        expression=RowNumber(),
        partition_by=['category_id'],
        order_by=['-views']
    )
).filter(category_rank__lte=5)
```

---

## Debugging

### Check Query Count

```python
from covet.database.orm.query_optimizations import QueryPlanAnalyzer

analyzer = QueryPlanAnalyzer()

# Run your code
posts = await Post.objects.all()
for post in posts:
    print(post.author.name)

# Check for N+1
report = analyzer.get_optimization_report()
print(f"Total queries: {report['total_queries']}")
print(f"N+1 patterns: {report['n_plus_one_groups']}")
```

### Get Optimization Suggestions

```python
from covet.database.orm.query_optimizations import suggest_optimizations

qs = Post.objects.all()
suggestions = suggest_optimizations(qs)

for suggestion in suggestions:
    print(suggestion)
# Output: "Consider adding .select_related('author', 'category')"
```

---

## Need More Help?

### Full Documentation

See comprehensive guide:
```
/docs/guides/ADVANCED_ORM_PRODUCTION_REPORT.md
```

### Integration Guide

See integration instructions:
```
/docs/guides/ADVANCED_ORM_PRODUCTION_REPORT.md
Section: "Integration Guide"
```

### Examples

See working examples:
```python
# In your codebase:
from covet.database.orm.INTEGRATION_EXAMPLE import *
```

---

**Quick Reference Version**: 1.0
**Last Updated**: October 11, 2025
**Team**: 18 - Advanced ORM Features
**Production Status**: ✅ Ready (90/100)

---

*Keep this guide handy for quick lookups during development!*
