from odoo import fields, models, api
from odoo.exceptions import Warning, ValidationError


class Book(models.Model):
    _sql_constraints = [
        ('library_book_name_date_pub_uq',
         'UNIQUE (name, date_published)',
         'Book title and publication date must be unique.')]
    _name = 'library.book'
    _description = 'Book'
    _order = 'name, date_published desc'
    # String fields
    name = fields.Char('Title', required=True, index=True, help='Book cover title')
    isbn = fields.Char('ISBN')
    book_type = fields.Selection(
        [
            ('paper', 'Paperback'),
            ('hard', 'Hardcover'),
            ('electronic', 'Electronic'),
            ('other', 'Other'),
        ], 'Type'

    )

    notes = fields.Text('Internal Notes')
    descr = fields.Html('Description')

    # Numeric fields:
    copies = fields.Integer(default=1)
    avg_rating = fields.Float('Average rating', (3, 2))
    price = fields.Monetary('Price', 'currency_id')
    currency_id = fields.Many2one('res.currency')

    # Date and time fields
    date_published = fields.Date()
    last_borrow_date = fields.Datetime(
        'Last borrowed on',
        default=lambda self: fields.Datetime.now()
    )

    # Other fields
    active = fields.Boolean('Active ?', default=True)
    image = fields.Binary('Cover')

    # Relational fields
    publisher_id = fields.Many2one('res.partner', string='Publisher')
    author_ids = fields.Many2many('res.partner', string='Authors')
    publisher_country_id = fields.Many2one(
        'res.country', string='Publisher country',
        compute='_compute_publisher_country',
        inverse='_inverse_publisher_country',
        search='_search_publisher_country'
    )


    def _inverse_publisher_country(self):
        for book in self:
            book.publisher_id.country_id = book.publisher_country_id


    def _search_publisher_country(self, operator, value):
        return [('publisher_id.country_id', operator, value)]


    @api.depends('publisher_id.country_id')
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id


    @api.multi
    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check


    @api.multi
    def button_check_isbn(self):
        for book in self:
            if not book.isbn:
                raise Warning('Please provide an ISBN for %s' % book.name)
            if book.isbn and not book._check_isbn():
                raise Warning('%s is not a valid ISBN' % book.isbn)
        return True

    @api.constrains('isbn')
    def _constraint_isbn_valid(self):
        for book in self:
            if book.isbn and not book._check_isbn():
                raise ValidationError('%s is an invalid ISBN' % book.isbn)
