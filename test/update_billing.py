from master_api import update_billing_info
from management_database import User

def test_update_billing_info():
    user = User.get_by_email("bob@jones.mil")
    user.customer_id = '-1'
    user.subscription_id = '-1'
    user.save()
    info = {
        'first_name':'Bob',
        'last_name':'Jones',
        'addr1':'1234 Fast Lane',
        'addr2':'',
        'city':'San Francisco',
        'state':'CA',
        'zip':'94103',
        'expiration_month':'05',
        'expiration_year':'2015',
        'cc_number':'1',
        'cvv':'734'
    }
    
    assert (user.customer_id == '-1')
    assert (user.subscription_id == '-1')
    update_billing_info("bob@jones.mil", info)
    user = User.get_by_email("bob@jones.mil")
    assert (user.customer_id != '-1')
    assert (user.subscription_id != '-1')
    
