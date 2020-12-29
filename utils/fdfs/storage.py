from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFS_Storage(Storage):
    """自定义文件存储类"""

    def __init__(self, client_conf=None, base_url=None):
        """初始化"""

        if client_conf is None:
            # client_conf = './utils/fdfs/client.conf'
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            # base_url = 'http://192.168.1.17:8888'
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        """保存文件使用"""

        # 创建fdfs client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到fdfs中
        res = client.upload_by_buffer(content.read())

        """@return dict {
            'Group name'      : group_name,
            'Remote file_id'  : remote_file_id,
            'Status'          : 'Upload successed.',
            'Local file name' : '',
            'Uploaded size'   : upload_size,
            'Storage IP'      : storage_ip
        } """

        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到Fast DFS失败')

        filename = res.get('Remote file_id')
        return filename

    def exists(self, name):
        """Django判断文件名是否可用，可用才上传保存。"""
        return False

    def url(self, name):
        """访问返回文件的路径"""
        return self.base_url + name
