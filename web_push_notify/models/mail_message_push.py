from odoo import models, api
import re
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        for message in messages:
            # 1. Filter: Only notify for comments/notifications, ignore internal notes
            if message.message_type not in ('comment', 'notification') or message.is_internal:
                continue
                
            # 2. Filter: Do not notify the author (you don't need a push for your own msg)
            recipients = message.partner_ids
            if message.author_id:
                recipients = recipients - message.author_id
            
            if not recipients:
                continue

            # 3. Prepare Body Text
            body_text = 'You have a new message'
            if message.body:
                # Remove HTML tags to get clean text
                clean = re.compile('<.*?>')
                body_text = re.sub(clean, '', message.body)
                # Truncate if too long
                body_text = body_text[:120] + '...' if len(body_text) > 120 else body_text

            # 4. CRITICAL: Generate the Correct URL
            # Default to generic web view
            click_url = '/web'

            # Case A: It is a Chat/Channel message
            if message.model == 'discuss.channel' and message.res_id:
                # Generate your custom URL format
                click_url = f'/yarics/discuss?active_id=discuss.channel_{message.res_id}'
            
            # Case B: It is a normal document (Invoice, SO, Task, etc.)
            elif message.res_id and message.model:
                click_url = f'/web#id={message.res_id}&model={message.model}&view_type=form'

            payload = {
                'title': message.author_id.name or 'Odoo Notification',
                'body': body_text,
                'url': click_url,
                'icon': f'/web/image/res.partner/{message.author_id.id}/avatar_128' if message.author_id else '/web/static/img/logo.png',
            }

            # 5. Send to all recipients
            subscriptions = self.env['push.subscription'].search([('partner_id', 'in', recipients.ids)])
            
            for sub in subscriptions:
                try:
                    sub.send_notification(payload)
                except Exception as e:
                    _logger.error("Failed to send push for message %s to partner %s: %s", message.id, sub.partner_id.name, e)

        return messages
