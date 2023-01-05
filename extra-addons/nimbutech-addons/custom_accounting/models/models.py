# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
import json

import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversalInherit(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        self.ensure_one()
        moves = self.move_ids

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], True],
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = bool(default_vals.get('auto_post'))
            is_cancel_needed = not is_auto_post and self.refund_method in (
                'cancel', 'modify')
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(
                default_values_list, cancel=is_cancel_needed)

            if self.refund_method == 'modify':
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data(
                        {'date': self.date if self.date_mode == 'custom' else move.date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves

        self.new_move_ids = moves_to_redirect

        for line in range(len(self.new_move_ids.line_ids)):
            record = self.env['custom_accounting.account.redirect'].search(
                [('account_origin_id.id', '=', self.new_move_ids.line_ids[line].account_id.id)])
            current_company = self.env.company
            
            _logger.info(current_company)
            _logger.info(record)
            _logger.info(record.account_destination_id.code)
            _logger.info(self.new_move_ids.line_ids[line].account_id.code)
            _logger.info(len(record))
            #odoo.addons.custom_accounting.models.models: custom_accounting.account.redirect(2,)
            _logger.info(self.env['account.account'].search([('code', '=', record.account_destination_id.code if len(
                record) > 0 else self.new_move_ids.line_ids[line].account_id.code), ('company_id', '=', current_company.id)]).id)
            self.new_move_ids.line_ids[line].account_id = self.env['account.account'].search([('code', '=', record.account_destination_id.code if len(
                record) > 0 else self.new_move_ids.line_ids[line].account_id.code), ('company_id', '=', current_company.id)]).id

        for i in self.new_move_ids.line_ids:
            _logger.info(i.account_id)

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }

        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
                'context': {'default_move_type':  moves_to_redirect.move_type},
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
            if len(set(moves_to_redirect.mapped('move_type'))) == 1:
                action['context'] = {
                    'default_move_type':  moves_to_redirect.mapped('move_type').pop()}
        return action


class AccountRedirect(models.Model):
    _name = 'custom_accounting.account.redirect'

    name = fields.Char(string='Name')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
        required=True,
        readonly=True,
    )

    account_origin_id = fields.Many2one(
        'account.account',
        string='Cuenta de origen',
        domain="[('company_id', '=', company_id)]",
        required=True
    )

    account_destination_id = fields.Many2one(
        'account.account',
        string='Cuenta de destino',
        domain="[('company_id', '=', company_id)]",
        required=True
    )

    @api.onchange('account_origin_id')
    def _onchange_account_origin_id(self):
        for record in self:
            if record.account_origin_id:
                record.name = record.account_origin_id.code

    @api.constrains('account_origin_id')
    def _check_unique_account_origin_id(self):
        for record in self:
            if record.account_origin_id:
                # Buscar si existe otro registro con el mismo account_origin_id
                other_record = self.env['custom_accounting.account.redirect'].search(
                    [('account_origin_id', '=', record.account_origin_id.id)])
                # Si hay mas de un registro significa que ya existe otro registro con el mismo account_origin_id
                if len(other_record) > 1:
                    raise ValidationError(
                        "Ya existe un registro con esta cuenta de origen. Por favor elige otra.")
