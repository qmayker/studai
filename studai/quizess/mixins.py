class NonEditableInlineMixin:
    classes = ["collapse"]
    extra = 0
    max_num = 1

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False
