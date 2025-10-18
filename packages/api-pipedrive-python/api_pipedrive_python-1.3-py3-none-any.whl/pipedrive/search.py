class MyDict(dict):
    def get_number(self, key):
        value = self.get(key)
        if value is None:
            return 0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0

class SearchItems(object):
    def __init__(self, client):
        self._client = client
        self.base_url = "https://api.pipedrive.com"
        self.data = self.search_term()
        self.persons = self.get_all_persons()
        
    def get_deal(self, deal_id, **kwargs):
        url = "deals/{}".format(deal_id)
        return self._client._get(self.base_url + url, **kwargs)
    
    def search_term(self, term, **kwargs):
        self.term = term
        url = f"/v1/itemSearch/web?strict_mode=True&term={term}&start=0"
        return self._client._get(self.base_url + url, **kwargs)


    def get_deals_by_person(self,id, **kwargs):
        url = f"/api/v1/persons/{id}/deals?start=0"
        result = self._client._get(self.base_url + url, **kwargs)

        if result['success']:
            return result['data']
        else:
            return []




    def get_all_persons(self):
        data = self.data
        persons_map = {}
        if data['success']:
            for entry in data['data']:
                if entry["item"]["type"] == "person":
                    person = entry["item"]
                    phones = person.get("phones",[])
                    phone_term = False
                    if phones:
                        for phone in phones:
                            if self.term in phone:
                                phone_term = True
                                break
                    if not phone_term:
                        continue
                    organization = (person.get("organization",{}).get("id") if person.get("organization",{}) else {})
                    deals = self.get_deals_by_person(person["id"])
                    if deals:

                        persons_map[person['id']] = {
                            "open":[],
                            "lost":[],
                            "won":[],
                            "deleted":[]
                        }
                        for deal in deals:
                            deal = MyDict(deal)
                            sdr = deal.get("e76364fa33cbe6838731ebeb22e66d66ce78b6e8")

                            dic_temp = {
                                "titulo":deal.get("title"),
                                "status":deal.get("status"),
                                "sdr":sdr,
                                "tem_sdr":bool(sdr),
                                "proprietario":deal.get("user_id"),
                                "produto":deal.get("65361ac9bebae4ea2dd64f702b2e51a6c5b41f65"),
                                "pessoa": person["name"],
                                "person_id": person["id"],
                                "organization_id":organization,
                                "has_organization": bool(organization),
                                "telefone": self.term,
                                "divida":deal.get_number("a0d93d57b615a84b923da8c5863fe63ece248731"),
                                "sd_rfb":deal.get_number("84c3ee5492c8c630f8bf05931a70c9ad4569f414"),
                                "sd_pgfn":deal.get_number("4f7e77dd589a6be3c2e1ead6ffbf8ec6e22f3bbb"),
                                "beneficio":deal.get_number("d7d14ed609e0a7c27ab1a6eb29f80674950616f3"),
                                "paga_mes":deal.get_number("2c74a476cb5e4a534ba8ce20d45b2832fe6274a3"),
                            }               
                            persons_map[person['id']][deal["status"]].append(dic_temp)
        return persons_map


