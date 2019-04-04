from odoo import models, fields


class Client(models.Model):
    _name = 'groupe_cayla.client'
    _description = 'Un prospect ou un client'
    _inherit = ['mail.thread','mail.activity.mixin']
    partner_id = fields.Many2one(
        'res.partner',
        delegate=True,
        ondelete='cascade',
        required=True
    )



