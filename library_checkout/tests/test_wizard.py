from odoo.tests.common import TransactionCase


class TestWizard(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        admin_user = self.env.ref('base.user_admin')
        self.Checkout = self.env['library.checkout'].sudo(admin_user)
        self.Wizard = self.env['library.checkout.massmessage'].sudo(admin_user)
        a_member = self.env['library.member'].create({'name': 'John'})
        self.checkout0 = self.Checkout.create({'member_id': a_member.id})

    def test_button_send(self):
        """ Send button should create messages on checkouts """
        msgs_before = len(self.checkout0.message_ids)
        Wizard0 = self.Wizard.with_context(active_ids = self.checkout0.ids)
        wizard0 = Wizard0.create({'message_body': 'Hello'})
        wizard0.button_send()
        msgs_after = len(self.checkout0.message_ids)
        self.assertEqual(msgs_after, msgs_before +1, 'Expected one additional message in the Checkout')

