{
    'name': 'Library Management',
    'description':'Manage library book catalogues and lending.',
    'author': 'Jean-Baptiste Roquefère',
    'website': 'www.laetis.fr',
    'depends': ['base'],
    'application': True,

    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_menu.xml',
        'views/book_view.xml',
        'views/book_category_view.xml',
    ]
}