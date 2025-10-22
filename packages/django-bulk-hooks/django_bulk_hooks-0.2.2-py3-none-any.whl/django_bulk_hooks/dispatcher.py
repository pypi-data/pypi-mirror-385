"""
HookDispatcher: Single execution path for all hooks.

Provides deterministic, priority-ordered hook execution,
similar to Salesforce's hook framework.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HookDispatcher:
    """
    Single execution path for all hooks.

    Responsibilities:
    - Execute hooks in priority order
    - Filter records based on conditions
    - Provide ChangeSet context to hooks
    - Fail-fast error propagation
    - Manage complete operation lifecycle (VALIDATE, BEFORE, AFTER)
    """

    def __init__(self, registry):
        """
        Initialize the dispatcher.

        Args:
            registry: The hook registry (provides get_hooks method)
        """
        self.registry = registry

    def execute_operation_with_hooks(
        self,
        changeset,
        operation,
        event_prefix,
        bypass_hooks=False,
        bypass_validation=False,
    ):
        """
        Execute operation with full hook lifecycle.

        This is the high-level method that coordinates the complete lifecycle:
        1. VALIDATE_{event}
        2. BEFORE_{event}
        3. Actual operation
        4. AFTER_{event}

        Args:
            changeset: ChangeSet for the operation
            operation: Callable that performs the actual DB operation
            event_prefix: 'create', 'update', or 'delete'
            bypass_hooks: Skip all hooks if True
            bypass_validation: Skip validation hooks if True

        Returns:
            Result of operation
        """
        if bypass_hooks:
            return operation()

        # VALIDATE phase
        if not bypass_validation:
            self.dispatch(changeset, f"validate_{event_prefix}", bypass_hooks=False)

        # BEFORE phase
        self.dispatch(changeset, f"before_{event_prefix}", bypass_hooks=False)

        # Execute the actual operation
        result = operation()

        # AFTER phase - use result if operation returns modified data
        if result and isinstance(result, list) and event_prefix == "create":
            # For create, rebuild changeset with assigned PKs
            from django_bulk_hooks.helpers import build_changeset_for_create

            changeset = build_changeset_for_create(changeset.model_cls, result)

        self.dispatch(changeset, f"after_{event_prefix}", bypass_hooks=False)

        return result

    def dispatch(self, changeset, event, bypass_hooks=False):
        """
        Dispatch hooks for a changeset with deterministic ordering.

        This is the single execution path for ALL hooks in the system.

        Args:
            changeset: ChangeSet instance with record changes
            event: Event name (e.g., 'after_update', 'before_create')
            bypass_hooks: If True, skip all hook execution

        Raises:
            Exception: Any exception raised by a hook (fails fast)
            RecursionError: If hooks create an infinite loop (Python's built-in limit)
        """
        if bypass_hooks:
            return

        # Get hooks sorted by priority (deterministic order)
        hooks = self.registry.get_hooks(changeset.model_cls, event)

        if not hooks:
            return

        # Execute hooks in priority order
        for handler_cls, method_name, condition, priority in hooks:
            self._execute_hook(handler_cls, method_name, condition, changeset)

    def _execute_hook(self, handler_cls, method_name, condition, changeset):
        """
        Execute a single hook with condition checking.

        Args:
            handler_cls: The hook handler class
            method_name: Name of the method to call
            condition: Optional condition to filter records
            changeset: ChangeSet with all record changes
        """
        # Filter records based on condition
        if condition:
            filtered_changes = [
                change
                for change in changeset.changes
                if condition.check(change.new_record, change.old_record)
            ]

            if not filtered_changes:
                # No records match condition, skip this hook
                return

            # Create filtered changeset
            from django_bulk_hooks.changeset import ChangeSet

            filtered_changeset = ChangeSet(
                changeset.model_cls,
                filtered_changes,
                changeset.operation_type,
                changeset.operation_meta,
            )
        else:
            # No condition, use full changeset
            filtered_changeset = changeset

        # Use DI factory to create handler instance
        from django_bulk_hooks.factory import create_hook_instance

        handler = create_hook_instance(handler_cls)
        method = getattr(handler, method_name)

        # Check if method has @select_related decorator
        preload_func = getattr(method, "_select_related_preload", None)
        if preload_func:
            # Preload relationships to prevent N+1 queries
            try:
                model_cls_override = getattr(handler, "model_cls", None)

                # Preload for new_records
                if filtered_changeset.new_records:
                    logger.debug(
                        f"Preloading relationships for {len(filtered_changeset.new_records)} "
                        f"new_records for {handler_cls.__name__}.{method_name}"
                    )
                    preload_func(
                        filtered_changeset.new_records, model_cls=model_cls_override
                    )

                # Also preload for old_records (for conditions that check previous values)
                if filtered_changeset.old_records:
                    logger.debug(
                        f"Preloading relationships for {len(filtered_changeset.old_records)} "
                        f"old_records for {handler_cls.__name__}.{method_name}"
                    )
                    preload_func(
                        filtered_changeset.old_records, model_cls=model_cls_override
                    )
            except Exception:
                logger.debug(
                    "select_related preload failed for %s.%s",
                    handler_cls.__name__,
                    method_name,
                    exc_info=True,
                )

        # Execute hook with ChangeSet
        # 
        # ARCHITECTURE NOTE: Hook Contract
        # ====================================
        # All hooks must accept **kwargs for forward compatibility.
        # We pass: changeset, new_records, old_records
        # 
        # Old hooks that don't use changeset: def hook(self, new_records, old_records, **kwargs)
        # New hooks that do use changeset:    def hook(self, changeset, new_records, old_records, **kwargs)
        # 
        # This is standard Python framework design (see Django signals, Flask hooks, etc.)
        try:
            method(
                changeset=filtered_changeset,
                new_records=filtered_changeset.new_records,
                old_records=filtered_changeset.old_records,
            )
        except Exception as e:
            # Fail-fast: re-raise to rollback transaction
            logger.error(
                f"Hook {handler_cls.__name__}.{method_name} failed: {e}",
                exc_info=True,
            )
            raise


# Global dispatcher instance
_dispatcher: Optional[HookDispatcher] = None


def get_dispatcher():
    """
    Get the global dispatcher instance.

    Creates the dispatcher on first access (singleton pattern).

    Returns:
        HookDispatcher instance
    """
    global _dispatcher
    if _dispatcher is None:
        # Import here to avoid circular dependency
        from django_bulk_hooks.registry import get_registry

        # Create dispatcher with the registry instance
        _dispatcher = HookDispatcher(get_registry())
    return _dispatcher
