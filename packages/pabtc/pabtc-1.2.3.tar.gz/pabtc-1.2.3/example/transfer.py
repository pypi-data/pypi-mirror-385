import argparse
import pabtc

# Transfer bitcoin to another account.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--script-type', type=str, choices=['p2pkh', 'p2sh-p2wpkh', 'p2wpkh', 'p2tr'])
parser.add_argument('--to', type=str, help='bitcoin address')
parser.add_argument('--value', type=float, help='bitcoin value')
args = parser.parse_args()

if args.net == 'develop':
    pabtc.config.current = pabtc.config.develop
if args.net == 'mainnet':
    pabtc.config.current = pabtc.config.mainnet
if args.net == 'testnet':
    pabtc.config.current = pabtc.config.testnet

accept_script = pabtc.core.script_pubkey(args.to)
accept_value = int(args.value * pabtc.denomination.bitcoin)
prikey = int(args.prikey, 0)
wallet = pabtc.wallet.Wallet(pabtc.wallet.Tp2pkh(prikey))
if args.script_type == 'p2pkh':
    wallet = pabtc.wallet.Wallet(pabtc.wallet.Tp2pkh(prikey))
if args.script_type == 'p2sh-p2wpkh':
    wallet = pabtc.wallet.Wallet(pabtc.wallet.Tp2shp2wpkh(prikey))
if args.script_type == 'p2wpkh':
    wallet = pabtc.wallet.Wallet(pabtc.wallet.Tp2wpkh(prikey))
if args.script_type == 'p2tr':
    wallet = pabtc.wallet.Wallet(pabtc.wallet.Tp2tr(prikey, bytearray()))
txid = wallet.transfer(accept_script, accept_value)
print(f'0x{txid.hex()}')
