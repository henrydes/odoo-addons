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
        ('vt_a_saisir', 'VT à mettre à jour'),
        ('annule_par_vt', 'Annulé par VT'),
        ('vt_incomplete', 'VT incomplète'),
        ('devis_a_editer', 'Devis à éditer'),
        ('attente_commande', 'Devis en attente de commande'),
        ('chantier_a_planifier', 'Chantier à planifier'),
        ('annule_par_client', 'Annulé par client'),
        ('chantier_a_saisir', 'Chantier à saisir'),
        ('annule_par_applicateur', 'Annulé par applicateur'),
        ('facture_client_a_editer', 'Facture client à éditer')
    ], default='nouveau'
    )

    # 1 Source apporteur
    date_entree = fields.Date()
    utilisateur_id = fields.Many2one('res.users')
    source_client = fields.Char()

    # 2 Maitrise d'oeuvre
    maitre_oeuvre = fields.Char()
    installateur = fields.Char()
    contrat = fields.Char()

    # 3 Planif VT
    planif_vt_id = fields.Many2one(
        'groupe_cayla.planif_vt',
        delegate=False,
        required=False
    )
    date_appel_planif_vt = fields.Date(compute='_compute_date_appel_planif_vt',
                                       string="Date appel", store=False)
    date_time_planif_planif_vt = fields.Datetime(compute='_compute_date_time_planif_planif_vt',
                                                 string="VT planifiée", store=False)
    utilisateur_planif_vt = fields.Many2one('res.users', compute='_compute_utilisateur_planif_vt',
                                            string="Utilisateur", store=False)
    technicien_planif_vt = fields.Many2one('res.users', compute='_compute_technicien_planif_vt',
                                           string="Technicien", store=False)

    @api.onchange('planif_vt_id')
    def on_change_state(self):
        for record in self:
            if record.planif_vt_id:
                record.etat = 'vt_a_saisir'
            else:
                record.etat = 'nouveau'

    @api.depends('planif_vt_id')
    def _compute_date_appel_planif_vt(self):
        for record in self:
            if record.planif_vt_id is None:
                record.date_appel_planif_vt = None
            else:
                record.date_appel_planif_vt = record.planif_vt_id.date_appel

    @api.depends('planif_vt_id')
    def _compute_date_time_planif_planif_vt(self):
        for record in self:
            if record.planif_vt_id is None:
                record.date_time_planif_planif_vt = None
            else:
                record.date_time_planif_planif_vt = record.planif_vt_id.date_time_planif

    @api.depends('planif_vt_id')
    def _compute_utilisateur_planif_vt(self):
        for record in self:
            if record.planif_vt_id is None:
                record.utilisateur_planif_vt = None
            else:
                record.utilisateur_planif_vt = record.planif_vt_id.utilisateur_id

    @api.depends('planif_vt_id')
    def _compute_technicien_planif_vt(self):
        for record in self:
            if record.planif_vt_id is None:
                record.technicien_planif_vt = None
            else:
                record.technicien_planif_vt = record.planif_vt_id.technicien_id

    # 4 Saisie VT
    vt_id = fields.Many2one(
        'groupe_cayla.vt',
        delegate=False,
        required=False
    )
    date_de_realisation_vt = fields.Date(compute='_compute_date_de_realisation_vt',
                                         string="Date de réalisation", store=False)
    vt_validee_vt = fields.Boolean(compute='_compute_vt_validee_vt',
                                   string="VT validée", store=False)
    documents_complets_vt = fields.Boolean(compute='_compute_documents_complets_vt',
                                           string="Documents complets", store=False)

    utilisateur_vt = fields.Many2one('res.users', compute='_compute_utilisateur_vt',
                                     string="Utilisateur", store=False)
    technicien_vt = fields.Many2one('res.users', compute='_compute_technicien_vt',
                                    string="Technicien", store=False)

    @api.onchange('vt_validee_vt', 'documents_complets_vt')
    def on_change_vt_state(self):
        for record in self:
            if record.vt_id:
                if record.vt_validee_vt is False:
                    record.etat = 'annule_par_vt'
                elif record.documents_complets_vt is False:
                    record.etat = 'vt_incomplete'
                else:
                    record.etat = 'devis_a_editer'

    @api.depends('vt_id')
    def _compute_utilisateur_vt(self):
        for record in self:
            if record.vt_id is None:
                record.utilisateur_vt = None
            else:
                record.utilisateur_vt = record.vt_id.utilisateur_id

    @api.depends('vt_id')
    def _compute_vt_validee_vt(self):
        for record in self:
            if record.vt_id is None:
                record.vt_validee_vt = None
            else:
                record.vt_validee_vt = record.vt_id.vt_validee

    @api.depends('vt_id')
    def _compute_documents_complets_vt(self):
        for record in self:
            if record.vt_id is None:
                record.documents_complets_vt = None
            else:
                record.documents_complets_vt = record.vt_id.documents_complets

    @api.depends('vt_id')
    def _compute_technicien_vt(self):
        for record in self:
            if record.vt_id is None:
                record.technicien_vt = None
            else:
                record.technicien_vt = record.vt_id.technicien_id

    @api.depends('vt_id')
    def _compute_date_de_realisation_vt(self):
        for record in self:
            if record.vt_id is None:
                record.date_de_realisation_vt = None
            else:
                record.date_de_realisation_vt = record.vt_id.date_de_realisation

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
    montant_ttc_devis = fields.Float(compute='_compute_montant_ttc_devis',
                                     string="Montant TTC", store=False)

    @api.onchange('date_acceptation_devis')
    def on_change_date_acceptation_devis(self):
        for record in self:
            if record.date_acceptation_devis:
                record.etat = 'chantier_a_planifier'

    @api.onchange('date_refus_devis')
    def on_change_date_refus_devis(self):
        for record in self:
            if record.date_refus_devis:
                record.etat = 'annule_par_client'

    @api.onchange('devis_id')
    def on_change_devis_id(self):
        for record in self:
            if record.devis_id:
                record.etat = 'attente_commande'

    @api.depends('devis_id')
    def _compute_numero_devis(self):
        for record in self:
            if record.devis_id is None:
                record.numero_devis = None
            else:
                record.numero_devis = record.devis_id.numero

    @api.depends('devis_id')
    def _compute_montant_ttc_devis(self):
        for record in self:
            if record.devis_id is None:
                record.montant_ttc_devis = None
            else:
                record.montant_ttc_devis = record.devis_id.montant_ttc

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

    # 6 Planif Chantier
    planif_chantier_id = fields.Many2one(
        'groupe_cayla.planif_chantier',
        delegate=False,
        required=False
    )
    date_appel_planif_chantier = fields.Date(compute='_compute_date_appel_planif_chantier',
                                             string="Date appel", store=False)
    date_time_planif_planif_chantier = fields.Datetime(compute='_compute_date_time_planif_planif_chantier',
                                                       string="Chantier planifié", store=False)
    utilisateur_id_planif_chantier = fields.Many2one('res.users', compute='_compute_utilisateur_id_planif_chantier',
                                                     string="Utilisateur", store=False)
    equipier_1_id_planif_chantier = fields.Many2one('res.users', compute='_compute_equipier_1_id_planif_chantier',
                                                    string="Equipe", store=False)
    equipier_2_id_planif_chantier = fields.Many2one('res.users', compute='_compute_equipier_2_id_planif_chantier',
                                                    string=" ", store=False)
    entreprise_planif_chantier = fields.Char(compute='_compute_entreprise_planif_chantier',
                                             string="Entreprise", store=False)
    entite_edition_devis_id_planif_chantier = fields.Many2one('groupe_cayla.entite_edition_devis',
                                                              compute='_compute_entite_edition_devis_id_planif_chantier',
                                                              string="Entité devis", store=False)
    entreprise_planif_chantier = fields.Char(compute='_compute_entreprise_planif_chantier',
                                             string="Entreprise", store=False)

    @api.onchange('planif_chantier_id')
    def on_change_state_chantier_id(self):
        for record in self:
            if record.planif_chantier_id:
                record.etat = 'chantier_a_saisir'
            else:
                record.etat = 'chantier_a_planifier'

    @api.depends('planif_chantier_id')
    def _compute_entreprise_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.entreprise_planif_chantier = None
            else:
                record.entreprise_planif_chantier = record.planif_chantier_id.entreprise

    @api.depends('planif_chantier_id')
    def _compute_date_appel_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.date_appel_planif_chantier = None
            else:
                record.date_appel_planif_chantier = record.planif_chantier_id.date_appel

    @api.depends('planif_chantier_id')
    def _compute_date_time_planif_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.date_time_planif_planif_chantier = None
            else:
                record.date_time_planif_planif_chantier = record.planif_chantier_id.date_time_planif

    @api.depends('planif_chantier_id')
    def _compute_utilisateur_id_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.utilisateur_id_planif_chantier = None
            else:
                record.utilisateur_id_planif_chantier = record.planif_chantier_id.utilisateur_id

    @api.depends('planif_chantier_id')
    def _compute_equipier_1_id_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.equipier_1_id_planif_chantier = None
            else:
                record.equipier_1_id_planif_chantier = record.planif_chantier_id.equipier_1_id

    @api.depends('planif_chantier_id')
    def _compute_equipier_2_id_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.equipier_2_id_planif_chantier = None
            else:
                record.equipier_2_id_planif_chantier = record.planif_chantier_id.equipier_2_id

    @api.depends('planif_chantier_id')
    def _compute_entreprise_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.entreprise_planif_chantier = None
            else:
                record.entreprise_planif_chantier = record.planif_chantier_id.entreprise

    @api.depends('planif_chantier_id')
    def _compute_entite_edition_devis_id_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.entite_edition_devis_id_planif_chantier = None
            else:
                record.entite_edition_devis_id_planif_chantier = record.planif_chantier_id.entite_devis_id

    # 4 Saisie Chantier
    chantier_id = fields.Many2one(
        'groupe_cayla.chantier',
        delegate=False,
        required=False
    )
    date_de_realisation_chantier = fields.Date(compute='_compute_date_de_realisation_chantier',
                                               string="Date de réalisation", store=False)
    equipier_1_id_chantier = fields.Many2one('res.users', compute='_compute_equipier_1_id_chantier',
                                             string="Equipe", store=False)
    equipier_2_id_chantier = fields.Many2one('res.users', compute='_compute_equipier_2_id_chantier',
                                             string=" ", store=False)
    type_produit_chantier = fields.Char(compute='_compute_type_produit_chantier',
                                        string='Type Produit', store=False)
    marque_produit_chantier = fields.Char(compute='_compute_marque_chantier',
                                  string='Marque', store=False)
    nb_sac_chantier = fields.Integer(compute='_compute_nb_sac_chantier',
                                  string='Nb sac', store=False)
    temps_passe_chantier = fields.Integer(compute='_compute_temps_passe_chantier',
                                       string='Temps passé', store=False)
    chantier_realise_chantier = fields.Boolean(compute='_compute_chantier_realise_chantier',
                                               string='Chantier réalisé', store=False)

    @api.depends('chantier_id')
    def _compute_date_de_realisation_chantier(self):
        for record in self:
            if record.chantier_id is None:
                record.date_de_realisation_chantier = None
            else:
                record.date_de_realisation_chantier = record.chantier_id.date_de_realisation

    @api.depends('chantier_id')
    def _compute_equipier_1_id_chantier(self):
        for record in self:
            if record.chantier_id is None:
                record.equipier_1_id_chantier = None
            else:
                record.equipier_1_id_chantier = record.chantier_id.equipier_1_id

    @api.depends('chantier_id')
    def _compute_equipier_2_id_chantier(self):
        for record in self:
            if record.chantier_id is None:
                record.equipier_2_id_chantier = None
            else:
                record.equipier_2_id_chantier = record.chantier_id.equipier_2_id

    @api.depends('chantier_id')
    def _compute_type_produit_chantier(self):
        for record in self:
            if record.chantier_id is None or len(record.chantier_id.lignes_chantier) == 0:
                record.type_produit_chantier = None
            else:
                record.type_produit_chantier = record.chantier_id.lignes_chantier[0].type_produit

    @api.depends('chantier_id')
    def _compute_marque_chantier(self):
        for record in self:
            if record.chantier_id is None or len(record.chantier_id.lignes_chantier) == 0:
                record.marque_produit_chantier = None
            else:
                record.marque_produit_chantier = record.chantier_id.lignes_chantier[0].marque_produit

    @api.depends('chantier_id')
    def _compute_nb_sac_chantier(self):
        for record in self:
            if record.chantier_id is None or len(record.chantier_id.lignes_chantier) == 0:
                record.nb_sac_chantier = None
            else:
                for ligne in record.chantier_id.lignes_chantier:
                    record.nb_sac_chantier += ligne.nb_sacs

    @api.depends('chantier_id')
    def _compute_temps_passe_chantier(self):
        for record in self:
            if record.chantier_id is None or len(record.chantier_id.lignes_chantier) == 0:
                record.temps_passe_chantier = None
            else:
                for ligne in record.chantier_id.lignes_chantier:
                    record.temps_passe_chantier += ligne.temps_passe

    @api.depends('chantier_id')
    def _compute_chantier_realise_chantier(self):
        for record in self:
            if record.chantier_id is None:
                record.chantier_realise_chantier = None
            else:
                record.chantier_realise_chantier = record.chantier_id.chantier_realise

    @api.onchange('chantier_realise_chantier')
    def on_change_chantier_state(self):
        for record in self:
            if record.chantier_id:
                if record.chantier_realise_chantier is False:
                    record.etat = 'annule_par_applicateur'
                else:
                    record.etat = 'facture_client_a_editer'
