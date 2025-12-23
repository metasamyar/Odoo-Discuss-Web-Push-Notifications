import json
import logging
from odoo import http

_logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    _logger.warning("pywebpush library not found. Web Push Notifications will not work.")

class PushService:
    @staticmethod
    def send_push(subscription, payload):
        """
        Send a push notification using pywebpush.
        :param subscription: push.subscription record
        :param payload: dict or string
        """
        if not webpush:
            _logger.error("pywebpush not installed. Cannot send notification.")
            return

        ir_config = subscription.env['ir.config_parameter'].sudo()
        vapid_private = ir_config.get_param('web_push_notify.vapid_private_key')
        vapid_email = ir_config.get_param('web_push_notify.vapid_mailto')

        if not vapid_private or not vapid_email:
            _logger.error("VAPID configuration missing.")
            return

        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.keys_p256dh,
                "auth": subscription.keys_auth
            }
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private,
                vapid_claims={"sub": vapid_email}
            )
            _logger.info("Push notification sent to %s", subscription.partner_id.name)
        except WebPushException as ex:
            _logger.error("Web Push Error: %s", ex)
            raise ex
        except Exception as e:
             _logger.error("Unexpected Error sending push: %s", e)
             raise e
