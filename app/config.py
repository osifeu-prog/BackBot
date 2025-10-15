import os
def effective_env():
    e = {k: os.environ.get(k, '').strip() for k in [
        'BOT_TOKEN','ADMIN_ID','PUBLIC_URL','WEBHOOK_ROUTE','LOG_LEVEL',
        'APPROVED_CHAT_ID','ARCHIVE_CHAT_ID','PAYMENTS_CHAT_ID','CONTACT_USERNAME',
        'SELA_NIS_VALUE','BSC_RPC_URL','SELA_TOKEN_ADDRESS','TREASURY_ADDRESS','TREASURY_PRIVATE_KEY'
    ]}
    if not e.get('WEBHOOK_ROUTE'): e['WEBHOOK_ROUTE']='/webhook'
    if not e.get('LOG_LEVEL'): e['LOG_LEVEL']='INFO'
    return e

def require_env():
    e = effective_env()
    missing = [k for k in ['BOT_TOKEN','ADMIN_ID','PUBLIC_URL','WEBHOOK_ROUTE'] if not e.get(k)]
    if missing:
        raise RuntimeError('Missing required: ' + ', '.join(missing))
    return e
