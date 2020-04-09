import ecdsa
import binascii
signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
verifying_key = signing_key.get_verifying_key()
print(binascii.hexlify(signing_key.to_string()))
print(signing_key.to_string())
print(binascii.hexlify(verifying_key.to_string()))
print(verifying_key.to_string())