# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Partner extension."""

    _inherit = 'res.partner'

    vat_type = fields.Selection([
        ('11', u'11 - Registro Civil'),
        ('12', u'12 - Tarjeta de identidad'),
        ('13', u'13 - Cédula de ciudadanía'),
        ('21', u'21 - Tarjeta de extranjería'),
        ('22', u'22 - Cédula de extranjería'),
        ('31', u'31 - NIT (Número de identificación tributaria)'),
        ('41', u'41 - Pasaporte'),
        ('42', u'42 - Documento de identificación extranjero'),
        ('43', u'43 - Sin identificación del exterior o para uso definido por la DIAN'),
        ('50', u'50 - NIT de otro pais'),
        ('91', u'91 - NUIP')
    ], string='VAT type',
        help='''Customer identifier, according to types given by the DIAN.
                If it is a natural person and has RUT use NIT''',
        required=False
    )
    vat_vd = fields.Char('vd', size=1, help='Digito de verificación', store=True)
    firstname = fields.Char()
    other_name = fields.Char()
    lastname = fields.Char()
    other_lastname = fields.Char()
    name = fields.Char(index=True)
    vat_num = fields.Char(string='NIF')

    @api.onchange('firstname', 'other_name', 'lastname', 'other_lastname')
    def _name_compute(self):
        for rec in self:
            if rec.company_type == 'person':
                rec.name = (str(rec.firstname) if rec.firstname else '') \
                           + ' ' + (str(rec.other_name) if rec.other_name else '') \
                           + ' ' + (str(rec.lastname) if rec.lastname else '') \
                           + ' ' + (str(rec.other_lastname) if rec.other_lastname else '')


    @api.onchange('vat_num', 'l10n_latam_identification_type_id')
    def _on_chage_vat(self):
        self.onchange_document_type()
        if self.l10n_latam_identification_type_id.l10n_co_document_code == 'rut' and self.vat_num:
            self.vat = str(self.vat_num) + '-' + str(self.vat_vd)
            self.vat_vd = self._check_vat_co()
        else:
            self.vat = self.vat_num

    @api.onchange('vat_vd')
    def _on_chage_vat_dv(self):
        if self.l10n_latam_identification_type_id.l10n_co_document_code == 'rut':
            self.vat = str(self.vat_num) + '-' + str(self.vat_vd)
        else:
            self.vat = self.vat_num

    #@api.model
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for record in self:
            if record.child_ids:
                for child in record.child_ids:
                    vals_ch= {
                        'vat_num' : record.vat_num,
                        'vat_vd' : record.vat_vd,
                        'vat' : record.vat,
                        'l10n_latam_identification_type_id' : record.l10n_latam_identification_type_id.id,
                        'vat_type' : record.vat_type,
                    }
                    child.write(vals_ch)
        return res

    @api.depends('vat_type', 'vat_num')
    def _check_vat_co(self):
        if self.vat_type != '31':
            return ''


        factor = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        factor = factor[-len(self.vat_num):]
        csum = sum([int(self.vat_num[i]) * factor[i] for i in range(len(self.vat_num))])
        check = csum % 11
        if check > 1:
            check = 11 - check
        return check

    def _onerror_msg(self, msg):
        return {'warning': {'title': _('Error!'), 'message': _(msg)}}

    @api.onchange('vat_type')
    def onchange_vat_type(self):

        return {'value': {'is_company': self.vat_type == '31'}}


    def _commercial_fields(self):
        """
        Return the list of fields that are managed by the commercial entity
        to which a partner belongs.

        These fields are meant to be hidden on partners that aren't
        `commercial entities` themselves, and will be delegated to
        the parent `commercial entity`. The list is meant to be
        extended by inheriting classes.
        """
        return ['website']

    def copy(self):
        [partner_dic] = self.read(['name', 'vat', 'vat_num', 'vat_vd'])
        default = {}
        default.update({
            'name': '(copy) ' + partner_dic.get('name'),
        })
        return super(ResPartner, self).copy(default)

    def _check_vat(self):
        if self.company_id and self.vat and self.search(
                [('company_id', '=', self.company_id.id), ('vat', '=ilike', self.vat),
                 ('parent_id', '=', None)]).id != self.id:
            return False
        return True


    @api.onchange("l10n_latam_identification_type_id")
    def onchange_document_type(self):
        if self.l10n_latam_identification_type_id.l10n_co_document_code == 'rut':
            self.vat_type = '31'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'id_document':
            self.vat_type = '13'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'id_card':
            self.vat_type = '12'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'passport':
            self.vat_type = '41'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'foreign_id_card':
            self.vat_type = '22'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'external_id':
            self.vat_type = '50'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'diplomatic_card':
            self.vat_type = ''
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'residence_document':
            self.vat_type = ''
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'civil_registration':
            self.vat_type = '11'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'national_citizen_id':
            self.vat_type = '13'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'niup_id':
            self.vat_type = '91'

