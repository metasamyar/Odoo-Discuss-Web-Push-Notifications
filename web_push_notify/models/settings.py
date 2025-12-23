from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_push_vapid_public_key = fields.Char(string='VAPID Public Key', config_parameter='web_push_notify.vapid_public_key')
    web_push_vapid_private_key = fields.Char(string='VAPID Private Key', config_parameter='web_push_notify.vapid_private_key')
    web_push_vapid_mailto = fields.Char(string='VAPID Mailto', config_parameter='web_push_notify.vapid_mailto', default='mailto:admin@example.com')
    
    # Firebase specific (optional if VAPID is standard)
    web_push_firebase_api_key = fields.Char(string='Firebase API Key', config_parameter='web_push_notify.firebase_api_key')
    web_push_firebase_project_id = fields.Char(string='Firebase Project ID', config_parameter='web_push_notify.firebase_project_id')
    web_push_firebase_messaging_sender_id = fields.Char(string='Firebase Messaging Sender ID', config_parameter='web_push_notify.firebase_messaging_sender_id')
    web_push_firebase_app_id = fields.Char(string='Firebase App ID', config_parameter='web_push_notify.firebase_app_id')
