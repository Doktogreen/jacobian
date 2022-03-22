from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
import ssl
from users.models import Business, Individual, UserDetails
from .models import Customers, InvoiceItem, Journal, JournalEntry, Vendor, Product, Asset, Liability
from django.shortcuts import get_object_or_404
from .dict import CATEGORY_TYPES
from decimal import Decimal
from .serializers import (
    CustomerSerializer, JournalEntrySerializer, JournalSerializer, VendorSerializer, ProductSerializer, AssetSerializer,
    LiabilitySerializer, InvoiceSerializer, TemplateInvoiceSerializer)
from rest_framework import viewsets
from rest_framework.response import Response
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Account, Invoice
from .serializers import AccountSerializer
from decouple import config
from middleware.response import *

# from django.contrib.auth.models import User


# Create your views here.

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customers.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request):
        body = json.loads(request.body)
        user = UserDetails.objects.get(uuid=body['uuid'])
        del request.data['uuid']
        Customers.objects.create(user=user, **request.data)
        return Response({"message": "Customer created successfully"})

    def retrieve(self, req, pk):
        user = UserDetails.objects.get(uuid=pk)
        queryset = Customers.objects.filter(user=user).distinct()
        serializers = CustomerSerializer(queryset, many=True)
        return Response(serializers.data)


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def create(self, request):
        body = json.loads(request.body)
        user = UserDetails.objects.get(uuid=body['uuid'])
        del request.data['uuid']
        Vendor.objects.create(user=user, **request.data)
        return Response({"message": "Vendor created successfully"})

    def retrieve(self, req, pk):
        user = UserDetails.objects.get(uuid=pk)
        queryset = Vendor.objects.filter(user=user).distinct()
        serializers = VendorSerializer(queryset, many=True)
        return Response(serializers.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request):
        body = json.loads(request.body)
        user = UserDetails.objects.get(uuid=body['uuid'])
        del request.data['uuid']
        Product.objects.create(user=user, **request.data, type="Product")
        return Response({"message": "Product created successfully"})

    def list(self, req):
        user = UserDetails.objects.get(user=req.user)
        try:

            queryset = Product.objects.filter(user=user).filter(type="Product")
            serializers = ProductSerializer(queryset, many=True)
        except:
            return Response({"data": []})
        return Response(serializers.data)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().filter(type="Service")
    serializer_class = ProductSerializer

    def create(self, request):
        body = json.loads(request.body)
        user = UserDetails.objects.get(uuid=body['uuid'])
        del request.data['uuid']
        Product.objects.create(user=user, **request.data, type="Service")
        return Response({"message": "Service created successfully"})

    def list(self, req):
        user = UserDetails.objects.get(user=req.user)
        try:

            queryset = Product.objects.filter(user=user).filter(type="Service")
            serializers = ProductSerializer(queryset, many=True)
        except:
            return Response({"data": []})
        return Response(serializers.data)


class AssetViewSet(viewsets.ModelViewSet):
    # Pngme integration
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def create(self, request):
        body = json.loads(request.body)
        user = UserDetails.objects.get(uuid=body['uuid'])
        del request.data['uuid']
        Asset.objects.create(user=user, **request.data)
        return Response({"message": "Asset created successfully"})

    def list(self, req):
        user = UserDetails.objects.get(user=req.user)
        try:

            queryset = Asset.objects.filter(user=user).distinct()
            serializers = AssetSerializer(queryset, many=True)
        except:
            return Response({"data": []})
        return Response(serializers.data)


class LiabilityViewSet(viewsets.ModelViewSet):
    # Pngme integration
    queryset = Liability.objects.all()
    serializer_class = LiabilitySerializer

    def create(self, request):
        body = json.loads(request.body)
        user = UserDetails.objects.get(uuid=body['uuid'])
        del request.data['uuid']
        Liability.objects.create(user=user, **request.data)
        return Response({"message": "Liability created successfully"})

    def list(self, req):
        user = UserDetails.objects.get(user=req.user)
        try:

            queryset = Liability.objects.filter(user=user).distinct()
            serializers = LiabilitySerializer(queryset, many=True)
        except:
            return Response({"data": []})
        return Response(serializers.data)


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CreateAccount(request):
    if request.method == 'POST':
        user = request.user
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        account = Account.objects.create(
            user=user, type=data['type'], name=data['name'], category=data['category'], description=data['description'])
        account.save()
        response = AccountSerializer(account)
        return Response(response.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ListAccount(request):
    if request.method == 'GET':
        user = request.user
        if request.GET.get('category'):
            category = request.GET.get('category')
            instance = Account.objects.filter(
                user=user).filter(category=category)
            serializer = AccountSerializer(instance, many=True)
            return Response({"message": "user " + category.lower() + " accounts", "accounts": serializer.data})
        if request.GET.get('type'):
            type = request.GET.get('type')
            if type.isupper() is False:
                type = type.upper()
            if type in ['ASSET', 'INCOME', 'LIABILITY', 'EQUITY', 'EXPENSE']:
                instance = Account.objects.filter(
                    user=user).filter(type=type)
                serializer = AccountSerializer(instance, many=True)
                return Response({"message": "user " + type.lower() + " accounts", "accounts": serializer.data})
            else:
                return Response({"details": "Invalid account type"}, status=status.HTTP_400_BAD_REQUEST)
        if request.GET.get('id'):
            id = request.GET.get('id')
            instance = Account.objects.get(pk=id)
            serializer = AccountSerializer(instance)
            return Response({"message": id + " account", "account": serializer.data})
        instance = Account.objects.filter(user=user)
        serializer = AccountSerializer(instance, many=True)
        return Response({"message": "User Accounts", "accounts": serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def TypesCategory(request):
    return Response({"message": "Types Category", "data": CATEGORY_TYPES})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def DefaultAccount(request):
    if request.method == 'POST':
        user = request.user
        category = ['ASSET', 'INCOME', 'LIABILITY', 'EQUITY', 'EXPENSE']
        for i in range(len(category)):
            if category[i] == 'ASSET':
                account = Account.objects.create(
                    user=user, name='Cash in Bank', type=category[i],
                    category='Cash and Bank',
                    description="Cash you haven’t deposited in the bank. Add your bank and credit card accounts to accurately categorize transactions that aren't cash.")
                account2 = Account.objects.create(
                    user=user, name='Accounts Receivable', type=category[i],
                    category='Expected Payments from Customers', description='Account recievables')
                account3 = Account.objects.create(
                    user=user, name='Asset in store', type=category[i],
                    category='Inventory', description='asset in the store yet to be sold')
                account.save()
                account2.save()
                account3.save()
            elif category[i] == 'INCOME':
                account = Account.objects.create(
                    user=user, name='Sales', type=category[i],
                    category='Income',
                    description="Payments from your customers for products and services that your business sold.")
                account2 = Account.objects.create(
                    user=user, name='Uncategorized Income', type=category[i],
                    category='Uncategorized Income',
                    description="Income you haven't categorized yet. Categorize it now to keep your records accurate.")
                account3 = Account.objects.create(
                    user=user, name='Gain on Foreign Exchange', type=category[i],
                    category='Gain On Foreign Exchange',
                    description="Foreign exchange gains happen when the exchange rate between your business's home currency and a foreign currency transaction changes and results in a gain. This can happen in the time between a transaction being entered in Wave and being settled, for example, between when you send an invoice and when your customer pays it. This can affect foreign currency invoice payments, bill payments, or foreign currency held in your bank account.")
                account.save()
                account2.save()
                account3.save()
            elif category[i] == 'LIABILITY':
                account = Account.objects.create(
                    user=user, name='Accounts Payable', type=category[i],
                    category='Expected Payments to Vendors', description="Expected Payments to Vendors")
                account2 = Account.objects.create(
                    user=user, name='Uncategorized Income', type=category[i],
                    category='Uncategorized Income',
                    description="Income you haven't categorized yet. Categorize it now to keep your records accurate.")
                account3 = Account.objects.create(
                    user=user, name='Normal', type=category[i],
                    category='Sales Taxes', description="Taxes deducted from sales")
                account.save()
                account2.save()
                account3.save()
            elif category[i] == 'EQUITY':
                account = Account.objects.create(
                    user=user, name='Owner Investment / Drawings', type=category[i],
                    category='Business Owner Contribution and Drawing',
                    description="Owner investment represents the amount of money or assets you put into your business, either to start the business or keep it running. An owner's draw is a direct withdrawal from business cash or assets for your personal use.")
                account2 = Account.objects.create(
                    user=user, name="Owner's Equity", type=category[i],
                    category='Retained Earnings: Profit',
                    description="Income you haven't categorized yet. Categorize it now to keep your records accurate.")
                account3 = Account.objects.create(
                    user=user, name='Normal', type=category[i],
                    category='Sales Taxes',
                    description="Owner's equity is what remains after you subtract business liabilities from business assets. In other words, it's what's left over for you if you sell all your assets and pay all your debts.")
                account.save()
                account2.save()
                account3.save()
            elif category[i] == 'EXPENSE':
                account = Account.objects.create(
                    user=user, name='Accounting Fees', type=category[i],
                    category='Operating Expense', description="Accounting or bookkeeping services for your business.")
                account2 = Account.objects.create(
                    user=user, name="Bank Service Charges", type=category[i],
                    category='Operating Expense',
                    description="Fees you pay to your bank like transaction charges, monthly charges, and overdraft charges.")
                account3 = Account.objects.create(
                    user=user, name='Payroll – Employee Benefits', type=category[i],
                    category='Payroll Expense',
                    description="Federal and provincial/state deductions taken from an employee's pay, like employment insurance. These are usually described as line deductions on the pay stub.")
                account.save()
                account2.save()
                account3.save()
        account = Account.objects.filter(user=user)
        serializer = AccountSerializer(account, many=True)
        return Response(
            {"message": "Default Accounts Created", "data": serializer.data},
            status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_account(request, **kwargs):
    if request.method == 'POST':
        if request.POST['id']:
            partial = kwargs.pop('partial', False)
            id = request.POST.get('id')
            instance = Account.objects.get(pk=id)
            serializer = AccountSerializer(
                instance=instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Journal Successful"}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_journal(request):
    if request.method == 'POST':
        data = request.data
        user = request.user
        if type(data) != list:
            return Response({"detail": "Array expected"}, status=status.HTTP_400_BAD_REQUEST)

        journal = Journal.objects.create(user=user)
        total_credit = Decimal(0)
        total_debit = Decimal(0)
        for i in range(len(data)):
            id = data[i]['id']
            credit = data[i]['credit']
            debit = abs(data[i]['debit'])

            account = Account.objects.get(pk=id)
            if account.type == "ASSET":
                account.calculate_asset_balance(
                    credit=credit, debit=debit)
            elif account.type == "LIABILITY":
                account.calculate_liability_balance(
                    credit=credit, debit=debit)
            elif account.type == "INCOME":
                account.calculate_income_balance(
                    credit=credit, debit=debit)
            elif account.type == "EXPENSE":
                account.calculate_expense_balance(
                    credit=credit, debit=debit)
            elif account.type == "EQUITY":
                account.calculate_equity_balance(
                    credit=credit, debit=debit)
            journal_entry = JournalEntry(
                journal=journal, account=account, credit=Decimal(data[i]['credit']), debit=Decimal(data[i]['debit']))
            journal_entry.save()
            total_credit += Decimal(data[i]['credit'])
            total_debit += Decimal(data[i]['debit'])

        journal.total_credit = total_credit
        journal.total_debit = total_debit
        journal.save()
        serializer_journal = JournalSerializer(journal)
        entries = JournalEntry.objects.filter(journal=journal)
        serializer_entries = JournalEntrySerializer(entries, many=True)

        return Response(
            {"message": "Journal Successful",
             "data": {"journal": serializer_journal.data, "journal_entries": serializer_entries.data}},
            status=status.HTTP_200_OK)


@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def delete_journal(request, uuid):
    if request.method == "DELETE":
        journal = get_object_or_404(Journal, reference=uuid)
        journal.delete()
        return Response({"message": "journal deleted successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"details": "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_journal(request):
    if request.method == 'GET':
        user = request.user
        if request.GET.get('ref'):
            id = request.GET.get('ref')
            instance = Journal.objects.get(reference=id)
            entry = JournalEntry.objects.filter(journal=instance)
            serializer = JournalSerializer(instance)
            entry_serializer = JournalEntrySerializer(entry, many=True)
            return Response({"message": "journal details", "journal": serializer.data,
                             "journal_entries": entry_serializer.data})
        else:
            instance = Journal.objects.filter(user=user)
            serializer = JournalSerializer(instance, many=True)
            return Response({"message": "journal details", "journal": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CreateInvoice(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        customer = Customers.objects.get(id=data['customer'])
        invoice = Invoice.objects.create(
            user=user, title=data['title'], description=data['description'], customer=customer, tax=data['tax']
        )
        invoice.save()
        for item in data['products']:
            prod = Product.objects.get(id=item['product_id'])
            InvoiceItem.objects.create(
                inv_uuid=invoice, product=prod, quantity=item['quantity']
            )
        return Response({"message": "Invoice Created", "data": {
            "uuid": invoice.id}}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def getInvoice(request, uuid):
    if request.method == 'GET':
        invoice = Invoice.objects.get(id=uuid)
        user = UserDetails.objects.get(user=request.user)
        user_type = invoice.user.userdetails.account_type
        email = user.email
        phone = invoice.user.userdetails.phone
        if user_type == "Individual":
            ud = Individual.objects.get(user=user)
            address = ud.address
            state = ud.state
            name = user.first_name + " " + user.last_name
        else:
            ud = Business.objects.get(user=user)
            address = ud.office_address
            state = ud.state
            name = ud.company_name

        invoiceItems = InvoiceItem.objects.filter(inv_uuid=invoice).values()
        products = []
        for item in invoiceItems:
            productList = {}
            product = Product.objects.get(id=item['product_id'])
            productList['name'] = product.name
            productList['description'] = product.description
            productList['price'] = product.price
            productList['quantity'] = item['quantity']
            productList['total'] = product.price * item['quantity']
            products.append(productList)

        data = {
            "id": invoice.id,
            "userdetail_uuid": invoice.user.userdetails.uuid,
            'title': invoice.title,
            'description': invoice.description,
            "status": invoice.status,
            "paid": invoice.paid,
            "accepted": invoice.accepted,
            "customer_business": invoice.customer.business_name,
            "customer_firstname": invoice.customer.first_name,
            "customer_lastname": invoice.customer.last_name,
            "customer_email": invoice.customer.email,
            "customer_address": invoice.customer.billing_address,
            "customer_city": invoice.customer.billing_city,
            "customer_country": invoice.customer.billing_country,
            "products": products,
            "name": name,
            "address": address,
            "state": state,
            "user_email": email,
            "user_phone": phone
        }
        return Response({"data": data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getallInvoice(request):
    if request.method == 'GET':
        user = request.user
        invoice = Invoice.objects.filter(user=user)
        response = InvoiceSerializer(invoice, many=True)
        return Response({"data": response.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getallInvoice(request):
    if request.method == 'GET':
        user = request.user
        invoice = Invoice.objects.filter(user=user)
        response = InvoiceSerializer(invoice, many=True)
        return Response({"data": response.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_invoice(request):
    """ 
    endpoint to send invoice to users customer with email
    """
    user = request.user
    try:
        request.data['invoice_id']
    except KeyError:
        return Response({"message": "invoice_id required"}, status=status.HTTP_400_BAD_REQUEST)

    if request.data['invoice_id']:
        id = request.data['invoice_id']
        invoice = get_object_or_404(Invoice, id=id)
        mail_subject = "Invoice from " + invoice.user.first_name + " for Product Purchase"
        mail_html_contect = "<p>Hello " + invoice.customer.first_name + "," + "</p><p> Please follow the link below to accept and pay for invoice immediately or later. </p><p>https://app.simplefinance.ng/viewInvoice/" + \
            id + "</P><p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
        send_email(invoice.customer.email,
                   mail_subject, mail_html_contect)
        invoice.status = "Sent"
        invoice.save()
        return Response({"message": "invoice sent to "+invoice.customer.email+" with ID "+str(invoice.id)})
    else:
        return Response({"message": "invoice_id required"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_invoice(request):
    """ 
    endpoint to update invoice
    """
    try:
        request.data['invoice_id']
    except KeyError:
        return Response({"message": "invoice_id required"}, status=status.HTTP_400_BAD_REQUEST)

    if request.data['invoice_id']:
        id = request.data['invoice_id']
        invoice = get_object_or_404(Invoice, id=id)
        del request.data['invoice_id']
        serializer = TemplateInvoiceSerializer(
            instance=invoice, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if serializer.data['status'] == 'Accepted' and serializer.data['paid'] == True:
            mail_subject = "Invoice Confirmation for Product Purchase"
            mail_html_contect = "<p>Hello " + invoice.customer.first_name + "," + "</p><p> This is a confirmation mail for invoice acceptance and payment for invoice "+invoice.title+"</P><p>To view invoice please click on link </p> <p>https://app.simplefinance.ng/viewInvoice/" + id + \
                "</P><p>We value you and we have assigned an account officer to you. Account Officer: Kehinde Olabanji Email address: kehinde@simplefing.com. <p>Your account officer would always be there to help you throughout your SimpleFi journey.</p> Download the SimpleFi App from the Play Store to keep track of your loan. <p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
            send_email(invoice.customer.email,
                       mail_subject, mail_html_contect)
        if serializer.data['status'] == 'Accepted':
            mail_subject = "Invoice Confirmation for Product Purchase"
            mail_html_contect = "<p>Hello " + invoice.customer.first_name + "," + "</p><p> This is a confirmation mail for invoice acceptance for invoice "+invoice.title+"</P><p>To view invoice please click on link </p> <p>https://app.simplefinance.ng/viewInvoice/" + id + \
                "</P><p>We value you and we have assigned an account officer to you. Account Officer: Kehinde Olabanji Email address: kehinde@simplefing.com. <p>Your account officer would always be there to help you throughout your SimpleFi journey.</p> Download the SimpleFi App from the Play Store to keep track of your loan. <p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
            send_email(invoice.customer.email,
                       mail_subject, mail_html_contect)
        elif serializer.data['status'] == 'Declined':
            mail_subject = "Invoice Declined for Product Purchase"
            mail_html_contect = "<p>Hello " + invoice.customer.first_name + "," + "</p><p> This is a confirmation mail for declined invoice "+invoice.title + \
                "</P><p>We value you and we have assigned an account officer to you. Account Officer: Kehinde Olabanji Email address: kehinde@simplefing.com. <p>Your account officer would always be there to help you throughout your SimpleFi journey.</p> Download the SimpleFi App from the Play Store to keep track of your loan. <p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
            send_email(invoice.customer.email,
                       mail_subject, mail_html_contect)
        return Response({"message": "invoice updated"})
    else:
        return Response({"message": "invoice_id required"}, status=status.HTTP_400_BAD_REQUEST)


def send_email(email, subject, html_content):
    message = Mail(
        from_email="support@simplefinance.ng",
        to_emails=email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e)
