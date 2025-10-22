
from typing import Dict, List


class Router(object):

    def __init__(self, collection: str,
                 routes: List[Dict[str, str]] = []) -> None:
        self.collection_url = '/' + collection
        self.resource_url = self.collection_url + '/<id>'
        self.resource_enum_url = self.resource_url.replace('<id>', '<id1>')

        if routes:
            self._routes = [
                r for r in self.get_crud() if r['action'] in routes]
        else:
            self._routes = self.get_crud()

    def get_crud(self) -> List[Dict[str, str]]:
        return [
            {
                'action': 'create',
                'method': 'POST',
                'url': self.collection_url,
                'callback': 'create'
            },
            {
                'action': 'get',
                'method': 'GET',
                'url': self.resource_url,
                'callback': 'get'
            },
            {
                'action': 'list',
                'method': 'GET',
                'url': self.collection_url,
                'callback': 'list'
            },
            {
                'action': 'update',
                'method': 'PUT',
                'url': self.resource_url,
                'callback': 'update'
            },
            {
                'action': 'delete',
                'method': 'DELETE',
                'url': self.resource_url,
                'callback': 'delete'
            },
            {
                'action': 'activate or deactivate multiple entities',
                'method': 'POST',
                'url': self.collection_url + '/activate_or_deactivate',
                'callback': 'activate_or_deactivate_multiple_entities'
            },
            {
                'action': 'Export data in XLSX',
                'method': 'POST',
                'url': self.collection_url + '/export_xlsx',
                'callback': 'export_xlsx'
            },
            {
                'action': 'Export data in PDF',
                'method': 'POST',
                'url': self.collection_url + '/export_pdf',
                'callback': 'export_pdf'
            },
            {
                'action': 'aplica o filtro na listagem pelo json',
                'method': 'POST',
                'url': self.collection_url + '/filtra_json',
                'callback': 'list_filtra_json'
            },
        ]

    @property
    def routes(self) -> List[Dict[str, str]]:
        return self._routes
