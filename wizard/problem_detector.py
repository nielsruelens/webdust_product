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
        #problems = [item for sublist in [x for x in problems] for item in sublist] #flatten the list


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

    def fix(self, cr, uid, ids, context=None):

        prod_db = self.pool.get('product.product')
        for wizard in self.browse(cr, uid, ids):
            if wizard.problems:
                prod_db.write(cr, uid, [x.product.id for x in wizard.problems], {}, context=context)
        return self.start(cr, uid, ids, context)


    def calculate(self, cr, uid):
        prod_db = self.pool.get('product.product')
        supplier_db = self.pool.get('product.supplierinfo')
        result = []

        # Find products that shouldn't be sellable
        # ----------------------------------------
        products = prod_db.search(cr, uid, [('sale_ok', '=', True)])
        if products:
            products = prod_db.read(cr, uid, products, ['id', 'state', 'seller_ids', 'supplier_storage_location'])
            suppliers = supplier_db.browse(cr, uid, [item for sublist in [x['seller_ids'] for x in products] for item in sublist])

            for product in products:
                if product['state'] == 'obsolete':
                    result.append((0,0,{'product': product['id'], 'problem': 'Product is obsolete, yet it is sellable.'}))
                    continue
                if product['state'] == 'draft':
                    result.append((0,0,{'product': product['id'], 'problem': 'Product is in draft, yet it is sellable.'}))
                    continue
                if len(product['seller_ids']) == 0:
                    result.append((0,0,{'product': product['id'], 'problem': 'Product does not have any sellers, yet it is sellable.'}))
                    continue
                if product['supplier_storage_location'] != '1015':
                    result.append((0,0,{'product': product['id'], 'problem': 'Product does not have supplier storage location 1015, yet it is sellable.'}))
                    continue

                problem = True
                for s in product['seller_ids']:
                    supplier = [x for x in suppliers if x.id == s][0]
                    if supplier.state in ('available','limited') and supplier.product_code:
                        problem = False
                if problem:
                    result.append((0,0,{'product': product['id'], 'problem': 'Product has invalid or missing supplier information, yet it is sellable.'}))
                    continue


        # Find products that should be sellable
        # -------------------------------------
        products = prod_db.search(cr, uid, [('sale_ok', '=', False),('supplier_storage_location','=','1015'),('procure_method','=','make_to_stock')])
        if products:
            products = prod_db.read(cr, uid, products, ['id', 'state', 'seller_ids'])
            suppliers = supplier_db.browse(cr, uid, [item for sublist in [x['seller_ids'] for x in products] for item in sublist])

            for product in products:

                if product['state'] in ('obsolete', 'draft') or len(product['seller_ids']) == 0:
                    continue

                sale_ok = False
                for s in product['seller_ids']:
                    supplier = [x for x in suppliers if x.id == s][0]
                    if supplier.state in ('available','limited') and supplier.product_code:
                        sale_ok = True
                if sale_ok:
                    result.append((0,0,{'product': product['id'], 'problem': 'Product should be sellable, yet it is not!.'}))

        return result


















