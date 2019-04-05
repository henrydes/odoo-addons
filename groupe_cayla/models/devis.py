from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Devis(models.Model):
    _name = 'groupe_cayla.devis'
    _description = 'Un devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un devis')
    ]
    client_id = fields.Many2one(
        'groupe_cayla.client',
        delegate=False,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    numero = fields.Char()
    date_edition = fields.Date(default=date.today())
    date_acceptation = fields.Date()
    date_envoi = fields.Date()
    date_refus = fields.Date()
    montant = fields.Float()

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('numero')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Devis numéro ' + d.numero

    @api.model
    def create(self, values):
        rec = super(Devis, self).create(values)
        if values['numero'] is not None:
            client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
            client.etat = 'attente_commande'
            client.devis_id = rec
        return rec
