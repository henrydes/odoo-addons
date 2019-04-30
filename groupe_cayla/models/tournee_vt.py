from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TourneeVT(models.Model):
    _name = 'groupe_cayla.tournee_vt'
    _description = 'Une tournée VT'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    client_id = fields.Many2one('groupe_cayla.client',required=True,ondelete='cascade')
    user_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    vts = fields.One2many('groupe_cayla.planif_vt', 'tournee_vt_id', string='Visites')


