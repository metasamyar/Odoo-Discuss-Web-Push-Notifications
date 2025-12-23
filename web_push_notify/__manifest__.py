{
    'name': 'Web Push Notifications',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Web Push Notifications with VAPID and Firebase support',
    'description': """
        Integrates Web Push Notifications into Odoo using VAPID keys.
        Supports configuration via Settings.
    """,
    'author': 'Samyar Khatibi',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/push_subscription_views.xml',
        'views/settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'web_push_notify/static/src/js/push_register.js',
        ],
    },
    'license': 'LGPL-3',
}
