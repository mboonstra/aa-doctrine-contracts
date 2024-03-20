import time

import bravado.exception
from django.core.management import BaseCommand
from esi.clients import EsiClientProvider
from esi.models import Token
from aadoctrinecontracts.models import Contract
from fittings.models import Fitting, FittingItem


class Command(BaseCommand):
    def handle(self, *args, **options):

        esi = EsiClientProvider()
        character_id = 2121819802  # character ID here references Ausaaki Kopori
        required_scopes = ["esi-contracts.read_corporation_contracts.v1"]
        token = Token.get_token(character_id, required_scopes)

        # First, loop over all fits & their contents
        fits = {}
        alliance_fits = Fitting.objects.all()
        for fit in alliance_fits:
            fitting_items = FittingItem.objects.filter(fit=fit)
            fit_dict = {}
            for item in fitting_items:
                fit_dict.update(
                    {item.type_id: item.quantity + (
                        fit_dict.get(item.type_id) if item.type_id in fit_dict.keys() else 0)}
                )
            fits.update({fit.id: fit_dict})

        access_token = token.valid_access_token()
        print(access_token)

        contracts = {}

        contract_ids = list()
        existing_contracts = Contract.objects.all()
        for contract in existing_contracts:
            if contract.status == "outstanding" and contract.contract_type == "item_exchange" and contract.matched_fitting is None:
                contract_ids.append(contract.contract_id)
                # DEBUGGING
                # if len(contract_ids) > 4:
                #     break

        print(len(contract_ids))
        i = 0
        for contract_id in contract_ids:
            print(str(i).ljust(3) + "/" + str(len(contract_ids)))
            contract_items = {}
            try:
                contract_contents = esi.client.Contracts.get_corporations_corporation_id_contracts_contract_id_items(
                    corporation_id=98664369,  # corporation ID references Baozi-You-Rou.
                    contract_id=contract_id,
                    token=access_token
                ).results()
                for entry in contract_contents:
                    contract_items.update(
                        {entry['type_id']: entry['quantity'] + (contract_items.get(entry['type_id']) if
                                                                entry['type_id'] in contract_items.keys() else 0)})
                contracts.update({contract_id: contract_items})
            except bravado.exception.HTTPNotFound:
                print("Contract not found, skipping.")
            i += 1
            time.sleep(0.5)

        for contract_id in contracts:
            for fit_id in fits:
                if fits.get(fit_id).items() <= contracts.get(contract_id).items():
                    print("Matched contract to fit '" + str(fit_id) + "'!")
                    # print("Fit id: " + str(fit_id))
                    # print("Contract id: " + str(contract_id))
                    contract_to_update = Contract.objects.get(id=str(contract_id))
                    # print(contract_to_update)
                    contract_to_update.matched_fitting = Fitting.objects.get(id=str(fit_id))
                    contract_to_update.save()
                    break
