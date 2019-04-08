from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Produit(models.Model):
    _name = 'groupe_cayla.produit'
    _description = 'Un produit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    sujet_devis_id = fields.Many2one('groupe_cayla.sujet_devis', required=True)

    marques_produit_id = fields.One2many('groupe_cayla.marque_produit', 'produit_id')

    tarif_particulier = fields.Float()
    tarif_pro = fields.Float()
    tarif_solidarite_energetique = fields.Float()

    libelle = fields.Char(required=True)
