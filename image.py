from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class webdust_image(osv.Model):

    _name = "webdust.image"
    _description = "Image URLs"


    _columns = {
        'product_id': fields.many2one('product.product', 'Product', select=True, required=True, ondelete='cascade'),
        'url' : fields.char('URL', size=256, required=True),
    }













