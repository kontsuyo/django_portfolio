from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    カスタム権限はオブジェクトの所有者にのみ編集を可能にする
    """

    def has_object_permission(self, request, view, obj):
        # 読み取り権限はどのリクエストに対しても許可され、
        # GET, HEAD, OPTIONSリクエストは常に許可する。
        if request.method in permissions.SAFE_METHODS:
            return True

        # 投稿者のみが許可される権限を記述
        return obj.author == request.user
