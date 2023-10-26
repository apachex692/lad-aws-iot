# Author: Sakthi Santhosh
# Created on: 10/10/2023
from boto3 import client
from os import chmod, getlogin, mkdir, path, system

class Thing:
    def __init__(self, thing_name: str) -> None:
        self._client_handle = client("iot")
        self.thing_name = thing_name

        self.CERT_BASE_DIR = f"/home/{getlogin()}/.aws/iot/certs"

    def jit_provision(self) -> None:
        cert_arn = self.generate_cert()

        self._client_handle.create_thing(thingName=self.thing_name)
        self.attach_principal(cert_arn=cert_arn)

        self.create_policy()
        self.attach_policy(cert_arn=cert_arn)

    def generate_cert(self) -> str:
        BASE_DIR = self.CERT_BASE_DIR + f"/{self.thing_name}"

        mkdir(BASE_DIR)

        request_handle = self._client_handle.create_keys_and_certificate(setAsActive=True)

        print(f"Info: Generating certificates at: {BASE_DIR}/")
        print("Info: Storing certificate to file:", BASE_DIR + "/certificate.pem.crt")
        with open(BASE_DIR + "/certificate.pem.crt", 'w') as file_handle:
            file_handle.write(request_handle["certificatePem"] + '\n')

        print("Info: Storing private key to file:", BASE_DIR + "/private.pem.key")
        with open(BASE_DIR + "/private.pem.key", 'w') as file_handle:
            file_handle.write(request_handle["keyPair"]["PrivateKey"] + '\n')

        print("Info: Storing public key to file:", BASE_DIR + "/public.pem.key")
        with open(BASE_DIR + "/public.pem.key", 'w') as file_handle:
            file_handle.write(request_handle["keyPair"]["PublicKey"] + '\n')

        if not path.exists(self.CERT_BASE_DIR + "/root-ca1.pem"):
            print("Info: No CA certificate exists, downloading default certificate AmazonRootCA1.")
            system(f"wget -O {self.CERT_BASE_DIR}/root-ca1.pem \"https://www.amazontrust.com/repository/AmazonRootCA1.pem\"") # FIXME: subprocess.shell()

        chmod(BASE_DIR + "/private.pem.key", 0o600)

        print("Info: Created certificates successfully.")
        return request_handle["certificateArn"]

    def list_certs(self) -> list[str]:
        request_handle = self._client_handle.list_certificates()
        result = []

        for cert in request_handle["certificates"]:
            result.append(cert["certificateArn"])
        return result

    def attach_principal(self, cert_arn: str) -> None:
        print(f"Info: Attaching principal \"{cert_arn}\" to thing \"{self.thing_name}\".")

        request_handle = self._client_handle.attach_thing_principal(
            thingName=self.thing_name,
            principal=cert_arn
        )

    def create_policy(self) -> None:
        print("Info: Creating policy from ./assets/thing-policy.json file.")

        with open("./assets/thing-policy.json") as file_handle:
            policy_document = file_handle.read()%(self.thing_name)

        print("Policy:", policy_document, sep="\n")

        request_handle = self._client_handle.create_policy(
            policyName=f"{self.thing_name}-policy",
            policyDocument=policy_document
        )

    def attach_policy(self, cert_arn: str=None) -> None:
        if cert_arn is None:
            available_certs = self.list_certs()

            print(f"Info: No certificate chosen. Listing all the certificates available for the thing \"{self.thing_name}\".")
            print("Certificate ARNs:")
            for index, cert in enumerate(available_certs, start=1):
                print(f"  {index}. {cert}")

            cert_no = int(input("\nChoose a certificate #: "))

            if cert_no < 0 or cert_no > len(available_certs):
                print("Error: Invalid certificate # chosen.")
                return

            cert_arn = available_certs[cert_no - 1]

        print("Info: Attaching policy to certificate with ARN:", cert_arn)

        request_handle = self._client_handle.attach_policy(
            policyName=f"{self.thing_name}-policy",
            target=cert_arn
        )
