# -*- coding: utf-8 -*-
{
    'name': "Groupe Cayla",

    'summary': """
        Fichier clients du Groupe Cayla""",

    'description': """
        Gestion des prospects et clients du groupe. Indicateurs de performances commerciaux.
    """,

    'author': "Laëtis",
    'website': "http://www.laetis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/groupe_cayla_security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/client.xml',
        'views/devis.xml',
        'views/planif_vt.xml',
        'views/vt.xml',
        'views/planif_chantier.xml',
        'views/chantier.xml',
        'views/entite_edition_devis.xml',
        'views/supplement_devis.xml',
        'views/ligne_supplement_devis.xml',
        'views/objet_devis.xml',
        'views/templates.xml',
        'views/taux_tva.xml',
        'views/sujet_devis.xml',
        'views/marque_produit.xml',
        'views/produit.xml',
        'views/modele_produit.xml',
        'views/ligne_devis.xml',
        'views/ligne_chantier.xml',
        'views/ligne_sujet_devis.xml',
        'views/type_client.xml',
        'views/zone_habitation.xml',
        'views/convention.xml',
        'views/fiche.xml',
        'views/type_chauffage.xml',
        'views/source_energie_chauffage.xml',
        'views/tarif_prime_cee.xml',
        'views/cee.xml',
        'views/ligne_cee.xml',
        'views/doublon_client.xml',
        'reports/report_pv_vt.xml',
        'views/facture.xml',
        'views/tournee_vt.xml',
        'views/delegataire.xml',
    ],
    'application': True,
}