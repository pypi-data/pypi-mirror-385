from saviialib.general_types.error_types.api.saviia_api_error_types import (
    SharePointFetchingError,
    SharePointDirectoryError,
    SharePointUploadError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import (
    EmptyDataError,
    FtpClientError,
    SharepointClientError,
)
from saviialib.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
    FtpListFilesArgs,
    FtpReadFileArgs,
)
from saviialib.libs.sharepoint_client import (
    SharepointClient,
    SharepointClientInitArgs,
    SpListFilesArgs,
    SpListFoldersArgs,
    SpUploadFileArgs,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs

from saviialib.libs.files_client import FilesClient, FilesClientInitArgs, WriteArgs
from saviialib.services.backup.use_cases.types import (
    FtpClientConfig,
    SharepointConfig,
    UpdateThiesDataUseCaseInput,
)
from saviialib.services.backup.utils import (
    parse_execute_response,
)
from saviialib.libs.zero_dependency.utils.datetime_utils import today, datetime_to_str
from .components.create_thies_statistics_file import create_thies_daily_statistics_file
from typing import Set, Dict, List


class UpdateThiesDataUseCase:
    def __init__(self, input: UpdateThiesDataUseCaseInput):
        self.sharepoint_client = self._initialize_sharepoint_client(
            input.sharepoint_config
        )
        self.logger = input.logger
        self.thies_ftp_client = self._initialize_thies_ftp_client(input.ftp_config)
        self.sharepoint_folders_path = input.sharepoint_folders_path
        self.ftp_server_folders_path = input.ftp_server_folders_path
        self.sharepoint_base_url = f"/sites/{self.sharepoint_client.site_name}"
        self.uploading = set()
        self.os_client = self._initialize_os_client()
        self.files_client = self._initialize_files_client()

    def _initialize_sharepoint_client(
        self, config: SharepointConfig
    ) -> SharepointClient:
        """Initialize the HTTP client."""
        try:
            return SharepointClient(
                SharepointClientInitArgs(config, client_name="sharepoint_rest_api")
            )
        except ConnectionError as error:
            raise SharepointClientError(error)

    def _initialize_thies_ftp_client(self, config: FtpClientConfig) -> FTPClient:
        """Initialize the FTP client."""
        try:
            return FTPClient(FtpClientInitArgs(config, client_name="ftplib_client"))
        except RuntimeError as error:
            raise FtpClientError(error)

    def _initialize_os_client(self) -> DirectoryClient:
        return DirectoryClient(DirectoryClientArgs(client_name="os_client"))

    def _initialize_files_client(self) -> FilesClient:
        return FilesClient(FilesClientInitArgs(client_name="aiofiles_client"))

    async def _validate_sharepoint_current_folders(self):
        async with self.sharepoint_client:
            folder_base_path = "/".join(
                self.sharepoint_folders_path[0].split("/")[0:-1]
            )
            relative_url = f"{self.sharepoint_base_url}/{folder_base_path}"
            response = await self.sharepoint_client.list_folders(
                SpListFoldersArgs(relative_url)
            )

        current_folders = [item["Name"] for item in response["value"]]  # type: ignore

        for folder_path in self.sharepoint_folders_path:
            folder_name = folder_path.split("/")[-1]
            if folder_name not in current_folders:
                raise SharePointDirectoryError(
                    reason=f"The current folder '{folder_name}' doesn't exist."
                )

    async def fetch_cloud_file_names(self) -> Set[str]:
        """Fetch file names from the RCER cloud."""
        await self._validate_sharepoint_current_folders()
        try:
            cloud_files = set()
            async with self.sharepoint_client:
                for folder_path in self.sharepoint_folders_path:
                    folder_name = folder_path.split("/")[-1]
                    relative_url = f"{self.sharepoint_base_url}/{folder_path}"
                    args = SpListFilesArgs(folder_relative_url=relative_url)
                    response = await self.sharepoint_client.list_files(args)
                    cloud_files.update(
                        {f"{folder_name}_{item['Name']}" for item in response["value"]}  # type: ignore
                    )
            return cloud_files
        except Exception as error:
            raise SharePointFetchingError(reason=error)

    async def fetch_thies_file_names(self) -> Set[str]:
        """Fetch file names from the THIES FTP server."""
        try:
            thies_files = set()
            for folder_path in self.ftp_server_folders_path:
                # AV for average, and EXT for extreme.
                prefix = "AVG" if "AV" in folder_path else "EXT"
                files = await self.thies_ftp_client.list_files(
                    FtpListFilesArgs(path=folder_path)
                )
                files_names = {f"{prefix}_{name}" for name in files}
                thies_files.update(files_names)
            return thies_files
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

    async def fetch_thies_file_content(self) -> Dict[str, bytes]:
        """Fetch the content of files from the THIES FTP server."""
        try:
            content_files = {}
            for file in self.uploading:
                prefix, filename = file.split("_", 1)
                # The first path is for AVG files. The second file is for EXT files
                folder_path = next(
                    (
                        path
                        for path in self.ftp_server_folders_path
                        if prefix == ("AVG" if "AV" in path else "EXT")
                    ),
                    self.ftp_server_folders_path[0],  # Default to the first path
                )
                file_path = f"{folder_path}/{filename}"
                content = await self.thies_ftp_client.read_file(
                    FtpReadFileArgs(file_path)
                )
                self.logger.debug(
                    "[thies_synchronization_lib] Fetching file '%s' from '%s'.",
                    file,
                    folder_path,
                )
                content_files[file] = (
                    content  # Save file content with its original name.
                )
            return content_files
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

    async def upload_thies_files_to_sharepoint(
        self, files: Dict
    ) -> Dict[str, List[str]]:
        """Upload files to SharePoint and categorize the results."""
        upload_results = {"failed_files": [], "new_files": []}

        async with self.sharepoint_client:
            for file, file_content in files.items():
                try:
                    origin, file_name = file.split("_", 1)
                    # Check if the first folder is for AVG, otherwise assume it's for EXT
                    if "AVG" in self.sharepoint_folders_path[0]:
                        avg_folder = self.sharepoint_folders_path[0]
                        ext_folder = self.sharepoint_folders_path[1]
                    else:
                        avg_folder = self.sharepoint_folders_path[1]
                        ext_folder = self.sharepoint_folders_path[0]

                    folder_path = avg_folder if origin == "AVG" else ext_folder

                    relative_url = f"{self.sharepoint_base_url}/{folder_path}"

                    args = SpUploadFileArgs(
                        folder_relative_url=relative_url,
                        file_content=file_content,
                        file_name=file_name,
                    )
                    await self.sharepoint_client.upload_file(args)
                    upload_results["new_files"].append(file)
                    self.logger.debug(
                        "[thies_synchronization_lib] File '%s' from '%s' uploaded successfully to '%s' ✅",
                        file_name,
                        folder_path,
                        relative_url,
                    )

                except ConnectionError as error:
                    self.logger.error(
                        "[thies_synchronization_lib] Unexpected error from with file '%s'",
                        file_name,
                    )
                    upload_results["failed_files"].append(
                        f"{file} (Error: {str(error)})"
                    )

        if upload_results["failed_files"]:
            raise SharePointUploadError(
                reason="Files failed to upload: "
                + ", ".join(upload_results["failed_files"])
            )

        return upload_results

    async def _sync_pending_files(self, thies_files: set, cloud_files: set) -> set:
        uploading = thies_files - cloud_files

        # Update content of the daily files
        daily_files = {
            prefix + datetime_to_str(today(), date_format="%Y%m%d") + ".BIN"
            for prefix in ["EXT_", "AVG_"]
        }
        for file in daily_files:
            if file in thies_files:
                uploading.add(file)

        return uploading

    async def _extract_thies_daily_statistics(self) -> None:
        # Create the folder thies-daily-files if doesnt exists
        self.logger.info("[thies_synchronization_lib] Creating Daily files directory")
        base_folder = "thies-daily-files"
        if not await self.os_client.isdir(base_folder):
            for dest_folder in {"ARCH_AV1", "ARCH_EX1"}:
                await self.os_client.makedirs(
                    self.os_client.join_paths(base_folder, dest_folder)
                )
        else:
            self.logger.info(
                "[thies_synchronization_lib] Thies daily files already exists"
            )

        # Read the daily files and save each data in the folder
        daily_files = [
            prefix + datetime_to_str(today(), date_format="%Y%m%d") + ".BIN"
            for prefix in ["AVG_", "EXT_"]
        ]
        # Receive from FTP server and  write the file in thies-daily-files
        for file in daily_files:
            prefix, filename = file.split("_", 1)
            # The first path is for AVG files. The second file is for EXT files
            folder_path = next(
                (
                    path
                    for path in self.ftp_server_folders_path
                    if prefix == ("AVG" if "AV" in path else "EXT")
                ),
                self.ftp_server_folders_path[0],  # Default to the first path
            )
            # Retrieve the AVG or EXT file
            file_path = f"{folder_path}/{filename}"
            try:
                content = await self.thies_ftp_client.read_file(
                    FtpReadFileArgs(file_path)
                )
            except FileNotFoundError as error:
                reason = (
                    str(error) + ". The file might not be available yet for statistics."
                )
                self.logger.warning("[thies_synchronization_lib] Warning: %s", reason)
                self.logger.warning(
                    "[thies_synchronization_lib] Skipping the creation of daily statistics %s",
                    filename,
                )
                return
            # Destination local folder
            self.logger.debug(file_path)

            dest_folder = "ARCH_AV1" if prefix == "AVG" else "ARCH_EX1"
            await self.files_client.write(
                WriteArgs(
                    file_name=filename,
                    file_content=content,
                    mode="wb",
                    destination_path=f"{base_folder}/{dest_folder}",
                )
            )
            # Retrieve the DESCFILE and save if is not in the base folder
            descfile_name = "DESCFILE.INI"
            if not await self.os_client.path_exists(
                self.os_client.join_paths(base_folder, dest_folder, descfile_name)
            ):
                descfile_path = f"{folder_path}/{descfile_name}"
                descfile_content = await self.thies_ftp_client.read_file(
                    FtpReadFileArgs(descfile_path)
                )
                await self.files_client.write(
                    WriteArgs(
                        file_name=descfile_name,
                        file_content=descfile_content,
                        mode="wb",
                        destination_path=f"{base_folder}/{dest_folder}",
                    )
                )
            else:
                self.logger.debug(
                    "[thies_synchronization_lib] DESCFILE.INI already exists in %s",
                    dest_folder,
                )
        # Read the files with ThiesDayData class
        await create_thies_daily_statistics_file(self.os_client, self.logger)

    async def execute(self):
        """Synchronize data from the THIES Center to the cloud."""
        self.logger.debug("[thies_synchronization_lib] Starting ...")
        try:
            thies_files = await self.fetch_thies_file_names()
        except RuntimeError as error:
            raise FtpClientError(error)
        self.logger.debug(
            "[thies_synchronization_lib] Total files fetched from THIES: %s",
            str(len(thies_files)),
        )
        try:
            cloud_files = await self.fetch_cloud_file_names()
        except RuntimeError as error:
            raise SharepointClient(error)  # type: ignore
        self.logger.debug(
            "[thies_synchronization_lib] Total files fetched from Sharepoint: %s",
            str(len(cloud_files)),
        )
        self.uploading = await self._sync_pending_files(thies_files, cloud_files)
        # Extract thies statistics for SAVIIA Sensors
        await self._extract_thies_daily_statistics()

        if not self.uploading:
            raise EmptyDataError(reason="No files to upload.")
        # Fetch the content of the files to be uploaded from THIES FTP Server
        thies_fetched_files = await self.fetch_thies_file_content()

        # Upload the fetched files to SharePoint and gather statistics
        upload_statistics = await self.upload_thies_files_to_sharepoint(
            thies_fetched_files
        )
        self.logger.info(upload_statistics)
        self.logger.debug(
            "[thies_synchronization_lib] All the files were uploaded successfully 🎉"
        )

        return parse_execute_response(thies_fetched_files, upload_statistics)  # type: ignore
