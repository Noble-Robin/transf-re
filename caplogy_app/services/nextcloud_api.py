import requests
import os
from urllib.parse import quote
from xml.etree import ElementTree as ET
from urllib.parse import unquote

class NextcloudAPI:
    def __init__(self, base_url: str, share_url: str, user: str, password: str):
        self.webdav = base_url
        self.share = share_url
        self.auth = (user, password)

    def list_nc_dir(self, path):
        # S'assurer que le chemin commence par /Shared/Biblio_Cours_Caplogy
        biblio_path = '/Shared/Biblio_Cours_Caplogy'
        if not path.startswith(biblio_path):
            if path.startswith('/'):
                path = biblio_path + path
            else:
                path = biblio_path + '/' + path
        try:
            url = self.webdav + path
            print(f"[NextcloudAPI] URL construite: {url}")
            print(f"[NextcloudAPI] Auth user: {self.auth[0]}")
            
            headers = {'Depth': '1'}
            print(f"[NextcloudAPI] Envoi de la requête PROPFIND...")
            
            resp = requests.request('PROPFIND', url, auth=self.auth, headers=headers, verify=False)
            print(f"[NextcloudAPI] Status code: {resp.status_code}")
            
            if resp.status_code != 207:
                print(f"[NextcloudAPI] Réponse inattendue: {resp.text}")
                resp.raise_for_status()
            
            print(f"[NextcloudAPI] Parsing XML response...")
            tree = ET.fromstring(resp.content)
            ns = {'d': 'DAV:'}
            current = path.rstrip('/')
            folders, files = [], []
            
            print(f"[NextcloudAPI] Traitement des éléments XML...")
            for resp_elem in tree.findall('d:response', ns):
                href = resp_elem.find('d:href', ns).text
                if href.endswith(current):
                    continue
                prop = resp_elem.find('d:propstat/d:prop', ns)
                is_collection = prop.find('d:resourcetype/d:collection', ns) is not None
                name = unquote(os.path.basename(href.rstrip('/')))
                if is_collection:
                    folders.append(name)
                else:
                    files.append(name)
            
            print(f"[NextcloudAPI] Résultat: {len(folders)} dossiers, {len(files)} fichiers")
            return folders, files
            
        except Exception as e:
            print(f"[NextcloudAPI ERROR] Erreur dans list_nc_dir: {str(e)}")
            import traceback
            print(f"[NextcloudAPI ERROR] Traceback: {traceback.format_exc()}")
            raise

    def upload_file_nextcloud(self, local_path, remote_dir):
        filename = os.path.basename(local_path)
        remote_path = remote_dir.rstrip('/') + '/' + quote(filename)
        url = self.webdav + remote_path
        with open(local_path, 'rb') as f:
            r = requests.put(url, auth=self.auth, data=f, verify=False)
        r.raise_for_status()
        return remote_path
    
    def share_file_nextcloud(self, path):
        if not path.startswith('/'):
            path = f"/{path}"
        headers = {'OCS-APIRequest': 'true', 'Accept': 'application/xml'}
        data = {'path': path, 'shareType': 3, 'permissions': 1}
        resp = requests.post(self.share, headers=headers, data=data, auth=self.auth, verify=False)
        resp.raise_for_status()
        tree = ET.fromstring(resp.text)
        return tree.find('.//url').text
    
    def get_share_url(self, file_path):
        """Génère une URL de partage Nextcloud pour un fichier donné"""
        try:
            # S'assurer que le chemin commence par /Shared/Biblio_Cours_Caplogy
            biblio_path = '/Shared/Biblio_Cours_Caplogy'
            if not file_path.startswith(biblio_path):
                if file_path.startswith('/'):
                    file_path = biblio_path + file_path
                else:
                    file_path = biblio_path + '/' + file_path
            
            return self.share_file_nextcloud(file_path)
        except Exception as e:
            print(f"Erreur lors de la génération de l'URL de partage pour {file_path}: {e}")
            return None
