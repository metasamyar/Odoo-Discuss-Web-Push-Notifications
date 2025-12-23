from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class PushSubscription(models.Model):
    _name = 'push.subscription'
    _description = 'Web Push Subscription'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    endpoint = fields.Char(string='Endpoint', required=True)
    keys_p256dh = fields.Char(string='Keys P256DH')
    keys_auth = fields.Char(string='Keys Auth')
    
    _sql_constraints = [
        ('endpoint_uniq', 'unique(endpoint)', 'The endpoint must be unique per subscription.')
    ]

    def send_notification(self, payload):
        """
        Send a push notification to this subscription.
        :param payload: dict containing 'title', 'body', 'icon', 'data'
        """
        self.ensure_one()
        from ..services.push_service import PushService
        try:
            PushService.send_push(self, payload)
        except Exception as e:
            _logger.error("Failed to send push notification to %s: %s", self.partner_id.name, e)
            # Optional: Remove invalid subscriptions (410 Gone)
            if "410" in str(e) or "Gone" in str(e):
                self.unlink()
