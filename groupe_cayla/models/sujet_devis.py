from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SujetDevis(models.Model):
    _name = 'groupe_cayla.sujet_devis'
    _description = 'Un sujet devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    lignes_sujet_devis = fields.One2many('groupe_cayla.ligne_sujet_devis', 'sujet_devis_id')

    libelle = fields.Char(required=True)
    tarif_tout_compris = fields.Boolean(default=True)

    tarif_particulier = fields.Float()
    tarif_pro = fields.Float()
    tarif_solidarite_energetique = fields.Float()

    detail = fields.Char()

    @api.model
    def create(self, values):
        rec = super(SujetDevis, self).create(values)
        if self.tarif_tout_compris:
            lignes_sujet_devis = self.env['groupe_cayla.ligne_sujet_devis'].search([('sujet_devis_id', '=', self.id)])
            for l in lignes_sujet_devis:
                l.tarif_particulier = self.tarif_particulier
                l.tarif_pro = self.tarif_pro
                l.tarif_solidarite_energetique = self.tarif_solidarite_energetique
        return rec

    @api.multi
    def write(self, vals):
        super().write(vals)
        sujet_devis = self.env['groupe_cayla.sujet_devis'].search([('id', '=', self.id)], limit=1)
        if sujet_devis.tarif_tout_compris:
            lignes_sujet_devis = self.env['groupe_cayla.ligne_sujet_devis'].search([('sujet_devis_id', '=', self.id)])
            for l in lignes_sujet_devis:
                l.tarif_particulier = self.tarif_particulier
                l.tarif_pro = self.tarif_pro
                l.tarif_solidarite_energetique = self.tarif_solidarite_energetique
        return True
