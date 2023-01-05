from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def _avatar_get_placeholder_path(self):
        if self.is_company:
            return "custom_modules/static/img/default_company.jpeg"
        if self.type == 'delivery':
            return "base/static/img/truck.png"
        if self.type == 'invoice':
            return "base/static/img/money.png"
        return super()._avatar_get_placeholder_path()


class AvatarMixin(models.AbstractModel):
    _inherit = 'avatar.mixin'
    
    def _avatar_get_placeholder_path(self):
        return "custom_modules/static/img/custom_user.png"