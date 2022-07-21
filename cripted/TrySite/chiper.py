from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP


def get_keys(masterpass):
    keys = RSA.generate(1024)
    public = keys.publickey().exportKey()
    private = keys.exportKey(
        passphrase=masterpass,
        pkcs=8,
        protection="scryptAndAES128-CBC"
    )
    return public, private


def is_masterpass(private, masterpass):
    try:
        RSA.import_key(private, passphrase=masterpass)
        return True
    except ValueError as ex:
        print("\tChiper", ex)
        return False


def encrypt(public: bytes, data):
    """return: encrypt_session, nonce, tag, chiper_text"""

    if isinstance(data, str):
        data = str.encode(data)
    session = get_random_bytes(16)
    chiper_rsa = PKCS1_OAEP.new(RSA.import_key(public))
    encrypt_session = chiper_rsa.encrypt(session)

    chiper_aes = AES.new(session, AES.MODE_EAX)
    chiper_text, tag = chiper_aes.encrypt_and_digest(data)
    nonce = chiper_aes.nonce

    return encrypt_session, nonce, tag, chiper_text


def decrypt(private: bytes, masterpass: str, encrypt_session: bytes, nonce: bytes, tag: bytes, cryped_data: bytes):
    chiper_rsa = PKCS1_OAEP.new(RSA.import_key(private, passphrase=masterpass))
    session = chiper_rsa.decrypt(encrypt_session)

    chiper_aes = AES.new(session, AES.MODE_EAX, nonce)
    data = chiper_aes.decrypt_and_verify(cryped_data, tag)

    return data


if __name__ == "__main__":
    master = input("master: ")
    text = "QWERTY Биг Большой Шифрт 1234556"

    public, private = get_keys(master)
    print(type(private))

    print(is_masterpass(private=private, masterpass=input("master to: ")))

    # session, nonce, tag, chiper_text = encrypt(public=public, data=str.encode(text))

    # dec_text = decrypt(
    #     private=private, masterpass=master,
    #     encrypt_session=session, tag=tag,
    #     nonce=nonce, cryped_data=chiper_text
    # )
    # print(text)
    # print(d := dec_text.decode())
    # print(text == d)
