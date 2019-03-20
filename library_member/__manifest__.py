{
    'name': 'Library Members',
    'description':'Manage people who can borrow books.',
    'author': 'Jean-Baptiste Roquefère',
    'website': 'www.laetis.fr',
    'depends': ['library_app', 'mail'],
    'application': True,

    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_menu.xml',
        'views/book_view.xml',
        'views/member_view.xml',
    ]
}