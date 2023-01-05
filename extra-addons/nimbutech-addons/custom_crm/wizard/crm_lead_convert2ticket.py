from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLeadConvert2Ticket(models.TransientModel):
    _inherit = 'crm.lead.convert2ticket'

    team_id = fields.Many2one(
        'helpdesk.team', string='Team', required=True, default=1)

    ticket_type_id = fields.Many2one(
        'helpdesk.ticket.type', "Ticket Type", default=1)

    def action_lead_to_helpdesk_ticket(self):
        self.ensure_one()

        # Obtener el lead a transformar
        lead = self.lead_id
        partner = self.partner_id

        template = self.env['mail.template'].search(
            [('name', '=', 'Lead to ticket')], limit=1)

        emails = ""
        for member in self.team_id.member_ids:
            emails += (str(member.email) + ",") or ""

        if len(template) > 0:
            template.send_mail(self.id, force_send=True)
        else:
            # Obtiene el servidor de correo de Odoo
            email = self.env['mail.mail'].create({
                'subject':'Un lead fue convertido en ticket',
                'body_html': 'El lead <b>{}</b> fue convertido en un ticket.'.format(lead.name),
                'email_to': emails,
                'email_from': 'gonzalezhugo744@gmail.com'
            })
            # Crear la plantilla por defecto
            self.env['mail.template'].create({
                'name': 'Lead to ticket',
                'subject':'Un lead fue convertido en ticket',
                'body_html': '<p>El lead <b><t t-out=" object.lead_id.contact_name"></t></b> se convirtió en ticket.</p>'.format(lead.name),
                'email_to': "{{ (','.join(filter(None, (member.email for member in object.team_id.member_ids))) if object.team_id.member_ids else '') }}",
                'model_id': self.env['ir.model'].search([('model', '=', 'crm.lead.convert2ticket')]).id,
                'email_from': 'gonzalezhugo744@gmail.com'
            })

            # Envía el correo electrónico
            email.send()

        if not partner and (lead.partner_name or lead.contact_name):
            lead._handle_partner_assignment(create_missing=True)
            partner = lead.partner_id

        # prepare new helpdesk.ticket values
        vals = {
            "name": lead.name,
            "description": lead.description,
            "team_id": self.team_id.id,
            "ticket_type_id": self.ticket_type_id.id,
            "partner_id": partner.id,
            "user_id": None
        }
        if lead.contact_name:
            vals["partner_name"] = lead.contact_name
        if lead.phone:  # lead phone is always sync with partner phone
            vals["partner_phone"] = lead.phone
        else:  # if partner is not on lead -> take partner phone first
            vals["partner_phone"] = partner.phone or lead.mobile or partner.mobile
        if lead.email_from:
            vals['email'] = lead.email_from

        # create and add a specific creation message
        ticket_sudo = self.env['helpdesk.ticket'].with_context(
            mail_create_nosubscribe=True, mail_create_nolog=True
        ).sudo().create(vals)
        ticket_sudo.message_post_with_view(
            'mail.message_origin_link', values={'self': ticket_sudo, 'origin': lead},
            subtype_id=self.env.ref(
                'mail.mt_note').id, author_id=self.env.user.partner_id.id
        )

        # move the mail thread
        lead.message_change_thread(ticket_sudo)
        # move attachments
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)])
        attachments.sudo().write(
            {'res_model': 'helpdesk.ticket', 'res_id': ticket_sudo.id})
        # archive the lead
        lead.action_archive()

        # return to ticket (if can see) or lead (if cannot)
        try:
            self.env['helpdesk.ticket'].check_access_rights('read')
            self.env['helpdesk.ticket'].browse(
                ticket_sudo.ids).check_access_rule('read')
        except:
            return {
                'name': _('Lead Converted'),
                'view_mode': 'form',
                'res_model': lead._name,
                'type': 'ir.actions.act_window',
                'res_id': lead.id
            }

        # return the action to go to the form view of the new Ticket
        view = self.env.ref('helpdesk.helpdesk_ticket_view_form')
        return {
            'name': _('Ticket created'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'res_id': ticket_sudo.id,
            'context': self.env.context
        }
