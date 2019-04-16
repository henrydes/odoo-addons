import logging
from datetime import date

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class DoublonClient(models.Model):
    _name = 'groupe_cayla.doublon_client'
    _description = 'Un doublon'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    client_existant_id = fields.Many2one('groupe_cayla.client')
    client_nouveau_id = fields.Many2one('groupe_cayla.client')

    client_existant_etat = fields.Selection(related="client_existant_id.etat", store=False)
    client_existant_ref = fields.Char(related="client_existant_id.ref", store=False)
    client_existant_title = fields.Many2one('res.partner.title', related="client_existant_id.title", store=False)
    client_existant_name = fields.Char(related="client_existant_id.name", store=False)
    client_existant_street = fields.Char(related="client_existant_id.street", store=False)
    client_existant_street2 = fields.Char(related="client_existant_id.street2", store=False)
    client_existant_zip = fields.Char(related="client_existant_id.zip", store=False)
    client_existant_city = fields.Char(related="client_existant_id.city", store=False)
    client_existant_prospect_qualifie = fields.Selection(related="client_existant_id.prospect_qualifie", store=False)
    client_existant_comment = fields.Text(related="client_existant_id.comment", store=False)


    client_nouveau_etat = fields.Selection(related="client_nouveau_id.etat", store=False)
    client_nouveau_ref = fields.Char(related="client_nouveau_id.ref", store=False)
    client_nouveau_title = fields.Many2one('res.partner.title', related="client_nouveau_id.title", store=False)
    client_nouveau_name = fields.Char(related="client_nouveau_id.name", store=False)
    client_nouveau_street = fields.Char(related="client_nouveau_id.street", store=False)
    client_nouveau_street2 = fields.Char(related="client_nouveau_id.street2", store=False)
    client_nouveau_zip = fields.Char(related="client_nouveau_id.zip", store=False)
    client_nouveau_city = fields.Char(related="client_nouveau_id.city", store=False)
    client_nouveau_prospect_qualifie = fields.Selection(related="client_nouveau_id.prospect_qualifie", store=False)
    client_nouveau_comment = fields.Text(related="client_nouveau_id.comment", store=False)

    _rec_name = 'label'
    label = fields.Char(compute='_label')

    @api.depends('client_existant_id', 'client_nouveau_id')
    def _label(self):
        for r in self:
            r.label = r.client_existant_id.name+' - '+r.client_nouveau_id.name

    @api.multi
    def garder_client_existant(self):
        self.client_nouveau_id.unlink()
        self.client_existant_id.a_dedoublonner = self.env['groupe_cayla.doublon_client'].search_count([('id', '!=', self.id), ('client_existant_id', '=', self.client_existant_id.id )])> 0
        self.unlink()
        return {
            'name': ('Doublons'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list',
            'target': 'current',
            'res_model': 'groupe_cayla.doublon_client',
            'view_id': False
        }

    @api.multi
    def garder_les_deux_clients(self):
        self.client_nouveau_id.a_dedoublonner = self.env['groupe_cayla.doublon_client'].search_count([('id', '!=', self.id), '|', ('client_nouveau_id', '=', self.client_nouveau_id.id), ('client_existant_id', '=', self.client_nouveau_id.id)])> 0

        self.client_existant_id.a_dedoublonner = self.env['groupe_cayla.doublon_client'].search_count([('id', '!=', self.id), ('client_existant_id', '=', self.client_existant_id.id )]) > 0
        self.unlink()
        return {
            'name': ('Doublons'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list',
            'target': 'current',
            'res_model': 'groupe_cayla.doublon_client',
            'view_id': False
        }

