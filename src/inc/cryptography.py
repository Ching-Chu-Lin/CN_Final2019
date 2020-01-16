from cryptography.fernet import Fernet
from Crypto import Random
from Crypto.PublicKey import RSA

def asymmetric_key_generation():
    #Generate private and public keys
    random_generator = Random.new().read
    private_key = RSA.generate(1024, random_generator)
    public_key = private_key.publickey()

    return private_key, public_key

def receive_decode( Key, conn, max_length): #me_privateKey
    #data = ( conn.recv( max_length))
    #cipher = PKCS1_OAEP.new( privateKey)
    #decrypted = cipher.decrypt( data).decode()

    cipher = Fernet( Key)
    data = conn.recv( max_length)
    decrypted = cipher.decrypt( data).decode()

    return decrypted

def encrypt_send( string, Key, conn): #u_publicKey
    #string = string.replace("\r\n", '')
    #cipher = PKCS1_OAEP.new( publicKey)
    #encrypted = cipher.encrypt( string.encode())
    #conn.send( encrypted)

    cipher = Fernet( Key)
    encrypted = cipher.encrypt( string.encode())
    conn.send( encrypted)

    return

def receive_decode_byte( Key, conn, max_length):
    cipher = Fernet( Key)
    data = conn.recv( max_length)
    decrypted = cipher.decrypt( data)
    return decrypted

def encrypt_send_byte( string, Key, conn):
    cipher = Fernet( Key)
    encrypted = cipher.encrypt( string)
    conn.send( encrypted)
    return


