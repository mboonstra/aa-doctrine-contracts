import logging

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from esi.decorators import token_required

from aadoctrinecontracts.models import Contract
from fittings.models import Fitting


# Create your views here.


def index(request):

    fittings = Fitting.objects.all()
    fit_id_dict = {}
    for fit in fittings:
        fit_id_dict.update({fit.id: "{} ({})".format(fit.name, fit.ship_type.name)})

    result = Contract.objects.all().values('matched_fitting').annotate(amount=Count('matched_fitting'))

    result_list = list()
    for contract_entry in result:
        if contract_entry.get("matched_fitting") in fit_id_dict.keys():
            result_list.append({"fit": fit_id_dict.get(contract_entry.get("matched_fitting")), "amount": contract_entry.get("amount")})

    return render(request, "doctrinecontracts/index.html", {
        'doctrines_availability': result_list
    })


@token_required(scopes="esi-contracts.read_corporation_contracts.v1")
def update_scopes(request, token):
    return HttpResponse("Updated scopes to include corporation contracts!")
