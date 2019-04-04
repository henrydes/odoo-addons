from odoo import models, fields, api


class Client(models.Model):
    _name = 'groupe_cayla.client'
    _description = 'Un prospect ou un client'
    _inherit = ['mail.thread','mail.activity.mixin']
    partner_id = fields.Many2one(
        'res.partner',
        delegate=True,
        ondelete='cascade',
        required=True
    )
    devis_id = fields.Many2one(
        'groupe_cayla.devis',
        delegate=False,
        required=False
    )
    etat = fields.Selection([
        ('nouveau', 'Nouveau prospect à contacter'),
        ('annule_client', 'Annulé par le client'),
        ('vt_a_planifier', 'VT à planifier'),
        ('vt_a_saisir', 'VT à saisir')]
    )

    date_edition_devis = fields.Date(compute='_compute_date_edition_devis',
                                     inverse='_inverse_date_edition_devis',string="Date édition devis")

    def _inverse_date_edition_devis(self):
        for client in self:
            client.devis_id.date_edition = client.date_edition_devis


    @api.depends('devis_id')
    def _compute_date_edition_devis(self):
        for record in self:
            if record.devis_id is None :
                record.date_edition_devis = None
            else :
                record.date_edition_devis = record.devis_id.date_edition


