from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BantWizard(models.TransientModel):
    _name = 'crm.bant.wizard'

    lead_id = fields.Many2one('crm.lead', readonly=True)

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

    def default_get(self, fields):
        lead_id = self.env.context.get('default_lead_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            default_values = {
                'lead_id': lead_id,
                'budget': lead.budget,
                'authority': lead.authority,
                'need': lead.need,
                'timing': lead.timing,
            }
            return default_values
        return {
            'budget': 'no_budget',
            'authority': 'no_decision_no_access',
            'need': 'no_need',
            'timing': 'not_defined'
        }

    def save_bant(self):
        lead = self.lead_id

        lead.write({
            'budget': self.budget,
            'authority': self.authority,
            'need': self.need,
            'timing': self.timing,
        })

