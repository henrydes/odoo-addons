from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class VT(models.Model):
    _name = 'groupe_cayla.vt'
    _description = "Visite technique"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà une VT')
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
    technicien_id = fields.Many2one(
        'hr.employee',
        delegate=False,
        required=True,
    )


    date_de_realisation = fields.Date(default=date.today(), required=True)

    vt_validee = fields.Boolean(default=False)
    documents_complets = fields.Boolean(default=False)

    numero_parcelle = fields.Char(string='Parcelle')
    nombre_spots = fields.Integer(default=None)
    longueur_gaine = fields.Integer(default=None)
    temps_estime = fields.Integer(compute='_compute_temps_etime', store=True, string='Tps estimé (mn)')

    infos = fields.Boolean(compute='_compute_infos', store=True)
    dossier_complet = fields.Boolean(compute='_compute_dossier_complet', store=True)

    adresse_1 = fields.Char(related='client_id.street')
    adresse_2 = fields.Char(related='client_id.street2')
    code_postal = fields.Char(related='client_id.zip')
    ville = fields.Char(related='client_id.city')

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('client_id.devis_id.superficie')
    def _compute_temps_etime(self):
        for d in self:
            if d.client_id.devis_id.superficie:
                d.temps_estime = (d.client_id.devis_id.superficie / 1.5 + 40)

    @api.depends('numero_parcelle', 'nombre_spots', 'longueur_gaine', 'temps_estime')
    def _compute_infos(self):
        for d in self:
            d.infos = d.numero_parcelle and d.nombre_spots is not None and d.longueur_gaine is not None and d.temps_estime

    @api.depends('infos', 'documents_complets', 'vt_validee')
    def _compute_dossier_complet(self):
        for d in self:
            d.dossier_complet = d.infos and d.documents_complets and d.vt_validee



    @api.depends('date_de_realisation')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'VT effectuée le ' + fields.Date.from_string(
                d.date_de_realisation).strftime('%d/%m/%Y')

    @api.model
    def create(self, values):
        rec = super(VT, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)

        client.vt_id = rec
        return rec

    @api.multi
    def write(self, values):
        client = self.client_id
        result = super().write(values)
        vt = self.env['groupe_cayla.vt'].search([('id', '=', self.id)], limit=1)

        return result

    @api.model
    def default_get(self, fields_list):
        res = models.Model.default_get(self, fields_list)
        if 'client_id' not in res:
            return res
        planif_vt = self.env['groupe_cayla.planif_vt'].search([('client_id', '=', res['client_id'])], limit=1)
        res['technicien_id'] = planif_vt.technicien_id.id
        return res
