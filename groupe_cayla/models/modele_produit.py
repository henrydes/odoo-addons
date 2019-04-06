from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ModeleProduit(models.Model):
    _name = 'groupe_cayla.modele_produit'
    _description = 'Un modèle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    marque_produit_id = fields.Many2one('groupe_cayla.marque_produit')
    libelle = fields.Char(required=True)
    acermi = fields.Char(required=False)
    epaisseur = fields.Integer(required=False, string='Epaisseur (mm)')
    resistance_thermique = fields.Char(required=False, string='Res.Ther.')

    @api.model
    def create(self, values):
        if values['resistance_thermique']:
            values['resistance_thermique'] = values['resistance_thermique'].replace('.', ',')
        rec = super(ModeleProduit, self).create(values)
        return rec

    @api.multi
    def write(self, values):
        if values['resistance_thermique']:
            values['resistance_thermique'] = values['resistance_thermique'].replace('.', ',')
        super().write(values)
        return True