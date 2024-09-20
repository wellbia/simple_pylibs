import os
import paramiko
import stat


class Client:

    def __init__(self, host, username, password, port=22):
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def __del__(self):
        self.sftp.close()
        self.transport.close()

    def mkdir_p(self, remote_directory):
        dirs = remote_directory.split("/")
        path = ""
        for dir in dirs:
            if dir:
                path += "/" + dir
                try:
                    self.sftp.stat(path)
                except FileNotFoundError:
                    self.sftp.mkdir(path)

    def upload_dir_sftp(self, local_dir, remote_dir):
        try:
            self.sftp.mkdir(remote_dir)
        except IOError:
            pass

        for item in os.listdir(local_dir):
            local_item = os.path.join(local_dir, item)
            remote_item = remote_dir + "/" + item

            if os.path.isfile(local_item):
                self.sftp.put(local_item, remote_item)
            else:
                try:
                    self.sftp.mkdir(remote_item)
                except IOError:
                    pass
                self.upload_dir_sftp(local_item, remote_item)

    def upload_sftp(self, local_dir, remote_dir):
        self.mkdir_p(remote_dir)

        self.upload_dir_sftp(local_dir, remote_dir)

    def download_dir_sftp(self, remote_dir, local_dir):
        os.makedirs(local_dir, exist_ok=True)

        for item in self.sftp.listdir_attr(remote_dir):
            remote_item = remote_dir + "/" + item.filename
            local_item = os.path.join(local_dir, item.filename)

            if stat.S_ISDIR(item.st_mode):
                self.download_dir_sftp(remote_item, local_item)
            else:
                self.sftp.get(remote_item, local_item)

    def download_sftp(self, remote_dir, local_dir):
        self.download_dir_sftp(remote_dir, local_dir)

    def download(self, remote_dir, local_dir):
        self.download_sftp(remote_dir, local_dir)

    def upload(self, remote_dir, local_dir):
        self.upload_sftp(local_dir, remote_dir)
