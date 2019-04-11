from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CEE(models.Model):
    _name = 'groupe_cayla.cee'
    _description = 'Un dossier CEE'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un dossier CEE')
    ]

    client_id = fields.Many2one(
        'groupe_cayla.client',
        required=True,
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    type_client_id = fields.Many2one('groupe_cayla.type_client', required=True)
    zone_habitation_id = fields.Many2one('groupe_cayla.zone_habitation', required=True)
    type_chauffage_id = fields.Many2one('groupe_cayla.type_chauffage', required=True)
    source_energie_chauffage = fields.Char(compute='_compute_source_energie_chauffage', store=False)

    convention_id = fields.Many2one('groupe_cayla.convention', required=True)
    fiche_1_id = fields.Many2one('groupe_cayla.fiche', required=True, string='Fiche')
    fiche_2_id = fields.Many2one('groupe_cayla.fiche', required=True, string='Fiche')

    ref_fiscale = fields.Char(required=True)
    foyer = fields.Integer(required=True)
    locataire = fields.Boolean(string='Locataire ?', required=True)

    @api.depends('type_chauffage_id')
    def _compute_source_energie_chauffage(self):
        for c in self:
            if c.type_chauffage_id:
                c.source_energie_chauffage = c.type_chauffage_id.source_energie_chauffage_id.libelle
