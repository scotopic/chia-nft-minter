import os
import sys
import argparse
import asyncio
import pathlib
import json
import time
from subprocess import PIPE, Popen

def chia_wallet_get_balance(wallet_id):
    print("get wallet balance ...")
    command  = """chia rpc wallet get_wallet_balance '{"wallet_id": 1}'"""
    
    with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
        output = process.communicate()[0].decode("utf-8")
        # print(output)
    
    try:
        wallet_response_json = json.loads(output)
        
        # print('-----------')
        # print(json.dumps(wallet_response_json, sort_keys=False, indent=4))
        # print('-----------')
        
        if wallet_response_json["success"] == True:
            wallet_balance_json = wallet_response_json["wallet_balance"]
        else:
            sys.exit(f"ERROR getting wallet balance")
        
    except Exception as e:
        print(e)
        sys.exit(f"ERROR reading {wallet_json}")
    
    print('-----------')
    print(json.dumps(wallet_response_json, sort_keys=False, indent=4))
    print('-----------')
    
    return wallet_balance_json

def chia_mint(minter_data):
    # minter_json_string = json.dumps(minter_data, sort_keys=False)
#     print("chia rpc wallet nft_mint_nft '" + minter_json_string + "';sleep 200;")
    
    print('-------------')
    print("STARTING MINT")
    
    while True:
        can_mint = False
        
        print("mint sleeping...")
        time.sleep(20)
        
        output = chia_wallet_get_balance(1)
        standard_balance = output["spendable_balance"]
        standard_total = output["confirmed_wallet_balance"]
        
        print('!!!')
        print(standard_balance)
        print(standard_total)
        print('!!!')
        
        # if standard_balance > 0 and standard_balance == standard_total:
        if standard_balance > 0 and standard_balance > 100000:
            print("yay")
            can_mint = True
        
        if can_mint is False:
            print("nope")
            continue
        
        print("mint goooooo...")
        minter_json_string = json.dumps(minter_data, sort_keys=False)
        minter_command  = "chia rpc wallet nft_mint_nft '" + minter_json_string + "'"
        
        with Popen(minter_command, stdout=PIPE, stderr=None, shell=True) as process:
            output = process.communicate()[0].decode("utf-8")
            print(output)
        print(minter_command)
        break
    

def nft_mint_nft(nft_data_path, wallet_id, fee_mojos, override_address):
    
    if os.path.exists(nft_data_path) != True:
        sys.exit(f"ERROR: data dir not found in {nft_data_path}")
    
    print(f"Attempting to minting data in {nft_data_path} ...")
    
    dir_enumerator = os.listdir(nft_data_path)
    dirs_sorted = sorted(dir_enumerator)
    
    for count, filename in enumerate(dirs_sorted):
        
        index = count - 1
        path = os.path.join(nft_data_path, filename)
        
        file_stem = pathlib.Path(filename).stem
        file_extension = pathlib.Path(filename).suffix
        
        if file_extension != ".json":
            continue
        
        try:
            with open(path, 'r') as f:
              nft_minter_data_json = json.load(f)
        except Exception as e:
            print(e)
            sys.exit(f"ERROR reading {path}")
        
        # print('-----------')
        # print(json.dumps(nft_minter_data_json, sort_keys=False, indent=4))
        # print('-----------')
        
        if len(override_address) > 0:
            nft_minter_data_json["royalty_address"] = override_address
            nft_minter_data_json["target_address"] = override_address
        
        nft_minter_data_json["wallet_id"] = wallet_id
        nft_minter_data_json["fee"] = fee_mojos
        nft_minter_data_json["edition_number"] = 1
        
        editions_total = int(nft_minter_data_json["edition_total"])
        
        if editions_total > 1:
            for edition_num in range(1, editions_total+1):
                nft_minter_data_json["edition_number"] = edition_num
                
                chia_mint(nft_minter_data_json)
        else:
            chia_mint(nft_minter_data_json)
        


def get_args():
    
    parser = argparse.ArgumentParser(description='Mint Chia NFTs.')
    
    ## Assumes metadata is validated
    parser.add_argument('-md', '--mint-data', metavar=('NFT_MINTING_DATA_PATH'), nargs=1, required=False, help='Use the minting data as source of input for what to mint.')
    parser.add_argument('-wi', '--wallet-id', metavar=('CHIA_WALLET_ID'), nargs=1, required=False, help='Chia wallet ID')
    parser.add_argument('-fm', '--fee-mojos', metavar=('CHIA_FEE_IN_MOJOS'), nargs=1, required=False, help='Chia fees in mojos. e.g -fm 100 is 0.000000000100 XCH')
    parser.add_argument('-oa', '--override-address', metavar=('CHIA_OVERRIDE_TARGET_ADDRESS_IN_DATA'), nargs=1, required=False, help='Overrides BOTH target address and royalty address found in data.')
    
    if len(sys.argv) < 2:
        # parser.print_usage()
        parser.print_help()
        sys.exit(1)
    
    return parser.parse_args()

async def main():
    
    ARGS = get_args()
    
    if ARGS.mint_data:
        nft_data_path = ARGS.mint_data[0]
        
        wallet_id = ARGS.wallet_id[0]
        fee_mojos = ARGS.fee_mojos[0]
        
        if ARGS.override_address:
            override_address = ARGS.override_address[0]
        
        nft_mint_nft(nft_data_path, wallet_id, fee_mojos, override_address)

# Prevent auto executing main when called from another program
if __name__ == "__main__":
    asyncio.run(main())
