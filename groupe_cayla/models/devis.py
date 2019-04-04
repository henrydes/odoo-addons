from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Devis(models.Model):
    _name = 'groupe_cayla.devis'
    _description = 'Un devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    client_id = fields.Many2one(
        'groupe_cayla.client',
        delegate=False,
        required=True
    )

    numero = fields.Char()
    date_edition = fields.Date()
    date_acceptation = fields.Date()
    date_refus = fields.Date()
    montant = fields.Float()

    @api.model
    def create(self, values):
        rec = super(Devis, self).create(values)
        if values['numero'] == '1':
            client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
            client.etat = 'vt_a_planifier'
            client.devis_id = rec
            _logger.info('Client is %s', client.name)
        return rec


