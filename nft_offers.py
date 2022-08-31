import os
import sys
import argparse
import asyncio
import pathlib
import json
import time
from subprocess import PIPE, Popen

import chia_overrides



# Chia dependency
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.util.hash import std_hash


# Offers
from chia.wallet.transaction_sorting import SortKey
from chia.wallet.util.wallet_types import WalletType
from chia.cmds.wallet import make_offer_cmd


LAUNCHER_ID_AS_NFT_KEY = "launcher_id_as_nft"
LAUNCHER_PUZHASH_AS_ADDRESS_KEY = "launcher_puzhash_as_address"
ROYALTY_PUZZLE_HASH_AS_ADDRESS_KEY = "royalty_puzzle_hash_as_address"
NFT_COIN_ID_AS_ADDRESS_KEY = "nft_coin_id_as_address"
UPDATER_PUZHASH_AS_ADDRESS_KEY = "updater_puzhash_as_address"


def list_of_nfts_simple(chia_nft_list_json, only_edition_number=None):
    nft_id_list = []
    
    # print('------2------')
    # print(json.dumps(chia_nft_list_json[0], sort_keys=False, indent=4))
    # print('------2------')
    
    num_of_items = len(chia_nft_list_json)
    leading_zeros = len(str(num_of_items))
    
    for nft_num in chia_nft_list_json:
        
        nft_info_json = chia_nft_list_json[nft_num]
        nft_id = nft_info_json[LAUNCHER_ID_AS_NFT_KEY]
        string_to_display = nft_num.zfill(leading_zeros)
        
        if not (nft_info_json.get('edition_total') is None):
            edition_total = nft_info_json["edition_total"]
            
            if edition_total > 1:
                edition_leading_zeros = len(str(edition_total))
                edition_num = nft_info_json["edition_number"]
                edition_num_str = str(edition_num).zfill(edition_leading_zeros)
                
                string_to_display += f"|{edition_num}/{str(edition_total)}"
            
        
        string_to_display += f"|{nft_id}"
        
        nft_id_list.append(string_to_display)
    
    return nft_id_list

def list_of_nfts_json(chia_nft_list_json, only_edition_number=None):
    nft_id_list = {}
    
    nft_num = 1
    
    # print('------1------')
    # print(json.dumps(chia_nft_list_json[0], sort_keys=False, indent=4))
    # print('------1------')
    
    for nft_json in chia_nft_list_json:
        
        new_attributes = {}
        
        new_attributes[LAUNCHER_ID_AS_NFT_KEY] = nft_json[LAUNCHER_ID_AS_NFT_KEY]
        
        if not (nft_json.get('edition_total') is None):
            editions_total = nft_json["edition_total"]
            if editions_total > 1:
                edition_num = nft_json["edition_number"]
                
                if only_edition_number != None:
                    if edition_num == only_edition_number:
                        new_attributes["edition_number"] = edition_num
                        new_attributes["edition_total"] = editions_total
                    else:
                        continue
                else:
                    new_attributes["edition_number"] = edition_num
                    new_attributes["edition_total"] = editions_total
                    
                
        
        nft_id_list[str(nft_num)] = new_attributes
        nft_num += 1
    
    return nft_id_list

async def nft_list_all(wallet_id, wallet_fingerprint, raw_output=False, json_output=False, edition_number=None):
    
    all_nfts_json_encoded = await get_nft_list(wallet_id, wallet_fingerprint)
    
    # print(json.dumps(all_nfts_json_encoded, sort_keys=False, indent=4))
    
    if raw_output == True:
        print(json.dumps(all_nfts_json_encoded, sort_keys=False, indent=4))
    elif json_output == True:
        list = list_of_nfts_json(all_nfts_json_encoded, edition_number)
        print(json.dumps(list, sort_keys=False, indent=4))
    else:
        list = list_of_nfts_json(all_nfts_json_encoded, edition_number)
        nft_id_list = list_of_nfts_simple(list)
        print("\n".join(nft_id_list))




from chia_overrides import list_nfts
from chia_overrides import execute_with_wallet
from chia.wallet.nft_wallet.nft_info import NFTInfo
from chia.wallet.util.address_type import AddressType
from chia.server.start_wallet import SERVICE_NAME
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
# from chia.types.blockchain_format.sized_bytes import bytes32

async def get_nft_list(wallet_id, wallet_fingerprint):
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    
    print("list nfts ...")
    wallet_rpc_port = None
    
    extra_params = {"wallet_id": wallet_id}
    nft_list = await execute_with_wallet(wallet_rpc_port, wallet_fingerprint, extra_params, list_nfts)
    
    if nft_list != None:
        if len(nft_list) > 0:
            for n in nft_list:
                nft = NFTInfo.from_json_dict(n)
                
                owner_did = None if nft.owner_did is None else encode_puzzle_hash(nft.owner_did, AddressType.DID.hrp(config))
                
                n[LAUNCHER_ID_AS_NFT_KEY] = encode_puzzle_hash(nft.launcher_id, AddressType.NFT.hrp(config))
                n[LAUNCHER_PUZHASH_AS_ADDRESS_KEY] = encode_puzzle_hash(nft.launcher_puzhash, AddressType.XCH.hrp(config))
                n[ROYALTY_PUZZLE_HASH_AS_ADDRESS_KEY] = encode_puzzle_hash(nft.royalty_puzzle_hash, AddressType.XCH.hrp(config))
                n[NFT_COIN_ID_AS_ADDRESS_KEY] = encode_puzzle_hash(nft.nft_coin_id, AddressType.XCH.hrp(config))
                n[UPDATER_PUZHASH_AS_ADDRESS_KEY] = encode_puzzle_hash(nft.updater_puzhash, AddressType.XCH.hrp(config))
                n["owner_did"] = owner_did
                n["data_hash"] = nft.data_hash.hex()
                n["metadata_hash"] = nft.metadata_hash.hex()
                n["license_hash"] = nft.license_hash.hex()
                
            # print(json.dumps(nft_list, sort_keys=False, indent=4))
            return nft_list
    else:
        print(f"No NFTs found for wallet with id {walletid} on key {wallet_fingerprint}")
        return None


def get_args():
    
    parser = argparse.ArgumentParser(description='Generate Chia offers, list available Chia NFTs in a wallet, generate offers in series.')
    
    # Required inputs
    parser.add_argument('-wi', '--wallet-id', metavar=('CHIA_WALLET_ID'), nargs=1, type=int, required=True, help='Chia wallet ID')
    parser.add_argument('-wf', '--wallet-fingerprint', metavar=('CHIA_WALLET_FINGERPRINT'), nargs=1, type=int, required=True, help='Chia wallet fingerprint')
    
    # Optional params
    parser.add_argument('-r', '--raw-output', action='store_true', required=False, help='Will show exactly what chia wallet RPC command shows AND encodes hex to hashes.')
    parser.add_argument('-j', '--json-output', action='store_true', required=False, help='Output the list as JSON instead.')
    parser.add_argument('-en', '--edition-number', metavar=('NFT_EDITION_NUMBER'), nargs=1, type=int, required=False, help='Only show/use NFTs with this edition number.')
    
    ## Assumes metadata is validated
    parser.add_argument('-l', '--list-all-nfts', action='store_true', required=False, help='Output a list of all NFTs.')
    
    if len(sys.argv) < 2:
        # parser.print_usage()
        parser.print_help()
        sys.exit(1)
    
    return parser.parse_args()

async def main():
    
    ARGS = get_args()
    
    is_json_output = False
    is_raw_output = False
    edition_number = None
    
    if ARGS.list_all_nfts:
        wallet_id = ARGS.wallet_id[0]
        wallet_fingerprint = ARGS.wallet_fingerprint[0]
        
        if ARGS.json_output:
            is_json_output = True
        
        if ARGS.raw_output:
            is_raw_output = True
        
        if ARGS.edition_number:
            edition_number = ARGS.edition_number[0]
        
        await nft_list_all(wallet_id, wallet_fingerprint, is_raw_output, is_json_output, edition_number)
    

# Prevent auto executing main when called from another program
if __name__ == "__main__":
    asyncio.run(main())
