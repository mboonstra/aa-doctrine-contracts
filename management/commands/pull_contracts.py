from django.core.management import BaseCommand
from esi.clients import EsiClientProvider
from esi.models import Token

from aadoctrinecontracts.models import Contract


class Command(BaseCommand):
    def handle(self, *args, **options):
        esi = EsiClientProvider()

        character_id = 2121819802  # character ID here references Ausaaki Kopori
        required_scopes = ["esi-contracts.read_corporation_contracts.v1"]

        # get a token
        token = Token.get_token(character_id, required_scopes)

        # call the endpoint
        # notifications = esi.client.Character.get_characters_character_id_notifications(
        #     # required parameter for endpoint
        #     character_id=character_id,
        #     # provide a valid access token, which wil be refresh the token if required
        #     token=token.valid_access_token()
        # ).results()

        access_token = token.valid_access_token()

        print("access token: " + access_token)

        corp_contracts = esi.client.Contracts.get_corporations_corporation_id_contracts(
            corporation_id=98664369, token=access_token  # corporation ID references Baozi-You-Rou.
        ).results()

        for contract in corp_contracts:
            if contract["assignee_id"] == 1727758877:  # assignee ID here references Northern Coalition.
                try:
                    created_contract = Contract.objects.get(id=str(contract["contract_id"]))
                    # print("Found contract in DB, updating...")
                except Contract.DoesNotExist:
                    created_contract = Contract(id=str(contract["contract_id"]))
                    print("Contract not in DB, created new contract with id " + str(created_contract.id))

                # set properties
                created_contract.contract_id = contract["contract_id"]
                created_contract.acceptor_id = contract["acceptor_id"]
                created_contract.assignee_id = contract["assignee_id"]
                created_contract.availability = contract["availability"]
                created_contract.collateral = contract["collateral"]
                created_contract.date_expired = contract["date_expired"]
                created_contract.date_issued = contract["date_issued"]
                created_contract.days_to_complete = contract["days_to_complete"]
                created_contract.end_location_id = contract["end_location_id"]
                created_contract.for_corporation = contract["for_corporation"]
                created_contract.issuer_id = contract["issuer_id"]
                created_contract.price = contract["price"]
                created_contract.reward = contract["reward"]
                created_contract.start_location_id = contract["start_location_id"]
                created_contract.status = contract["status"]
                created_contract.title = contract["title"]
                created_contract.contract_type = contract["type"]
                created_contract.volume = contract["volume"]
                created_contract.buyout = contract["buyout"]
                created_contract.date_accepted = contract["date_accepted"]
                created_contract.date_completed = contract["date_completed"]
                created_contract.issuer_corporation_id = contract["issuer_corporation_id"]

                # save
                print(
                    "Saving contract with ID "
                    + str(created_contract.contract_id)
                    + ' and description "'
                    + created_contract.title
                    + '"'
                )
                created_contract.save()

        print(len(corp_contracts))

        contract_names = {}
        for contract_name in list(Contract.objects.values_list("title", flat=True)):

            if contract_name not in contract_names.keys():
                contract_names.update({contract_name: 1})
            else:
                contract_names[contract_name] += 1
        print(contract_names)
