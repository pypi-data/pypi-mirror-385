"""
Multi-table inheritance (MTI) handler service.

Handles detection and planning for multi-table inheritance operations.

This handler is PURE LOGIC - it does not execute database operations.
It returns plans (data structures) that the BulkExecutor executes.
"""

import logging
from django.db.models import AutoField

logger = logging.getLogger(__name__)


class MTIHandler:
    """
    Handles multi-table inheritance (MTI) operation planning.

    This service detects MTI models and builds execution plans.
    It does NOT execute database operations - that's the BulkExecutor's job.
    
    Responsibilities:
    - Detect MTI models
    - Build inheritance chains
    - Create parent/child instances (in-memory only)
    - Return execution plans
    """

    def __init__(self, model_cls):
        """
        Initialize MTI handler for a specific model.

        Args:
            model_cls: The Django model class
        """
        self.model_cls = model_cls
        self._inheritance_chain = None

    def is_mti_model(self):
        """
        Determine if the model uses multi-table inheritance.

        Returns:
            bool: True if model has concrete parent models
        """
        for parent in self.model_cls._meta.all_parents:
            if parent._meta.concrete_model != self.model_cls._meta.concrete_model:
                return True
        return False

    def get_inheritance_chain(self):
        """
        Get the complete inheritance chain from root to child.

        Returns:
            list: Model classes ordered from root parent to current model
                 Returns empty list if not MTI model
        """
        if self._inheritance_chain is None:
            self._inheritance_chain = self._compute_chain()
        return self._inheritance_chain

    def _compute_chain(self):
        """
        Compute the inheritance chain by walking up the parent hierarchy.

        Returns:
            list: Model classes in order [RootParent, Parent, Child]
        """
        chain = []
        current_model = self.model_cls

        while current_model:
            if not current_model._meta.proxy:
                chain.append(current_model)

            # Get concrete parent models
            parents = [
                parent
                for parent in current_model._meta.parents.keys()
                if not parent._meta.proxy
            ]

            current_model = parents[0] if parents else None

        # Reverse to get root-to-child order
        chain.reverse()
        return chain

    def get_parent_models(self):
        """
        Get all parent models in the inheritance chain.

        Returns:
            list: Parent model classes (excludes current model)
        """
        chain = self.get_inheritance_chain()
        if len(chain) <= 1:
            return []
        return chain[:-1]  # All except current model

    def get_local_fields_for_model(self, model_cls):
        """
        Get fields defined directly on a specific model in the chain.

        Args:
            model_cls: Model class to get fields for

        Returns:
            list: Field objects defined on this model
        """
        return list(model_cls._meta.local_fields)

    # ==================== MTI BULK CREATE PLANNING ====================

    def build_create_plan(
        self,
        objs,
        batch_size=None,
        update_conflicts=False,
        unique_fields=None,
        update_fields=None,
    ):
        """
        Build an execution plan for bulk creating MTI model instances.
        
        This method does NOT execute any database operations.
        It returns a plan that the BulkExecutor will execute.
        
        Args:
            objs: List of model instances to create
            batch_size: Number of objects per batch
            update_conflicts: Enable UPSERT on conflict
            unique_fields: Fields for conflict detection
            update_fields: Fields to update on conflict
            
        Returns:
            MTICreatePlan object
        """
        from django_bulk_hooks.operations.mti_plans import MTICreatePlan, ParentLevel
        
        if not objs:
            return None
        
        inheritance_chain = self.get_inheritance_chain()
        if len(inheritance_chain) <= 1:
            raise ValueError("build_create_plan called on non-MTI model")
        
        batch_size = batch_size or len(objs)
        
        # Build parent levels
        parent_levels = self._build_parent_levels(
            objs,
            inheritance_chain,
            update_conflicts=update_conflicts,
            unique_fields=unique_fields,
            update_fields=update_fields,
        )
        
        # Build child object templates (without parent links - executor adds them)
        child_objects = []
        for obj in objs:
            child_obj = self._create_child_instance_template(obj, inheritance_chain[-1])
            child_objects.append(child_obj)
        
        return MTICreatePlan(
            inheritance_chain=inheritance_chain,
            parent_levels=parent_levels,
            child_objects=child_objects,
            child_model=inheritance_chain[-1],
            original_objects=objs,
            batch_size=batch_size,
        )

    def _build_parent_levels(
        self,
        objs,
        inheritance_chain,
        update_conflicts=False,
        unique_fields=None,
        update_fields=None,
    ):
        """
        Build parent level objects for each level in the inheritance chain.
        
        This is pure in-memory object creation - no DB operations.
        
        Returns:
            List of ParentLevel objects
        """
        from django_bulk_hooks.operations.mti_plans import ParentLevel
        
        parent_levels = []
        parent_instances_map = {}  # Maps obj id() -> {model_class: parent_instance}
        
        for level_idx, model_class in enumerate(inheritance_chain[:-1]):
            parent_objs_for_level = []
            
            for obj in objs:
                # Get current parent from previous level
                current_parent = None
                if level_idx > 0:
                    prev_parents = parent_instances_map.get(id(obj), {})
                    current_parent = prev_parents.get(inheritance_chain[level_idx - 1])
                
                # Create parent instance
                parent_obj = self._create_parent_instance(obj, model_class, current_parent)
                parent_objs_for_level.append(parent_obj)
                
                # Store in map
                if id(obj) not in parent_instances_map:
                    parent_instances_map[id(obj)] = {}
                parent_instances_map[id(obj)][model_class] = parent_obj
            
            # Determine upsert parameters for this level
            level_update_conflicts = False
            level_unique_fields = []
            level_update_fields = []
            
            if update_conflicts and unique_fields:
                # Filter unique_fields and update_fields to only those in this model
                model_fields_by_name = {f.name: f for f in model_class._meta.local_fields}
                
                # Normalize unique fields
                normalized_unique = []
                for uf in unique_fields or []:
                    if uf in model_fields_by_name:
                        normalized_unique.append(uf)
                    elif uf.endswith("_id") and uf[:-3] in model_fields_by_name:
                        normalized_unique.append(uf[:-3])
                
                # Check if this model has a matching constraint
                if normalized_unique and self._has_matching_constraint(model_class, normalized_unique):
                    # Filter update fields
                    filtered_updates = [
                        uf for uf in (update_fields or []) if uf in model_fields_by_name
                    ]
                    
                    if filtered_updates:
                        level_update_conflicts = True
                        level_unique_fields = normalized_unique
                        level_update_fields = filtered_updates
            
            # Create parent level
            parent_level = ParentLevel(
                model_class=model_class,
                objects=parent_objs_for_level,
                original_object_map={id(p): id(o) for p, o in zip(parent_objs_for_level, objs)},
                update_conflicts=level_update_conflicts,
                unique_fields=level_unique_fields,
                update_fields=level_update_fields,
            )
            parent_levels.append(parent_level)
        
        return parent_levels

    def _has_matching_constraint(self, model_class, normalized_unique):
        """Check if model has a unique constraint matching the given fields."""
        try:
            from django.db.models import UniqueConstraint
            constraint_field_sets = [
                tuple(c.fields) for c in model_class._meta.constraints 
                if isinstance(c, UniqueConstraint)
            ]
        except Exception:
            constraint_field_sets = []
        
        # Check unique_together
        ut = getattr(model_class._meta, "unique_together", ()) or ()
        if isinstance(ut, tuple) and ut and not isinstance(ut[0], (list, tuple)):
            ut = (ut,)
        ut_field_sets = [tuple(group) for group in ut]
        
        # Compare as sets
        provided_set = set(normalized_unique)
        for group in constraint_field_sets + ut_field_sets:
            if provided_set == set(group):
                return True
        return False

    def _create_parent_instance(self, source_obj, parent_model, current_parent):
        """
        Create a parent instance from source object (in-memory only).
        
        Args:
            source_obj: Original object with data
            parent_model: Parent model class to create instance of
            current_parent: Parent instance from previous level (if any)
            
        Returns:
            Parent model instance (not saved)
        """
        parent_obj = parent_model()
        
        # Copy field values from source
        for field in parent_model._meta.local_fields:
            if hasattr(source_obj, field.name):
                value = getattr(source_obj, field.name, None)
                if value is not None:
                    if (field.is_relation and not field.many_to_many and 
                        not field.one_to_many):
                        # Handle FK fields
                        if hasattr(value, "pk") and value.pk is not None:
                            setattr(parent_obj, field.attname, value.pk)
                        else:
                            setattr(parent_obj, field.attname, value)
                    else:
                        setattr(parent_obj, field.name, value)
        
        # Link to parent if exists
        if current_parent is not None:
            for field in parent_model._meta.local_fields:
                if (hasattr(field, "remote_field") and field.remote_field and
                    field.remote_field.model == current_parent.__class__):
                    setattr(parent_obj, field.name, current_parent)
                    break
        
        # Copy object state
        if hasattr(source_obj, '_state') and hasattr(parent_obj, '_state'):
            parent_obj._state.adding = source_obj._state.adding
            if hasattr(source_obj._state, 'db'):
                parent_obj._state.db = source_obj._state.db
        
        # Handle auto_now_add and auto_now fields
        for field in parent_model._meta.local_fields:
            if getattr(field, 'auto_now_add', False):
                if getattr(parent_obj, field.name) is None:
                    field.pre_save(parent_obj, add=True)
                    setattr(parent_obj, field.attname, field.value_from_object(parent_obj))
            elif getattr(field, 'auto_now', False):
                field.pre_save(parent_obj, add=True)
        
        return parent_obj

    def _create_child_instance_template(self, source_obj, child_model):
        """
        Create a child instance template (in-memory only, without parent links).
        
        The executor will add parent links after creating parent objects.
        
        Args:
            source_obj: Original object with data
            child_model: Child model class
            
        Returns:
            Child model instance (not saved, no parent links)
        """
        child_obj = child_model()
        
        # Copy field values (excluding AutoField and parent links)
        for field in child_model._meta.local_fields:
            if isinstance(field, AutoField):
                continue
            
            # Skip parent link fields - executor will set these
            if field.is_relation and hasattr(field, 'related_model'):
                # Check if this field is a parent link
                if child_model._meta.get_ancestor_link(field.related_model) == field:
                    continue
            
            if hasattr(source_obj, field.name):
                value = getattr(source_obj, field.name, None)
                if value is not None:
                    if (field.is_relation and not field.many_to_many and 
                        not field.one_to_many):
                        if hasattr(value, "pk") and value.pk is not None:
                            setattr(child_obj, field.attname, value.pk)
                        else:
                            setattr(child_obj, field.attname, value)
                    else:
                        setattr(child_obj, field.name, value)
        
        # Copy object state
        if hasattr(source_obj, '_state') and hasattr(child_obj, '_state'):
            child_obj._state.adding = source_obj._state.adding
            if hasattr(source_obj._state, 'db'):
                child_obj._state.db = source_obj._state.db
        
        # Handle auto_now_add and auto_now fields
        for field in child_model._meta.local_fields:
            if getattr(field, 'auto_now_add', False):
                if getattr(child_obj, field.name) is None:
                    field.pre_save(child_obj, add=True)
                    setattr(child_obj, field.attname, field.value_from_object(child_obj))
            elif getattr(field, 'auto_now', False):
                field.pre_save(child_obj, add=True)
        
        return child_obj

    # ==================== MTI BULK UPDATE PLANNING ====================

    def build_update_plan(self, objs, fields, batch_size=None):
        """
        Build an execution plan for bulk updating MTI model instances.
        
        This method does NOT execute any database operations.
        
        Args:
            objs: List of model instances to update
            fields: List of field names to update
            batch_size: Number of objects per batch
            
        Returns:
            MTIUpdatePlan object
        """
        from django_bulk_hooks.operations.mti_plans import MTIUpdatePlan, ModelFieldGroup
        
        if not objs:
            return None
        
        inheritance_chain = self.get_inheritance_chain()
        if len(inheritance_chain) <= 1:
            raise ValueError("build_update_plan called on non-MTI model")
        
        batch_size = batch_size or len(objs)
        
        # Handle auto_now fields
        for obj in objs:
            for model in inheritance_chain:
                for field in model._meta.local_fields:
                    if getattr(field, 'auto_now', False):
                        field.pre_save(obj, add=False)
        
        # Add auto_now fields to update list
        auto_now_fields = set()
        for model in inheritance_chain:
            for field in model._meta.local_fields:
                if getattr(field, 'auto_now', False):
                    auto_now_fields.add(field.name)
        
        all_fields = list(fields) + list(auto_now_fields)
        
        # Group fields by model
        field_groups = []
        for model_idx, model in enumerate(inheritance_chain):
            model_fields = []
            
            for field_name in all_fields:
                try:
                    field = self.model_cls._meta.get_field(field_name)
                    if field in model._meta.local_fields:
                        # Skip auto_now_add fields for updates
                        if not getattr(field, 'auto_now_add', False):
                            model_fields.append(field_name)
                except Exception:
                    continue
            
            if model_fields:
                # Determine filter field
                if model_idx == 0:
                    filter_field = "pk"
                else:
                    # Find parent link
                    parent_link = None
                    for parent_model in inheritance_chain:
                        if parent_model in model._meta.parents:
                            parent_link = model._meta.parents[parent_model]
                            break
                    filter_field = parent_link.attname if parent_link else "pk"
                
                field_groups.append(ModelFieldGroup(
                    model_class=model,
                    fields=model_fields,
                    filter_field=filter_field,
                ))
        
        return MTIUpdatePlan(
            inheritance_chain=inheritance_chain,
            field_groups=field_groups,
            objects=objs,
            batch_size=batch_size,
        )
