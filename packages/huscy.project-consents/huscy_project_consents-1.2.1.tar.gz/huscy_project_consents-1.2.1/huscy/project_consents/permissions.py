from rest_framework.permissions import BasePermission, SAFE_METHODS

from huscy.projects.services import is_project_member, is_project_member_with_write_permission


class CanChangeProject(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return any([
            request.user.has_perm('projects.change_project'),
            is_project_member_with_write_permission(view.project, request.user),
        ])


class CanCreateProjectConsentToken(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('project_consents.add_projectconsenttoken')


class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        return is_project_member(view.project, request.user)
