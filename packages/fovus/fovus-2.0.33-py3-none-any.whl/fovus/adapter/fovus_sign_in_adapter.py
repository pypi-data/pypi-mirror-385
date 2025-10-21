import asyncio
import json
import logging
import platform
import webbrowser
from http import HTTPStatus
from importlib.metadata import version

import boto3
import botocore
import botocore.exceptions
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from typing_extensions import Coroutine, Union
from websockets.client import WebSocketClientProtocol, connect

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.adapter.fovus_cognito_adapter import (
    CognitoTokens,
    DeviceInformation,
    FovusCognitoAdapter,
)
from fovus.cli.ssl import ssl_context
from fovus.config.config import Config
from fovus.constants.cli_constants import (
    AUTH_WS_API_URL,
    CLIENT_ID,
    SSO_USER_POOL_ID,
    USER_POOL_ID,
    WORKSPACE_SSO_CLIENT_ID,
)
from fovus.exception.user_exception import UserException
from fovus.util.file_util import FileUtil


class FovusSignInAdapter:
    user_pool_id: str
    client_id: str
    user_pool_region: str
    sso_user_pool_id: str
    workspace_sso_client_id: str
    cognito_client: CognitoIdentityProviderClient
    device_information: Union[DeviceInformation, None] = None
    is_gov: bool = False

    def __init__(self, is_gov: Union[bool, None] = None) -> None:
        self.user_pool_id = Config.get(USER_POOL_ID)
        self.client_id = Config.get(CLIENT_ID)
        self.sso_user_pool_id = Config.get(SSO_USER_POOL_ID)
        self.workspace_sso_client_id = Config.get(WORKSPACE_SSO_CLIENT_ID)
        self.user_pool_region = self.user_pool_id.split("_", maxsplit=1)[0]

        self.is_gov = False if is_gov is None else is_gov

        self.cognito_client: CognitoIdentityProviderClient = boto3.client(
            "cognito-idp",
            region_name=self.user_pool_region,
        )

    def sign_in_concurrent(self, email: Union[str, None] = None, password: Union[str, None] = None) -> None:
        asyncio.run(self.sign_in(email, password))

    async def sign_in(self, email: Union[str, None] = None, password: Union[str, None] = None) -> None:
        FileUtil.remove_credentials()
        FileUtil.remove_cache_file()

        if email and password:
            self.sign_in_with_email_password(email, password)
            return

        url = Config.get(AUTH_WS_API_URL)

        websocket: WebSocketClientProtocol
        async with connect(url, ssl=ssl_context) as websocket:
            await websocket.send(json.dumps({"action": "GET_SIGN_IN_URL"}))
            cognito_challenges: list[asyncio.Future] = []
            connection_id: Union[str, None] = None
            usernames: list[Union[str, None]] = []
            challenge_answers: list[Coroutine] = []

            async for message in websocket:
                res = json.loads(message)
                action = res["action"]

                if action == "GET_SIGN_IN_URL_RESPONSE":
                    connection_id = self._get_sign_in_url_response(res)

                elif action == "IS_VALID":
                    usernames = self._is_valid(res, connection_id, cognito_challenges)

                elif action == "CHALLENGE_ANSWER":
                    challenge_answers.append(self._challenge_answer(res, cognito_challenges, usernames))

                if len(usernames) > 0 and len(usernames) == len(challenge_answers):
                    cognito_tokens_list: list[CognitoTokens] = await asyncio.gather(*challenge_answers)

                    primary_cognito_tokens = cognito_tokens_list[0]
                    sso_cognito_tokens_list = cognito_tokens_list[1:]

                    if primary_cognito_tokens is None:
                        raise UserException(HTTPStatus.BAD_REQUEST, None, "Login failed")

                    fovus_cognito_adapter: FovusCognitoAdapter = FovusCognitoAdapter(primary_cognito_tokens)
                    fovus_api_adapter = FovusApiAdapter(fovus_cognito_adapter)

                    if len(sso_cognito_tokens_list) > 0:
                        fovus_api_adapter.step_up_session(
                            {
                                "ssoIdTokens": [
                                    sso_cognito_tokens["id_token"] for sso_cognito_tokens in sso_cognito_tokens_list
                                ]
                            }
                        )
                    fovus_api_adapter.print_user_info(title="Login successful")

                    await websocket.close()

    def _get_sign_in_url_response(self, res: dict) -> str:
        connection_id = res["connectionId"]
        sign_in_url = res["signInUrl"]
        print(
            "----------------------------------------------------------",
            "  Open the sign in URL to authenticate with Fovus",
            "",
            "  Sign in URL:",
            f"  {sign_in_url}",
            "----------------------------------------------------------",
            sep="\n",
        )

        try:
            webbrowser.open(sign_in_url)
        except webbrowser.Error:
            logging.warning("Unable to open sign in URL in browser.")

        return connection_id

    def _is_valid(
        self, res: dict, connection_id: Union[str, None], cognito_challenges: list[asyncio.Future]
    ) -> list[Union[str, None]]:
        if not res["isValid"] or connection_id is None:
            raise UserException(HTTPStatus.BAD_REQUEST, self.__class__.__name__, "Login failed")

        print("Logging in...")

        try:
            FovusCognitoAdapter.sign_out()
        except UserException:
            pass

        primary_username = res["username"]
        workspace_sso_usernames = res["workspaceSsoUsernames"]
        usernames = [primary_username]
        usernames.extend(workspace_sso_usernames)

        try:
            self.device_information = FovusCognitoAdapter.load_device_information()
        except UserException:
            pass

        for idx, username in enumerate(usernames):
            cognito_challenge: asyncio.Future = asyncio.Future()
            cognito_challenges.append(cognito_challenge)
            if idx == 0:
                self._initiate_auth(self.client_id, username, connection_id, str(idx), True, cognito_challenge)
            else:
                self._initiate_auth(
                    self.workspace_sso_client_id, username, connection_id, str(idx), False, cognito_challenge
                )

        return usernames

    def _initiate_auth(
        self,
        client_id: str,
        username: str,
        connection_id: str,
        username_index: str,
        include_device_information: bool,
        cognito_challenge: asyncio.Future,
    ) -> None:
        try:
            initiate_auth_response = self.cognito_client.initiate_auth(
                AuthFlow="CUSTOM_AUTH",
                AuthParameters=self._add_device_key({"USERNAME": username}, include_device_information),
                ClientId=client_id,
            )

            challenge_responses = self._add_device_key(
                {"USERNAME": username, "ANSWER": "none"}, include_device_information
            )

            respond_to_auth_challenge_response = self.cognito_client.respond_to_auth_challenge(
                ChallengeName="CUSTOM_CHALLENGE",
                ChallengeResponses=challenge_responses,
                ClientId=client_id,
                Session=initiate_auth_response["Session"],
                ClientMetadata={"connectionId": connection_id, "usernameIndex": username_index},
            )

            cognito_challenge.set_result(respond_to_auth_challenge_response)
        except botocore.exceptions.ClientError as exc:
            if (
                exc.response["Error"]["Code"] == "ResourceNotFoundException"
                and exc.response["Error"]["Message"] == "Device does not exist."
            ):
                logging.info("remove device information in initiate auth")
                FileUtil.remove_device_information()
                self.device_information = None
                self._initiate_auth(
                    client_id, username, connection_id, username_index, include_device_information, cognito_challenge
                )

    async def _challenge_answer(
        self, res: dict, cognito_challenges: list[asyncio.Future], usernames: list[Union[str, None]]
    ) -> CognitoTokens:
        if len(usernames) == 0 or None in usernames:
            raise UserException(HTTPStatus.BAD_REQUEST, self.__class__.__name__, "Login failed")

        challenge_answer = res["challengeAnswer"]
        username_index = res.get("usernameIndex")
        if username_index is None:
            raise UserException(HTTPStatus.BAD_REQUEST, self.__class__.__name__, "Login failed")

        username_index = int(username_index)
        username = usernames[username_index]
        cognito_challenge_response = await cognito_challenges[username_index]

        if username_index == 0:
            return await self._handle_primary_user_challenge(username, challenge_answer, cognito_challenge_response)

        return await self._handle_sso_user_challenge(username, challenge_answer, cognito_challenge_response)

    async def _handle_primary_user_challenge(
        self, username: str, challenge_answer: str, cognito_challenge_response: dict
    ) -> CognitoTokens:
        response = self.cognito_client.respond_to_auth_challenge(
            ChallengeName="CUSTOM_CHALLENGE",
            ChallengeResponses=self._add_device_key({"ANSWER": challenge_answer, "USERNAME": username}),
            ClientId=self.client_id,
            Session=cognito_challenge_response["Session"],
        )

        if "ChallengeName" in response and response["ChallengeName"] == "DEVICE_SRP_AUTH":
            if self.device_information is None:
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    "Device information is not found.",
                )

            response = FovusCognitoAdapter.respond_to_device_srp_challenge(
                response,
                self.device_information,
                self.cognito_client,
                self.client_id,
                username,
                self.user_pool_id,
                self.user_pool_region,
            )

        id_token = response["AuthenticationResult"]["IdToken"]
        access_token = response["AuthenticationResult"]["AccessToken"]
        refresh_token = response["AuthenticationResult"]["RefreshToken"]

        if "NewDeviceMetadata" in response["AuthenticationResult"]:
            device_key: str = response["AuthenticationResult"]["NewDeviceMetadata"]["DeviceKey"]
            device_group_key: str = response["AuthenticationResult"]["NewDeviceMetadata"]["DeviceGroupKey"]

            salt, verifier, device_password = FovusCognitoAdapter.generate_device_secrets(device_key, device_group_key)

            current_fovus_version = version("fovus")
            device_name = f"Fovus CLI@{current_fovus_version}-{platform.platform()}"

            self.cognito_client.confirm_device(
                AccessToken=access_token,
                DeviceKey=device_key,
                DeviceName=device_name,
                DeviceSecretVerifierConfig={"PasswordVerifier": verifier, "Salt": salt},
            )

            self.device_information = {
                "device_name": device_name,
                "device_key": device_key,
                "device_group_key": device_group_key,
                "device_password": device_password,
                "verifier": verifier,
                "salt": salt,
            }

            FovusCognitoAdapter.save_device_information(self.device_information)

        cognito_tokens: CognitoTokens = {
            "id_token": id_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "is_gov": self.is_gov,
        }

        FovusCognitoAdapter.save_credentials(cognito_tokens)

        return cognito_tokens

    async def _handle_sso_user_challenge(
        self, username: str, challenge_answer: str, cognito_challenge_response: dict
    ) -> CognitoTokens:
        response = self.cognito_client.respond_to_auth_challenge(
            ChallengeName="CUSTOM_CHALLENGE",
            ChallengeResponses={"ANSWER": challenge_answer, "USERNAME": username},
            ClientId=self.workspace_sso_client_id,
            Session=cognito_challenge_response["Session"],
        )

        id_token = response["AuthenticationResult"]["IdToken"]
        access_token = response["AuthenticationResult"]["AccessToken"]
        refresh_token = response["AuthenticationResult"]["RefreshToken"]

        cognito_tokens: CognitoTokens = {
            "id_token": id_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "is_gov": None,
        }

        sso_provider_id = username.split("_")[0]
        if sso_provider_id is None:
            raise UserException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                self.__class__.__name__,
                "An internal error has occurred. Login failed",
            )

        FovusCognitoAdapter.save_workspace_sso_token(sso_provider_id, cognito_tokens)

        return cognito_tokens

    def sign_in_with_email_password(self, email: str, password: str) -> None:
        """Sign in using email and password (standard Cognito flow)."""
        try:
            self.device_information = FovusCognitoAdapter.load_device_information()
        except UserException:
            pass

        print(f"Signing in: {email}")

        try:
            initiate_auth_response = self.cognito_client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                },
                ClientId=self.client_id,
            )
            self._handle_successful_authentication(initiate_auth_response)

        except botocore.exceptions.ClientError as exc:
            error_code = exc.response["Error"]["Code"]
            error_message = exc.response["Error"]["Message"]

            if "NotAuthorizedException" in error_code:
                if "Incorrect username or password" in error_message:
                    raise UserException(
                        HTTPStatus.BAD_REQUEST, self.__class__.__name__, "Invalid email or password"
                    ) from exc
                if "User does not exist" in error_message:
                    raise UserException(HTTPStatus.BAD_REQUEST, self.__class__.__name__, "User not found") from exc
            elif "UserNotFoundException" in error_code:
                raise UserException(HTTPStatus.BAD_REQUEST, self.__class__.__name__, "User not found") from exc

            raise UserException(
                HTTPStatus.BAD_REQUEST, self.__class__.__name__, f"Authentication failed: {error_message}"
            ) from exc

    def _handle_successful_authentication(self, response: dict) -> None:
        """Handle successful authentication response."""
        id_token = response["AuthenticationResult"]["IdToken"]
        access_token = response["AuthenticationResult"]["AccessToken"]
        refresh_token = response["AuthenticationResult"]["RefreshToken"]

        if "NewDeviceMetadata" in response["AuthenticationResult"]:
            device_key: str = response["AuthenticationResult"]["NewDeviceMetadata"]["DeviceKey"]
            device_group_key: str = response["AuthenticationResult"]["NewDeviceMetadata"]["DeviceGroupKey"]

            salt, verifier, device_password = FovusCognitoAdapter.generate_device_secrets(device_key, device_group_key)

            current_fovus_version = version("fovus")
            device_name = f"Fovus CLI@{current_fovus_version}-{platform.platform()}"

            self.cognito_client.confirm_device(
                AccessToken=access_token,
                DeviceKey=device_key,
                DeviceName=device_name,
                DeviceSecretVerifierConfig={"PasswordVerifier": verifier, "Salt": salt},
            )

            self.device_information = {
                "device_name": device_name,
                "device_key": device_key,
                "device_group_key": device_group_key,
                "device_password": device_password,
                "verifier": verifier,
                "salt": salt,
            }

            FovusCognitoAdapter.save_device_information(self.device_information)

        cognito_tokens: CognitoTokens = {
            "id_token": id_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "is_gov": self.is_gov,
        }

        FovusCognitoAdapter.save_credentials(cognito_tokens)

        fovus_cognito_adapter = FovusCognitoAdapter(cognito_tokens)
        fovus_api_adapter = FovusApiAdapter(fovus_cognito_adapter)
        fovus_api_adapter.print_user_info(title="Login successful")

    def _add_device_key(self, params: dict, include_device_key=True) -> dict:
        if include_device_key and self.device_information is not None:
            params["DEVICE_KEY"] = self.device_information["device_key"]

        return params
