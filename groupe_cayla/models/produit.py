from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Produit(models.Model):
    _name = 'groupe_cayla.produit'
    _description = 'Un produit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'
    _sql_constraints = [
        ('libelle', 'unique (libelle)', 'Ce produit existe déjà')
    ]

    marques_produit_id = fields.Many2many('groupe_cayla.marque_produit')
    modeles_produit_id = fields.Many2many('groupe_cayla.modele_produit')

    libelle = fields.Char(required=True)
