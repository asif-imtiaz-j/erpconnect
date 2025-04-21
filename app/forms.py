from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField,
    FloatField, TextAreaField, BooleanField, DateField, HiddenField
)
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VendorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    contact_info = StringField('Contact Info')
    address = StringField('Address')
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive')])
    submit = SubmitField('Save')

class InvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    status = SelectField('Status', choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    category = StringField('Category', validators=[Optional()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    approved = BooleanField('Mark as Approved')
    submit = SubmitField('Save Invoice')

class InvoiceMessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class InvoiceAnnotationForm(FlaskForm):
    content = TextAreaField('Annotation', validators=[DataRequired()])
    submit = SubmitField('Add Note')

class VendorMessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class ReportBuilderForm(FlaskForm):
    export_type = SelectField('Export Format', choices=[('none', 'Display Only'), ('csv', 'CSV'), ('pdf', 'PDF'), ('xlsx', 'Excel')])
    include_tags = BooleanField('Include Tags')
    include_notes = BooleanField('Include Annotations')
    include_messages = BooleanField('Include Messages')
    status_filter = SelectField('Status Filter', choices=[('', 'All'), ('paid', 'Paid'), ('unpaid', 'Unpaid')])
    category_filter = StringField('Category Filter', validators=[Optional()])
    submit = SubmitField('Generate Report')
