"""
Bulk executor service for database operations.

This service coordinates bulk database operations with validation and MTI handling.
"""

import logging
from django.db import transaction

logger = logging.getLogger(__name__)


class BulkExecutor:
    """
    Executes bulk database operations.

    This service coordinates validation, MTI handling, and actual database
    operations. It's the only service that directly calls Django ORM methods.

    Dependencies are explicitly injected via constructor.
    """

    def __init__(self, queryset, analyzer, mti_handler):
        """
        Initialize bulk executor with explicit dependencies.

        Args:
            queryset: Django QuerySet instance
            analyzer: ModelAnalyzer instance (replaces validator + field_tracker)
            mti_handler: MTIHandler instance
        """
        self.queryset = queryset
        self.analyzer = analyzer
        self.mti_handler = mti_handler
        self.model_cls = queryset.model

    def bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
        **kwargs,
    ):
        """
        Execute bulk create operation.

        NOTE: Coordinator is responsible for validation before calling this method.
        This executor trusts that inputs have already been validated.

        Args:
            objs: List of model instances to create (pre-validated)
            batch_size: Number of objects to create per batch
            ignore_conflicts: Whether to ignore conflicts
            update_conflicts: Whether to update on conflict
            update_fields: Fields to update on conflict
            unique_fields: Fields to use for conflict detection
            **kwargs: Additional arguments

        Returns:
            List of created objects
        """
        if not objs:
            return objs

        # Execute bulk create - validation already done by coordinator
        return self._execute_bulk_create(
            objs,
            batch_size,
            ignore_conflicts,
            update_conflicts,
            update_fields,
            unique_fields,
            **kwargs,
        )

    def _execute_bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
        **kwargs,
    ):
        """
        Execute the actual Django bulk_create.

        This is the only method that directly calls Django ORM.
        We must call the base Django QuerySet to avoid recursion.
        """
        from django.db.models import QuerySet

        # Create a base Django queryset (not our HookQuerySet)
        base_qs = QuerySet(model=self.model_cls, using=self.queryset.db)

        return base_qs.bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )

    def bulk_update(self, objs, fields, batch_size=None):
        """
        Execute bulk update operation.

        NOTE: Coordinator is responsible for validation before calling this method.
        This executor trusts that inputs have already been validated.

        Args:
            objs: List of model instances to update (pre-validated)
            fields: List of field names to update
            batch_size: Number of objects to update per batch

        Returns:
            Number of objects updated
        """
        if not objs:
            return 0

        # Execute bulk update - use base Django QuerySet to avoid recursion
        # Validation already done by coordinator
        from django.db.models import QuerySet

        base_qs = QuerySet(model=self.model_cls, using=self.queryset.db)
        return base_qs.bulk_update(objs, fields, batch_size=batch_size)

    def delete_queryset(self):
        """
        Execute delete on the queryset.

        NOTE: Coordinator is responsible for validation before calling this method.
        This executor trusts that inputs have already been validated.

        Returns:
            Tuple of (count, details dict)
        """
        if not self.queryset:
            return 0, {}

        # Execute delete via QuerySet
        # Validation already done by coordinator
        from django.db.models import QuerySet

        return QuerySet.delete(self.queryset)
