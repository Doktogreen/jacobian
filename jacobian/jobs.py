from account.models import Invoice
from account.views import send_email
from loan.models import Loan
from services.crm import get_loan_account_detail


def invoice_daily_reminder():
    invoice = Invoice.objects.all().filter(accepted=True)
    for invoice in invoice.iterator():
        #print(invoice.customer.email)
        id = invoice.id
        mail_subject = "Invoice Reminder for Product Purchase"
        mail_html_contect = "<p>Hello " + invoice.customer.first_name + "," + "</p><p> This is a reminder mail for invoice acceptance for invoice "+invoice.title+"</P><p>To Pay for invoice please click on link </p> <p>https://app.simplefinance.ng/api/invoice/" + str(id) + \
            "</P><p>We value you and we have assigned an account officer to you. Account Officer: Kehinde Olabanji Email address: kehinde@simplefing.com. <p>Your account officer would always be there to help you throughout your SimpleFi journey.</p> Download the SimpleFi App from the Play Store to keep track of your loan. <p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
        send_email(invoice.customer.email, mail_subject, mail_html_contect)
        return True

def checking_loan_status_on_crm():
    loan = Loan.objects.all().filter(status="pending")
    for loan in loan.iterator():
        loan_detail = get_loan_account_detail(loan.crm_loan_id)
        if loan_detail['status']['value'] == "Active":
            loan.status = "Approved"
            loan.save()
            

        
        