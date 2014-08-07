from openerp.osv import fields,osv
from openerp.tools.translate import _

class webdust_product_problem_detector_line(osv.TransientModel):
    _name = 'webdust.product.problem.detector.line'
    _description = 'Product Problem Detector Line'

    _columns = {
        'product': fields.many2one('product.product', 'Product', select=True),
        'problem': fields.char('Problem', size=300),
        'wizard': fields.many2one('webdust.product.problem.detector', 'Wizard', ondelete='cascade', required=True, select=True),
    }



class webdust_product_problem_detector(osv.TransientModel):
    _name = "webdust.product.problem.detector"
    _description = 'Product Problem Detector'

    _columns = {
        'problems': fields.one2many('webdust.product.problem.detector.line', 'wizard', 'Problems'),
    }


    def start(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]

        problems = self.calculate(cr, uid)
        problems = [item for sublist in [x for x in problems] for item in sublist] #flatten the list


        self.write(cr, uid, ids, {'problems': problems}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'webdust.product.problem.detector',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }


    def calculate(self, cr, uid):
        prod_db = self.pool.get('product.product')
        products = prod_db.search(cr, uid, [('sale_ok', '=', True)])
        if not products: return []
        products = prod_db.read(cr, uid, products, ['id', 'state', 'seller_ids', 'supplier_storage_location'])

        result = []

        # The easy ones
        # -------------
        result.append([(0,0,{'product': x['id'], 'problem': 'Product is obsolete, yet it is sellable.'}) for x in products if x['state'] == 'obsolete'])
        result.append([(0,0,{'product': x['id'], 'problem': 'Product does not have any sellers, yet it is sellable.'}) for x in products if not x['seller_ids']])
        result.append([(0,0,{'product': x['id'], 'problem': 'Product does not have supplier storage location 1015, yet it is sellable.'}) for x in products if  x['supplier_storage_location'] != '1015'])
        return result


















