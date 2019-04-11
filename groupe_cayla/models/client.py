from odoo import models, fields, api


class Client(models.Model):
    _name = 'groupe_cayla.client'
    _description = 'Un prospect ou un client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'res_partner_id'}
    res_partner_id = fields.Many2one(comodel_name="res.partner", ondelete="restrict", required=True)

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
        required=False,
        ondelete='set null'
    )
    date_appel_planif_vt = fields.Date(compute='_compute_planif_vt',
                                       string="Date appel", store=False)
    date_time_planif_planif_vt = fields.Datetime(compute='_compute_planif_vt',
                                                 string="VT planifiée", store=False)
    utilisateur_planif_vt = fields.Many2one('res.users', compute='_compute_planif_vt',
                                            string="Utilisateur", store=False)
    technicien_planif_vt = fields.Many2one('res.users', compute='_compute_planif_vt',
                                           string="Technicien", store=False)

    @api.onchange('planif_vt_id')
    def on_change_state(self):
        for record in self:
            if record.planif_vt_id:
                record.etat = 'vt_a_saisir'
            else:
                record.etat = 'nouveau'

    @api.depends('planif_vt_id')
    def _compute_planif_vt(self):
        for record in self:
            if record.planif_vt_id is None:
                record.date_appel_planif_vt = None
                record.date_time_planif_planif_vt = None
                record.utilisateur_planif_vt = None
                record.technicien_planif_vt = None
            else:
                record.date_appel_planif_vt = record.planif_vt_id.date_appel
                record.date_time_planif_planif_vt = record.planif_vt_id.date_time_planif
                record.utilisateur_planif_vt = record.planif_vt_id.utilisateur_id
                record.technicien_planif_vt = record.planif_vt_id.technicien_id

    # 4 Saisie VT
    vt_id = fields.Many2one(
        'groupe_cayla.vt',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_de_realisation_vt = fields.Date(compute='_compute_vt',
                                         string="Date de réalisation", store=False)
    vt_validee_vt = fields.Boolean(compute='_compute_vt',
                                   string="VT validée", store=False)
    documents_complets_vt = fields.Boolean(compute='_compute_vt',
                                           string="Documents complets", store=False)

    utilisateur_vt = fields.Many2one('res.users', compute='_compute_vt',
                                     string="Utilisateur", store=False)
    technicien_vt = fields.Many2one('res.users', compute='_compute_vt',
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
    def _compute_vt(self):
        for record in self:
            if record.vt_id is None:
                record.utilisateur_vt = None
                record.vt_validee_vt = None
                record.documents_complets_vt = None
                record.technicien_vt = None
                record.date_de_realisation_vt = None
            else:
                record.utilisateur_vt = record.vt_id.utilisateur_id
                record.vt_validee_vt = record.vt_id.vt_validee
                record.documents_complets_vt = record.vt_id.documents_complets
                record.technicien_vt = record.vt_id.technicien_id
                record.date_de_realisation_vt = record.vt_id.date_de_realisation

    # 5.1 Edition devis
    devis_id = fields.Many2one(
        'groupe_cayla.devis',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_edition_devis = fields.Date(compute='_compute_devis',
                                     string="Edition", store=False)
    date_envoi_devis = fields.Date(compute='_compute_devis',
                                   string="Envoyé le", store=False)
    date_acceptation_devis = fields.Date(compute='_compute_devis',
                                         string="Accepté le", store=False)
    date_refus_devis = fields.Date(compute='_compute_devis',
                                   string="Refusé le", store=False)
    utilisateur_devis = fields.Many2one('res.users', compute='_compute_devis',
                                        string="Utilisateur", store=False)
    numero_devis = fields.Char(compute='_compute_devis',
                               string="N° Devis", store=False)
    montant_ttc_devis = fields.Float(compute='_compute_devis',
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
    def _compute_devis(self):
        for record in self:
            if record.devis_id is None:
                record.numero_devis = None
                record.montant_ttc_devis = None
                record.date_edition_devis = None
                record.date_envoi_devis = None
                record.date_acceptation_devis = None
                record.date_refus_devis = None
                record.utilisateur_devis = None

            else:
                record.numero_devis = record.devis_id.numero
                record.montant_ttc_devis = record.devis_id.montant_ttc
                record.date_edition_devis = record.devis_id.date_edition
                record.date_envoi_devis = record.devis_id.date_envoi
                record.date_acceptation_devis = record.devis_id.date_acceptation
                record.date_refus_devis = record.devis_id.date_refus
                record.utilisateur_devis = record.devis_id.user_id

    # 5.2 Saisie CEE
    cee_id = fields.Many2one(
        'groupe_cayla.cee',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    type_client_cee = fields.Many2one('groupe_cayla.type_client', compute='_compute_cee',
                                      string="Type client", store=False)
    convention_cee = fields.Many2one('groupe_cayla.convention', compute='_compute_cee',
                                     string="Délégataire", store=False)
    fiche_1_cee = fields.Many2one('groupe_cayla.fiche', compute='_compute_cee',
                                  string="Fiche", store=False)
    fiche_2_cee = fields.Many2one('groupe_cayla.fiche', compute='_compute_cee',
                                  string=" ", store=False)

    @api.depends('cee_id')
    def _compute_cee(self):
        for record in self:
            if record.cee_id is None:
                record.type_client_cee = None
                record.convention_cee = None
                record.fiche_1_cee = None
                record.fiche_2_cee = None

            else:
                record.type_client_cee = record.cee_id.type_client_id
                record.convention_cee = record.cee_id.convention_id
                record.fiche_1_cee = record.cee_id.fiche_1_id
                record.fiche_2_cee = record.cee_id.fiche_2_id

    # 6 Planif Chantier
    planif_chantier_id = fields.Many2one(
        'groupe_cayla.planif_chantier',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_appel_planif_chantier = fields.Date(compute='_compute_planif_chantier',
                                             string="Date appel", store=False)
    date_time_planif_planif_chantier = fields.Datetime(compute='_compute_planif_chantier',
                                                       string="Chantier planifié", store=False)
    utilisateur_id_planif_chantier = fields.Many2one('res.users', compute='_compute_planif_chantier',
                                                     string="Utilisateur", store=False)
    equipier_1_id_planif_chantier = fields.Many2one('res.users', compute='_compute_planif_chantier',
                                                    string="Equipe", store=False)
    equipier_2_id_planif_chantier = fields.Many2one('res.users', compute='_compute_planif_chantier',
                                                    string=" ", store=False)
    entreprise_planif_chantier = fields.Char(compute='_compute_planif_chantier',
                                             string="Entreprise", store=False)
    entite_edition_devis_id_planif_chantier = fields.Many2one('groupe_cayla.entite_edition_devis',
                                                              compute='_compute_planif_chantier',
                                                              string="Entité devis", store=False)
    entreprise_planif_chantier = fields.Char(compute='_compute_planif_chantier',
                                             string="Entreprise", store=False)

    @api.onchange('planif_chantier_id')
    def on_change_state_chantier_id(self):
        for record in self:
            if record.planif_chantier_id:
                record.etat = 'chantier_a_saisir'
            else:
                record.etat = 'chantier_a_planifier'

    @api.depends('planif_chantier_id')
    def _compute_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.entreprise_planif_chantier = None
                record.date_appel_planif_chantier = None
                record.date_time_planif_planif_chantier = None
                record.utilisateur_id_planif_chantier = None
                record.equipier_1_id_planif_chantier = None
                record.equipier_2_id_planif_chantier = None
                record.entreprise_planif_chantier = None
                record.entite_edition_devis_id_planif_chantier = None
            else:
                record.entreprise_planif_chantier = record.planif_chantier_id.entreprise
                record.date_appel_planif_chantier = record.planif_chantier_id.date_appel
                record.date_time_planif_planif_chantier = record.planif_chantier_id.date_time_planif
                record.utilisateur_id_planif_chantier = record.planif_chantier_id.utilisateur_id
                record.equipier_1_id_planif_chantier = record.planif_chantier_id.equipier_1_id
                record.equipier_2_id_planif_chantier = record.planif_chantier_id.equipier_2_id
                record.entreprise_planif_chantier = record.planif_chantier_id.entreprise
                record.entite_edition_devis_id_planif_chantier = record.planif_chantier_id.entite_devis_id

    # 4 Saisie Chantier
    chantier_id = fields.Many2one(
        'groupe_cayla.chantier',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_de_realisation_chantier = fields.Date(compute='_compute_chantier',
                                               string="Date de réalisation", store=False)
    equipier_1_id_chantier = fields.Many2one('res.users', compute='_compute_chantier',
                                             string="Equipe", store=False)
    equipier_2_id_chantier = fields.Many2one('res.users', compute='_compute_chantier',
                                             string=" ", store=False)
    produit_chantier = fields.Char(compute='_compute_chantier',
                                   string='Type Produit', store=False)
    marque_produit_chantier = fields.Char(compute='_compute_chantier',
                                          string='Marque', store=False)
    nb_sac_chantier = fields.Integer(compute='_compute_chantier',
                                     string='Nb sac', store=False)
    temps_passe_chantier = fields.Integer(compute='_compute_chantier',
                                          string='Temps passé', store=False)
    chantier_realise_chantier = fields.Boolean(compute='_compute_chantier',
                                               string='Chantier réalisé', store=False)

    @api.depends('chantier_id')
    def _compute_chantier(self):
        for record in self:
            if record.chantier_id is None:
                record.date_de_realisation_chantier = None
                record.equipier_1_id_chantier = None
                record.equipier_2_id_chantier = None
                record.produit_chantier = None
                record.marque_produit_chantier = None
                record.nb_sac_chantier = None
                record.temps_passe_chantier = None
                record.chantier_realise_chantier = None
            else:
                record.date_de_realisation_chantier = record.chantier_id.date_de_realisation
                record.equipier_1_id_chantier = record.chantier_id.equipier_1_id
                record.equipier_2_id_chantier = record.chantier_id.equipier_2_id
                if len(record.chantier_id.lignes_chantier) > 0:
                    record.produit_chantier = record.chantier_id.lignes_chantier[0].produit_id.libelle
                if len(record.chantier_id.lignes_chantier) > 1:
                    record.produit_chantier += ', ...'
                if len(record.chantier_id.lignes_chantier) > 0:
                    record.marque_produit_chantier = record.chantier_id.lignes_chantier[0].marque_produit_id.libelle
                if len(record.chantier_id.lignes_chantier) > 1:
                    record.marque_produit_chantier += ', ...'
                for ligne in record.chantier_id.lignes_chantier:
                    record.nb_sac_chantier += ligne.nb_sacs
                for ligne in record.chantier_id.lignes_chantier:
                    record.temps_passe_chantier += ligne.temps_passe
                record.chantier_realise_chantier = record.chantier_id.chantier_realise

    @api.onchange('chantier_realise_chantier')
    def on_change_chantier_state(self):
        for record in self:
            if record.chantier_id:
                if record.chantier_realise_chantier is False:
                    record.etat = 'annule_par_applicateur'
                else:
                    record.etat = 'facture_client_a_editer'

    @api.model
    def default_get(self, fields_list):
        res = models.Model.default_get(self, fields_list)
        france = self.env['res.country'].search([('name', '=', 'France')], limit=1)
        res['country_id'] = france.id
        return res
