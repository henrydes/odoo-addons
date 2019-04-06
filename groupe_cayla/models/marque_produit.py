from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MarqueProduit(models.Model):
    _name = 'groupe_cayla.marque_produit'
    _description = 'Une marque'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    produit_id = fields.Many2one('groupe_cayla.produit')


    libelle = fields.Char(required=True )
