
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ObjetDevis(models.Model):
    _name = 'groupe_cayla.objet_devis'
    _description = 'Un objet devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
