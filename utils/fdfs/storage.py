from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client


class FDFS_Storage(Storage):
    """自定义文件存储类"""
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        """保存文件使用"""

        # 创建fdfs client对象
        client = Fdfs_client('./utils/fdfs/client.conf')

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

    def exits(self, name):
        """Django判断文件名是否可用，可用才上传保存。"""
        return False