def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

bank_info = [
  {
    "name": "Access Bank",
    "slug": "access-bank",
    "code": "044",
    "ussd": "*901#"
  },
  {
    "name": "Access Bank (Diamond)",
    "slug": "access-bank-diamond",
    "code": "063",
    "ussd": "*426#"
  },
  {
    "name": "ALAT by WEMA",
    "slug": "alat-by-wema",
    "code": "035A",
    "ussd": "*945*100#"
  },
  {
    "name": "ASO Savings and Loans",
    "slug": "asosavings",
    "code": "401",
    "ussd": ""
  },
  {
    "name": "Bowen Microfinance Bank",
    "slug": "bowen-microfinance-bank",
    "code": "50931",
    "ussd": ""
  },
  {
    "name": "CEMCS Microfinance Bank",
    "slug": "cemcs-microfinance-bank",
    "code": "50823",
    "ussd": ""
  },
  {
    "name": "Citibank Nigeria",
    "slug": "citibank-nigeria",
    "code": "023",
    "ussd": ""
  },
  {
    "name": "Ecobank Nigeria",
    "slug": "ecobank-nigeria",
    "code": "050",
    "ussd": "*326#"
  },
  {
    "name": "Ekondo Microfinance Bank",
    "slug": "ekondo-microfinance-bank",
    "code": "562",
    "ussd": "*540*178#"
  },
  {
    "name": "Fidelity Bank",
    "slug": "fidelity-bank",
    "code": "070",
    "ussd": "*770#"
  },
  {
    "name": "First Bank of Nigeria",
    "slug": "first-bank-of-nigeria",
    "code": "011",
    "ussd": "*894#"
  },
  {
    "name": "First City Monument Bank",
    "slug": "first-city-monument-bank",
    "code": "214",
    "ussd": "*329#"
  },
  {
    "name": "Globus Bank",
    "slug": "globus-bank",
    "code": "00103",
    "ussd": "*989#"
  },
  {
    "name": "Guaranty Trust Bank",
    "slug": "guaranty-trust-bank",
    "code": "058",
    "ussd": "*737#"
  },
  {
    "name": "Hasal Microfinance Bank",
    "slug": "hasal-microfinance-bank",
    "code": "50383",
    "ussd": "*322*127#"
  },
  {
    "name": "Heritage Bank",
    "slug": "heritage-bank",
    "code": "030",
    "ussd": "*322#"
  },
  {
    "name": "Jaiz Bank",
    "slug": "jaiz-bank",
    "code": "301",
    "ussd": "*389*301#"
  },
  {
    "name": "Keystone Bank",
    "slug": "keystone-bank",
    "code": "082",
    "ussd": "*7111#"
  },
  {
    "name": "Kuda Bank",
    "slug": "kuda-bank",
    "code": "50211",
    "ussd": ""
  },
  {
    "name": "One Finance",
    "slug": "one-finance",
    "code": "565",
    "ussd": "*1303#"
  },
  {
    "name": "Parallex Bank",
    "slug": "parallex-bank",
    "code": "526",
    "ussd": "*322*318*0#"
  },
  {
    "name": "Polaris Bank",
    "slug": "polaris-bank",
    "code": "076",
    "ussd": "*833#"
  },
  {
    "name": "Providus Bank",
    "slug": "providus-bank",
    "code": "101",
    "ussd": ""
  },
  {
    "name": "Rubies MFB",
    "slug": "rubies-mfb",
    "code": "125",
    "ussd": "*7797#"
  },
  {
    "name": "Sparkle Microfinance Bank",
    "slug": "sparkle-microfinance-bank",
    "code": "51310",
    "ussd": ""
  },
  {
    "name": "Stanbic IBTC Bank",
    "slug": "stanbic-ibtc-bank",
    "code": "221",
    "ussd": "*909#"
  },
  {
    "name": "Standard Chartered Bank",
    "slug": "standard-chartered-bank",
    "code": "068",
    "ussd": ""
  },
  {
    "name": "Sterling Bank",
    "slug": "sterling-bank",
    "code": "232",
    "ussd": "*822#"
  },
  {
    "name": "Suntrust Bank",
    "slug": "suntrust-bank",
    "code": "100",
    "ussd": "*5230#"
  },
  {
    "name": "TAJ Bank",
    "slug": "taj-bank",
    "code": "302",
    "ussd": "*898#"
  },
  {
    "name": "TCF MFB",
    "slug": "tcf-mfb",
    "code": "51211",
    "ussd": "*908#"
  },
  {
    "name": "Titan Trust Bank",
    "slug": "titan-trust-bank",
    "code": "102",
    "ussd": "*922#"
  },
  {
    "name": "Union Bank of Nigeria",
    "slug": "union-bank-of-nigeria",
    "code": "032",
    "ussd": "*826#"
  },
  {
    "name": "United Bank For Africa",
    "slug": "united-bank-for-africa",
    "code": "033",
    "ussd": "*919#"
  },
  {
    "name": "Unity Bank",
    "slug": "unity-bank",
    "code": "215",
    "ussd": "*7799#"
  },
  {
    "name": "VFD",
    "slug": "vfd",
    "code": "566",
    "ussd": ""
  },
  {
    "name": "Wema Bank",
    "slug": "wema-bank",
    "code": "035",
    "ussd": "*945#"
  },
  {
    "name": "Zenith Bank",
    "slug": "zenith-bank",
    "code": "057",
    "ussd": "*966#"
  }
]


CARD_TERMINAL_TYPES = {
  "00": 'Administrative terminal',
  "01":'POS terminal',
  "02":'ATM',
  "03":'Home terminal',
  "04":'Electronic Cash Register (ECR)',
  "05":'Dial terminal',
  "06":'Travellers check machine',
  "07":'Fuel machine',
  "08":'Scrip machine',
  "09":'Coupon machine',
  "10":'Ticket machine',
  "11":'Point-of-Banking terminal',
  "12":'Teller',
  "13":'Franchise teller',
  "14":'Personal banking',
  "15":'Public utility',
  "16":'Vending',
  "17":'Self-service',
  "18":'Authorization',
  "19":'Payment',
  "20":'VRU',
  "21":'Smart phone',
  "22":'Interactive television',
  "23":'Personal digital assistant',
  "24":'Screen phone',
  "25":'Business banking',
  "90":'E-commerce - No encryption; no authentication',
  "91":'E-commerce - SET/3D-Secure encryption; cardholder certificate not used (non-authenticated)',
  "92":'E-commerce - SET/3D-Secure encryption; cardholder certificate used (authenticated)',
  "93":'E-commerce - SET encryption, chip cryptogram used; cardholder certificate not used',
  "94":'E-commerce - SET encryption, chip cryptogram used; cardholder certificate used',
  "95":'E-commerce - Channel encryption (SSL); cardholder certificate not used (non-authenticated)',
  "96":'E-commerce - Channel encryption (SSL); chip cryptogram used, cardholder certificate not used'
}
