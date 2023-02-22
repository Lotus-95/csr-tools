import os
import stat
import requests
import json
from typing import List, Dict, Tuple
from .utils import download_file


class CsrCluster:
    cluster_host = {
        '2080ti': 'gz.csr-biotech.com:2080', # '192.168.0.170',
        'v100': 'gz.csr-biotech.com:3080', # '192.168.0.173'
    }
    base_url = 'http://{host_address}/rest-server/api/v1/'

    def __init__(self, username: str,
                 passwd: str,
                 cluster: str = '2080ti'):
        assert cluster in self.cluster_host, f'unknown cluster {cluster}'
        self.proxies = {
            'http': 'socks5://127.0.0.1:1080',
            'http': 'socks5://127.0.0.1:1080'
        }
        self.sess = requests.Session()
        # self.sess.proxies = self.proxies
        self.base_url = self.base_url.format(host_address=self.cluster_host[cluster])
        self.username = username

        self._login(username, passwd)

    def _login(self, username, passwd) -> bool:
        data = dict(username=username, password=passwd)
        api_url = os.path.join(self.base_url, 'token')
        ret = self.sess.post(api_url, data=data)
        ret.raise_for_status()

        token = json.loads(ret.content)['token']
        headers = self.sess.headers
        headers['Authorization'] = 'Bearer {token}'.format(
            token=token)
        headers['Cookie'] = 'user={username}; token={token}; admin=false'.format(
            username=username, token=token)
        # requests.utils.add_dict_to_cookiejar(self.sess.cookies, token)
        self.sess.headers = headers
        return ret.status_code == 200

    def get_user_info(self) -> Dict:
        api_url = os.path.join(self.base_url, 'user', 'me')
        ret = self.sess.get(api_url)
        ret.raise_for_status()
        user_info = json.loads(ret.content)
        return user_info

    def get_jobs_info(self) -> List:
        api_url = os.path.join(self.base_url, 'jobs')
        ret = self.sess.get(api_url)
        ret.raise_for_status()

        return json.loads(ret.content)

    def get_job_config_info(self, job_name: str) -> Dict:
        api_url = os.path.join(self.base_url, 'user',
                               self.username, 'jobs', job_name, 'config')
        ret = self.sess.get(api_url)
        ret.raise_for_status()

        return json.loads(ret.content)

    def submit_job(self, job_config_path: str) -> Dict:
        api_url = os.path.join(self.base_url, 'user',
                               self.username, 'jobs')
        headers = self.sess.headers.copy()
        headers['Content-Type'] = 'application/json'
        ret = self.sess.post(api_url, headers=headers, data=json.dumps(json.load(open(job_config_path, 'r'))))
        ret.encoding = ret.apparent_encoding
        return None if ret.status_code == 201 else ret.text

    def get_job_ssh_info(self, job_name: str) -> Dict:
        api_url = os.path.join(self.base_url, 'user',
                               self.username, 'jobs', job_name, 'ssh')
        ret = self.sess.get(api_url)
        ret.raise_for_status()

        return json.loads(ret.content)

    def get_job_host_port(self, job_name: str) -> Tuple:
        container = self.get_job_ssh_info(job_name)['containers'][0]
        return container['sshIp'], container['sshPort']

    def delete_job(self, job_name: str):
        api_url = os.path.join(self.base_url, 'user',
                               self.username, 'jobs', job_name)
        ret = self.sess.delete(api_url)
        ret.raise_for_status()
        return json.loads(ret.content)['message']

    def download_job_private_key(self, job_name: str, save_path: str = '') -> str:
        private_download_link = self.get_job_ssh_info(job_name)['keyPair']
        if not save_path:
            save_dir = os.path.join(os.environ['HOME'], '.csr')
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            save_path = private_download_link['privateKeyFileName']
            save_path = os.path.join(save_dir, 'private_keys', save_path)
            if not os.path.exists(os.path.join(save_dir, 'private_keys')):
                os.mkdir(os.path.join(save_dir, 'private_keys'))
        if os.path.exists(save_path):
            return save_path
        self._download(
            private_download_link['privateKeyDirectDownloadLink'], save_path)
        os.chmod(save_path, stat.S_IRUSR)
        return save_path
    
    def get_nfs_file(self, filename):
        api_url = os.path.join(self.base_url, 'nfs', self.username, 'file', filename)
        download_file(self.sess, api_url)

    def _download(self, file_url: str, save_path: str):
        ret = self.sess.get(file_url, proxies=self.proxies)
        ret.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(ret.content)

    def get_quota(self):
        api_url = os.path.join(self.base_url, 'user',
                               self.username, 'virtualGroups')
        
        r = self.sess.get(api_url)
        r.raise_for_status()
        return json.loads(r.content)