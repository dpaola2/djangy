# Standard Python libraries
import datetime
# Djangy libraries installed in our virtualenv
from djangy_server_shared import * # referenced?
from management_database.models import User, AllocationChange, Chargable, BillingEvent, Subscription
# Libraries within this package
from devpayments import DevPayException
import exceptions, devpayments
import application_api

def update_billing_info(email, info):
    def _unpack_customer_info():
        return {
            'first_name':info.get('first_name', ''),
            'last_name':info.get('last_name', ''),
            'email':email
        }

    def _unpack_billing_info():
        return {
            'number':info['cc_number'],
            'exp_month':info['expiration_month'],
            'exp_year':info['expiration_year'],
            'cvc':info['cvv']
        }

    def _create_new_customer():
        devpay = devpayments.Client(DEVPAYMENTS_API_KEY)
        try:
            result = devpay.createCustomer(
                mnemonic = _unpack_customer_info()['email'],
                card = _unpack_billing_info()
            )
            user.customer_id = result.id
            user.save()
        except DevPayException as e:
            return e.message
        return True

    def _update_customer():
        devpay = devpayments.Client(DEVPAYMENTS_API_KEY)
        try:
            result = devpay.updateCustomer(
                id = user.customer_id,
                mnemonic = _unpack_customer_info()['email'],
                card = _unpack_billing_info()
            )
            user.customer_id = result.id
            user.save()
        except DevPayException as e:
            return e.message
        return True

    user = User.get_by_email(email)
    if not user:
        raise exceptions.UserNotFoundException(email)
    message = True
    if user.customer_id == '-1' or user.customer_id == '':
        try:
            result = _create_new_customer()
            if True != result:
                message = result
        except Exception as e:
            log_error_message(e)
            return "Our system encountered an error.  Please contact support@djangy.com."
    else:
        try:
            result = _update_customer()
            if True != result:
                message = result
        except Exception as e:
            log_error_message(e)
            return "Our system encountered an error.  Please contact support@djangy.com."

    try:
        cust_info = _unpack_customer_info()
        user.first_name = cust_info.get('first_name', '')
        user.last_name = cust_info.get('last_name', '')
        user.save()
    except Exception as e:
        log_error_message(e)
        return "Our system encountered an error.  Please contact support@djangy.com."
    return message

def retrieve_billing_info(user):
    customer_id = user.customer_id
    if customer_id == '-1' or customer_id == '':
        return None
    try:
        devpay = devpayments.Client(DEVPAYMENTS_API_KEY)
        result = devpay.retrieveCustomer(id=customer_id)
        last4 = result.active_card.get('last4', '')
        usage = ''
        try:
            usage = result.next_recurring_charge.get('amount', '')
        except:
            pass
        bill_date = ''
        try:
            bill_date = result.next_recurring_charge.get('date', '')
        except:
            pass
        if last4 != '':
            last4 = "**** **** **** %s" % last4
        return {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'cc_number':last4,
            'usage':usage,
            'bill_date':bill_date
        }
    except DevPayException as e:
        log_error_message(e.message)
        return None
    except Exception as e:
        log_error_message(e)
        return None

def report_all_usage():
    emails = [user.email for user in User.objects.all()]

    for email in emails:
        report_user_usage(email)

def report_user_usage(email):
    user = User.get_by_email(email)
    if not user:
        raise exceptions.UserNotFoundException(email)
    for application in user.application_set.all():
        changes = AllocationChange.objects.filter(application=application).filter(billed=False)
        if changes.count() < 1:
            continue
        log_info_message("for application %s, reporting %s changes" % (application, changes.count()))
        for chargable in Chargable.objects.all():
            total_seconds = 0.0
            total_cents = 0.0
            # only look at allocs from before one minute ago
            now = datetime.datetime.now() - datetime.timedelta(seconds=60)
            allocs = list(changes.filter(chargable=chargable).filter(timestamp__lt=now).order_by('-timestamp'))
            if len(allocs) < 1:
                continue
            latest = allocs[-1]
            latest_copy = AllocationChange(application = application, chargable = chargable, quantity = latest.quantity, timestamp = now)
            latest_copy.save()
            allocs.insert(0, latest_copy)
            for alloc in allocs:
                if alloc == latest_copy:
                    continue
                diff = (now - alloc.timestamp).seconds
                if chargable.component == Chargable.components['application_processes']:
                    # the (alloc.quantity - 1) is to ensure the first process is free
                    price = (diff * (alloc.quantity - 1) * (chargable.price / 3600.0))
                else:
                    price = (diff * (alloc.quantity) * (chargable.price / 3600.0))
                total_cents += price
                total_seconds += diff
                now = alloc.timestamp
                alloc.billed = True
            total_hours = (total_seconds / 3600) + 1
            result = report_usage(user, total_cents, memo="%s hours for %s" % (total_hours, chargable))
            if result:
                [alloc.save() for alloc in allocs]
                be = BillingEvent(
                    email = email,
                    customer_id = user.customer_id,
                    application_name = application.name,
                    chargable_name = str(chargable),
                    cents = total_cents,
                    success = True,
                    memo = "devpayments dump: %s" % str(result)
                )
                be.save()
                log_info_message("Reported %s cents for %s for application %s" % (total_cents, chargable, application.name))
            else:
                be = BillingEvent(
                    email = email,
                    customer_id = user.customer_id,
                    application_name = application.name,
                    chargable_name = str(chargable),
                    cents = total_cents,
                    success = False,
                    memo = "devpayments dump: %s" % str(result)
                )
                be.save()
                log_error_message("Reporting failed for %s cents for %s for application %s: %s" % (total_cents, chargable, application.name, result))

def report_usage(user, quantity, memo=""):
    devpay = devpayments.Client(DEVPAYMENTS_API_KEY)
    try:
        result = devpay.billCustomer(
            id = user.customer_id,
            amount = int(quantity),
            currency = 'usd'
        )
        return result
    except Exception as e:
        log_error_message(e)
        return False

def update_devpayments_subscription(user):
    total_cents = sum([sub.price for sub in user.get_active_subscriptions()])
    customer_id = user.customer_id

    devpay = devpayments.Client(DEVPAYMENTS_API_KEY)
    try:
        result = devpay.updateCustomer(
            id = user.customer_id,
            subscription = {
                'amount':total_cents,
                'per':'month',
                'currency':'usd'
            }
        )
        return result
    except Exception as e:
        log_error_message(e)
        return False
