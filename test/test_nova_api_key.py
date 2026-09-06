from src.security.nova_api_key import NovaKey

nova_key = NovaKey()

key = nova_key.generate()
print(f"nova key = ", key)
