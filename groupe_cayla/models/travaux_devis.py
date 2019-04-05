
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TravauxDevis(models.Model):
    _name = 'groupe_cayla.travaux_devis'
    _description = 'Un type de travaux devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    prix_unitaire = fields.Float(required=True)

