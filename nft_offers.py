import os
import sys
import argparse
import asyncio
import pathlib
import json
import time
from subprocess import PIPE, Popen

# Chia dependency
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.util.hash import std_hash

# # copy from https://github.com/Chia-Network/chia-dev-tools/blob/main/cdv/cmds/cli.py
# def hash_cmd(data: str):
#     if data[:2] == "0x":
#         hash_data = bytes.fromhex(data[2:])
#     else:
#         hash_data = bytes(data, "utf-8")
#     return std_hash(hash_data)

# async def wait_for_chia_wallet_sync_for_fingerprint(chia_wallet_fingerprint):
#     is_synced = False
#
#     while True:
#
#
#     return is_synced

def chia_wallet_list_nfts(wallet_id):
    print("list all nfts for wallet id " + wallet_id + " ...")
    wallet_id_str = str(wallet_id)
    command  = "chia rpc wallet nft_get_nfts '{\"wallet_id\": "+ wallet_id_str + "}'"
    
    with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
        output = process.communicate()[0].decode("utf-8")
        # print(output)
    
    try:
        chia_nft_list_json = json.loads(output)
    except Exception as e:
        print(e)
        sys.exit(f"ERROR reading {output}")
    
    return chia_nft_list_json

def list_of_nfts_raw_and_encoded(chia_nft_list_json):
    
    nft_list = chia_nft_list_json["nft_list"]
    
    for nft_json in nft_list:
        for key in nft_json:
            value = nft_json[key]
            
            puzzle_hash = None
            
            # NFT id
            if key == "launcher_id":
                puzzle_hash = value
                prefix = "nft"
                converted_value = encode_puzzle_hash(bytes32.from_hexstr(puzzle_hash), prefix)
                nft_json[key] = converted_value
            elif "puzhash" in key or "puzzle_hash" in key or "coin_id" in key:
                puzzle_hash = value
                prefix = "xch"
                converted_value = encode_puzzle_hash(bytes32.from_hexstr(puzzle_hash), prefix)
                nft_json[key] = converted_value
            elif key == "owner_did":
                puzzle_hash = value
                prefix = "chia:did"
                converted_value = encode_puzzle_hash(bytes32.from_hexstr(puzzle_hash), prefix)
                nft_json[key] = converted_value
            # technically could do this but then it won't match chain_info data
            # elif isinstance(value, str) and value[:2] == "0x":
                # nft_json[key] = value[2:]
            
            if puzzle_hash != None:
                converted_value = encode_puzzle_hash(bytes32.from_hexstr(puzzle_hash), prefix)
                nft_json[key] = converted_value
    
    return nft_list

def list_of_nfts_simple(chia_nft_list_json):
    nft_id_list = []
    
    for nft_num in chia_nft_list_json:
        
        nft_info_json = chia_nft_list_json[nft_num]
        
        nft_id = nft_info_json["launcher_id"]
        
        # print("nft_id:" + nft_id)
        string_to_display = nft_num
        
        edition_num = nft_info_json["edition_number"]
        edition_total = nft_info_json["edition_total"]
        
        if edition_num != None and edition_total != None:
            string_to_display += f"|{str(edition_num)}/{str(edition_total)}"
        
        string_to_display += f"|{nft_id}"
        
        nft_id_list.append(string_to_display)
    
    return nft_id_list

def list_of_nfts_json(chia_nft_list_json):
    nft_id_list = {}
    
    nft_num = 1
    for nft_json in chia_nft_list_json:
        
        new_attributes = {}
        
        new_attributes["launcher_id"] = nft_json["launcher_id"]
        
        editions_total = nft_json["edition_total"]
        if editions_total > 1:
            new_attributes["edition_number"] = nft_json["edition_number"]
            new_attributes["edition_total"] = editions_total
        
        nft_id_list[str(nft_num)] = new_attributes
        nft_num += 1
    
    return nft_id_list

def nft_list_all(wallet_id, raw_output=False, json_output=False):
    
    all_nfts_json = chia_wallet_list_nfts(wallet_id)
    all_nfts_json_encoded = list_of_nfts_raw_and_encoded(all_nfts_json)
    
    if raw_output == True:
        print(json.dumps(all_nfts_json_encoded, sort_keys=False, indent=4))
    elif json_output == True:
        list = list_of_nfts_json(all_nfts_json_encoded)
        print(json.dumps(list, sort_keys=False, indent=4))
    else:
        list = list_of_nfts_json(all_nfts_json_encoded)
        nft_id_list = list_of_nfts_simple(list)
        print("\n".join(nft_id_list))
    

def get_args():
    
    parser = argparse.ArgumentParser(description='Generate Chia offers, list available Chia NFTs in a wallet, generate offers in series.')
    
    ## Assumes metadata is validated
    parser.add_argument('-l', '--list-all-nfts', action='store_true', required=False, help='Output a list of all NFTs.')
    parser.add_argument('-wi', '--wallet-id', metavar=('CHIA_WALLET_ID'), nargs=1, required=False, help='Chia wallet ID')
    # parser.add_argument('-wf', '--wallet-fingerprint', metavar=('CHIA_WALLET_FINGERPRINT'), nargs=1, required=False, help='Chia wallet fingerprint')
    parser.add_argument('-r', '--raw-output', action='store_true', required=False, help='Will show exactly what chia wallet RPC command shows AND encodes hex to hashes.')
    parser.add_argument('-j', '--json-output', action='store_true', required=False, help='Output the list as JSON instead.')
    
    if len(sys.argv) < 2:
        # parser.print_usage()
        parser.print_help()
        sys.exit(1)
    
    return parser.parse_args()

async def main():
    
    ARGS = get_args()
    
    is_json_output = False
    is_raw_output = False
    
    if ARGS.list_all_nfts:
        wallet_id = ARGS.wallet_id[0]
        
        if ARGS.json_output:
            is_json_output = True
        
        if ARGS.raw_output:
            is_raw_output = True
        
        # nft_list_all(wallet_id, wallet_fingerprint, json_output)
        nft_list_all(wallet_id, is_raw_output, is_json_output)

# Prevent auto executing main when called from another program
if __name__ == "__main__":
    asyncio.run(main())
