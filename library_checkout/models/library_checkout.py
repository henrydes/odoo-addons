from odoo import api, exceptions, fields, models


class Checkout(models.Model):
    _name = 'library.checkout'
    _description = 'Checkout request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'request_date'

    @api.model
    def _default_stage(self):
        Stage = self.env['library.checkout.stage']
        return Stage.search([], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    num_other_checkouts = fields.Integer(compute='_compute_num_other_checkouts')
    checkout_date = fields.Date(readonly=True, required=False)
    close_date = fields.Date(readonly=True, required=False)
    num_books = fields.Integer(compute='_compute_num_books', store=True)
    member_id = fields.Many2one(
        'library.member',
        required=True)
    user_id = fields.Many2one(
        'res.users',
        'Librarian',
        default=lambda s: s.env.uid
    )
    member_image = fields.Binary(related='member_id.partner_id.image')
    request_date = fields.Date(
        default=lambda s: fields.Date.today())
    line_ids = fields.One2many(
        'library.checkout.line',
        'checkout_id',
        string='Borrowed books'
    )

    stage_id = fields.Many2one(
        'library.checkout.stage',
        default=_default_stage,
        group_extand='_group_extand_stage_id')
    state = fields.Selection(related='stage_id.state')

    def _compute_num_other_checkouts(self):
        for rec in self:
            domain = [
                ('member_id', '=', rec.member_id.id),
                ('state', 'in', ['open']),
                ('id', '!=', rec.id)
            ]
            rec.num_other_checkouts = self.search_count(domain)

    @api.model
    def create(self, vals):
        if 'stage_id' in vals:
            Stage = self.env['library.checkout.stage']
            new_state = Stage.browse(vals['stage_id']).state
            if new_state == 'open':
                vals['checkout_date'] = fields.Date.today()

        new_record = super().create(vals)

        if new_record.state == 'done':
            raise exceptions.UserError(
                'Not allowed to create a checkout in the done stage'
            )
        return new_record

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            Stage = self.env['library.checkout.stage']
            new_state = Stage.browse(vals['stage_id']).state
            if new_state == 'open' and self.state != 'open':
                vals['checkout_date'] = fields.Date.today()
            if (new_state == 'done' and self.state != 'done') or (new_state == 'cancel' and self.state != 'cancel'):
                vals['close_date'] = fields.Date.today()
        super().write(vals)
        return True

    @api.depends('line_ids')
    def _compute_num_books(self):
        for book in self:
            book.num_books = len(book.line_ids)

    def button_done(self):
        Stage = self.env['library.checkout.stage']
        done_stage = Stage.search(
            [('state', '=', 'done')],
            limit=1
        )
        for checkout in self:
            checkout.stage_id = done_stage
        return True


class CheckoutLine(models.Model):
    _name = 'library.checkout.line'
    _description = 'Borrow request line'
    checkout_id = fields.Many2one('library.checkout')
    book_id = fields.Many2one('library.book')
