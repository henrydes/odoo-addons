from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MarqueProduit(models.Model):
    _name = 'groupe_cayla.marque_produit'
    _description = 'Une marque'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    produit_id = fields.Many2one('groupe_cayla.produit', required=True)
    modeles_produit_id = fields.One2many('groupe_cayla.modele_produit', 'marque_produit_id')

    libelle = fields.Char(required=True)
