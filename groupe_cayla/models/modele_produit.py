from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ModeleProduit(models.Model):
    _name = 'groupe_cayla.modele_produit'
    _description = 'Un modèle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    marque_produit_id = fields.Many2one('groupe_cayla.marque_produit')
    libelle = fields.Char(required=True )
