from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneSujetDevis(models.Model):
    _name = 'groupe_cayla.ligne_sujet_devis'
    _description = 'Une ligne sujet devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sujet_devis_id = fields.Many2one('groupe_cayla.sujet_devis', required=False, string='Sujet')
    produit_id = fields.Many2one('groupe_cayla.produit', required=True, string='Produit')

    tarif_particulier = fields.Float()
    tarif_pro = fields.Float()
    tarif_solidarite_energetique = fields.Float()
    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('produit_id')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = d.produit_id.libelle
