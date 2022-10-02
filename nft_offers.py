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
                
                string_to_display += f"|{edition_num_str}/{str(edition_total)}"
            
        
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





####################################################################
#     OFFER CREATION
####################################################################
from chia_overrides import make_offer
from chia_overrides import execute_with_wallet
from chia.server.start_wallet import SERVICE_NAME
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
async def nft_create_offer(wallet_fingerprint, offer, xch_request, project_name, file_output_dir, fee=0, skip_prompts=True, edition_number=None):
    '''
    nft_to_offer = coins_maker[0]
    nft_info: Optional[PuzzleInfo] = match_puzzle(nft_to_offer.full_puzzle)
    nft_asset_id: bytes32 = create_asset_id(nft_info)  # type: ignore
    driver_dict: Dict[bytes32, Optional[PuzzleInfo]] = {nft_asset_id: nft_info}

    xch_request = 100
    maker_fee = uint64(10)
    offer_nft_for_xch = {wallet_maker.id(): xch_request, nft_asset_id: -1}

    success, trade_make, error = await trade_manager_maker.create_offer_for_ids(
        offer_nft_for_xch, driver_dict, fee=maker_fee
    )
    assert success is True
    assert error is None
    assert trade_make is not None
    '''
    print("making an offer ...")
    
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    wallet_rpc_port = None
    
    if edition_number:
        offer_file_name=f"{project_name}_ed_{edition_number}_{offer}_x_{xch_request}_xch.offer"
    else:
        offer_file_name=f"{project_name}_{offer}_x_{xch_request}_xch.offer"
    
    offer = f"{offer}:1"
    request = f"1:{xch_request}"
    filepath = f"{file_output_dir}/{offer_file_name}"
    extra_params = {"offers": [offer], "requests": [request], "filepath": filepath, "fee": fee, "skip_prompts": skip_prompts}
    
    try:
        if os.path.exists(file_output_dir) != True:
            os.mkdir(file_output_dir)
    except Exception as e:
        print(e)
        sys.exit(f"ERROR creating {file_output_dir}")
    
    print('---------')
    print(extra_params)
    print('---------')
    await execute_with_wallet(wallet_rpc_port, wallet_fingerprint, extra_params, make_offer)
    
    # make_offer_cmd(1, 3936560748, "nft16lf2eyrhhaalslhtvhwa9xufyx8gccn9ytqjy0kwpakt2pz2ylsq7kvl5d:1", "1:0.3", "test_offer.offer")
    print("done making an offer")


async def nft_create_offer_for_edition(wallet_fingerprint, wallet_id, xch_request, project_name, file_output_dir, edition_number, fee=0, skip_prompts=True):
    
    # get a list of NFTs to edition
    all_nfts_json_encoded = await get_nft_list(wallet_id, wallet_fingerprint)
    
    # loop through each and create offers
    for nft_to_offer in all_nfts_json_encoded:
        
        # offers for ALL editions/NFTs
        nft_id = nft_to_offer["launcher_id_as_nft"]
        nft_edition_num = nft_to_offer["edition_number"]
        
        if edition_number > 0 and edition_number != nft_edition_num:
            # skip non-specified editions
            continue
        
        await nft_create_offer(wallet_fingerprint, nft_id, xch_request, project_name, file_output_dir, fee, skip_prompts, nft_edition_num)

import requests
import json
import pathlib
async def nft_upload_offers(file_output_dir):
    
    DEXIE_URI_TESTNET = "https://api-testnet.dexie.space/v1/offers"
    DEXIE_URI_MAINNET = "https://api.dexie.space/v1/offers"
    
    if os.path.exists(file_output_dir) != True:
        sys.exit(f"ERROR output dir not found: {file_output_dir}")
    
    using_testnet = True
    dexie_api_uri = DEXIE_URI_TESTNET
    
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    
    chia_selected_network = config["selected_network"]
    
    if "mainnet" in chia_selected_network:
        dexie_api_uri = DEXIE_URI_MAINNET
        using_testnet = False
    
    print(f"uploading offers via {dexie_api_uri}")
    
    # POST https://api.dexie.space/v1/offers
    # curl -X POST -H 'Content-Type: application/json' -d '{"offer":"offer1..."}' https://api.dexie.space/v1/offers
    
    dir_enumerator = os.listdir(file_output_dir)
    dirs_sorted = sorted(dir_enumerator)
    
    file_index = 1
    for count, filename in enumerate(dirs_sorted):
        
        file_extension = pathlib.Path(filename).suffix
        
        if ".offer" not in file_extension:
            continue
        
        full_file_path = f"{file_output_dir}/{filename}"
        try:
            with open(full_file_path, 'r') as infile:
                offer_file = infile.readline()
        except Exception as e:
            print(e)
            sys.exit(f"ERROR reading {full_file_path}")
        
        offer_file_json_payload = {"offer": f"{offer_file}"}
        
        upload_response = requests.post(dexie_api_uri, json=offer_file_json_payload)
        
        # print(upload_response.status_code)
        # print(upload_response.json())
        
        filename_response = filename + ".response"
        json_response = upload_response.json()
        
        resp_string = "error"
        if json_response["success"] == True:
            resp_string = "success"
        
        known_string = '-'
        if 'known' in json_response and json_response["known"] == True:
            known_string = "known"
            
        print(f"{file_index} | {resp_string} | {known_string}")
        
        # save the json
        try:
            with open(f"{file_output_dir}/" + filename_response, 'w') as outfile:
                json.dump(json_response, outfile, sort_keys=False, indent=4)
        except Exception as e:
            print(e)
            sys.exit(f"ERROR writing out {filename_response}")
        
        file_index += 1
    

def get_args():
    
    parser = argparse.ArgumentParser(description='Generate Chia offers, list available Chia NFTs in a wallet, generate offers in series.')
    
    ## Available commands (assumes metadata is validated)
    parser.add_argument('-l', '--list-all-nfts', action='store_true', required=False, help='Output a list of all NFTs.')
    parser.add_argument('-co', '--create-offer', action='store_true', required=False, help='Create Chia NFT offer file.')
    parser.add_argument('-up', '--upload-offers', action='store_true', required=False, help='Upload Chia NFT offers to Dexie.space')
    
    # Required inputs
    parser.add_argument('-wi', '--wallet-id', metavar=('CHIA_WALLET_ID'), nargs=1, type=int, required=False, help='Chia wallet ID')
    parser.add_argument('-wf', '--wallet-fingerprint', metavar=('CHIA_WALLET_FINGERPRINT'), nargs=1, type=int, required=False, help='Chia wallet fingerprint')
    
    # Optional params
    parser.add_argument('-r', '--raw-output', action='store_true', required=False, help='Will show exactly what chia wallet RPC command shows AND encodes hex to hashes.')
    parser.add_argument('-j', '--json-output', action='store_true', required=False, help='Output the list as JSON instead.')
    parser.add_argument('-en', '--edition-number', metavar=('NFT_EDITION_NUMBER'), nargs=1, type=int, required=False, help='Only show/use NFTs with this edition number.')
    
    ## Making offers
    parser.add_argument('-o', '--offering', metavar=('NFT_OFFER'), nargs=1, required=False, help='NFT being offered')
    parser.add_argument('-xch', '--xch-request', metavar=('XCH_REQUEST'), nargs=1, required=False, help='XCH amount being asked. ')
    parser.add_argument('-pn', '--project-name', metavar=('NFT_PROJECT_NAME'), nargs=1, required=False, help='Short identifier to add to offer file eg. dogs, fup, ghosts')
    parser.add_argument('-fo', '--file-output-dir', metavar=('OFFER_FILE_OUTPUT_DIR'), nargs=1, required=False, help='Filepath of the offer to create')
    parser.add_argument('-m', '--fee', metavar=('OFFER_FEE'), nargs=1, required=False, help='Offer fee (default = 0)')
    parser.add_argument('-sp', '--skip-prompts', metavar=('SKIP_PROMPRTS'), nargs=1, type=bool, required=False, help='Skip any confirmation prompts (Default: True)')
    
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
    fee = 0
    skip_prompts = True
    
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
    
    if ARGS.create_offer:
        wallet_fingerprint = ARGS.wallet_fingerprint[0]
        
        xch_request = ARGS.xch_request[0]
        project_name = ARGS.project_name[0]
        file_output_dir = ARGS.file_output_dir[0]
        
        if ARGS.fee:
            fee = ARGS.fee[0]
        
        if ARGS.skip_prompts:
            skip_prompts = ARGS.skip_prompts[0]
        
        if ARGS.edition_number:
            wallet_id = ARGS.wallet_id[0]
            edition_number = ARGS.edition_number[0]
            
            await nft_create_offer_for_edition(wallet_fingerprint, wallet_id, xch_request, project_name, file_output_dir, edition_number, fee, skip_prompts)
        else:
            offer = ARGS.offering[0]
            
            await nft_create_offer(wallet_fingerprint, offer, xch_request, project_name, file_output_dir, fee, skip_prompts)
    
    if ARGS.upload_offers:
        
        file_output_dir = ARGS.file_output_dir[0]
        
        await nft_upload_offers(file_output_dir)

# Prevent auto executing main when called from another program
if __name__ == "__main__":
    asyncio.run(main())
