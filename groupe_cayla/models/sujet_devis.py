from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SujetDevis(models.Model):
    _name = 'groupe_cayla.sujet_devis'
    _description = 'Un sujet devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    type_tarif = fields.Selection([
        ('tout_compris', 'Tout compris'),
        ('detail', 'Par produit')
    ], default='tout_compris', required=True)

    tarif_particulier = fields.Float()
    tarif_pro = fields.Float()
    tarif_solidarite_energetique = fields.Float()
