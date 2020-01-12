from Crypto.PublicKey import RSA
from Crypto import Random

def key_generation():
    #Generate private and public keys
    random_generator = Random.new().read
    private_key = RSA.generate(1024, random_generator)
    public_key = private_key.publickey()

    return private_key, public_key

def receive_decode( privateKey, conn, max_length): #me_privateKey
    data = ( conn.recv( max_length))
    #data = data.replace("\r\n", '') #remove new line character
    #encrypted = eval( data)
    decrypted = privateKey.decrypt( data).decode("utf-8") 

    return decrypted

def encrypt_send( string, publicKey, conn): #u_publicKey
    string = string.replace("\r\n", '')
    encrypted = publicKey.encrypt( string.encode(), 32)
    conn.send( encrypted[0])

    return


