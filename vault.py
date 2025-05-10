#!/usr/bin/python
import sys
import os
import base64
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


'''
The goal is to remove the reliance on env variables to store api keys.
These api keys are needed for interaction with external sources.

When a program runs, it should decrypt at runtime using a supplied token 
and key as program arguments.

The secret is the credential that an external source needs.
The key is a random value that, when given a token, returns
the secret.

The key must be kept somewhere safe and never exposed to the commandline
history.
'''
def print_usage():
    usage = '''
Usage:
    1) vault -n|--new [destination_file_path]:
        |-> Prompts the user for the following:
            -Destination : FilePath (Optional)
            -Passphrase : String 
            -Credential : String

        Then, encrypts the Credential with Passphrase and saves the result to Destination.
        The Destination holds the salt and encrypted credential.

        If the destination file already exists, DOES NOT overwrite the contents.
        
    2) vault -r|--retrieve [source_file_path]:
        |-> Prompts the user for the following:
            -Source : String (Optional)
            -Passphrase : String

        Prints the result within shell prompt.

    3) vault -h|--help:
    
        Prints the usage. (todo as prgm expands)
    '''
    print(usage)

def enter_new_credentials(destination: str) -> (str,str,str):
    if len(destination) == 0:
        destination = input("Enter Destination FilePath: ")
    credential = getpass.getpass("Enter Credential: ")
    passphrase = getpass.getpass("Enter Passphrase: ")
    print(destination)
    return (passphrase, credential, destination)

def decrypt_existing_key_with_source(source=None) -> str:

    if source == None:
        source = input("Enter Source FilePath: ")

    passphrase = getpass.getpass("Enter Passphrase: ")

    if False == file_exists(source):
        print(f"Key does not exist... Exiting...")
        exit(1)
    else:
        print("Key exists... reading...")
        try:
            print(source)
            file = open(source, "r")
            line = file.read()
            kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=base64.b64decode(line[0:24]),
                    iterations=1_200_000
            )
            file.close()
            key = base64.b64encode(kdf.derive(passphrase.encode()))
            f = Fernet(key)
            return f.decrypt(line[24:].encode()).decode()
        except Exception as e:
            print(f"error reading file: {e}")
            exit(1)
 
    return _decrypt_key(passphrase.encode(), source)

def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)

def generate_salt() -> bytes:
    return os.urandom(16)

def create_key(passphrase: bytes, credential: bytes) -> (str, str):
    salt = generate_salt()
    encoded_salt = base64.b64encode(salt)
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_200_000
    )
    return (encoded_salt.decode(), Fernet(base64.b64encode(kdf.derive(passphrase))).encrypt(credential).decode())

 
if __name__ == "__main__":
    argc = len(sys.argv)
    if argc == 2 or argc == 3:
        if sys.argv[1] == "-n" or sys.argv[1] == "--new":
            try:
                destination = "" 
                if argc == 3:
                    destination = str(sys.argv[2])
                    (passphrase, credential, file_path)= enter_new_credentials(destination)
                else:
                    (passphrase, credential, file_path)= enter_new_credentials()
                (s,k) = create_key(passphrase.encode(),credential.encode())
                print(f"Creating key in {destination}.")
                file = open(file_path, "w")
                file.write(s)
                file.write(k)
                file.close()
                os.chmod(file_path, 0o600)
                print(f"File {file_path} created for your secret key. KEEP THIS PROTECTED.")
            except Exception as e:
                print(f"Error writing to file: {e}")
        if sys.argv[1] == "-r" or sys.argv[1] == "--retrieve":
            if argc == 3:
                file_path = str(sys.argv[2])
                print(f"You are responsible for keeping this key safe. Do not store anywhere.\n")
                print(f"DO NOT EXPOSE: {decrypt_existing_key_with_source(file_path)} ")
                exit(0)
            else:
                print(f"You are responsible for keeping this key safe. Do not store anywhere.\n")
                print(f"DO NOT EXPOSE: {decrypt_existing_key_with_source()} ")
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print_usage()
            exit(0)
    else:
        print_usage()
        exit(1)

