from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
class Ot_registration(models.Model):
    _name="ot.registration"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="employee"
    @api.model
    def get_user_current(self):
        """
        Get id in current user
        """
        return self.env["hr.employee"].search([("user_id","=",self.env.uid)])
    @api.onchange("employee")
    def get_manage(self):
        """
        get manage in user current
        """
        for record in self:
            id_user=record.employee.parent_id
            record.manage=id_user

    @api.onchange("ot_id.total_hours","ot_id")
    def _onchange_total_ot(self):
        """
        Get total_hours in table tree ot
        """
        total_ot=0
        self.total_ot=sum(self.ot_id.mapped('total_hours'))
        
        print(f"total_ot: {self.total_ot}")
    @api.constrains("ot_id.start_ot", "ot_id")
    def constrains_start_date(self):
        print(f"len self: {len(self)}")
        list_start_ot=self.ot_id.mapped('start_ot')
        data=self.env['ot'].search([])
        print(f"data: {data}")
        # list_end_ot=self.ot_id.mapped('end_ot')
        print(f"list start ot: {list_start_ot}")
        for r in range(1,len(list_start_ot)):
            if list_start_ot[r].month!=list_start_ot[r-1].month:
                raise ValidationError(_("The months in from and to or records must be the same"))
    

    @api.constrains("ot_id.end_ot", "ot_id")
    def constrains_end_date(self):
        """
        vali
        """
        list_ot=self.ot_id.read()
        for ot in list_ot:
            if ot["start_ot"]>=ot["end_ot"]:
                print(f"ot: {ot}")
                raise ValidationError(_("The start date must be after the end date"))
    @api.constrains("ot_id.ot_category", "ot_id")
    def constrain_ot_category(self):
        for r in self:
            if r.ot_id.ot_category=="Không thể xác định":
                raise ValidationError(_("Category Không thể xác định"))

    @api.onchange('ot_id.start_ot', 'ot_id.end_ot','ot_id')
    def _onchange_ot_month(self):
        """
            get month in list ot
        """
        if len(self.ot_id.mapped("start_ot"))>0:
            _start_ot=self.ot_id.mapped("start_ot")[0]
            _end_ot=self.ot_id.mapped('end_ot')[0]
            if _start_ot and _end_ot:
                if _start_ot.month==_end_ot.month:
                    # print(f"")
                    self.ot_month=str(_start_ot.month)+"/"+str(_start_ot.year)
    @api.multi
    def send_approve(self):
        """
        send ot registration to pm
        """
        template=self.env.ref("ot_management.send_mail_ot")
        for record in self:
            record.state="to_approve"
            for r in record.ot_id:
                r.state=record.state
            template.send_mail(record.id)
    @api.multi
    def PM_approve(self):
        """
        pm approve ot registration from employee
        """
        template=self.env.ref("ot_management.send_mail_ot_dl")
        for record in self:
            record.state = 'approve'
            for r in record.ot_id:
                r.state=record.state
            template.send_mail(record.id)        


    @api.multi
    def Refused(self):
        """
        PM or DL refused ot registration from employee
        """
        template=self.env.ref("ot_management.send_mail_refused_employee")
        for record in self:
            record.state = 'refused'
            for r in record.ot_id:
                r.state=record.state
            template.send_mail(record.id)

    @api.multi
    def DL_approve(self):
        """
        DL approve ot registration from employee
        """
        template=self.env.ref("ot_management.send_mail_response_employee")
        for record in self:
            record.state = 'done'
            for r in record.ot_id:
                r.state=record.state
            template.send_mail(record.id)






    project_id=fields.Many2one("project.project", string="Project", required=True)
    ot_id=fields.One2many('ot', 'ot_registration_id', string='ot id',ondelete='casade', required=True)
    approver=fields.Many2one("hr.employee",string="Approver")
    employee=fields.Many2one("hr.employee", string="employee", default=get_user_current, tracking=True)
    manage=fields.Many2one("hr.employee",string="manage")
    ot_month=fields.Char("OT Month")
    total_ot=fields.Integer(string="Total OT")
    month_first_line=fields.Datetime()
    # create_date=fields.Char(string="Create date")
    state=fields.Selection([("draft","Draft"),("to_approve","To Approve"),("approve","PM Approver"),("done","DL Approver"),("refused","Refused")],default='draft', tracking=True)
    @api.onchange("project_id")
    def _change_approver(self):
        if self.project_id:
            print(f"ID user project: {self.project_id.user_id.id}")
            pm=self.project_id.user_id.id
            if pm:
                self.approver=self.env["hr.employee"].sudo().search([('user_id','=',self.project_id.user_id.id)])
                print(f"approve: {self.approver.id}")
                print(f"total_ot in ot registration: {self.total_ot}")
            else: self.approver=None

    @api.model
    def get_user_current(self):
        """
        get current user
        """
        return self.env["hr.employee"].search([("user_id","=",self.env.uid)])
    
    
    
    
        
