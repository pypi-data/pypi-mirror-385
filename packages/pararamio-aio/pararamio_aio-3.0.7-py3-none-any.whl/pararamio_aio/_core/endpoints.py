"""API endpoints constants for pararamio."""

__all__ = [
    'AUTH_ENDPOINTS',
    'CHAT_ENDPOINTS',
    'FILE_ENDPOINTS',
    'POST_ENDPOINTS',
    'USER_ENDPOINTS',
]


# User-related endpoints
USER_ENDPOINTS = {
    'search': '/user/search',
    'list': '/user/list',
    'profile': '/user/profile',
    'activity': '/activity',
}

# Chat-related endpoints
CHAT_ENDPOINTS = {
    'core': '/core/chat',
    'list': '/core/chat',
    'create': '/core/chat',
    'edit': '/core/chat/{chat_id}',
    'delete': '/core/chat/{chat_id}',
    'transfer': '/core/chat/{chat_id}/transfer/{org_id}',
    'hide': '/core/chat/{chat_id}/hide',
    'show': '/core/chat/{chat_id}/show',
    'favorite': '/core/chat/{chat_id}/favorite',
    'unfavorite': '/core/chat/{chat_id}/unfavorite',
    'enter': '/core/chat/{chat_id}/enter',
    'quit': '/core/chat/{chat_id}/quit',
    'custom_title': '/core/chat/{chat_id}/custom_title',
    'add_users': '/core/chat/{chat_id}/user/{ids}',
    'delete_users': '/core/chat/{chat_id}/user/{ids}',
    'add_admins': '/core/chat/{chat_id}/admin/{ids}',
    'delete_admins': '/core/chat/{chat_id}/admin/{ids}',
    'add_groups': '/core/chat/{chat_id}/group/{ids}',
    'delete_groups': '/core/chat/{chat_id}/group/{ids}',
    'private_message': '/core/chat/pm/{user_id}',
    'sync': '/core/chat/sync',
}

# Post-related endpoints
POST_ENDPOINTS = {
    'list': '/msg/post',
    'create': '/msg/post',
    'edit': '/msg/post/{post_id}',
    'delete': '/msg/post/{post_id}',
    'search': '/posts/search',
    'last_read': '/msg/lastread/{chat_id}',
}

# Authentication endpoints
AUTH_ENDPOINTS = {
    'login': '/auth/login',
    'logout': '/auth/logout',
    'second_step': '/auth/second_step',
    'profile': '/auth/profile',
}

# File-related endpoints
FILE_ENDPOINTS = {
    'upload': '/msg/file',
    'download': '/msg/file/{file_id}',
}
