"""
MTI operation plans - Data structures for multi-table inheritance operations.

These are pure data structures returned by MTIHandler to be executed by BulkExecutor.
This separates planning (logic) from execution (database operations).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ParentLevel:
    """
    Represents one level in the parent hierarchy for MTI bulk create.
    
    Attributes:
        model_class: The parent model class for this level
        objects: List of parent instances to create
        original_object_map: Maps parent instance id() -> original object id()
        update_conflicts: Whether to enable UPSERT for this level
        unique_fields: Fields for conflict detection (if update_conflicts=True)
        update_fields: Fields to update on conflict (if update_conflicts=True)
    """
    model_class: Any
    objects: List[Any]
    original_object_map: Dict[int, int] = field(default_factory=dict)
    update_conflicts: bool = False
    unique_fields: List[str] = field(default_factory=list)
    update_fields: List[str] = field(default_factory=list)


@dataclass
class MTICreatePlan:
    """
    Plan for executing bulk_create on an MTI model.
    
    This plan describes WHAT to create, not HOW to create it.
    The executor is responsible for executing this plan.
    
    Attributes:
        inheritance_chain: List of model classes from root to child
        parent_levels: List of ParentLevel objects, one per parent model
        child_objects: List of child instances to create (not yet with parent links)
        child_model: The child model class
        original_objects: Original objects provided by user
        batch_size: Batch size for operations
    """
    inheritance_chain: List[Any]
    parent_levels: List[ParentLevel]
    child_objects: List[Any]
    child_model: Any
    original_objects: List[Any]
    batch_size: int = None


@dataclass
class ModelFieldGroup:
    """
    Represents fields to update for one model in the inheritance chain.
    
    Attributes:
        model_class: The model class
        fields: List of field names to update on this model
        filter_field: Field to use for filtering (e.g., 'pk' or parent link attname)
    """
    model_class: Any
    fields: List[str]
    filter_field: str = "pk"


@dataclass
class MTIUpdatePlan:
    """
    Plan for executing bulk_update on an MTI model.
    
    Attributes:
        inheritance_chain: List of model classes from root to child
        field_groups: List of ModelFieldGroup objects
        objects: Objects to update
        batch_size: Batch size for operations
    """
    inheritance_chain: List[Any]
    field_groups: List[ModelFieldGroup]
    objects: List[Any]
    batch_size: int = None

