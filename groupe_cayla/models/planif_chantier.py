from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PlanifChantier(models.Model):
    _name = 'groupe_cayla.planif_chantier'
    _description = "Planification d'un chantier"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un chantier planifié')
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
    equipier_1_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )
    equipier_2_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    date_appel = fields.Date(default=date.today(), required=True)
    date_time_planif = fields.Datetime()

    entreprise = fields.Char(compute='_compute_entreprise')
    entite_devis_id = fields.Many2one('groupe_cayla.entite_edition_devis', compute='_compute_entite_edition_devis')

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('client_id')
    def _compute_entreprise(self):
        for d in self:
            d.entreprise = d.client_id.installateur

    @api.depends('client_id')
    def _compute_entite_edition_devis(self):
        for d in self:
            d.entite_devis_id = d.client_id.devis_id.entite_edition_id

    @api.depends('date_appel')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Appelé le ' + fields.Date.from_string(
                d.date_appel).strftime('%d/%m/%Y')

    @api.model
    def create(self, values):
        rec = super(PlanifChantier, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        client.etat = 'chantier_a_saisir'
        client.planif_chantier_id = rec
        return rec
