"""
Bulk operation coordinator - Single entry point for all bulk operations.

This facade hides the complexity of wiring up multiple services and provides
a clean, simple API for the QuerySet to use.
"""

import logging
from django.db import transaction
from django.db.models import QuerySet as BaseQuerySet

from django_bulk_hooks.helpers import (
    build_changeset_for_create,
    build_changeset_for_update,
    build_changeset_for_delete,
)

logger = logging.getLogger(__name__)


class BulkOperationCoordinator:
    """
    Single entry point for coordinating bulk operations.

    This coordinator manages all services and provides a clean facade
    for the QuerySet. It wires up services and coordinates the hook
    lifecycle for each operation type.

    Services are created lazily and cached.
    """

    def __init__(self, queryset):
        """
        Initialize coordinator for a queryset.

        Args:
            queryset: Django QuerySet instance
        """
        self.queryset = queryset
        self.model_cls = queryset.model

        # Lazy initialization
        self._analyzer = None
        self._mti_handler = None
        self._executor = None
        self._dispatcher = None

    @property
    def analyzer(self):
        """Get or create ModelAnalyzer"""
        if self._analyzer is None:
            from django_bulk_hooks.operations.analyzer import ModelAnalyzer

            self._analyzer = ModelAnalyzer(self.model_cls)
        return self._analyzer

    @property
    def mti_handler(self):
        """Get or create MTIHandler"""
        if self._mti_handler is None:
            from django_bulk_hooks.operations.mti_handler import MTIHandler

            self._mti_handler = MTIHandler(self.model_cls)
        return self._mti_handler

    @property
    def executor(self):
        """Get or create BulkExecutor"""
        if self._executor is None:
            from django_bulk_hooks.operations.bulk_executor import BulkExecutor

            self._executor = BulkExecutor(
                queryset=self.queryset,
                analyzer=self.analyzer,
                mti_handler=self.mti_handler,
            )
        return self._executor

    @property
    def dispatcher(self):
        """Get or create Dispatcher"""
        if self._dispatcher is None:
            from django_bulk_hooks.dispatcher import get_dispatcher

            self._dispatcher = get_dispatcher()
        return self._dispatcher

    # ==================== PUBLIC API ====================

    @transaction.atomic
    def create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
        bypass_hooks=False,
        bypass_validation=False,
    ):
        """
        Execute bulk create with hooks.

        Args:
            objs: List of model instances to create
            batch_size: Number of objects per batch
            ignore_conflicts: Ignore conflicts if True
            update_conflicts: Update on conflict if True
            update_fields: Fields to update on conflict
            unique_fields: Fields to check for conflicts
            bypass_hooks: Skip all hooks if True
            bypass_validation: Skip validation hooks if True

        Returns:
            List of created objects
        """
        if not objs:
            return objs

        # Validate
        self.analyzer.validate_for_create(objs)

        # Build initial changeset
        changeset = build_changeset_for_create(
            self.model_cls,
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )

        # Execute with hook lifecycle
        def operation():
            return self.executor.bulk_create(
                objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
            )

        return self.dispatcher.execute_operation_with_hooks(
            changeset=changeset,
            operation=operation,
            event_prefix="create",
            bypass_hooks=bypass_hooks,
            bypass_validation=bypass_validation,
        )

    @transaction.atomic
    def update(
        self,
        objs,
        fields,
        batch_size=None,
        bypass_hooks=False,
        bypass_validation=False,
    ):
        """
        Execute bulk update with hooks.

        Args:
            objs: List of model instances to update
            fields: List of field names to update
            batch_size: Number of objects per batch
            bypass_hooks: Skip all hooks if True
            bypass_validation: Skip validation hooks if True

        Returns:
            Number of objects updated
        """
        if not objs:
            return 0

        # Validate
        self.analyzer.validate_for_update(objs)

        # Fetch old records using analyzer (single source of truth)
        old_records_map = self.analyzer.fetch_old_records_map(objs)

        # Build changeset
        from django_bulk_hooks.changeset import ChangeSet, RecordChange

        changes = [
            RecordChange(
                new_record=obj,
                old_record=old_records_map.get(obj.pk),
                changed_fields=fields,
            )
            for obj in objs
        ]
        changeset = ChangeSet(self.model_cls, changes, "update", {"fields": fields})

        # Execute with hook lifecycle
        def operation():
            return self.executor.bulk_update(objs, fields, batch_size=batch_size)

        return self.dispatcher.execute_operation_with_hooks(
            changeset=changeset,
            operation=operation,
            event_prefix="update",
            bypass_hooks=bypass_hooks,
            bypass_validation=bypass_validation,
        )

    @transaction.atomic
    def update_queryset(
        self, update_kwargs, bypass_hooks=False, bypass_validation=False
    ):
        """
        Execute queryset update with hooks.
        
        ARCHITECTURE: Database-Layer vs Application-Layer Updates
        ==========================================================
        
        Unlike bulk_update(objs), queryset.update() is a pure SQL UPDATE operation.
        The database evaluates ALL expressions (F(), Subquery, Case, functions, etc.)
        without Python ever seeing the new values.
        
        To maintain Salesforce's hook contract (AFTER hooks see accurate new_records),
        we ALWAYS refetch instances after the update for AFTER hooks.
        
        This is NOT a hack - it respects the fundamental architectural difference:
        
        1. queryset.update():  Database evaluates → Must refetch for AFTER hooks
        2. bulk_update(objs):  Python has values → No refetch needed
        
        The refetch handles ALL database-level changes:
        - F() expressions: F('count') + 1
        - Subquery: Subquery(related.aggregate(...))
        - Case/When: Case(When(status='A', then=Value('Active')))
        - Database functions: Upper('name'), Concat(...)
        - Database hooks/defaults
        - Any other DB-evaluated expression
        
        Trade-off:
        - Cost: 1 extra SELECT query per queryset.update() call
        - Benefit: 100% correctness for ALL database expressions

        Args:
            update_kwargs: Dict of fields to update
            bypass_hooks: Skip all hooks if True
            bypass_validation: Skip validation hooks if True

        Returns:
            Number of objects updated
        """
        # Fetch instances BEFORE update
        instances = list(self.queryset)
        if not instances:
            return 0

        # Fetch old records for comparison (single bulk query)
        old_records_map = self.analyzer.fetch_old_records_map(instances)

        # Build changeset for VALIDATE and BEFORE hooks
        # These see pre-update state, which is correct
        changeset_before = build_changeset_for_update(
            self.model_cls,
            instances,
            update_kwargs,
            old_records_map=old_records_map,
        )

        if bypass_hooks:
            # No hooks - just execute the update
            return BaseQuerySet.update(self.queryset, **update_kwargs)

        # Execute VALIDATE and BEFORE hooks
        if not bypass_validation:
            self.dispatcher.dispatch(changeset_before, "validate_update", bypass_hooks=False)
        self.dispatcher.dispatch(changeset_before, "before_update", bypass_hooks=False)

        # Execute the actual database UPDATE
        # Database evaluates all expressions here (Subquery, F(), etc.)
        result = BaseQuerySet.update(self.queryset, **update_kwargs)

        # Refetch instances to get actual post-update values from database
        # This ensures AFTER hooks see the real final state
        pks = [obj.pk for obj in instances]
        refetched_instances = list(
            self.model_cls.objects.filter(pk__in=pks)
        )

        # Build changeset for AFTER hooks with accurate new values
        changeset_after = build_changeset_for_update(
            self.model_cls,
            refetched_instances,  # Fresh from database
            update_kwargs,
            old_records_map=old_records_map,  # Still have old values for comparison
        )

        # Execute AFTER hooks with accurate new_records
        self.dispatcher.dispatch(changeset_after, "after_update", bypass_hooks=False)

        return result

    @transaction.atomic
    def delete(self, bypass_hooks=False, bypass_validation=False):
        """
        Execute delete with hooks.

        Args:
            bypass_hooks: Skip all hooks if True
            bypass_validation: Skip validation hooks if True

        Returns:
            Tuple of (count, details dict)
        """
        # Get objects
        objs = list(self.queryset)
        if not objs:
            return 0, {}

        # Validate
        self.analyzer.validate_for_delete(objs)

        # Build changeset
        changeset = build_changeset_for_delete(self.model_cls, objs)

        # Execute with hook lifecycle
        def operation():
            # Call base Django QuerySet.delete() to avoid recursion
            return BaseQuerySet.delete(self.queryset)

        return self.dispatcher.execute_operation_with_hooks(
            changeset=changeset,
            operation=operation,
            event_prefix="delete",
            bypass_hooks=bypass_hooks,
            bypass_validation=bypass_validation,
        )

    def clean(self, objs, is_create=None):
        """
        Execute validation hooks only (no database operations).

        This is used by Django's clean() method to hook VALIDATE_* events
        without performing the actual operation.

        Args:
            objs: List of model instances to validate
            is_create: True for create, False for update, None to auto-detect

        Returns:
            None
        """
        if not objs:
            return

        # Auto-detect if is_create not specified
        if is_create is None:
            is_create = objs[0].pk is None

        # Build changeset based on operation type
        if is_create:
            changeset = build_changeset_for_create(self.model_cls, objs)
            event = "validate_create"
        else:
            # For update validation, no old records needed - hooks handle their own queries
            changeset = build_changeset_for_update(self.model_cls, objs, {})
            event = "validate_update"

        # Dispatch validation event only
        self.dispatcher.dispatch(changeset, event, bypass_hooks=False)
