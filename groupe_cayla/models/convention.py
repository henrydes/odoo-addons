import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Convention(models.Model):
    _name = 'groupe_cayla.convention'
    _description = 'Convention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
