from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Chantier(models.Model):
    _name = 'groupe_cayla.chantier'
    _description = "Un chantier"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un chantier')
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
    type_produit_1 = fields.Char()
    type_produit_2 = fields.Char()
    marque_1 = fields.Char()
    marque_2 = fields.Char()
    nb_sac_1 = fields.Integer()
    nb_sac_2 = fields.Integer()
    temps_passe_1 = fields.Char()
    temps_passe_2 = fields.Char()

    date_de_realisation = fields.Date(default=date.today(), required=True)

    reglement = fields.Float()
    chantier_realise = fields.Boolean(default=False)

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')


    @api.depends('date_de_realisation')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Chantier effectué le ' + fields.Date.from_string(
                d.date_de_realisation).strftime('%d/%m/%Y')

    @api.model
    def create(self, values):
        rec = super(Chantier, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        if values['chantier_realise'] is False:
            client.etat = 'annule_par_applicateur'
        else:
            client.etat = 'facture_client_a_editer'
        client.chantier_id = rec
        return rec

    @api.multi
    def write(self, values):
        client = self.client_id
        result = super().write(values)
        chantier = self.env['groupe_cayla.chantier'].search([('id', '=', self.id)], limit=1)
        if chantier.chantier_realise:
            _logger.info('le chantier a été réalisé')
            client.etat = 'facture_client_a_editer'
        else:
            _logger.info('le chantier n a pas été réalise')
            client.etat = 'annule_par_applicateur'
        return result
