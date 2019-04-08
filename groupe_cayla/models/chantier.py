from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Chantier(models.Model):
    _name = 'groupe_cayla.chantier'
    _description = "Un chantier"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un chantier')
    ]
    client_id = fields.Many2one(
        'groupe_cayla.client',
        delegate=False,
        required=True,
        ondelete='cascade'
    )
    utilisateur_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )
    equipier_1_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )
    equipier_2_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    date_de_realisation = fields.Date(default=date.today(), required=True)

    reglement = fields.Float()
    chantier_realise = fields.Boolean(default=False)

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    lignes_chantier = fields.One2many('groupe_cayla.ligne_chantier', 'chantier_id', string='Lignes')

    @api.depends('date_de_realisation')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Chantier effectué le ' + fields.Date.from_string(
                d.date_de_realisation).strftime('%d/%m/%Y')

    @api.model
    def create(self, values):
        rec = super(Chantier, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        if values['chantier_realise'] is False:
            client.etat = 'annule_par_applicateur'
        else:
            client.etat = 'facture_client_a_editer'
        client.chantier_id = rec
        return rec

    @api.multi
    def write(self, values):
        client = self.client_id
        result = super().write(values)
        chantier = self.env['groupe_cayla.chantier'].search([('id', '=', self.id)], limit=1)
        if chantier.chantier_realise:
            _logger.info('le chantier a été réalisé')
            client.etat = 'facture_client_a_editer'
        else:
            _logger.info('le chantier n a pas été réalise')
            client.etat = 'annule_par_applicateur'
        return result

    @api.model
    def default_get(self, fields_list):
        res = models.Model.default_get(self, fields_list)
        if 'client_id' not in res:
            return res
        client = self.env['groupe_cayla.client'].search([('id', '=', res['client_id'])], limit=1)
        lignes_devis = client.devis_id.lignes_devis
        type_ligne_chantier = self.env['groupe_cayla.ligne_chantier']
        lignes_chantier = []
        for ligne_devis in lignes_devis:
            lc = type_ligne_chantier.create({
                'sujet_devis_id': ligne_devis.sujet_devis_id.id,
                'produit_id': ligne_devis.produit_id.id,
                'marque_produit_id': ligne_devis.marque_produit_id.id,
                'modele_produit_id': ligne_devis.modele_produit_id.id,

            })
            lignes_chantier.append(lc.id)
        res['lignes_chantier'] = lignes_chantier

        planif_chantier = self.env['groupe_cayla.planif_chantier'].search([('client_id', '=', res['client_id'])], limit=1)
        res['equipier_1_id'] = planif_chantier.equipier_1_id.id
        res['equipier_2_id'] = planif_chantier.equipier_2_id.id

        return res
