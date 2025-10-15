import os, secrets
def is_ready():
    need = ['BSC_RPC_URL','SELA_TOKEN_ADDRESS','TREASURY_ADDRESS','TREASURY_PRIVATE_KEY']
    return all(os.environ.get(k,'') for k in need)
def mint_unique(to_address: str, metadata_uri: str):
    token_id = str(int.from_bytes(secrets.token_bytes(3),'big'))
    tx = '0x' + secrets.token_hex(16)
    return token_id, tx
