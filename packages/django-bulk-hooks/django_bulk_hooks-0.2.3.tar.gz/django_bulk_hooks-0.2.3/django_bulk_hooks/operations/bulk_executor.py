"""
Bulk executor service for database operations.

This service coordinates bulk database operations with validation and MTI handling.
"""

import logging
from django.db import transaction
from django.db.models import AutoField

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

        # Check if this is an MTI model and route accordingly
        if self.mti_handler.is_mti_model():
            logger.info(f"Detected MTI model {self.model_cls.__name__}, using MTI bulk create")
            # Build execution plan
            plan = self.mti_handler.build_create_plan(
                objs,
                batch_size=batch_size,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
            )
            # Execute the plan
            return self._execute_mti_create_plan(plan)

        # Non-MTI model - use Django's native bulk_create
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

        # Check if this is an MTI model and route accordingly
        if self.mti_handler.is_mti_model():
            logger.info(f"Detected MTI model {self.model_cls.__name__}, using MTI bulk update")
            # Build execution plan
            plan = self.mti_handler.build_update_plan(objs, fields, batch_size=batch_size)
            # Execute the plan
            return self._execute_mti_update_plan(plan)

        # Non-MTI model - use Django's native bulk_update
        # Validation already done by coordinator
        from django.db.models import QuerySet

        base_qs = QuerySet(model=self.model_cls, using=self.queryset.db)
        return base_qs.bulk_update(objs, fields, batch_size=batch_size)

    # ==================== MTI PLAN EXECUTION ====================

    def _execute_mti_create_plan(self, plan):
        """
        Execute an MTI create plan.
        
        This is where ALL database operations happen for MTI bulk_create.
        
        Args:
            plan: MTICreatePlan object from MTIHandler
            
        Returns:
            List of created objects with PKs assigned
        """
        from django.db import transaction
        from django.db.models import QuerySet as BaseQuerySet
        
        if not plan:
            return []
        
        with transaction.atomic(using=self.queryset.db, savepoint=False):
            # Step 1: Create all parent objects level by level
            parent_instances_map = {}  # Maps original obj id() -> {model: parent_instance}
            
            for parent_level in plan.parent_levels:
                # Bulk create parents for this level
                bulk_kwargs = {"batch_size": len(parent_level.objects)}
                
                if parent_level.update_conflicts:
                    bulk_kwargs["update_conflicts"] = True
                    bulk_kwargs["unique_fields"] = parent_level.unique_fields
                    bulk_kwargs["update_fields"] = parent_level.update_fields
                
                # Use base QuerySet to avoid recursion
                base_qs = BaseQuerySet(model=parent_level.model_class, using=self.queryset.db)
                created_parents = base_qs.bulk_create(parent_level.objects, **bulk_kwargs)
                
                # Copy generated fields back to parent objects
                for created_parent, parent_obj in zip(created_parents, parent_level.objects):
                    for field in parent_level.model_class._meta.local_fields:
                        created_value = getattr(created_parent, field.name, None)
                        if created_value is not None:
                            setattr(parent_obj, field.name, created_value)
                    
                    parent_obj._state.adding = False
                    parent_obj._state.db = self.queryset.db
                
                # Map parents back to original objects
                for parent_obj in parent_level.objects:
                    orig_obj_id = parent_level.original_object_map[id(parent_obj)]
                    if orig_obj_id not in parent_instances_map:
                        parent_instances_map[orig_obj_id] = {}
                    parent_instances_map[orig_obj_id][parent_level.model_class] = parent_obj
            
            # Step 2: Add parent links to child objects
            for child_obj, orig_obj in zip(plan.child_objects, plan.original_objects):
                parent_instances = parent_instances_map.get(id(orig_obj), {})
                
                for parent_model, parent_instance in parent_instances.items():
                    parent_link = plan.child_model._meta.get_ancestor_link(parent_model)
                    if parent_link:
                        setattr(child_obj, parent_link.attname, parent_instance.pk)
                        setattr(child_obj, parent_link.name, parent_instance)
            
            # Step 3: Bulk create child objects using _batched_insert (to bypass MTI check)
            base_qs = BaseQuerySet(model=plan.child_model, using=self.queryset.db)
            base_qs._prepare_for_bulk_create(plan.child_objects)
            
            # Partition objects by PK status
            objs_without_pk, objs_with_pk = [], []
            for obj in plan.child_objects:
                if obj._is_pk_set():
                    objs_with_pk.append(obj)
                else:
                    objs_without_pk.append(obj)
            
            # Get fields for insert
            opts = plan.child_model._meta
            fields = [f for f in opts.local_fields if not f.generated]
            
            # Execute bulk insert
            if objs_with_pk:
                returned_columns = base_qs._batched_insert(
                    objs_with_pk,
                    fields,
                    batch_size=len(objs_with_pk),
                )
                if returned_columns:
                    for obj, results in zip(objs_with_pk, returned_columns):
                        if hasattr(opts, "db_returning_fields") and hasattr(opts, "pk"):
                            for result, field in zip(results, opts.db_returning_fields):
                                if field != opts.pk:
                                    setattr(obj, field.attname, result)
                        obj._state.adding = False
                        obj._state.db = self.queryset.db
                else:
                    for obj in objs_with_pk:
                        obj._state.adding = False
                        obj._state.db = self.queryset.db
            
            if objs_without_pk:
                filtered_fields = [
                    f for f in fields
                    if not isinstance(f, AutoField) and not f.primary_key
                ]
                returned_columns = base_qs._batched_insert(
                    objs_without_pk,
                    filtered_fields,
                    batch_size=len(objs_without_pk),
                )
                if returned_columns:
                    for obj, results in zip(objs_without_pk, returned_columns):
                        if hasattr(opts, "db_returning_fields"):
                            for result, field in zip(results, opts.db_returning_fields):
                                setattr(obj, field.attname, result)
                        obj._state.adding = False
                        obj._state.db = self.queryset.db
                else:
                    for obj in objs_without_pk:
                        obj._state.adding = False
                        obj._state.db = self.queryset.db
            
            created_children = plan.child_objects
            
            # Step 4: Copy PKs and auto-generated fields back to original objects
            pk_field_name = plan.child_model._meta.pk.name
            
            for orig_obj, child_obj in zip(plan.original_objects, created_children):
                # Copy PK
                child_pk = getattr(child_obj, pk_field_name)
                setattr(orig_obj, pk_field_name, child_pk)
                
                # Copy auto-generated fields from all levels
                parent_instances = parent_instances_map.get(id(orig_obj), {})
                
                for model_class in plan.inheritance_chain:
                    # Get source object for this level
                    if model_class in parent_instances:
                        source_obj = parent_instances[model_class]
                    elif model_class == plan.child_model:
                        source_obj = child_obj
                    else:
                        continue
                    
                    # Copy auto-generated field values
                    for field in model_class._meta.local_fields:
                        if field.name == pk_field_name:
                            continue
                        
                        # Skip parent link fields
                        if hasattr(field, 'remote_field') and field.remote_field:
                            parent_link = plan.child_model._meta.get_ancestor_link(model_class)
                            if parent_link and field.name == parent_link.name:
                                continue
                        
                        # Copy auto_now_add, auto_now, and db_returning fields
                        if (getattr(field, 'auto_now_add', False) or 
                            getattr(field, 'auto_now', False) or
                            getattr(field, 'db_returning', False)):
                            source_value = getattr(source_obj, field.name, None)
                            if source_value is not None:
                                setattr(orig_obj, field.name, source_value)
                
                # Update object state
                orig_obj._state.adding = False
                orig_obj._state.db = self.queryset.db
        
        return plan.original_objects

    def _execute_mti_update_plan(self, plan):
        """
        Execute an MTI update plan.
        
        Updates each table in the inheritance chain using CASE/WHEN for bulk updates.
        
        Args:
            plan: MTIUpdatePlan object from MTIHandler
            
        Returns:
            Number of objects updated
        """
        from django.db import transaction
        from django.db.models import Case, Value, When, QuerySet as BaseQuerySet
        
        if not plan:
            return 0
        
        total_updated = 0
        
        # Get PKs for filtering
        root_pks = [
            getattr(obj, "pk", None) or getattr(obj, "id", None) 
            for obj in plan.objects 
            if getattr(obj, "pk", None) or getattr(obj, "id", None)
        ]
        
        if not root_pks:
            return 0
        
        with transaction.atomic(using=self.queryset.db, savepoint=False):
            # Update each table in the chain
            for field_group in plan.field_groups:
                if not field_group.fields:
                    continue
                
                base_qs = BaseQuerySet(model=field_group.model_class, using=self.queryset.db)
                
                # Check if records exist
                existing_count = base_qs.filter(**{f"{field_group.filter_field}__in": root_pks}).count()
                if existing_count == 0:
                    continue
                
                # Build CASE statements for bulk update
                case_statements = {}
                for field_name in field_group.fields:
                    field = field_group.model_class._meta.get_field(field_name)
                    
                    # Use column name for FK fields
                    if getattr(field, 'is_relation', False) and hasattr(field, 'attname'):
                        db_field_name = field.attname
                        target_field = field.target_field
                    else:
                        db_field_name = field_name
                        target_field = field
                    
                    when_statements = []
                    for pk, obj in zip(root_pks, plan.objects):
                        obj_pk = getattr(obj, "pk", None) or getattr(obj, "id", None)
                        if obj_pk is None:
                            continue
                        
                        value = getattr(obj, db_field_name)
                        when_statements.append(
                            When(
                                **{field_group.filter_field: pk},
                                then=Value(value, output_field=target_field),
                            )
                        )
                    
                    if when_statements:
                        case_statements[db_field_name] = Case(
                            *when_statements, output_field=target_field
                        )
                
                # Execute bulk update
                if case_statements:
                    try:
                        updated_count = base_qs.filter(
                            **{f"{field_group.filter_field}__in": root_pks}
                        ).update(**case_statements)
                        total_updated += updated_count
                    except Exception as e:
                        logger.error(f"MTI bulk update failed for {field_group.model_class.__name__}: {e}")
        
        return total_updated

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
