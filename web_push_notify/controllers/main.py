from odoo import http
from odoo.http import request

class WebPushController(http.Controller):

    @http.route('/web_push/vapid_public_key', type='json', auth='user')
    def get_vapid_public_key(self):
        return request.env['ir.config_parameter'].sudo().get_param('web_push_notify.vapid_public_key')

    @http.route('/web_push/firebase_config', type='json', auth='user')
    def get_firebase_config(self):
        params = request.env['ir.config_parameter'].sudo()
        return {
            'apiKey': params.get_param('web_push_notify.firebase_api_key'),
            'projectId': params.get_param('web_push_notify.firebase_project_id'),
            'messagingSenderId': params.get_param('web_push_notify.firebase_messaging_sender_id'),
            'appId': params.get_param('web_push_notify.firebase_app_id'),
        }

    @http.route('/web_push/subscribe', type='json', auth='user')
    def subscribe(self, endpoint, keys):
        partner = request.env.user.partner_id
        # Check if subscription exists
        existing = request.env['push.subscription'].sudo().search([
            ('endpoint', '=', endpoint)
        ], limit=1)

        if existing:
            existing.write({
                'partner_id': partner.id,
                'keys_p256dh': keys.get('p256dh'),
                'keys_auth': keys.get('auth'),
            })
        else:
            request.env['push.subscription'].sudo().create({
                'partner_id': partner.id,
                'endpoint': endpoint,
                'keys_p256dh': keys.get('p256dh'),
                'keys_auth': keys.get('auth'),
            })
        return {'status': 'success'}

    @http.route('/web_push_sw.js', type='http', auth='public')
    def service_worker(self):
        """
        Serve the service worker with the correct scope headers.
        """
        import os
        from odoo.modules import get_module_resource
        
        sw_path = get_module_resource('web_push_notify', 'static/src/sw/push_sw.js')
        with open(sw_path, 'rb') as f:
            content = f.read()
            
        response = request.make_response(content, [
            ('Content-Type', 'application/javascript'),
            ('Service-Worker-Allowed', '/'),
        ])
        return response
