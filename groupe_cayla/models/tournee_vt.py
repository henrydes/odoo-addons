from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TourneeVT(models.Model):
    _name = 'groupe_cayla.tournee_vt'
    _description = 'Une tournée VT'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    vts = fields.Many2many('groupe_cayla.planif_vt', string='Visites')

    @api.model
    def default_get(self, fields_names):
        defaults = super().default_get(fields_names)
        client_ids = self.env.context['active_ids']
        defaults['user_id'] = self.env.context['uid']
        defaults['vts'] = [p.id for p in self.env['groupe_cayla.planif_vt'].search([('client_id', 'in', client_ids)])]
        return defaults
