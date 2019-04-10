import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Fiche(models.Model):
    _name = 'groupe_cayla.fiche'
    _description = 'Fiche'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
