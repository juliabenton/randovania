from typing import Optional, Callable


class EditableObject:
    _nested_edit_level: int = 0
    _is_dirty: bool = False
    _on_changes: Optional[Callable[[], None]] = None

    def __enter__(self):
        self._nested_edit_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._nested_edit_level == 1:
            if self._is_dirty:
                if self._on_changes is not None:
                    self._on_changes()
        self._nested_edit_level -= 1

    # Events
    def _set_on_changes(self, value):
        self._on_changes = value

    on_changes = property(fset=_set_on_changes)

    def _check_editable_and_mark_dirty(self):
        """Checks if _nested_edit_level is not 0 and marks at least one value was changed."""
        assert self._nested_edit_level != 0, "Attempting to edit an EditableObject, but it wasn't made editable"
        self._is_dirty = True

    def edit_field(self, field_name: str, new_value):
        current_value = getattr(self, field_name)
        if current_value != new_value:
            self._check_editable_and_mark_dirty()
            setattr(self, "_" + field_name, new_value)
