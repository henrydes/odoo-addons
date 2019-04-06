
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SupplementDevis(models.Model):
    _name = 'groupe_cayla.supplement_devis'
    _description = 'Un type de supplement devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    prix_unitaire = fields.Float(required=True)

