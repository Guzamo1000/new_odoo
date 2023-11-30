from odoo.exceptions import ValidationError
import pytz
from odoo import models, fields, api, _
from datetime import datetime, time, timedelta


class Ot(models.Model):
    _name = "ot"
    _desciption = "OT management"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def tz_utc_to_local(self, utc_time):
        return utc_time + self.utc_offset()

    def tz_local_to_utc(self, local_time):
        return local_time - self.utc_offset()

    def utc_offset(self):
        user_timezone = self.env.user.tz or 'GMT'
        hours = int(datetime.now(pytz.timezone(user_timezone)).strftime('%z')[:3])
        return timedelta(hours=hours)

    

   
    @api.onchange("start_ot", "end_ot")
    def _change_total_house(self):
        """
        Calculate the total number of hours Ot
        """
        
        for record in self:

            if record.start_ot and record.end_ot and record.end_ot > record.start_ot:
                total_hours = (record.end_ot - record.start_ot)
                print(f"total hours: {total_hours}")
                record.total_hours = total_hours.total_seconds() / 3600

    @api.onchange("total_hours")
    def _change_category_ot_and_ot_month(self):
        """
        Convert period ot to type ot and get month in ot
        """
        for record in self:
            if record.start_ot and record.end_ot:
                
                start_ot = record.start_ot + self.utc_offset()
                end_ot = record.end_ot + self.utc_offset()
                timenow = datetime.now().date()
                timenow=datetime.combine(timenow,time(23,59,59))
                print(f"start_ot: {start_ot}")
                print(f"end_ot: {end_ot}")
                if start_ot > end_ot or (timenow-start_ot).days>2:
                    print(f"Quá thời gian: {(timenow-start_ot).days}")
                    record.ot_category = "Không thể xác định"
                else:
                    date_start = start_ot.date()
                    date_end = end_ot.date()
                    time_start = start_ot.time()
                    time_end = end_ot.time()
<<<<<<< HEAD
=======
                    
>>>>>>> 43c776c9ace642351ae39aeb8d38963a58a9fd85
                    if date_start == date_end:
                        # print(f"day: {date_}")
                        if date_start.weekday() == 5 and date_end.weekday() == 5:
                            record.ot_category = "Thứ 7"
                        elif date_start.weekday() == 6 and date_end.weekday() == 6:
                            record.ot_category = "Chủ nhật"
                            # if time_start > time(18, 30, 00) and time_end < time(23, 59, 59):
                            #     record.ot_category = "Ngày cuối tuần ban đêm"
                        else:
                            if (time_start >= time(6, 00, 00)) and (time_end <= time(8, 30, 00)):
                                record.ot_category = "OT ban ngày"
                            elif (time_start >= time(18, 30, 00)) and (time_end <= time(22, 00, 00)):
                                print("NGÀY BÌNH THƯỜNG")
                                record.ot_category = "Ngày bình thường"
                            elif (time_start >= time(22,0,0) and  time_end <= time(23, 59, 59)) or (time_start>=time(0,0,0) and time_end<=time(6,0,0)) :
                                record.ot_category = "Ngày bình thường - ban đêm"

                            else:
                                record.ot_category = "Không thể xác định"
                    elif start_ot.day == end_ot.day - 1:
                        
                        if (time_start >= time(18, 30, 00) and time_start <= time(23, 59, 59)) and (
                                time_end >= time(00, 00, 00) and time_end <= time(6, 00, 00)):
                            if date_start.weekday()==6 and date_end.weekday()==0:
                                record.ot_category="Ngày cuối tuần-ban đêm"
                            else:
                                record.ot_category = "Ngày bình thường - ban đêm"

                        else:
                            record.ot_category = "Không thể xác định"
                    else:
                        record.ot_category = "Không thể xác định"
                   
            else:
                record.ot_category = "Không thể xác định"

    @api.constrains("start_ot", "end_ot")
    def check_month(self):
        data=self.env['ot'].search([])
        print(f"data: {self}")
        for r in range(len(self)):
            start_ot_r=(self[r]['start_ot']+self.utc_offset())
            end_ot_r=(self[r]['end_ot']+self.utc_offset())
            for i in range(r+1,len(self)):
                start_ot_i=(self[i]['start_ot']+self.utc_offset())
                end_ot_i=self[i]['end_ot']+self.utc_offset()    
                if start_ot_r.month!=start_ot_i.month:
                    raise ValidationError(_("The months in from and to or records must be the same"))
                print(f"r: {start_ot_r.day} and i {start_ot_i.day} ")
                if start_ot_r.day==start_ot_i.day:
                    print(f"r: {self[r]['ot_category']} and i {self[i]['ot_category']} ")
                    if self[r]['state']==self[i]['state']:
                        if (start_ot_i>=start_ot_r and start_ot_i<=end_ot_r) or (end_ot_i>=start_ot_r and end_ot_i<=end_ot_r) or (start_ot_r>=start_ot_i and start_ot_r<=end_ot_i) or (end_ot_r>=start_ot_i and end_ot_r<=end_ot_i) : 
                            print(f"start_ot_i: {self[i]['start_ot']} and end_ot_i: {self[i]['end_ot']}")
                            print(f"start_ot_r: {self[r]['start_ot']} and end_ot_r: {self[r]['end_ot']}")
                        # if self[r]['']
                            raise ValidationError(_("Same time ot"))

    

    start_ot = fields.Datetime(string="From", default=datetime.now(), required=True)
    end_ot = fields.Datetime(string="to", default=datetime.now(),required=True)
    total_hours = fields.Float(string="OT hours")
    location = fields.Selection([("WFH", "WFH"), ("BZ", "BZ")], string="WFB/BZ")
    task = fields.Many2one("project.task", string="Job taken")
    ot_category = fields.Char("OT Category", store=True, compute_sudo=True)
    state = fields.Selection(
        [("draft", "Draft"), ("to_approve", "To Approve"), ("approve", "PM Approver"), ("done", "DL Approver"),
         ("refused", "Refused")], default='draft', store=True)
    evidences_ids = fields.Many2many("ir.attachment", "evidences_ir_attachmen", "ot_id", "ir_attachment_id",
                                     "Evidences in attachment")
    late_approved = fields.Boolean(string="Late approved")
    hr_notes = fields.Char(string="HR notes")
    attendance_notes = fields.Char(string="Attendance notes")
    warning = fields.Char(strig="Warning", default="Exceed OT plan")
    create_date = fields.Datetime("Create On")
    employee_id = fields.Many2one("hr.employee", string="employee ids")
    ot_registration_id = fields.Many2one("ot.registration", string="ot ids")
    project_name = fields.Many2one("project.project", string="Project", related='ot_registration_id.project_id',
                                   compute_sudo=True, store=True, tracking=True)
    employee = fields.Many2one("hr.employee", string="Employee", related='ot_registration_id.employee',
                               compute_sudo=True, store=True, tracking=True)
    manage_approve = fields.Many2one("hr.employee", string="Approve", related='ot_registration_id.approver',
                                     compute_sudo=True, store=True, tracking=True)

    manager_deparment=fields.Many2one("hr.employee", string="Manage", related='ot_registration_id.manage',  compute_sudo=True, store=True, tracking=True)