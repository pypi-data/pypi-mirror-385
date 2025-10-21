import argparse
import base64
import pathlib
from datetime import datetime
from sys import stderr

import argon2
from Cryptodome.Cipher import AES

__version__ = "1.0.0"


class JournalEntry:
    """Simple class that bundles all the different parts of a journal entry for easy access
    throughout the proram."""

    def __init__(self, plaintext: str = ""):
        self.plaintext: str = plaintext
        self.nonce: bytes = None
        self.tag: bytes = None
        self.ciphertext: bytes = None
        self.argon_type: str = None
        self.argon_version: str = None
        self.argon_params: str = None
        self.salt: str = None
        self.password_hash: str = None

    def __str__(self):
        return (
            f"Nonce: {repr(self.nonce)}\n"
            + f"Tag: {repr(self.tag)}\n"
            + f"Argon Type: {self.argon_type}\n"
            + f"Argon Version: {self.argon_version}\n"
            + f"Argon Params: {self.argon_params}\n"
            + f"Salt: {self.salt}"
        )

    def encrypt_text(self) -> None:
        # Convert the password hash into binary representation
        # More info on padding: <https://stackoverflow.com/questions/2941995/>
        password_hash_binary = base64.b64decode(
            self.password_hash + "=" * (-len(self.password_hash) % 4)
        )
        # Create an AES cipher object
        cipher = AES.new(password_hash_binary, AES.MODE_OCB)
        assert len(cipher.nonce) == 15
        self.nonce = cipher.nonce
        # Convert plaintext into binary representation
        data = self.plaintext.encode("utf-8")
        # Encrypt
        ciphertext, tag = cipher.encrypt_and_digest(data)
        # Save
        self.ciphertext = ciphertext
        self.tag = tag

    def write_entry(self) -> None:
        # The default storage directory for the information from this app
        directory_path = pathlib.Path().home() / ".mnemosyne" / "entries"
        # Make sure that the base directories actually exist
        directory_path.mkdir(parents=True, exist_ok=True)
        # The path to the current new journal entry file
        file_path = directory_path / datetime.now().strftime("%Y%m%d%H%M%S.txt")
        with open(file_path, "w") as my_file:
            nonceb64 = base64.b64encode(self.nonce).decode("utf-8")
            my_file.write("Nonce$" + nonceb64 + "\n")
            tagb64 = base64.b64encode(self.tag).decode("utf-8")
            my_file.write("Tag$" + tagb64 + "\n")
            my_file.write("Argon Type$" + self.argon_type + "\n")
            my_file.write("Argon Version$" + self.argon_version + "\n")
            my_file.write("Argon Params$" + self.argon_params + "\n")
            my_file.write("Argon Salt$" + self.salt + "\n")
            ciphertextb64 = base64.b64encode(self.ciphertext).decode("utf-8")
            my_file.write("Ciphertext$" + ciphertextb64 + "\n")

    def get_encryption_key(self, text_password: str) -> None:
        password_hasher = argon2.PasswordHasher()
        hashed = password_hasher.hash(text_password)
        parts = hashed.split("$")
        self.argon_type = parts[1]
        self.argon_version = parts[2]
        self.argon_params = parts[3]
        self.salt = parts[4]
        self.password_hash = parts[5]

    def decrypt_text(self, text_password: str) -> None:
        password_hasher = argon2.PasswordHasher()
        hashed_password = password_hasher.hash(
            text_password,
            salt=base64.b64decode(self.salt + "=" * (-len(self.salt[-1]) % 4)),
        )
        parts = hashed_password.split("$")
        if (
            self.argon_type != parts[1]
            or self.argon_version != parts[2]
            or self.argon_params != parts[3]
        ):
            print(
                "The argon2 version seems to no longer match the one used to encrypt this text.",
                file=stderr,
            )
        password_hash_binary = base64.b64decode(parts[-1] + "=" * (-len(parts[-1]) % 4))
        cipher = AES.new(password_hash_binary, mode=AES.MODE_OCB, nonce=self.nonce)
        try:
            self.plaintext = cipher.decrypt_and_verify(
                self.ciphertext, self.tag
            ).decode("utf-8")
        except ValueError:
            print("The message was modified or key was incorrect.")


def show_license_details() -> None:
    print(
        "This app is licensed under the GPL v3 or later license. Please see\n<https://www.gnu.org/licenses/gpl-3.0.en.html> for a complete copy of the license, as well as the LICENSE.md\nfile included with this Python package."
    )


def show_copying() -> None:
    print(
        "For full information on what is and is not allowed in term of copying, distribution, and\nreuse of the code in this app, please see the full license at\n<https://www.gnu.org/licenses/gpl-3.0.en.html>."
    )


def read_entry(file_name: str) -> JournalEntry:
    directory_path = pathlib.Path().home() / ".mnemosyne" / "entries"
    file_path = directory_path / file_name
    with open(file_path, "r") as my_file:
        data = my_file.read()
        content = data.split("\n")
        entry = JournalEntry()
        entry.nonce = base64.b64decode(content[0].split("$")[1])
        entry.tag = base64.b64decode(content[1].split("$")[1])
        entry.argon_type = content[2].split("$")[1]
        entry.argon_version = content[3].split("$")[1]
        entry.argon_params = content[4].split("$")[1]
        entry.salt = content[5].split("$")[1]
        entry.ciphertext = base64.b64decode(content[6].split("$")[1])
        return entry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        help="Show the version information for this app.",
        action="store_true",
    )
    parser.add_argument(
        "--license-details",
        help="Print the working license for this app.",
        action="store_true",
    )
    parser.add_argument(
        "--show-copying",
        help="Print the conditions under which the code for this app can be reused.",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--content",
        help="The content of the journal entry. I.e. the text you are writing.",
    )
    parser.add_argument(
        "-p", "--password", help="The password used for encryption/decryption."
    )
    parser.add_argument(
        "-r",
        "--read",
        help="Opens up a specific journal entry for reading given the entry timestamp in the YYYYMMDDHHMMSS format.",
    )
    args = parser.parse_args()
    if args.version:
        print(f"Mnemosyne Journaling by Siru: Version {__version__}")
    elif args.license_details:
        show_license_details()
    elif args.show_copying:
        show_copying()
    elif args.read is not None:
        if args.password is None:
            print("Please provide the password to decrypt the journal entry.")
        else:
            entry = read_entry(args.read + ".txt")
            entry.decrypt_text(args.password)
            print(f"Entry Text:\n{entry.plaintext}")
    elif args.content is None:
        print(
            "Please provide a content to be stored as the journal entry using the --content option."
        )
    elif args.password is None:
        print(
            "Journal entries can only be stored if a password is provided using the --password option."
        )
    else:
        entry = JournalEntry(args.content)
        entry.get_encryption_key(args.password)
        entry.encrypt_text()
        entry.write_entry()
        print("The journal entry was stored succesfully.")
