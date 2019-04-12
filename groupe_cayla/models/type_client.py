import logging


from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class TypeClient(models.Model):
    _name = 'groupe_cayla.type_client'
    _description = 'Un type de client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    code = fields.Char(required=True)
    libelle = fields.Char(required=True)

    donne_droit_tarif_solidarite_energetique = fields.Boolean(default=False, string='Donne droit au tarif Solidarité Energétique')
    mode_calcul_reversion = fields.Selection([
        ('multiplication', '(Tarif ligne devis * TAUX) - 1 '),
        ('division', ('Tarif prime / TAUX'))
    ], default='division', string='Mode de calcul de la reversion CEE')
    taux_reversion = fields.Float(default=1.1, string='Taux pour calcul de la reversion CEE')
    taux_reversion_char = fields.Char(string='Taux pour calcul de la reversion CEE', compute='_compute_taux_reversion_char', store=False)

    @api.depends('taux_reversion')
    def _compute_taux_reversion_char(self):
        for t in self:
            if t.taux_reversion:
                t.taux_reversion_char = str(t.taux_reversion)
