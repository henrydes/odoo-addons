from odoo import api, exceptions, fields, models
import logging

_logger = logging.getLogger(__name__)

class CheckoutMassMessage(models.TransientModel):
    _name = 'library.checkout.massmessage'
    _description = 'Send message to borrowers'
    checkout_ids = fields.Many2many(
        'library.checkout',
        string='Checkouts'
    )
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, field_names):
        defaults = super().default_get(field_names)
        checkout_ids = self.env.context['active_ids']
        defaults['checkout_ids'] = checkout_ids
        return defaults;

    @api.multi
    def button_send(self):
        self.ensure_one()
        if not self.checkout_ids:
            raise exceptions.UserError('Select at least one checkout')
        if not self.message_body:
            raise exceptions.UserError('Type a message')
        for checkout in self.checkout_ids:
            checkout.message_post(
                body=self.message_body,
                subject=self.message_subject,
                subtype='mail.mt_comment'
            )
        _logger.info(
            'Posted %d messages to Checkouts: %s',
            len(self.checkout_ids),
            str(self.checkout_ids)
        )
        return True
