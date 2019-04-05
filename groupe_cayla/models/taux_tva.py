
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TauxTVA(models.Model):
    _name = 'groupe_cayla.taux_tva'
    _description = 'Un taux de TVA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    taux = fields.Float(required=True)

