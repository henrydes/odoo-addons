from odoo import models, fields, api


class Client(models.Model):
    _name = 'groupe_cayla.client'
    _description = 'Un prospect ou un client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    partner_id = fields.Many2one(
        'res.partner',
        delegate=True,
        ondelete='cascade',
        required=True
    )

    etat = fields.Selection([
        ('nouveau', 'Nouveau prospect à contacter'),
        ('annule_client', 'Annulé par le client'),
        ('vt_a_planifier', 'VT à planifier'),
        ('vt_a_saisir', 'VT à saisir')], default='nouveau'
    )

    # 1 Source apporteur
    date_entree = fields.Date()
    utilisateur_id = fields.Many2one('res.users')
    source_client = fields.Char()

    # 2 Maitrise d'oeuvre
    maitre_oeuvre = fields.Char()
    installateur = fields.Char()
    contrat = fields.Char()

    # 5 Edition devis
    devis_id = fields.Many2one(
        'groupe_cayla.devis',
        delegate=False,
        required=False
    )
    date_edition_devis = fields.Date(compute='_compute_date_edition_devis',
                                     string="Edition", store=False)
    date_envoi_devis = fields.Date(compute='_compute_date_envoi_devis',
                                   string="Envoyé le", store=False)
    date_acceptation_devis = fields.Date(compute='_compute_date_acceptation_devis',
                                         string="Accepté le", store=False)
    date_refus_devis = fields.Date(compute='_compute_date_refus_devis',
                                   string="Refusé le", store=False)
    utilisateur_devis = fields.Many2one('res.users', compute='_compute_utilisateur_devis',
                                        string="Utilisateur", store=False)
    numero_devis = fields.Char(compute='_compute_numero_devis',
                               string="N° Devis", store=False)
    montant_devis = fields.Char(compute='_compute_montant_devis',
                                string="Montant", store=False)

    @api.depends('devis_id')
    def _compute_numero_devis(self):
        for record in self:
            if record.devis_id is None:
                record.numero_devis = None
            else:
                record.numero_devis = record.devis_id.numero

    @api.depends('devis_id')
    def _compute_montant_devis(self):
        for record in self:
            if record.devis_id is None:
                record.montant_devis = None
            else:
                record.montant_devis = record.devis_id.montant

    @api.depends('devis_id')
    def _compute_date_edition_devis(self):
        for record in self:
            if record.devis_id is None:
                record.date_edition_devis = None
            else:
                record.date_edition_devis = record.devis_id.date_edition

    @api.depends('devis_id')
    def _compute_date_envoi_devis(self):
        for record in self:
            if record.devis_id is None:
                record.date_envoi_devis = None
            else:
                record.date_envoi_devis = record.devis_id.date_envoi

    @api.depends('devis_id')
    def _compute_date_acceptation_devis(self):
        for record in self:
            if record.devis_id is None:
                record.date_acceptation_devis = None
            else:
                record.date_acceptation_devis = record.devis_id.date_acceptation

    @api.depends('devis_id')
    def _compute_date_refus_devis(self):
        for record in self:
            if record.devis_id is None:
                record.date_refus_devis = None
            else:
                record.date_refus_devis = record.devis_id.date_refus

    @api.depends('devis_id')
    def _compute_utilisateur_devis(self):
        for record in self:
            if record.devis_id is None:
                record.utilisateur_devis = None
            else:
                record.utilisateur_devis = record.devis_id.user_id
