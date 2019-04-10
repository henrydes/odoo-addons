import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class TypeClient(models.Model):
    _name = 'groupe_cayla.type_client'
    _description = 'Un type de client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    code = fields.Char(required=True)
    libelle = fields.Char(required=True)
