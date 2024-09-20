from office365.runtime.auth.authentication_context import ClientCredential
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext

from .utils import check_path_exists, create_folder, print_upload_progress

import os


class Client():
	def __init__(self, cid: str, csec: str, base_url: str):
		self.cid = cid
		self.csec = csec
		self.base_url = base_url

		credentials = ClientCredential(self.cid, self.csec)
		self.ctx = ClientContext(self.base_url).with_credentials(credentials)
	
	def upload_file(self, src: str, dst: str, check_dir: bool=True):
		try:
			if check_dir:
				dirs = [d for d in dst.split("/")[3:] if d]
				for i in range(len(dirs)):
					path = "/".join(dirs[:i+1])
					valid = check_path_exists(self.ctx, path)

					if valid is None:
						create_folder(self.ctx, path)

			target_folder = self.ctx.web.get_folder_by_server_relative_url(dst)
			response = target_folder.files.create_upload_session(
				src, 10000000, print_upload_progress
			)

			self.ctx.execute_query()
			print(f"[INFO] {response.serverRelativeUrl} Success uploaded")
		except Exception as e:
			print(f"[ERROR] Upload Failed")
			print(e)

	def upload_dir(self, src: str, dst: str):
		try:
			dirs = [d for d in dst.split("/")[3:] if d]
			for i in range(len(dirs)):
				path = "/".join(dirs[:i+1])
				valid = check_path_exists(self.ctx, path)

				if valid is None:
					create_folder(self.ctx, path)

			for file in os.listdir(src):
				path = '%s/%s' % (src, file)
				
				if os.path.isdir(path):
					ndir = f"{dst}/{file}"
					self.upload_dir(path, ndir)
				else:
					self.upload_file(path, dst, check_dir=False)
		except Exception as e:
			print(f"[ERROR] Upload failed")
			print(e)

	def download_file(self, src: str, dst: str):
		try:
			with open(dst, "wb") as f:
				file = self.ctx.web.get_file_by_server_relative_url(src)
				file.download(f)
				self.ctx.execute_query()
				print(f"[INFO] Download Success {src} => {dst}")
		except Exception as e:
			print(f"[ERROR] Download failed")
			print(e)

	def download_dir(self, src: str, dst: str):
		try:
			folder = self.ctx.web.get_folder_by_server_relative_url(src)
			files = folder.files
			folders = folder.folders

			os.makedirs(dst, exist_ok=True)

			self.ctx.load(files)
			self.ctx.load(folders)
			self.ctx.execute_query()

			for item in files:
				self.download_file(item.properties["ServerRelativeUrl"], os.path.join(dst, item.properties["Name"]))
			
			for item in folders:
				self.download_dir(item.properties["ServerRelativeUrl"], os.path.join(dst, item.properties["Name"]))
		except Exception as e:
			print(f"[ERROR] Donwload failed")
			print(e)
	
	def list_dir(self, src: str):
		try:
			result = []

			folder = self.ctx.web.get_folder_by_server_relative_url(src)
			files = folder.files
			folders = folder.folders

			self.ctx.load(files)
			self.ctx.load(folders)
			self.ctx.execute_query()

			for item in folders:
				result.append((item.properties["Name"], True))
			
			for item in files:
				result.append((item.properties["Name"], False))

		except Exception as e:
			print(e)
		
		return result