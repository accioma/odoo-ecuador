# -*- coding: utf-8 -*-

from odoo import api, fields, models

from stdnum import ec


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    @api.depends('identifier', 'name')
    def name_get(self):
        data = []
        for partner in self:
            display_val = u'{0} {1}'.format(
                partner.identifier or '*',
                partner.name
            )
            data.append((partner.id, display_val))
        return data

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if not args:
            args = []
        if name:
            partners = self.search([('identifier', operator, name)] + args, limit=limit)
            if not partners:
                partners = self.search([('name', operator, name)] + args, limit=limit)
        else:
            partners = self.search(args, limit=limit)
        return partners.name_get()

    def _check_identifier(self, cr, uid, ids):
        for partner in self.browse(cr, uid, ids):
            if partner.type_identifier == 'cedula':
                return ec.ci.is_valid(partner.identifier)
            elif partner.type_identifier == 'ruc':
                return ec.ruc.is_valid(partner.identifier)
            else:
                return True

    identifier = fields.Char(
        'Cedula/ RUC',
        size=13,
        required=True,
        help='Identificación o Registro Unico de Contribuyentes')
    type_identifier = fields.Selection(
        [
            ('cedula', 'CEDULA'),
            ('ruc', 'RUC'),
            ('pasaporte', 'PASAPORTE')
            ],
        'Tipo ID',
        required=True,
        default='pasaporte'
    )
    tipo_persona = fields.Selection(
        [
            ('6', 'Persona Natural'),
            ('9', 'Persona Juridica')
        ],
        string='Persona',
        required=True,
        default='9'
    )
    company_type = fields.Selection(default='company')

    _constraints = [
        (_check_identifier, 'Error en su Cedula/RUC/Pasaporte', ['identifier'])
        ]

    _sql_constraints = [
        ('partner_unique',
         'unique(identifier,type_identifier,tipo_persona,company_id)',
         u'El identificador es único.'),
        ]

    def validate_from_sri(self):
        """
        TODO
        """
        SRI_LINK = "https://declaraciones.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos1.jspa"  # noqa
        texto = '0103893954'  # noqa


class ResCompany(models.Model):
    _inherit = 'res.company'

    accountant_id = fields.Many2one('res.partner', 'Contador')
    sri_id = fields.Many2one('res.partner', 'Servicio de Rentas Internas')
    cedula_rl = fields.Char('Cédula Representante Legal', size=10)
