from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TarifPrimeCEE(models.Model):
    _name = 'groupe_cayla.tarif_prime_cee'
    _description = "Tarif prime CEE"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    prix_unitaire = fields.Float(required=True, string='Prime unitaire')

    sujet_devis_id = fields.Many2one('groupe_cayla.sujet_devis', required=True, ondelete='restrict')
    convention_id = fields.Many2one('groupe_cayla.convention', required=True, ondelete='restrict')
    zone_habitation_id = fields.Many2one('groupe_cayla.zone_habitation', required=True, ondelete='restrict')
    type_client_id = fields.Many2one('groupe_cayla.type_client', required=True, ondelete='restrict')
    source_energie_chauffage_id = fields.Many2one('groupe_cayla.source_energie_chauffage', required=False,
                                                  ondelete='restrict')

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('sujet_devis_id', 'convention_id', 'zone_habitation_id', 'type_client_id',
                 'source_energie_chauffage_id')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = d.sujet_devis_id.libelle + ' * ' + d.convention_id.libelle + ' * ' + d.zone_habitation_id.libelle + ' * ' + d.type_client_id.libelle
            if d.source_energie_chauffage_id:
                d.combination = d.combination + ' * ' + d.source_energie_chauffage_id.libelle
