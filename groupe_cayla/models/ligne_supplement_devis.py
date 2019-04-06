from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneSupplementDevis(models.Model):
    _name = 'groupe_cayla.ligne_supplement_devis'
    _description = 'Une ligne supplement devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    devis_id = fields.Many2one('groupe_cayla.devis')

    supplement_devis_id = fields.Many2one('groupe_cayla.supplement_devis', required=True, string='Type')

    quantite = fields.Float(required=True)
    tarif = fields.Float(required=True)
    prix_unitaire = fields.Float(required=True)

    @api.onchange('supplement_devis_id')
    def onchange_supplement_devis_id(self):
        if self.supplement_devis_id:
            self.prix_unitaire = self.supplement_devis_id.prix_unitaire
            self.quantite = 1
        else:
            self.prix_unitaire_1 = 0
            self.quantite = 0

    @api.onchange('prix_unitaire', 'quantite')
    def onchange_prix_unitaire(self):
        self.tarif = self.prix_unitaire * self.quantite