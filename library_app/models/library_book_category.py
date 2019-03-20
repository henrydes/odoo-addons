from odoo import api, fields, models

class BookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Book category'
    _parent_store = True

    name = fields.Char(translate=False, required=True)
    #hierarchy fields
    parent_id = fields.Many2one(
        'library.book.category',
        'Parent category',
        ondelete='restrict')
    parent_path = fields.Char(index=True)

    highlighted_id = fields.Reference(
        [('library.book', 'Book'), ('res.partner', 'Author')],
        'Category highlight'
    )

    # Optional but good to have
    child_ids = fields.One2many(
        'library.book.category',
        'parent_id',
        'Subcategories'
    )
