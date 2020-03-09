from django.http import HttpResponse
from django.template import loader
from django.shortcuts import Http404
from django.utils.dates import MONTHS

from constance import config

from prolife.core.models import Order
from prolife.utils import get_formatted_report


def sales(request):
    if request.user.is_superuser:
        YEAR = config.YEAR

        raw_sales_rep_report = Order.get_dispatched_order_in_year_by_sales_rep(YEAR)
        sales_rep_report = get_formatted_report(raw_sales_rep_report)

        raw_customers_report = Order.get_dispatched_order_in_year_by_customers(YEAR)
        customers_report = get_formatted_report(raw_customers_report)
        customers_report = {k: v for k, v in sorted(customers_report.items(), key=lambda kv:sum(kv[1].values()), reverse=True)}

        context = {
            'sales_rep_report': sales_rep_report,
            'customers_report': customers_report,
            'custom_html': config.CUSTOM_HTML,
            'months': MONTHS,
            'has_permission': True,
        }

        template = loader.get_template('core/report/sales.html')

        return HttpResponse(template.render(context, request))
    else:
        raise Http404("You are not authorized to access this page")
