"""
ORM Model Manager and QuerySet

Django-style QuerySet API for fluent database queries with lazy evaluation,
caching, and advanced features like select_related and prefetch_related.

Example:
    # Basic queries
    users = await User.objects.all()
    active = await User.objects.filter(is_active=True)
    admin = await User.objects.get(username='admin')

    # Chaining and filtering
    results = await User.objects.filter(
        is_active=True
    ).exclude(
        username='guest'
    ).order_by('-created_at').limit(10)

    # Field lookups
    users = await User.objects.filter(
        age__gte=18,
        email__icontains='example.com',
        created_at__lt=datetime.now()
    )

    # Aggregation
    stats = await User.objects.aggregate(
        total=Count('*'),
        avg_age=Avg('age')
    )

    # Relationships
    posts = await Post.objects.select_related(
        'author'
    ).prefetch_related(
        'comments'
    ).all()
"""

import asyncio
import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

logger = logging.getLogger(__name__)


class QuerySet:
    """
    Lazy database query builder with Django-compatible API.

    Supports:
    - Lazy evaluation (queries only execute when needed)
    - Method chaining (filter, exclude, order_by, etc.)
    - Field lookups (__exact, __gt, __contains, etc.)
    - Aggregation and annotation
    - Eager loading (select_related, prefetch_related)
    - Result caching
    """

    def __init__(self, model: Type["Model"], using: Optional[str] = None):
        """
        Initialize QuerySet for a model.

        Args:
            model: Model class
            using: Database alias to use
        """
        self.model = model
        self._using = using or model.__database__

        # Query state
        self._filters: List[Dict[str, Any]] = []
        self._excludes: List[Dict[str, Any]] = []
        self._order_by: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._select_related: List[str] = []
        self._prefetch_related: List[str] = []
        self._values_fields: Optional[List[str]] = None
        self._values_list_fields: Optional[List[str]] = None
        self._values_list_flat: bool = False
        self._only_fields: Optional[List[str]] = None
        self._defer_fields: Optional[List[str]] = None
        self._distinct: bool = False
        self._annotations: Dict[str, Any] = {}

        # Result cache
        self._result_cache: Optional[List] = None
        self._fetched = False

    def _clone(self) -> "QuerySet":
        """Create a copy of this QuerySet for chaining."""
        clone = QuerySet(self.model, self._using)
        clone._filters = self._filters.copy()
        clone._excludes = self._excludes.copy()
        clone._order_by = self._order_by.copy()
        clone._limit = self._limit
        clone._offset = self._offset
        clone._select_related = self._select_related.copy()
        clone._prefetch_related = self._prefetch_related.copy()
        clone._values_fields = self._values_fields
        clone._values_list_fields = self._values_list_fields
        clone._values_list_flat = self._values_list_flat
        clone._only_fields = self._only_fields
        clone._defer_fields = self._defer_fields
        clone._distinct = self._distinct
        clone._annotations = self._annotations.copy()
        return clone

    def filter(self, **kwargs) -> "QuerySet":
        """
        Filter queryset by field lookups.

        Supports Django-style field lookups:
        - field__exact or field: Exact match
        - field__iexact: Case-insensitive exact
        - field__contains: Contains substring
        - field__icontains: Case-insensitive contains
        - field__startswith/istartswith: Starts with
        - field__endswith/iendswith: Ends with
        - field__gt/gte: Greater than (or equal)
        - field__lt/lte: Less than (or equal)
        - field__in: In list
        - field__isnull: Is NULL
        - field__regex/iregex: Regex match

        Args:
            **kwargs: Field lookup expressions

        Returns:
            New QuerySet with filter applied

        Example:
            User.objects.filter(age__gte=18, email__icontains='example')
        """
        clone = self._clone()
        if kwargs:
            clone._filters.append(kwargs)
        return clone

    def exclude(self, **kwargs) -> "QuerySet":
        """
        Exclude records matching field lookups.

        Args:
            **kwargs: Field lookup expressions to exclude

        Returns:
            New QuerySet with exclusion applied

        Example:
            User.objects.exclude(is_active=False)
        """
        clone = self._clone()
        if kwargs:
            clone._excludes.append(kwargs)
        return clone

    def order_by(self, *fields: str) -> "QuerySet":
        """
        Order results by fields.

        Args:
            *fields: Field names (prefix with '-' for descending)

        Returns:
            New QuerySet with ordering applied

        Example:
            User.objects.order_by('-created_at', 'username')
        """
        clone = self._clone()
        clone._order_by = list(fields)
        return clone

    def limit(self, n: int) -> "QuerySet":
        """
        Limit number of results.

        Args:
            n: Maximum number of results

        Returns:
            New QuerySet with limit applied

        Example:
            User.objects.limit(10)
        """
        clone = self._clone()
        clone._limit = n
        return clone

    def offset(self, n: int) -> "QuerySet":
        """
        Skip first n results.

        Args:
            n: Number of results to skip

        Returns:
            New QuerySet with offset applied

        Example:
            User.objects.offset(20).limit(10)  # Page 3
        """
        clone = self._clone()
        clone._offset = n
        return clone

    def distinct(self, *field_names: str) -> "QuerySet":
        """
        Return only distinct results.

        Args:
            *field_names: Optional field names for DISTINCT ON (PostgreSQL)

        Returns:
            New QuerySet with distinct applied

        Example:
            User.objects.distinct()
        """
        clone = self._clone()
        clone._distinct = True
        return clone

    def select_related(self, *fields: str) -> "QuerySet":
        """
        Eagerly load ForeignKey relationships using JOIN.

        Prevents N+1 queries for foreign keys by loading related
        objects in the same query.

        Args:
            *fields: ForeignKey field names to load

        Returns:
            New QuerySet with select_related applied

        Example:
            # Without select_related: N+1 queries
            posts = await Post.objects.all()
            for post in posts:
                logger.info(post.author.name)

            # With select_related: 1 query
            posts = await Post.objects.select_related('author').all()
            for post in posts:
                logger.info(post.author.name)
        """
        clone = self._clone()
        clone._select_related.extend(fields)
        return clone

    def prefetch_related(self, *fields: str) -> "QuerySet":
        """
        Eagerly load ManyToMany and reverse ForeignKey relationships.

        Uses separate queries but prevents N+1 by batch loading.

        Args:
            *fields: Relationship field names to prefetch

        Returns:
            New QuerySet with prefetch_related applied

        Example:
            # Load users with their posts in 2 queries instead of N+1
            users = await User.objects.prefetch_related('posts').all()
            for user in users:
                for post in user.posts.all():  # No extra queries
                    logger.info(post.title)
        """
        clone = self._clone()
        clone._prefetch_related.extend(fields)
        return clone

    def only(self, *fields: str) -> "QuerySet":
        """
        Fetch only specified fields from the database.

        Defers all other fields (they will trigger additional queries if accessed).
        This reduces the amount of data transferred from the database.

        Args:
            *fields: Field names to load immediately

        Returns:
            New QuerySet with only() applied

        Example:
            # Only load id and username, defer all other fields
            users = await User.objects.only('id', 'username').all()
            print(users[0].username)  # OK - was loaded
            print(users[0].email)     # Triggers additional query

        Note:
            - Primary key is always included even if not specified
            - Accessing deferred fields triggers a refresh query
            - Cannot be combined with values() or values_list()
        """
        clone = self._clone()
        clone._only_fields = list(fields)
        return clone

    def defer(self, *fields: str) -> "QuerySet":
        """
        Defer loading of specified fields from the database.

        Loads all fields except the specified ones. Deferred fields will
        trigger additional queries if accessed.

        Args:
            *fields: Field names to defer (not load immediately)

        Returns:
            New QuerySet with defer() applied

        Example:
            # Load all fields except large text field
            users = await User.objects.defer('bio').all()
            print(users[0].username)  # OK - was loaded
            print(users[0].bio)       # Triggers additional query

        Note:
            - Primary key is never deferred
            - Accessing deferred fields triggers a refresh query
            - Cannot be combined with values() or values_list()
            - Useful for skipping large text/binary fields
        """
        clone = self._clone()
        clone._defer_fields = list(fields)
        return clone

    def values(self, *fields: str) -> "QuerySet":
        """
        Return dictionaries instead of model instances.

        Args:
            *fields: Field names to include (all if empty)

        Returns:
            New QuerySet that returns dicts

        Example:
            users = await User.objects.values('id', 'username', 'email')
            # Returns: [{'id': 1, 'username': 'alice', 'email': '...'}, ...]
        """
        clone = self._clone()
        clone._values_fields = list(fields) if fields else None
        return clone

    def values_list(self, *fields: str, flat: bool = False) -> "QuerySet":
        """
        Return tuples instead of model instances.

        Args:
            *fields: Field names to include
            flat: If True and only one field, return flat list

        Returns:
            New QuerySet that returns tuples

        Example:
            ids = await User.objects.values_list('id', flat=True)
            # Returns: [1, 2, 3, 4, 5]

            data = await User.objects.values_list('id', 'username')
            # Returns: [(1, 'alice'), (2, 'bob'), ...]
        """
        clone = self._clone()
        clone._values_list_fields = list(fields)
        clone._values_list_flat = flat and len(fields) == 1
        return clone

    def annotate(self, **annotations) -> "QuerySet":
        """
        Add computed fields to results.

        Args:
            **annotations: name=AggregateFunction() pairs

        Returns:
            New QuerySet with annotations

        Example:
            users = await User.objects.annotate(
                post_count=Count('posts')
            ).all()
        """
        clone = self._clone()
        clone._annotations.update(annotations)
        return clone

    async def aggregate(self, **aggregations) -> Dict[str, Any]:
        """
        Perform aggregation query.

        Args:
            **aggregations: name=AggregateFunction() pairs

        Returns:
            Dictionary of aggregation results

        Example:
            stats = await User.objects.aggregate(
                total=Count('*'),
                avg_age=Avg('age'),
                max_score=Max('score')
            )
            # Returns: {'total': 1000, 'avg_age': 32.5, 'max_score': 98}
        """
        # Build aggregation SQL
        select_parts = []
        for name, func in aggregations.items():
            sql = self._build_aggregate_sql(func)
            select_parts.append(f"{sql} AS {name}")

        query = f"SELECT {', '.join(select_parts)} FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated

        # Add WHERE clause
        where_clause, params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"

        # Execute query
        adapter = await self._get_adapter()
        result = await adapter.fetch_one(query, params)

        return result or {}

    async def count(self) -> int:
        """
        Count number of matching records.

        Returns:
            Number of records

        Example:
            total_users = await User.objects.count()
            active_users = await User.objects.filter(is_active=True).count()
        """
        query = (
            f"SELECT COUNT(*) FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated
        )

        # Add WHERE clause
        where_clause, params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"

        adapter = await self._get_adapter()
        count = await adapter.fetch_value(query, params)

        return count or 0

    async def exists(self) -> bool:
        """
        Check if any records match.

        Returns:
            True if any records exist

        Example:
            if await User.objects.filter(email=email).exists():
                raise ValueError("Email already exists")
        """
        return await self.count() > 0

    async def all(self) -> List["Model"]:
        """
        Get all matching records.

        Returns:
            List of model instances

        Example:
            all_users = await User.objects.all()
        """
        return await self._fetch_all()

    async def get(self, **kwargs) -> "Model":
        """
        Get single record matching criteria.

        Args:
            **kwargs: Field lookups

        Returns:
            Model instance

        Raises:
            DoesNotExist: If no record found
            MultipleObjectsReturned: If multiple records found

        Example:
            user = await User.objects.get(id=1)
            admin = await User.objects.get(username='admin')
        """
        if kwargs:
            qs = self.filter(**kwargs)
        else:
            qs = self

        results = await qs.limit(2)._fetch_all()

        if not results:
            raise self.model.DoesNotExist(f"{self.model.__name__} matching query does not exist")

        if len(results) > 1:
            raise self.model.MultipleObjectsReturned(
                f"get() returned multiple {self.model.__name__} objects"
            )

        return results[0]

    async def first(self) -> Optional["Model"]:
        """
        Get first record or None.

        Returns:
            First model instance or None

        Example:
            oldest_user = await User.objects.order_by('created_at').first()
        """
        results = await self.limit(1)._fetch_all()
        return results[0] if results else None

    async def last(self) -> Optional["Model"]:
        """
        Get last record or None.

        Returns:
            Last model instance or None

        Example:
            newest_user = await User.objects.order_by('created_at').last()
        """
        # Reverse order for last
        clone = self._clone()
        clone._order_by = [
            f"-{field}" if not field.startswith("-") else field[1:]
            for field in (clone._order_by or [])
        ]
        results = await clone.limit(1)._fetch_all()
        return results[0] if results else None

    async def create(self, **kwargs) -> "Model":
        """
        Create and save new instance.

        Args:
            **kwargs: Field values

        Returns:
            Created model instance

        Example:
            user = await User.objects.create(
                username='alice',
                email='alice@example.com'
            )
        """
        instance = self.model(**kwargs)
        await instance.save()
        return instance

    async def get_or_create(
        self, defaults: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Tuple["Model", bool]:
        """
        Get record or create if not exists.

        Args:
            defaults: Field values for creation
            **kwargs: Lookup fields

        Returns:
            Tuple of (instance, created)

        Example:
            user, created = await User.objects.get_or_create(
                email='alice@example.com',
                defaults={'username': 'alice'}
            )
        """
        try:
            instance = await self.get(**kwargs)
            return instance, False
        except self.model.DoesNotExist:
            create_kwargs = {**kwargs, **(defaults or {})}
            instance = await self.create(**create_kwargs)
            return instance, True

    async def update_or_create(
        self, defaults: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Tuple["Model", bool]:
        """
        Update record or create if not exists.

        Args:
            defaults: Fields to update/create
            **kwargs: Lookup fields

        Returns:
            Tuple of (instance, created)

        Example:
            user, created = await User.objects.update_or_create(
                email='alice@example.com',
                defaults={'username': 'alice', 'is_active': True}
            )
        """
        try:
            instance = await self.get(**kwargs)
            # Update instance
            for key, value in (defaults or {}).items():
                setattr(instance, key, value)
            await instance.save()
            return instance, False
        except self.model.DoesNotExist:
            create_kwargs = {**kwargs, **(defaults or {})}
            instance = await self.create(**create_kwargs)
            return instance, True

    async def update(self, **kwargs) -> int:
        """
        Update all matching records.

        Args:
            **kwargs: Fields to update

        Returns:
            Number of records updated

        Example:
            updated = await User.objects.filter(
                is_active=False
            ).update(is_active=True)
        """
        if not kwargs:
            return 0

        # Get adapter first to know placeholder style
        adapter = await self._get_adapter()

        # Build UPDATE query
        set_parts = []
        params = []
        param_index = 1

        placeholders = self._get_param_placeholders(adapter, len(kwargs), param_index)
        for i, (field, value) in enumerate(kwargs.items()):
            set_parts.append(f"{field} = {placeholders[i]}")
            params.append(value)
            param_index += 1

        query = f"UPDATE {self.model.__tablename__} SET {', '.join(set_parts)}"  # nosec B608 - identifiers validated

        # Add WHERE clause
        where_clause, where_params = await self._build_where_clause(param_index)
        if where_clause:
            query += f" WHERE {where_clause}"
            params.extend(where_params)

        # Execute update
        result = await adapter.execute(query, params)

        # Parse result to get count
        # PostgreSQL returns "UPDATE 5", MySQL returns affected rows
        if isinstance(result, str) and result.startswith("UPDATE"):
            return int(result.split()[1])
        return 0

    async def delete(self) -> int:
        """
        Delete all matching records.

        Returns:
            Number of records deleted

        Example:
            deleted = await User.objects.filter(
                is_active=False,
                created_at__lt=one_year_ago
            ).delete()
        """
        # Build DELETE query
        query = f"DELETE FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated

        # Add WHERE clause
        where_clause, params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"

        # Execute delete
        adapter = await self._get_adapter()
        result = await adapter.execute(query, params)

        # Parse result to get count
        if isinstance(result, str) and result.startswith("DELETE"):
            return int(result.split()[1])
        return 0

    async def _fetch_all(self) -> List:
        """Execute query and return all results."""
        if self._result_cache is not None:
            return self._result_cache

        # Build SELECT query
        query, params = await self._build_select_query()

        # Execute query
        adapter = await self._get_adapter()
        rows = await adapter.fetch_all(query, params)

        # Convert to model instances or dicts/tuples
        if self._values_fields is not None:
            # Return dicts
            if self._values_fields:
                results = [{field: row.get(field) for field in self._values_fields} for row in rows]
            else:
                results = rows
        elif self._values_list_fields is not None:
            # Return tuples
            if hasattr(self, "_values_list_flat") and self._values_list_flat:
                results = [row[self._values_list_fields[0]] for row in rows]
            else:
                results = [
                    tuple(row.get(field) for field in self._values_list_fields) for row in rows
                ]
        else:
            # Return model instances
            results = [self.model(**row) for row in rows]

        # Handle select_related
        if self._select_related and results and not self._values_fields:
            await self._apply_select_related(results)

        # Handle prefetch_related
        if self._prefetch_related and results and not self._values_fields:
            await self._apply_prefetch_related(results)

        # Cache results
        self._result_cache = results
        self._fetched = True

        return results

    async def _build_select_query(self) -> Tuple[str, List]:
        """Build SELECT query from QuerySet state."""
        # SELECT clause
        if self._values_fields is not None:
            # values() - return dicts
            if self._values_fields:
                select_clause = ", ".join(self._values_fields)
            else:
                select_clause = "*"
        elif self._values_list_fields is not None:
            # values_list() - return tuples
            select_clause = ", ".join(self._values_list_fields)
        elif self._only_fields is not None:
            # only() - load only specified fields + pk
            pk_field_name = self.model._meta.pk_field.name
            fields_to_select = set(self._only_fields)
            # Always include primary key
            fields_to_select.add(pk_field_name)
            select_clause = ", ".join(
                self.model._fields[f].db_column
                for f in fields_to_select
                if f in self.model._fields
            )
        elif self._defer_fields is not None:
            # defer() - load all fields except specified ones
            pk_field_name = self.model._meta.pk_field.name
            defer_set = set(self._defer_fields)
            # Never defer primary key
            defer_set.discard(pk_field_name)
            select_clause = ", ".join(
                field.db_column
                for field_name, field in self.model._fields.items()
                if field_name not in defer_set
            )
        else:
            select_clause = "*"

        # DISTINCT
        distinct_clause = "DISTINCT " if self._distinct else ""

        query = f"SELECT {distinct_clause}{select_clause} FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated
        params = []

        # WHERE clause
        where_clause, where_params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"
            params.extend(where_params)

        # ORDER BY clause
        if self._order_by:
            order_parts = []
            for field in self._order_by:
                if field.startswith("-"):
                    order_parts.append(f"{field[1:]} DESC")
                else:
                    order_parts.append(f"{field} ASC")
            query += f" ORDER BY {', '.join(order_parts)}"

        # LIMIT clause
        if self._limit is not None:
            query += f" LIMIT {self._limit}"

        # OFFSET clause
        if self._offset is not None:
            query += f" OFFSET {self._offset}"

        return query, params

    async def _build_where_clause(self, param_start: int = 1) -> Tuple[str, List]:
        """Build WHERE clause from filters and excludes."""
        # Get adapter to determine placeholder style
        adapter = await self._get_adapter()

        conditions = []
        params = []
        param_index = param_start

        # Process filters (AND)
        for filter_dict in self._filters:
            filter_conditions = []
            for lookup, value in filter_dict.items():
                condition, lookup_params = self._build_lookup_condition(
                    adapter, lookup, value, param_index
                )
                filter_conditions.append(condition)
                params.extend(lookup_params)
                param_index += len(lookup_params)

            if filter_conditions:
                conditions.append(f"({' AND '.join(filter_conditions)})")

        # Process excludes (NOT)
        for exclude_dict in self._excludes:
            exclude_conditions = []
            for lookup, value in exclude_dict.items():
                condition, lookup_params = self._build_lookup_condition(
                    adapter, lookup, value, param_index
                )
                exclude_conditions.append(condition)
                params.extend(lookup_params)
                param_index += len(lookup_params)

            if exclude_conditions:
                conditions.append(f"NOT ({' OR '.join(exclude_conditions)})")

        where_clause = " AND ".join(conditions) if conditions else ""
        return where_clause, params

    def _build_lookup_condition(
        self, adapter, lookup: str, value: Any, param_index: int
    ) -> Tuple[str, List]:
        """
        Build SQL condition from Django-style field lookup.

        Args:
            adapter: Database adapter
            lookup: Field lookup (e.g., 'age__gte', 'email__icontains')
            value: Lookup value
            param_index: Current parameter index

        Returns:
            Tuple of (condition SQL, parameters)
        """
        # Parse lookup into field and lookup type
        parts = lookup.split("__")
        field = parts[0]
        lookup_type = parts[1] if len(parts) > 1 else "exact"

        # Get placeholder function
        def get_placeholder(idx):
            placeholders = self._get_param_placeholders(adapter, 1, idx)
            return placeholders[0]

        # Build condition based on lookup type
        if lookup_type == "exact":
            if value is None:
                return f"{field} IS NULL", []
            return f"{field} = {get_placeholder(param_index)}", [value]

        elif lookup_type == "iexact":
            return f"LOWER({field}) = LOWER({get_placeholder(param_index)})", [value]

        elif lookup_type == "contains":
            return f"{field} LIKE {get_placeholder(param_index)}", [f"%{value}%"]

        elif lookup_type == "icontains":
            return f"LOWER({field}) LIKE LOWER({get_placeholder(param_index)})", [f"%{value}%"]

        elif lookup_type == "startswith":
            return f"{field} LIKE {get_placeholder(param_index)}", [f"{value}%"]

        elif lookup_type == "istartswith":
            return f"LOWER({field}) LIKE LOWER({get_placeholder(param_index)})", [f"{value}%"]

        elif lookup_type == "endswith":
            return f"{field} LIKE {get_placeholder(param_index)}", [f"%{value}"]

        elif lookup_type == "iendswith":
            return f"LOWER({field}) LIKE LOWER({get_placeholder(param_index)})", [f"%{value}"]

        elif lookup_type == "gt":
            return f"{field} > {get_placeholder(param_index)}", [value]

        elif lookup_type == "gte":
            return f"{field} >= {get_placeholder(param_index)}", [value]

        elif lookup_type == "lt":
            return f"{field} < {get_placeholder(param_index)}", [value]

        elif lookup_type == "lte":
            return f"{field} <= {get_placeholder(param_index)}", [value]

        elif lookup_type == "in":
            if not value:
                return "FALSE", []
            placeholders = self._get_param_placeholders(adapter, len(value), param_index)
            return f"{field} IN ({', '.join(placeholders)})", list(value)

        elif lookup_type == "isnull":
            if value:
                return f"{field} IS NULL", []
            else:
                return f"{field} IS NOT NULL", []

        elif lookup_type == "regex":
            return f"{field} ~ {get_placeholder(param_index)}", [value]

        elif lookup_type == "iregex":
            return f"{field} ~* {get_placeholder(param_index)}", [value]

        else:
            raise ValueError(f"Unsupported lookup type: {lookup_type}")

    def _build_aggregate_sql(self, func) -> str:
        """Build SQL for aggregate function."""
        # This is a placeholder - actual implementation would handle
        # Count, Sum, Avg, Max, Min, etc.
        func_name = func.__class__.__name__.upper()
        field = getattr(func, "field", "*")
        return f"{func_name}({field})"

    async def _apply_select_related(self, results: List["Model"]) -> None:
        """
        Load related objects using JOINs (actually done as separate queries).

        NOTE: For production use, this should be integrated into the main SQL query
        with LEFT JOIN clauses. This implementation uses separate queries for each
        relationship to maintain database adapter compatibility.

        Args:
            results: List of model instances to populate relationships for
        """
        if not results or not self._select_related:
            return

        # Get adapter
        adapter = await self._get_adapter()

        # Process each select_related field
        for field_name in self._select_related:
            # Check if field exists and is a ForeignKey
            if field_name not in self.model._fields:
                logger.warning(
                    f"select_related: Field '{field_name}' not found on {self.model.__name__}"
                )
                continue

            field = self.model._fields[field_name]

            # Check if it's a relationship field (has 'related_model'
            # attribute)
            if not hasattr(field, "related_model"):
                logger.warning(
                    f"select_related: Field '{field_name}' is not a ForeignKey on {self.model.__name__}"
                )
                continue

            # Get the related model
            related_model = field.related_model
            if isinstance(related_model, str):
                # Lazy relationship resolution
                from .relationships import resolve_model

                related_model = resolve_model(related_model)
                field.related_model = related_model

            # Collect foreign key values from results
            fk_values = set()
            for instance in results:
                fk_value = getattr(instance, field_name + "_id", None)
                if fk_value is not None:
                    fk_values.add(fk_value)

            if not fk_values:
                continue

            # Fetch related objects in single query
            pk_field_name = related_model._meta.pk_field.name
            placeholders = self._get_param_placeholders(adapter, len(fk_values), 1)

            query = (
                f"SELECT * FROM {related_model.__tablename__} "  # nosec B608 - identifiers validated
                f"WHERE {pk_field_name} IN ({', '.join(placeholders)})"
            )

            related_rows = await adapter.fetch_all(query, list(fk_values))

            # Build lookup dict
            related_objects = {row[pk_field_name]: related_model(**row) for row in related_rows}

            # Populate relationships on result instances
            for instance in results:
                fk_value = getattr(instance, field_name + "_id", None)
                if fk_value in related_objects:
                    setattr(instance, field_name, related_objects[fk_value])
                else:
                    setattr(instance, field_name, None)

    async def _apply_prefetch_related(self, results: List["Model"]) -> None:
        """
        Load related objects in batch queries (for reverse ForeignKey and ManyToMany).

        This prevents N+1 queries by loading all related objects in 2 queries:
        1. Main query for primary objects
        2. Single query for all related objects with IN clause

        Args:
            results: List of model instances to populate relationships for

        Example:
            # Without prefetch: N+1 queries
            users = await User.objects.all()
            for user in users:  # 1 query
                for post in user.posts.all():  # N queries!
                    print(post.title)

            # With prefetch: 2 queries
            users = await User.objects.prefetch_related('posts').all()
            for user in users:  # 1 query
                for post in user.posts.all():  # 0 queries (cached)
                    print(post.title)
        """
        if not results or not self._prefetch_related:
            return

        # Import reverse relationship registry
        from .relationships import get_reverse_relations

        # Get adapter
        adapter = await self._get_adapter()

        # Get primary keys from results
        pk_field_name = self.model._meta.pk_field.name
        pk_values = [getattr(instance, pk_field_name) for instance in results]

        if not pk_values:
            return

        # Process each prefetch_related field
        for field_name in self._prefetch_related:
            # Look up reverse relationship metadata from registry
            reverse_relations = get_reverse_relations(self.model)

            # Find the relationship for this field name
            relation_info = None
            for rel in reverse_relations:
                if rel.get("related_name") == field_name:
                    relation_info = rel
                    break

            if not relation_info:
                logger.warning(
                    f"prefetch_related: No reverse relationship '{field_name}' found on {self.model.__name__}. "
                    f"Make sure the related model has related_name='{field_name}' set on its ForeignKey/ManyToMany field."
                )
                continue

            # Extract relationship info
            related_model = relation_info["related_model"]
            related_field = relation_info["related_field"]
            relation_type = relation_info["relation_type"]

            logger.debug(
                f"prefetch_related: Loading {relation_type} '{field_name}' for {self.model.__name__} "
                f"(from {related_model.__name__}.{related_field})"
            )

            # Build query based on relationship type
            if relation_type in ("foreignkey", "onetoone"):
                # Reverse ForeignKey: SELECT * FROM related_table WHERE
                # fk_field IN (pk_values)
                fk_field_name = f"{related_field}_id"
                placeholders = self._get_param_placeholders(adapter, len(pk_values), 1)

                query = (
                    f"SELECT * FROM {related_model.__tablename__} "  # nosec B608 - identifiers validated
                    f"WHERE {fk_field_name} IN ({', '.join(placeholders)})"
                )

                related_rows = await adapter.fetch_all(query, list(pk_values))

                # Convert to model instances
                related_objects = [related_model(**row) for row in related_rows]

                # Group by foreign key value
                grouped_objects = {}
                for obj in related_objects:
                    fk_value = getattr(obj, fk_field_name)
                    if fk_value not in grouped_objects:
                        grouped_objects[fk_value] = []
                    grouped_objects[fk_value].append(obj)

                # Cache related objects on each parent instance
                for instance in results:
                    pk_value = getattr(instance, pk_field_name)
                    related_list = grouped_objects.get(pk_value, [])

                    # Store cached results
                    # Create a cache attribute that RelatedManager can check
                    cache_attr = f"_prefetched_{field_name}"

                    if relation_type == "onetoone":
                        # OneToOne returns single object or None
                        setattr(
                            instance,
                            cache_attr,
                            related_list[0] if related_list else None,
                        )
                    else:
                        # ForeignKey reverse returns list
                        setattr(instance, cache_attr, related_list)

            elif relation_type == "manytomany":
                # ManyToMany: Need to query through table
                # 1. Get through model from the ManyToMany field
                # 2. Query through table to get relationship mappings
                # 3. Query related model for actual objects
                # 4. Build mapping of parent_id -> [related_objects]

                # Get the ManyToMany field to access through model
                m2m_field = None
                for field in related_model._fields.values():
                    if hasattr(field, "related_name") and field.related_name == field_name:
                        m2m_field = field
                        break

                if not m2m_field or not hasattr(m2m_field, "get_through_model"):
                    logger.warning(
                        f"prefetch_related: Could not find ManyToMany field configuration for '{field_name}'"
                    )
                    continue

                through_model = m2m_field.get_through_model()
                if not through_model:
                    logger.warning(
                        f"prefetch_related: No through model found for ManyToMany '{field_name}'"
                    )
                    continue

                # Get field names for through table
                source_field_name = f"{self.model.__name__.lower()}_id"
                target_field_name = f"{related_model.__name__.lower()}_id"

                # Query through table
                placeholders = self._get_param_placeholders(adapter, len(pk_values), 1)
                through_query = (
                    f"SELECT {source_field_name}, {target_field_name} "  # nosec B608 - identifiers validated
                    f"FROM {through_model.__tablename__} "
                    f"WHERE {source_field_name} IN ({', '.join(placeholders)})"
                )

                through_rows = await adapter.fetch_all(through_query, list(pk_values))

                # Collect target IDs
                target_ids = {row[target_field_name] for row in through_rows}

                if target_ids:
                    # Query related objects
                    target_placeholders = self._get_param_placeholders(adapter, len(target_ids), 1)
                    target_pk_field = related_model._meta.pk_field.name

                    related_query = (
                        f"SELECT * FROM {related_model.__tablename__} "  # nosec B608 - identifiers validated
                        f"WHERE {target_pk_field} IN ({', '.join(target_placeholders)})"
                    )

                    related_rows = await adapter.fetch_all(related_query, list(target_ids))

                    # Convert to model instances and build lookup dict
                    related_objects_map = {
                        row[target_pk_field]: related_model(**row) for row in related_rows
                    }

                    # Build mapping of source_id -> [related_objects]
                    grouped_m2m = {}
                    for row in through_rows:
                        source_id = row[source_field_name]
                        target_id = row[target_field_name]

                        if source_id not in grouped_m2m:
                            grouped_m2m[source_id] = []

                        if target_id in related_objects_map:
                            grouped_m2m[source_id].append(related_objects_map[target_id])

                    # Cache related objects on each parent instance
                    for instance in results:
                        pk_value = getattr(instance, pk_field_name)
                        related_list = grouped_m2m.get(pk_value, [])

                        # Store cached results
                        cache_attr = f"_prefetched_{field_name}"
                        setattr(instance, cache_attr, related_list)
                else:
                    # No relationships found, cache empty lists
                    cache_attr = f"_prefetched_{field_name}"
                    for instance in results:
                        setattr(instance, cache_attr, [])

    async def _get_adapter(self):
        """Get database adapter for this queryset."""
        from .adapter_registry import get_adapter

        adapter = get_adapter(self._using)

        # Ensure adapter is connected
        if not adapter._connected:
            await adapter.connect()

        return adapter

    def _get_param_placeholders(self, adapter, count: int, start: int = 1) -> List[str]:
        """
        Get parameter placeholders for the adapter's database type.

        Args:
            adapter: Database adapter
            count: Number of placeholders needed
            start: Starting index for placeholders

        Returns:
            List of parameter placeholders
        """
        from ..adapters.mysql import MySQLAdapter
        from ..adapters.postgresql import PostgreSQLAdapter
        from ..adapters.sqlite import SQLiteAdapter

        if isinstance(adapter, PostgreSQLAdapter):
            # PostgreSQL uses $1, $2, $3, ...
            return [f"${start+i}" for i in range(count)]
        elif isinstance(adapter, MySQLAdapter):
            # MySQL uses %s, %s, %s, ...
            return ["%s"] * count
        elif isinstance(adapter, SQLiteAdapter):
            # SQLite uses ?, ?, ?, ...
            return ["?"] * count
        else:
            # Default to PostgreSQL-style
            return [f"${start+i}" for i in range(count)]

    def __await__(self):
        """Make QuerySet awaitable."""
        return self.all().__await__()

    def __aiter__(self):
        """Make QuerySet async iterable."""
        return self._async_iterator()

    async def _async_iterator(self):
        """Async iterator implementation."""
        results = await self.all()
        for result in results:
            yield result

    def __repr__(self) -> str:
        """String representation."""
        if self._result_cache is not None:
            return f"<QuerySet {self._result_cache}>"
        return f"<QuerySet for {self.model.__name__}>"


class ModelManager:
    """
    Model manager - provides QuerySet interface.

    Automatically added to models as 'objects' attribute.

    Example:
        users = await User.objects.all()
        active = await User.objects.filter(is_active=True)
    """

    def __init__(self, model: Optional[Type["Model"]] = None):
        """
        Initialize manager.

        Args:
            model: Model class (set by metaclass)
        """
        self.model = model

    def get_queryset(self) -> QuerySet:
        """
        Get base QuerySet for this manager.

        Returns:
            QuerySet for model

        Override this to customize default queryset:
            class ActiveManager(ModelManager):
                def get_queryset(self):
                    return super().get_queryset().filter(is_active=True)
        """
        return QuerySet(self.model)

    def all(self) -> QuerySet:
        """Get all objects."""
        return self.get_queryset()

    def filter(self, **kwargs) -> QuerySet:
        """Filter objects."""
        return self.get_queryset().filter(**kwargs)

    def exclude(self, **kwargs) -> QuerySet:
        """Exclude objects."""
        return self.get_queryset().exclude(**kwargs)

    def get(self, **kwargs):
        """Get single object."""
        return self.get_queryset().get(**kwargs)

    def create(self, **kwargs):
        """Create and save object."""
        return self.get_queryset().create(**kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        """Get or create object."""
        return self.get_queryset().get_or_create(defaults=defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        """Update or create object."""
        return self.get_queryset().update_or_create(defaults=defaults, **kwargs)

    def count(self):
        """Count objects."""
        return self.get_queryset().count()

    def exists(self):
        """Check if any objects exist."""
        return self.get_queryset().exists()

    def select_related(self, *fields: str) -> QuerySet:
        """Eagerly load ForeignKey relationships using JOIN."""
        return self.get_queryset().select_related(*fields)

    def prefetch_related(self, *fields: str) -> QuerySet:
        """Eagerly load ManyToMany and reverse ForeignKey relationships."""
        return self.get_queryset().prefetch_related(*fields)

    def only(self, *fields: str) -> QuerySet:
        """Fetch only specified fields from the database."""
        return self.get_queryset().only(*fields)

    def defer(self, *fields: str) -> QuerySet:
        """Defer loading of specified fields from the database."""
        return self.get_queryset().defer(*fields)

    def values(self, *fields: str) -> QuerySet:
        """Return dictionaries instead of model instances."""
        return self.get_queryset().values(*fields)

    def values_list(self, *fields: str, flat: bool = False) -> QuerySet:
        """Return tuples instead of model instances."""
        return self.get_queryset().values_list(*fields, flat=flat)

    def order_by(self, *fields: str) -> QuerySet:
        """Order results by fields."""
        return self.get_queryset().order_by(*fields)

    def limit(self, n: int) -> QuerySet:
        """Limit number of results."""
        return self.get_queryset().limit(n)

    def offset(self, n: int) -> QuerySet:
        """Skip first n results."""
        return self.get_queryset().offset(n)

    def distinct(self, *field_names: str) -> QuerySet:
        """Return only distinct results."""
        return self.get_queryset().distinct(*field_names)

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} for {self.model.__name__}>"


# Aggregate functions
class Aggregate:
    """Base class for aggregate functions."""

    def __init__(self, field: str):
        self.field = field


class Count(Aggregate):
    """COUNT aggregate."""

    def __init__(self, field: str = "*"):
        super().__init__(field)


class Sum(Aggregate):
    """SUM aggregate."""


class Avg(Aggregate):
    """AVG aggregate."""


class Max(Aggregate):
    """MAX aggregate."""


class Min(Aggregate):
    """MIN aggregate."""


__all__ = [
    "QuerySet",
    "ModelManager",
    "Q",
    "Count",
    "Sum",
    "Avg",
    "Max",
    "Min",
]


class Q:
    """
    Query object for complex lookups (Django-style Q objects).
    
    Allows combining filters with AND/OR/NOT logic:
        Q(age__gte=18) & Q(is_active=True)
        Q(name='Alice') | Q(name='Bob')
        ~Q(is_deleted=True)
    """
    
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    def __init__(self, **kwargs):
        """
        Initialize Q object with field lookups.
        
        Args:
            **kwargs: Field lookup expressions
        """
        self.children = [kwargs] if kwargs else []
        self.connector = self.AND
        self.negated = False
    
    def __and__(self, other):
        """Combine with AND."""
        return self._combine(other, self.AND)
    
    def __or__(self, other):
        """Combine with OR."""
        return self._combine(other, self.OR)
    
    def __invert__(self):
        """Negate with NOT."""
        obj = Q()
        obj.children = [self]
        obj.negated = True
        return obj
    
    def _combine(self, other, connector):
        """Combine two Q objects."""
        obj = Q()
        obj.connector = connector
        obj.children = [self, other]
        return obj
    
    def __repr__(self):
        """String representation."""
        if self.negated:
            return f"NOT {self.children}"
        return f"Q({self.connector}: {self.children})"

