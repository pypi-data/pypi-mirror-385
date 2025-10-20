"""BaSyx Server interface for REST API communication."""

import json
import logging
from pathlib import Path

from basyx.aas import model

from aas_http_client.client import AasHttpClient, _create_client
from aas_http_client.utilities.sdk_tools import convert_to_dict as _to_dict
from aas_http_client.utilities.sdk_tools import convert_to_object as _to_object

logger = logging.getLogger(__name__)


class SdkWrapper:
    """Represents a wrapper for the BaSyx Python SDK to communicate with a REST API."""

    _client: AasHttpClient = None
    base_url: str = ""

    def __init__(self, config_string: str, password: str = ""):
        """Initializes the wrapper with the given configuration.

        :param config_string: Configuration string for the BaSyx server connection.
        :param password: Password for the BaSyx server interface client, defaults to "".
        """
        client = _create_client(config_string, password)

        if not client:
            raise ValueError("Failed to create AAS HTTP client with the provided configuration.")

        self._client = client
        self.base_url = client.base_url

    # region shells

    def post_asset_administration_shell(self, aas: model.AssetAdministrationShell) -> model.AssetAdministrationShell | None:
        """Creates a new Asset Administration Shell.

        :param aas: Asset Administration Shell to post
        :return: Response data as a dictionary or None if an error occurred
        """
        aas_data = _to_dict(aas)
        content: dict = self._client.post_asset_administration_shell(aas_data)
        return _to_object(content)

    def put_asset_administration_shell_by_id(self, identifier: str, aas: model.AssetAdministrationShell) -> bool:
        """Creates or replaces an existing Asset Administration Shell.

        :param identifier: Identifier of the AAS to update
        :param aas: Asset Administration Shell data to update
        :return: True if the update was successful, False otherwise
        """
        aas_data = _to_dict(aas)
        return self._client.put_asset_administration_shell_by_id(identifier, aas_data)

    def put_submodel_by_id_aas_repository(self, aas_id: str, submodel_id: str, submodel: model.Submodel) -> bool:
        """Updates the Submodel.

        :param aas_id: ID of the AAS to update the submodel for
        :param submodel: Submodel data to update
        :return: True if the update was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.put_submodel_by_id_aas_repository(aas_id, submodel_id, sm_data)

    def get_all_asset_administration_shells(self) -> list[model.AssetAdministrationShell] | None:
        """Returns all Asset Administration Shells.

        :return: Asset Administration Shells objects or None if an error occurred
        """
        content: dict = self._client.get_all_asset_administration_shells()

        if not content:
            return None

        results: list = content.get("result", [])
        if not results:
            logger.warning("No shells found on server.")
            return []

        aas_list: list[model.AssetAdministrationShell] = []

        for result in results:
            if not isinstance(result, dict):
                logger.error(f"Invalid shell data: {result}")
                return None

            aas = _to_object(result)

            if aas:
                aas_list.append(aas)

        return aas_list

    def get_asset_administration_shell_by_id(self, aas_id: str) -> model.AssetAdministrationShell | None:
        """Returns a specific Asset Administration Shell.

        :param aas_id: ID of the AAS to retrieve
        :return: Asset Administration Shells object or None if an error occurred
        """
        content: dict = self._client.get_asset_administration_shell_by_id(aas_id)

        if not content:
            logger.warning(f"No shell found with ID '{aas_id}' on server.")
            return None

        return _to_object(content)

    def get_asset_administration_shell_by_id_reference_aas_repository(self, aas_id: str) -> model.Reference | None:
        """Returns a specific Asset Administration Shell as a Reference.

        :param aas_id: ID of the AAS reference to retrieve
        :return: Asset Administration Shells reference object or None if an error occurred
        """
        # workaround because serialization not working
        aas = self.get_asset_administration_shell_by_id(aas_id)
        return model.ModelReference.from_referable(aas)

        # content: dict = self._client.get_asset_administration_shell_by_id_reference_aas_repository(aas_id)
        # return _to_object(content)

    def get_submodel_by_id_aas_repository(self, aas_id: str, submodel_id: str) -> model.Submodel | None:
        """Returns the Submodel.

        :param aas_id: ID of the AAS to retrieve the submodel from
        :param submodel_id: ID of the submodel to retrieve
        :return: Submodel object or None if an error occurred
        """
        content: dict = self._client.get_submodel_by_id_aas_repository(aas_id, submodel_id)
        return _to_object(content)

    def delete_asset_administration_shell_by_id(self, aas_id: str) -> bool:
        """Deletes an Asset Administration Shell.

        :param aas_id: ID of the AAS to retrieve
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.delete_asset_administration_shell_by_id(aas_id)

    # endregion

    # region submodels

    def post_submodel(self, submodel: model.Submodel) -> model.Submodel | None:
        """Creates a new Submodel.

        :param submodel: submodel data as a dictionary
        :return: Response data as a dictionary or None if an error occurred
        """
        sm_data = _to_dict(submodel)
        content: dict = self._client.post_submodel(sm_data)
        return _to_object(content)

    def put_submodels_by_id(self, identifier: str, submodel: model.Submodel) -> bool:
        """Updates a existing Submodel.

        :param identifier: Identifier of the submodel to update
        :param submodel: Submodel data to update
        :return: True if the update was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.put_submodels_by_id(identifier, sm_data)

    def get_all_submodels(self) -> list[model.Submodel] | None:
        """Returns all Submodels.

        :return: Submodel objects or None if an error occurred
        """
        content: list = self._client.get_all_submodels()

        if not content:
            return []

        results: list = content.get("result", [])
        if not results:
            logger.warning("No submodels found on server.")
            return []

        submodels: list[model.Submodel] = []

        for result in results:
            if not isinstance(result, dict):
                logger.error(f"Invalid submodel data: {result}")
                return None

            submodel = _to_object(result)

            if submodel:
                submodels.append(submodel)

        return submodels

    def get_submodel_by_id(self, submodel_id: str) -> model.Submodel | None:
        """Returns a specific Submodel.

        :param submodel_id: ID of the submodel to retrieve
        :return: Submodel object or None if an error occurred
        """
        content = self._client.get_submodel_by_id(submodel_id)

        if not content:
            logger.warning(f"No submodel found with ID '{submodel_id}' on server.")
            return None

        return _to_object(content)

    def patch_submodel_by_id(self, submodel_id: str, submodel: model.Submodel):
        """Updates an existing Submodel.

        :param submodel_id: Encoded ID of the Submodel to delete
        :return: True if the patch was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.patch_submodel_by_id(submodel_id, sm_data)

    def delete_submodel_by_id(self, submodel_id: str) -> bool:
        """Deletes a Submodel.

        :param submodel_id: ID of the submodel to delete
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.delete_submodel_by_id(submodel_id)

    def get_all_submodel_elements_submodel_repository(
        self,
        submodel_id: str,
    ) -> list[model.SubmodelElement] | None:
        """Returns all submodel elements including their hierarchy. !!!Serialization to model.SubmodelElement currently not possible.

        :param submodel_id: Encoded ID of the Submodel to retrieve elements from
        :return: List of Submodel elements or None if an error occurred
        """
        content = self._client.get_all_submodel_elements_submodel_repository(submodel_id)

        if not content:
            return []

        results: list = content.get("result", [])
        if not results:
            logger.warning("No submodels found on server.")
            return []

        submodel_elements: list[model.SubmodelElement] = []

        for result in results:
            if not isinstance(result, dict):
                logger.error(f"Invalid submodel data: {result}")
                return None

            submodel_element = _to_object(result)

            if submodel_element:
                submodel_elements.append(submodel_element)

        return submodel_elements

    def post_submodel_element_submodel_repo(self, submodel_id: str, submodel_element: model.SubmodelElement) -> model.SubmodelElement | None:
        """Creates a new submodel element. !!!Serialization to model.SubmodelElements currently not possible.

        :param submodel_id: Encoded ID of the submodel to create elements for
        :param submodel_element: Submodel element to create
        :return: List of submodel element objects or None if an error occurred
        """
        sme_data = _to_dict(submodel_element)
        content: dict = self._client.post_submodel_element_submodel_repo(submodel_id, sme_data)
        return _to_object(content)

    def get_submodel_element_by_path_submodel_repo(self, submodel_id: str, submodel_element_path: str) -> model.SubmodelElement | None:
        """Returns a specific submodel element from the Submodel at a specified path.

        :param submodel_id: Encoded ID of the Submodel to retrieve element from
        :param submodel_element_path: Path of the Submodel element to retrieve
        :return: Submodel element object or None if an error occurred
        """
        content: dict = self._client.get_submodel_element_by_path_submodel_repo(submodel_id, submodel_element_path)
        print(content)
        return _to_object(content)

    def patch_submodel_element_by_path_value_only_submodel_repo(self, submodel_id: str, submodel_element_path: str, value: str) -> bool:
        """Updates the value of an existing SubmodelElement.

        :param submodel_id: Encoded ID of the Submodel to update submodel element for
        :param submodel_element_path: Path of the Submodel element to update
        :param value: Submodel element value to update as string
        :return: True if the patch was successful, False otherwise
        """
        return self._client.patch_submodel_element_by_path_value_only_submodel_repo(submodel_id, submodel_element_path, value)

    # endregion

    def get_client(self) -> AasHttpClient:
        """Returns the underlying AAS HTTP client.

        :return: The AAS HTTP client instance.
        """
        return self._client


# region wrapper


def create_wrapper_by_url(
    base_url: str,
    username: str = "",
    password: str = "",
    http_proxy: str = "",
    https_proxy: str = "",
    time_out: int = 200,
    connection_time_out: int = 60,
    ssl_verify: str = True,  # noqa: FBT002
    trust_env: bool = True,  # noqa: FBT001, FBT002
) -> SdkWrapper | None:
    """Create a wrapper for a AAS server connection from the given parameters.

    :param base_url: base URL of the BaSyx server, e.g. "http://basyx_python_server:80/"_
    :param username: username for the BaSyx server interface client, defaults to ""_
    :param password: password for the BaSyx server interface client, defaults to ""_
    :param http_proxy: http proxy URL, defaults to ""_
    :param https_proxy: https proxy URL, defaults to ""_
    :param time_out: timeout for the API calls, defaults to 200
    :param connection_time_out: timeout for the connection to the API, defaults to 60
    :param ssl_verify: whether to verify SSL certificates, defaults to True
    :param trust_env: Whether to trust environment variables for proxy settings, defaults to True
    :return: An instance of SdkWrapper initialized with the provided parameters.
    """
    logger.info(f"Create AAS server wrapper from URL '{base_url}'.")
    config_dict: dict[str, str] = {}
    config_dict["base_url"] = base_url
    config_dict["username"] = username
    config_dict["http_proxy"] = http_proxy
    config_dict["https_proxy"] = https_proxy
    config_dict["time_out"] = time_out
    config_dict["connection_time_out"] = connection_time_out
    config_dict["ssl_verify"] = ssl_verify
    config_dict["trust_env"] = trust_env
    return create_wrapper_by_dict(config_dict, password)


def create_wrapper_by_dict(configuration: dict, password: str = "") -> SdkWrapper | None:
    """Create a wrapper for a AAS server connection from the given configuration.

    :param config: Dictionary containing the BaSyx server connection settings.
    :param password: Password for the BaSyx server interface client, defaults to "".
    :return: An instance of SdkWrapper initialized with the provided parameters.
    """
    logger.info("Create AAS server wrapper from dictionary.")
    config_string = json.dumps(configuration, indent=4)
    return SdkWrapper(config_string, password)


def create_wrapper_by_config(config_file: Path, password: str = "") -> SdkWrapper | None:
    """Create a wrapper for a AAS server connection from a given configuration file.

    :param config_file: Path to the configuration file containing the BaSyx server connection settings.
    :param password: password for the BaSyx server interface client, defaults to ""_
    :return: An instance of SdkWrapper initialized with the provided parameters.
    """
    logger.info(f"Create AAS wrapper client from configuration file '{config_file}'.")
    if not config_file.exists():
        config_string = "{}"
        logger.warning(f"Configuration file '{config_file}' not found. Using default config.")
    else:
        config_string = config_file.read_text(encoding="utf-8")
        logger.debug(f"Configuration file '{config_file}' found.")
    return SdkWrapper(config_string, password)


# endregion
