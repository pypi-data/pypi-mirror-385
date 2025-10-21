from datetime import datetime, timedelta
from time import sleep
from typing import Optional

import requests

from mlops_codex.__model_states import ModelExecutionState
from mlops_codex.__utils import (
    parse_json_to_yaml,
    parse_url,
)
from mlops_codex.exceptions import (
    AuthenticationError,
    ExecutionError,
    GroupError,
    InputError,
    ModelError,
    ServerError,
)
from mlops_codex.http_request_handler import refresh_token, try_login
from mlops_codex.logger_config import get_logger
from mlops_codex.shared.utils import check_lib_version

logger = get_logger()


class BaseMLOps:
    """
    Super base class to initialize other variables and URLs for other MLOps classes.
    """

    def __init__(
        self,
        *,
        login: str,
        password: str,
        tenant: str
    ) -> None:

        check_lib_version()

        self.credentials = (login, password, tenant)
        self.base_url = "https://neomaril.datarisk.net/"
        self.base_url = parse_url(self.base_url)

        self.user_token, self.version = try_login(
            self.credentials[0],
            self.credentials[1],
            self.credentials[2],
            self.base_url,
        )
        logger.info("Successfully connected to MLOps")

    def _logs(
        self,
        *,
        url,
        credentials,
        start: Optional[str] = None,
        end: Optional[str] = None,
        routine: Optional[str] = None,
        type: Optional[str] = None,
    ):
        if not start and not end:
            end = datetime.today().strftime("%d-%m-%Y")
            start = (datetime.today() - timedelta(days=6)).strftime("%d-%m-%Y")

        if not start and end:
            start = (datetime.strptime(end, "%d-%m-%Y") - timedelta(days=6)).strftime(
                "%d-%m-%Y"
            )

        if start and not end:
            end = (datetime.strptime(start, "%d-%m-%Y") + timedelta(days=6)).strftime(
                "%d-%m-%Y"
            )

        query = {"start": start, "end": end}

        if routine:
            assert routine in ["Run", "Host"]
            query["routine"] = routine

        if type:
            assert type in ["Ok", "Error", "Debug", "Warning"]
            query["type"] = type

        response = requests.get(
            url,
            params=query,
            headers={
                "Authorization": "Bearer " + refresh_token(*credentials, self.base_url)
            },
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            logger.error(
                "Login or password are invalid, please check your credentials."
            )
            raise AuthenticationError("Login not authorized.")

        if response.status_code >= 500:
            logger.error("Server is not available. Please, try it later.")
            raise ServerError("Server is not available!")

        logger.error(response.text)
        raise InputError("Bad Input. Client error")


class BaseMLOpsClient(BaseMLOps):
    """
    Base class for MLOps client side related classes. This is the class that contains some methods related to Client models administration.
    Mainly related to initialize environment and its variables, but also to generate groups.
    A group is a way to organize models clustering for different users and also to increase security.
    Each group has a unique token that should be used to run the models that belongs to that.

    Parameters
    ----------
    login: str
        Login for authenticating with the client. You can also use the env variable MLOPS_USER to set this
    password: str
        Password for authenticating with the client. You can also use the env variable MLOPS_PASSWORD to set this

    Raises
    ------
    NotImplementedError
        When the environment is production, because it is not implemented yet

    Example
    -------
    In this example you can see how to create a group and after consult the list of groups that already exists.

    .. code-block:: python

        from mlops_codex.base import BaseMLOpsClient

        def start_group(password):
            client = BaseMLOpsClient(password)
            isCreated = client.create_group('ex_group', 'Group for example purpose')

            print(client.list_groups())

            return isCreated
    """

    def list_groups(self) -> list:
        """
        List all existing groups.

        Raises
        ------
        ServerError
            Unexpected server error

        Returns
        -------
        list
            Return groups that exists in the database
        """

        url = f"{self.base_url}/groups"

        token = refresh_token(*self.credentials, self.base_url)

        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + token,
                "Neomaril-Origin": "Codex",
                "Neomaril-Method": self.list_groups.__qualname__,
            },
        )

        if response.status_code == 200:
            results = response.json()["Results"]
            return results

        formatted_msg = parse_json_to_yaml(response.json())

        if response.status_code == 401:
            logger.error(
                "Login or password are invalid, please check your credentials."
            )
            raise AuthenticationError("Login not authorized.")

        if response.status_code >= 500:
            logger.error("Server is not available. Please, try it later.")
            raise ServerError("Server is not available!")

        logger.error(f"Something went wrong...\n{formatted_msg}")
        raise InputError("Bad Input. Client error")

    def create_group(self, *, name: str, description: str) -> str:
        """
        Create a group for multiple models of the same final client at the end if it returns TRUE, a message with the token for that group will be returned as a INFO message.
        You should keep this token information to be able to run the model of that group afterward.

        Parameters
        ----------
        name: str
            Name of the group. Must be 32 characters long and with no special characters (some parsing will be made)
        description: str
            Short description of the group

        Raises
        ------
        AuthenticationError
            Raised if there is an authentication issue.
        GroupError
            Raised if there is an error related to the group.
        ServerError
            Raised if the server encounters an issue.

        Returns
        -------
        str
            Returns the group token
        """
        data = {"name": name, "description": description}

        url = f"{self.base_url}/groups"
        token = refresh_token(*self.credentials, self.base_url)

        response = requests.post(
            url,
            data=data,
            headers={
                "Authorization": "Bearer " + token,
                "Neomaril-Origin": "Codex",
                "Neomaril-Method": self.create_group.__qualname__,
            },
        )

        if response.status_code == 201:
            t = response.json().get("Token")
            logger.info(
                f"Group '{name}' inserted. Use the token for scoring. Carefully save it as we won't show it again."
            )
            return t

        formatted_msg = parse_json_to_yaml(response.json())

        if response.status_code == 409:
            logger.error(f"Something went wrong:\n {formatted_msg}")
            raise GroupError("Group already exist, nothing was changed.")

        if response.status_code == 401:
            logger.error(
                "Login or password are invalid, please check your credentials."
            )
            raise AuthenticationError("Login not authorized.")

        if response.status_code >= 500:
            logger.error("Server is not available. Please, try it later.")
            raise ServerError("Server is not available!")

        logger.error(f"Something went wrong:\n {formatted_msg}")
        raise InputError("Bad Input. Client error")

    def refresh_group_token(self, *, name: str, force: bool = False) -> str:
        """
        Refresh the group token. If the token it's still valid it won't be changed, unless you use parameter force = True.
        At the end a message with the token for that group will be returned as a INFO message.
        You should keep this new token information to be able to run the model of that group afterward.

        Parameters
        ---------
        name: str
            Name of the group to have the token refreshed
        force: bool
            Force token expiration even if it's still valid (this can make multiple models integrations stop working, so use with care)

        Raises
        ------
        AuthenticationError
            Raised if there is an authentication issue.
        GroupError
            Raised if there is an error related to the group.
        ServerError
            Raised if the server encounters an issue.
        InputError
            Something went wrong in the input

        Returns
        -------
        str
            Returns group token.

        Example
        --------
        Suppose that you lost the token to access your group, you can create a new one forcing it with this method as at the example below.

        .. code-block:: python

            from mlops_codex.base import BaseMLOpsClient

            def update_group_token(model_client, group_name):
                model_client.refresh_group_token('ex_group', True)
                print(client.list_groups())

                return isCreated
        """

        url = f"{self.base_url}/groups/refresh/{name}"
        token = refresh_token(*self.credentials, self.base_url)

        response = requests.get(
            url,
            params={"force": str(force).lower()},
            headers={
                "Authorization": "Bearer " + token,
                "Neomaril-Origin": "Codex",
                "Neomaril-Method": self.refresh_group_token.__qualname__,
            },
        )

        if response.status_code == 201:
            t = response.json()["Token"]
            logger.info(f"Group '{name}' was refreshed.")
            return t

        formatted_msg = parse_json_to_yaml(response.json())

        if response.status_code == 401:
            logger.error(
                "Login or password are invalid, please check your credentials."
            )
            raise AuthenticationError("Login not authorized.")

        if response.status_code >= 500:
            logger.error("Server is not available. Please, try it later.")
            raise ServerError("Server is not available!")

        logger.error(f"Something went wrong...\n{formatted_msg}")
        raise InputError("Bad Input. Client error")


class MLOpsExecution(BaseMLOps):
    """
    Base class for MLOps asynchronous model executions. With this class you can visualize the status of an execution and download the results after and execution has finished.

    Parameters
    ----------
    parent_id: str
        Model id (hash) from the model you want to access
    exec_type: str
        Flag that contains which type of execution you use. It can be 'AsyncModel' or 'Training'
    group: Optional[str], optional
        Group the model is inserted
    exec_id: Optional[str], optional
        Execution id
    login: Optional[str], optional
        Login for authenticating with the client. You can also use the env variable MLOPS_USER to set this
    password: Optional[str], optional
        Password for authenticating with the client. You can also use the env variable MLOPS_PASSWORD to set this

    Raises
    ------
    InputError
        Invalid execution type
    ModelError
        If the execution id was not found or wasn't possible to retrieve it

    Example
    -------
    In this example you can see how to get the status of an existing execution and download its results

    .. code-block:: python

        from mlops_codex.base import MLOpsExecution
        from mlops_codex.model import MLOpsModelClient

        def get_execution_status(password, data_path):
            client = BaseMLOpsClient(password)
            model = client.create_model('Example notebook Async',
                                'score',
                                data_path+'app.py',
                                data_path+'model.pkl',
                                data_path+'requirements.txt',
                                python_version='3.9',
                                operation="Async",
                                input_type='csv'
                                )

            execution = model.predict(data_path+'input.csv')

            execution.get_status()

            execution.download_result()
    """

    def __init__(
        self,
        *,
        login: str,
        password: str,
        tenant: str,
        parent_id: str,
        exec_type: str,
        group: Optional[str] = None,
        exec_id: Optional[str] = None,
        group_token: Optional[str] = None,
    ) -> None:
        super().__init__(login=login, password=password, tenant=tenant)

        self.exec_type = exec_type
        self.exec_id = exec_id
        self.status = ModelExecutionState.Requested
        self.group = group
        self.__token = group_token

        if exec_type == "AsyncModel":
            self.__url_path = "model/async"
        elif exec_type == "Training":
            self.__url_path = "training"
        elif exec_type == "AsyncPreprocessing":
            self.__url_path = "preprocessing/async"
        else:
            raise InputError(
                f"Invalid execution type '{exec_type}'. Valid options are 'AsyncModel' and 'Training'"
            )

        if exec_type == "AsyncPreprocessing":
            # TODO: CHANGEME when add describe execution for preprocessing

            self.execution_data = {}

            self.status = ModelExecutionState.Running

        else:
            url = f"{self.base_url}/{self.__url_path.replace('/async', '')}/describe/{group}/{parent_id}/{exec_id}"
            response = requests.get(
                url,
                headers={
                    "Authorization": "Bearer "
                    + refresh_token(*self.credentials, self.base_url)
                },
            )

            if response.status_code == 401:
                logger.error(
                    "Login or password are invalid, please check your credentials."
                )
                raise AuthenticationError("Login not authorized.")

            if response.status_code == 404:
                logger.error(
                    f'Unable to retrieve execution "{exec_id}"\n{response.text}'
                )
                raise ModelError(f'Execution "{exec_id}" not found.')

            if response.status_code >= 500:
                logger.error("Server is not available. Please, try it later.")
                raise ServerError("Server is not available!")

            self.execution_data = response.json()["Description"]

            self.status = ModelExecutionState[self.execution_data["ExecutionState"]]

    def __repr__(self) -> str:
        return f"""MLOps{self.exec_type}Execution(exec_id="{self.exec_id}", status="{self.status}")"""

    def __str__(self):
        return (
            f'MLOPS {self.exec_type}Execution:{self.exec_id} (Status: {self.status})"'
        )

    def get_status(self) -> dict:
        """
        Gets the status of the related execution.

        Raises
        ------
        ExecutionError
            Execution unavailable

        Returns
        -------
        dict
            Returns the execution status.
        """

        url = f"{self.base_url}/{self.__url_path}/status/{self.group}/{self.exec_id}"

        response = requests.get(
            url, headers={"Authorization": "Bearer " + self.__token}
        )
        if response.status_code not in [200, 410]:
            formatted_msg = parse_json_to_yaml(response.json())
            logger.error(f"Something went wrong...\n{formatted_msg}")
            raise ExecutionError(f'Execution "{self.exec_id}" unavailable')

        result = response.json()

        self.status = ModelExecutionState[result["Status"]]
        self.execution_data["ExecutionState"] = result["Status"]

        return result

    def wait_ready(self) -> None:
        """
        Waits the execution until is no longer running

        Example
        -------
        >>> model.wait_ready()
        """

        self.status = ModelExecutionState[self.get_status()["Status"]]
        while self.status in [
            ModelExecutionState.Requested,
            ModelExecutionState.Running,
        ]:
            sleep(30)
            self.status = ModelExecutionState[self.get_status()["Status"]]
        if self.status == ModelExecutionState.Failed:
            logger.error("Execution failed! Please check the logs")
            raise ExecutionError(
                "Execution failed"
            )  # TODO: how to improve this message?
        logger.info("Execution completed successfully")

    def download_result(
        self, *, path: Optional[str] = "./", filename: Optional[str] = "output.zip"
    ) -> None:
        """
        Gets the output of the execution.

        Parameters
        ---------
        path: Optional[str], optional
            Path of the result file. Default value is './'
        filename: Optional[str], optional
            Name of the result file. Default value is 'output.zip'

        Raises
        ------
        ExecutionError
            Execution is unavailable or failed status.
        """
        if self.status in [ModelExecutionState.Running, ModelExecutionState.Requested]:
            self.status = ModelExecutionState[self.get_status()["Status"]]

        if self.exec_type in ["AsyncModel", "AsyncPreprocessing"]:
            token = self.__token
        elif self.exec_type == "Training":
            token = refresh_token(*self.credentials, self.base_url)

        if self.status == ModelExecutionState.Succeeded:
            url = (
                f"{self.base_url}/{self.__url_path}/result/{self.group}/{self.exec_id}"
            )
            response = requests.get(
                url,
                headers={
                    "Authorization": "Bearer " + token,
                    "Neomaril-Origin": "Codex",
                    "Neomaril-Method": self.download_result.__qualname__,
                },
            )
            if response.status_code not in [200, 410]:
                formatted_msg = parse_json_to_yaml(response.json())
                logger.error(f"Something went wrong...\n{formatted_msg}")
                raise ExecutionError(f'Execution "{self.exec_id}" unavailable')

            if not path.endswith("/"):
                filename = "/" + filename

            with open(path + filename, "wb") as f:
                f.write(response.content)

            logger.info(f"Output saved in {path + filename}")
        elif self.status == ModelExecutionState.Failed:
            raise ExecutionError("Execution failed")
        else:
            logger.info(f"Execution not ready. Status is {self.status}")

    def execution_info(self) -> None:
        """Show the execution data in a better format"""
        logger.info(f"Result:\n{parse_json_to_yaml(self.execution_data)}")
