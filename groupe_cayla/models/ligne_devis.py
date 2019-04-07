from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneDevis(models.Model):
    _name = 'groupe_cayla.ligne_devis'
    _description = 'Une ligne devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    devis_id = fields.Many2one('groupe_cayla.devis')

    sujet_devis_id = fields.Many2one('groupe_cayla.sujet_devis', required=True, string='Sujet')
    produit_id = fields.Many2one('groupe_cayla.produit', required=True)
    marque_produit_id = fields.Many2one('groupe_cayla.marque_produit', required=True, string='Marque')
    modele_produit_id = fields.Many2one('groupe_cayla.modele_produit', required=True, string='Modèle')

    @api.onchange('sujet_devis_id')
    def on_change_sujet_devis_id(self):
        for record in self:
            if record.sujet_devis_id:
                record.produit_id = None
                record.marque_produit_id = None
                record.modele_produit_id = None

    @api.onchange('produit_id')
    def on_change_produit_id(self):
        for record in self:
            if record.produit_id:
                record.marque_produit_id = None
                record.modele_produit_id = None
                marques = self.env['groupe_cayla.marque_produit'].search(
                    [('produit_id', '=', record.produit_id.id)])
                if marques and len(marques) == 1:
                    record.marque_produit_id = marques[0]


    @api.onchange('marque_produit_id')
    def on_change_marque_produit_id(self):
        for record in self:
            if record.marque_produit_id:
                record.modele_produit_id = None
                modeles = self.env['groupe_cayla.modele_produit'].search(
                    [('marque_produit_id', '=', record.marque_produit_id.id)])
                if modeles and len(modeles) == 1:
                    record.modele_produit_id = modeles[0]



