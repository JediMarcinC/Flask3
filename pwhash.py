from passlib.hash import sha256_crypt

pwd = sha256_crypt.encrypt('password')
pwd2 = sha256_crypt.encrypt('password')

print(len(pwd), type(pwd), pwd)
print(pwd2)

print()

print(sha256_crypt.verify('password', pwd2))



# print(sha256_crypt.verify('password', pwd2))
