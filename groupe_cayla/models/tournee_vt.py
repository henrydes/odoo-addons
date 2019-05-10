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

    technicien_id = fields.Many2one('hr.employee',compute='_compute_tournee')
    date_tournee = fields.Date(compute='_compute_tournee')
    vts = fields.Many2many('groupe_cayla.planif_vt', string='Visites')

    @api.depends('vts')
    def _compute_tournee(self):
        for d in self:
            if d.vts and len(d.vts) > 0:
                d.technicien_id = d.vts[0].technicien_id
                d.date_tournee = d.vts[0].date_time_planif.date()

    @api.model
    def default_get(self, fields_names):
        defaults = super().default_get(fields_names)
        defaults['user_id'] = self.env.context['uid']
        if 'active_ids' in self.env.context:
            client_ids = self.env.context['active_ids']
            defaults['vts'] = [p.id for p in self.env['groupe_cayla.planif_vt'].search([('client_id', 'in', client_ids)])]
        return defaults
