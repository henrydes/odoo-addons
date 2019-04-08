from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SujetDevis(models.Model):
    _name = 'groupe_cayla.sujet_devis'
    _description = 'Un sujet devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    tarif_tout_compris = fields.Boolean(default=True)

    tarif_particulier = fields.Float()
    tarif_pro = fields.Float()
    tarif_solidarite_energetique = fields.Float()

    detail = fields.Char()

    @api.model
    def create(self, values):
        rec = super(SujetDevis, self).create(values)
        if self.tarif_tout_compris: pass
        # produits = self.env['groupe_cayla.produit'].search([('sujet_devis_id', '=', self.id)])
        # for p in produits:
        #    p.tarif_particulier = self.tarif_particulier
        #    p.tarif_pro = self.tarif_pro
        #    p.tarif_eco = self.tarif_eco
        return rec

    @api.multi
    def write(self, vals):
        super().write(vals)
        sujet_devis = self.env['groupe_cayla.sujet_devis'].search([('id', '=', self.id)], limit=1)
        if sujet_devis.tarif_tout_compris: pass
            # produits = self.env['groupe_cayla.produit'].search([('sujet_devis_id', '=', self.id)])
            # for p in produits:
            #     p.tarif_particulier = self.tarif_particulier
            #     p.tarif_pro = self.tarif_pro
            #     p.tarif_solidarite_energetique = self.tarif_solidarite_energetique
        return True
