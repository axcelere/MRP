# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
import math
from datetime import datetime
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import UserError, ValidationError


class Mrp_inherit(models.Model):
    _inherit = "mrp.bom.line"

    flexible_consume = fields.Boolean(string="Flexible Consume")

class Mrp_inherit(models.Model):
    _inherit = "stock.move"

    flexible_consume = fields.Boolean(string="Flexible Consume",related="bom_line_id.flexible_consume")



class Mrp_inherit(models.Model):
    _inherit = "mrp.production"


    # prueba
    # def _get_move_raw_values(self, bom_line, line_data):

    #     res = super(Mrp_inherit, self)._get_move_raw_values(bom_line, line_data)


    #     print ("res====================tttttttt=================",bom_line.flexible_consume)

    #     res.update({'flexible_consume' : bom_line.flexible_consume})

    #     return res

    def button_mark_done(self):
        # button_mark_done
        for wo in self.workorder_ids:
            
            if wo.state not in ['done','cancel']:
                raise UserError(_('Work order %s is still running') % wo.name)
        
        return super(Mrp_inherit,self).button_mark_done()

    
    def _compute_workorde1(self):
        for mrp in self :
            workorders_res = self.env['mrp.workorder'].search([('production_id','=',mrp.id)],order="id desc", limit=1)
            if workorders_res.state == 'done' :
                mrp.is_post_inventory = True
                stock_moveline = self.env['stock.move.line'].search([('reference','=',mrp.name)])
                
                for move in stock_moveline :
                    if move.state == 'done' :
                        mrp.is_post_inventory = False
                        break
                    else:
                        pass
            else :
                mrp.is_post_inventory = False

        return

    is_post_inventory = fields.Boolean(compute='_compute_workorde1',string='Is Post Inventory')

class MrpWorkorder_inherit(models.Model):
    _inherit = "mrp.workorder"

    new_qty_producing = fields.Float(string="New Qty production")
    is_done_workorder = fields.Boolean('Is Done WorkOrder',compute='_compute_is_done_workorder',readonly="False")
    
    
    def _compute_is_done_workorder(self):
        for line in self :
            workorder_ids = self.env['mrp.workorder'].search([('production_id','=',line.production_id.id)],order="id desc", limit=1)
            
            if line.id == workorder_ids.id :
                line.is_done_workorder = True
            else : 
                line.is_done_workorder = False
        return


    def do_finish(self):
        res = super(MrpWorkorder_inherit, self).do_finish()

        if self.is_done_workorder == True :
            self.action_custom_done()
            self.production_id.write({'state' : 'to_close'})
        return res


    def action_custom_done(self):
        if self.new_qty_producing <= 0:
            raise UserError(_('Please ensure the quantity to produce is nonnegative and does not exceed the remaining quantity.'))

        stock_move_ids = self.production_id.move_finished_ids

        for line in stock_move_ids :

            if line.product_id.id == self.product_id.id :
                for move_line in line.move_line_ids :
                    move_line.write({'qty_done' : self.new_qty_producing})


        for raw in self.production_id.move_raw_ids :

            print (raw.product_id.name,"====================================",raw.flexible_consume)
            if raw.flexible_consume == True :
                qty = raw.product_uom_qty
                new = self.new_qty_producing
                old = self.production_id.product_qty
                if old > 0 :
                    new_raw = (new * qty) / old

                    raw.write({'quantity_done' :new_raw })

        return 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
