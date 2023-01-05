# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Lead
    partner_name = fields.Char(
        'Company Name', tracking=20, index=True,
        compute='_compute_partner_name', readonly=False, store=True,
        help='The name of the future partner company that will be created while converting the lead into opportunity',
        required=True
    )

    street = fields.Char('Street', compute='_compute_partner_address_values',
                         readonly=False, store=True, required=True)

    phone = fields.Char(
        'Phone', tracking=50,
        compute='_compute_phone', inverse='_inverse_phone', readonly=False, store=True, required=True)

    mobile = fields.Char('Mobile', compute='_compute_mobile',
                         readonly=False, store=True, required=True)

    contact_name = fields.Char(
        'Contact Name', tracking=30,
        compute='_compute_contact_name', readonly=False, store=True, required=True)

    email_from = fields.Char(
        'Email', tracking=40, index=True,
        compute='_compute_email_from', inverse='_inverse_email_from', readonly=False, store=True, required=True)

    function = fields.Char('Job Position', compute='_compute_function',
                           readonly=False, store=True, required=True)

    team_id = fields.Many2one(
        'crm.team', string='Sales Team', check_company=True, index=True, tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_team_id', ondelete="restrict", readonly=False, store=True, required=True)

    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True, required=True)

    description = fields.Html('Notes', required=True)

    state = fields.Selection(
        string='Estado',
        selection=[
            ('open', 'Abierto'), ('qualified', 'Calificado'), ('disqualified', 'Descalificado')],
        default='disqualified'
    )

    # Cliente potencial
    process = fields.Selection(
        string="Proceso",
        selection=[
            ('sls', 'SLS'),
            ('pos', 'POS')
        ]
    )

    close_date = fields.Date(
        string="Fecha de cierre"
    )

    number_of_employees = fields.Integer('Número de empleados', required=True)

    industry = fields.Selection(
        string='Industria',
        selection=[
            ('1', 'ADMINISTRACIÓN PÚBLICA Y DEFENSA; SEGURIDAD SOCIAL OBLIGATORIA'),
            ('2', 'ACTIVIDADES ADMINISTRATIVAS Y SERVICIOS DE SOPORTE'),
            ('3', 'AGRICULTURA, FORESTAL Y PESCA'),
            ('4', 'ACTIVIDADES DE ALOJAMIENTO Y SERVICIO DE ALIMENTOS'),
            ('5', 'ACTIVIDADES DE BIENES RAICES'),
            ('6', 'ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS'),
            ('7', 'CONSTRUCCIÓN'),
            ('8', 'EDUCACIÓN'),
            ('9', 'ARTES, ENTRETENIMIENTO Y RECREACIÓN'),
            ('10', 'ACTIVIDADES DE ORGANIZACIONES Y CUERPOS EXTRATERRITORIALES'),
            ('11', 'FABRICACIÓN'),
            ('12', 'ACTIVIDADES FINANCIERAS Y SEGUROS'),
            ('13', 'INFORMACIÓN Y COMUNICACIÓN'),
            ('14', 'COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS DE MOTOR Y MOTOCICLETAS'),
            ('15', 'MINAS Y CANTERAS'),
            ('16', 'ACTIVIDADES DE OTROS SERVICIOS'),
            ('17', 'ACTIVIDADES DE SALUD HUMANA Y TRABAJO SOCIAL'),
            ('18', 'ABASTECIMIENTO DE AGUA, ALCANTARILLADO, GESTIÓN DE RESIDUOS Y ACTIVIDADES DE REMEDIACIÓN'),
            ('19', 'SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO'),
            ('20', 'TRANSPORTACIÓN Y ALMACENAJE')
        ]
    )

    website = fields.Char(
        'Website',
        index=True,
        help="Website of the contact",
        compute="_compute_website",
        readonly=False,
        store=True,
        required=True
    )

    budget = fields.Selection(
        string='Presupuesto',
        selection=[
            ('no_budget', 'No tiene presupuesto'),
            ('no_budget_but_want', 'No tiene presupuesto pero le gustaría tenerlo'),
            ('budget_not_enough', 'Tiene presupuesto, pero no es suficiente'),
            ('budget_enough', 'Tiene presupuesto y es suficiente'),
            ('budget_exceeds', 'Tiene presupuesto y se excede')
        ],
        default='no_budget'
    )

    authority = fields.Selection(
        string='Autoridad',
        selection=[
            ('no_decision_no_access',
             'No toma la decisión, ni tiene acceso a quien la toma'),
            ('no_decision_access',
             'No toma la decisión, pero tiene acceso a quien la toma'),
            ('no_decision_influence', 'No toma decisión, pero influye en quien la toma'),
            ('decision_together', 'Toma la decisión en conjunto con otras personas'),
            ('decision_only', 'Es quien toma la decisión')
        ],
        default='no_decision_no_access'
    )

    need = fields.Selection(
        string='Necesidad',
        selection=[
            ('no_need', 'No tiene necesidad'),
            ('no_need_but_want', 'No tiene necesidad pero le gustaría tenerlo'),
            ('need_not_indispensable', 'Tiene necesidad, pero no es indispensable'),
            ('need_covered', 'Tiene necesidad, pero tiene con quien cubrirla'),
            ('need_dont_know_how', 'Tiene necesidad y no sabe como solucionarlo')
        ],
        default='no_need'
    )

    timing = fields.Selection(
        string='Tiempo',
        selection=[
            ('not_defined', 'No tiene definido cuando'),
            ('after_year', 'Después de un año'),
            ('between_6_12_months', 'Entre 6 y 12 meses'),
            ('between_3_6_months', 'Entre 3 y 6 meses'),
            ('less_than_3_months', 'En menos de 3 meses')
        ],
        default='not_defined'
    )

    # Calificado
    request_type = fields.Selection(
        string='Solicitud preventa',
        selection=[
            ('internal', 'Interno'),
            ('ally', 'Aliado')
        ]
    )

    opportunity_type = fields.Selection(
        string='Crear Oportunidad',
        selection=[
            ('products', 'Productos'),
            ('values', 'Valores')
        ]
    )

    # Propuesta
    administrative_description = fields.Text(
        string='Descripción de técnica del proyecto')

    contract_modality = fields.Selection(string='Modalidad del contrato',
                                         selection=[
                                             ('single_payment_services',
                                              'Único pago servicios'),
                                             ('single_payment_onpremise',
                                              'Único pago - Onpremise'),
                                             ('annual_commitment_monthly_payment',
                                              'Compromiso anual - Pago mensual'),
                                             ('annual_commitment_annual_payment',
                                              'Compromiso Anual - Pago Anual'),
                                         ],
                                         )

    supporting_offer = fields.Text(string='Sustentar oferta')

    presale = fields.Selection(
        string='Preventa',
        selection=[
            ('0', 'Sin aliado'),
            ('1', 'Jeduca'),
            ('2', 'Intcomex'),
            ('3', 'Nube IT'),
            ('4', 'Innfuturum'),
            ('5', 'Sinova'),
            ('6', 'German Villaraga'),
            ('7', 'Otro')
        ]
    )

    # Negociacion
    nit = fields.Char(string="Nit")

    def check_required_fields(self, vals):
        errors = []
        if not vals.get('industry'):
            errors.append('Industria')
        if not vals.get('number_of_employees'):
            errors.append('Número de empleados')
        if not vals.get('website'):
            errors.append('Sitio web')
        if not vals.get('street'):
            errors.append('Dirección')
        if not vals.get('phone'):
            errors.append('Telefono')
        if not vals.get('mobile'):
            errors.append('Móvil')
        if not vals.get('contact_name'):
            errors.append('Nombre del contacto')
        if not vals.get('email_from'):
            errors.append('Correo electrónico')
        if not vals.get('function'):
            errors.append('Puesto')
        if not vals.get('team_id'):
            errors.append('Equipo de ventas')
        if not vals.get('user_id'):
            errors.append('Vendedor')
        if not vals.get('description'):
            errors.append('Nota')
        return errors

    def check_required_potential_client_fields(self):
        errors = []
        if not self.partner_name:
            errors.append('Partner')
        if not self.process:
            errors.append('Proceso')
        if not self.industry:
            errors.append('Industria')
        if not self.website:
            errors.append('Sitio web')
        if not self.partner_name:
            errors.append('Partner')
        if not self.street:
            errors.append('Dirección')
        if not self.phone:
            errors.append('Telefono')
        if not self.mobile:
            errors.append('Móvil')
        if not self.contact_name:
            errors.append('Nombre del contacto')
        if not self.email_from:
            errors.append('Correo electrónico')
        if not self.function:
            errors.append('Puesto')
        if not self.team_id:
            errors.append('Equipo de ventas')
        if not self.user_id:
            errors.append('Vendedor')
        if not self.state:
            errors.append('Estado')
        if not self.budget:
            errors.append('BANT/Presupuesto')
        if not self.authority:
            errors.append('BANT/Autoridad')
        if not self.need:
            errors.append('BANT/Necesidad')
        if not self.timing:
            errors.append('BANT/Tiempo')
        return errors

    def check_required_qualified_fields(self):
        errors = []
        if not self.request_type:
            errors.append('Solicitud de preventa')
        if not self.request_type:
            errors.append('Oportunidad')
        return errors

    def check_required_proposition_fields(self):
        errors = []
        if not self.administrative_description:
            errors.append('Descripción administrativa')
        if not self.contract_modality:
            errors.append('Modalidad de contrato')
        if not self.supporting_offer:
            errors.append('Sustentar oferta')
        if not self.presale:
            errors.append('Preventa')
        return errors

    def check_required_deal_fields(self):
        errors = []
        if not self.nit:
            errors.append('NIT')
        return errors

    def check_required_formalize_fields(self):
        errors = []
        return errors

    @api.model
    def create(self, vals):
        errors = self.check_required_fields(vals)
        if len(errors) == 0:
            return super(CrmLead, self).create(vals)
        else:
            message = "Debes completar los siguientes campos: \n" + \
                ", ".join(errors)
            raise ValidationError(message)

    @api.onchange('stage_id')
    def _onchange_other_field(self):
        option = self.stage_id.name.lower().strip()
        if option == 'cliente potencial':
            errors = self.check_required_potential_client_fields()
            if len(errors) > 0:
                message = "Debes completar los siguientes campos para poder cambiar de fase: \n" + \
                    ", ".join(errors)
                raise ValidationError(message)
        if option == 'qualified':
            errors = self.check_required_qualified_fields()
            if len(errors) > 0:
                message = "Debes completar los siguientes campos para poder cambiar de fase: \n" + \
                    ", ".join(errors)
                raise ValidationError(message)
        if option == 'proposition':
            errors = self.check_required_proposition_fields()
            if len(errors) > 0:
                message = "Debes completar los siguientes campos para poder cambiar de fase: \n" + \
                    ", ".join(errors)
                raise ValidationError(message)
        if option == 'negociación':
            errors = self.check_required_deal_fields()
            if len(errors) > 0:
                message = "Debes completar los siguientes campos para poder cambiar de fase: \n" + \
                    ", ".join(errors)
                raise ValidationError(message)
        if option == 'formalización':
            errors = self.check_required_formalize_fields()
            if len(errors) > 0:
                message = "Debes completar los siguientes campos para poder cambiar de fase: \n" + \
                    ", ".join(errors)
                raise ValidationError(message)

    def action_set_won_rainbowman(self):
        self.ensure_one()
        self.action_set_won()

        if self.stage_id.name.lower() == 'ganado':
            self.close_date = datetime.today()

        message = self._get_rainbowman_message()
        if message:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/web/image/%s/%s/image_1024' % (self.team_id.user_id._name, self.team_id.user_id.id) if self.team_id.user_id.image_1024 else '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        return True

    def open_crm_bant_wizard_form(self):
        self.ensure_one()
        return {
            'name': 'BANT',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.bant.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }
