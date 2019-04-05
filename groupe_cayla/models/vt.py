from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class VT(models.Model):
    _name = 'groupe_cayla.vt'
    _description = "Visite technique"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà une VT')
    ]
    client_id = fields.Many2one(
        'groupe_cayla.client',
        delegate=False,
        required=True,
    )
    utilisateur_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )
    technicien_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    date_de_realisation = fields.Date(default=date.today(), required=True)

    vt_validee = fields.Boolean(default=False)
    documents_complets = fields.Boolean(default=False)

    adresse = fields.Text()

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('date_de_realisation')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'VT effectuée le ' + fields.Date.from_string(
                d.date_de_realisation).strftime('%d/%m/%Y')

    @api.model
    def create(self, values):
        rec = super(VT, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        if values['vt_validee'] is False:
            client.etat = 'annule_par_vt'
        elif values['documents_complets'] is False:
            client.etat = 'vt_incomplete'
        else:
            client.etat = 'devis_a_editer'

        client.vt_id = rec
        return rec


