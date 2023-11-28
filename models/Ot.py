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
                timenow = datetime.now()
                
                if start_ot > end_ot or end_ot.day>=(timenow.day-2):
                    record.ot_category = "Không thể xác định"
                else:
                    date_start = start_ot.date()
                    date_end = end_ot.date()
                    time_start = start_ot.time()
                    time_end = end_ot.time()
                    
                    if date_start == date_end:
                        if date_start.weekday() == 5 and date_end.weekday() == 5:
                            record.ot_category = "Thứ 7"
                        elif date_start.weekday() == 6 and date_end.weekday() == 6:
                            record.ot_category = "Chủ nhật"
                            if time_start > time(17, 30, 00) and time_end < time(23, 59, 59):
                                record.ot_category = "Ngày cuối tuần ban đêm"
                        else:
                            if (time_start >= time(6, 00, 00)) and (time_end <= time(8, 30, 00)):
                                record.ot_category = "OT ban ngày"
                            elif (time_start >= time(18, 30, 00)) and (time_end <= time(22, 00, 00)):
                                print("NGÀY BÌNH THƯỜNG")
                                record.ot_category = "Ngày bình thường"
                            elif time_start >= time(18, 30, 00) and time_end <= time(23, 59, 59) and time_end >= time(
                                    22, 00, 00):
                                record.ot_category = "Ngày bình thường - ban đêm"

                            else:
                                record.ot_category = "Không thể xác định"
                    elif start_ot.day == end_ot.day - 1:
                        
                        if (time_start >= time(18, 30, 00) and time_start <= time(23, 59, 59)) and (
                                time_end >= time(00, 00, 00) and time_end <= time(6, 00, 00)):
                            record.ot_category = "Ngày bình thường - ban đêm"

                        else:
                            record.ot_category = "Không thể xác định"
                    else:
                        record.ot_category = "Không thể xác định"
                   
            else:
                record.ot_category = "Không thể xác định"

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