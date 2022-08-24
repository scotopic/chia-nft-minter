import os
import sys
import argparse
import asyncio
import pathlib
import json
import hashlib

def checksum(filename, hash_factory=hashlib.sha256, chunk_num_blocks=128):
    h = hash_factory()
    with open(filename,'rb') as f: 
        while chunk := f.read(chunk_num_blocks*h.block_size): 
            h.update(chunk)
    return h.hexdigest()

def hashes_in_dir(dir_path, file_extension_to_check):
    hashes_list = []
    
    dir_enumerator = os.listdir(dir_path)
    dirs_sorted = sorted(dir_enumerator)
    
    for count, filename in enumerate(dirs_sorted):
        
        path = os.path.join(dir_path, filename)
        
        file_stem = pathlib.Path(filename).stem
        file_extension = pathlib.Path(filename).suffix
        
        if file_extension != file_extension_to_check:
            continue
        
        try:
            hash = checksum(path)
            hashes_list.append(hash)
        except Exception as e:
            print(e)
            sys.exit(f"ERROR reading {path}")
    
    return hashes_list

def nft_prep_nft(nft_data_path, nft_metadata_path, nft_license_path, nft_minting_data_output_path, uri_data_ipfs, uri_metadata_ipfs, uri_license_ipfs, edition_total, royalty_percentage, royalty_address, target_address):
    
    if os.path.exists(nft_data_path) != True:
        sys.exit(f"ERROR: data dir not found in {nft_data_path}")
    if os.path.exists(nft_metadata_path) != True:
        sys.exit(f"ERROR: metadata dir not found in: {nft_metadata_path}")
    
    try:
        if os.path.exists(nft_minting_data_output_path) != True:
            os.mkdir(nft_minting_data_output_path)
    except Exception as e:
        print(e)
        sys.exit(f"ERROR creating {nft_minting_data_output_path}")
    
    print(f"Creating minting data in {nft_minting_data_output_path} ...")
    
    
    # Store hashes into a dict and write to disk after it's populated
    # hashes_dict = {
    #     "01": {
    #         "data_hash": "...",
    #         "metadata_hash": "..."
    #     }
    # }
    
    hashes_dict = {}
    
    ### PARSE DATA
    data_hashes = hashes_in_dir(nft_data_path, file_extension_to_check=".png")
    
    ### PARSE METADATA
    metadata_hashes = hashes_in_dir(nft_metadata_path, file_extension_to_check=".json")
    
    ### PARSE LICENSE
    # TODO: This should only look for 1 file
    license_hash = checksum(nft_license_path)
    
    ### ASSMEMBLE HASHES
    # TODO: This should probably be parametarized / improved
    dir_enumerator = os.listdir(nft_metadata_path)
    dirs_sorted = sorted(dir_enumerator)
    
    for count, filename in enumerate(dirs_sorted):
        
        index = count - 1
        path = os.path.join(nft_metadata_path, filename)
        
        file_stem = pathlib.Path(filename).stem
        file_extension = pathlib.Path(filename).suffix
        
        if file_extension != ".json":
            continue
        
        try:
            data_hash = data_hashes[index]
            metadata_hash = metadata_hashes[index]
            hashes_dict[f"{file_stem}"] = {"data_hash":f"{data_hash}", "metadata_hash":f"{metadata_hash}"}
            
            
            data_uri_full = f"{uri_data_ipfs}/{file_stem}.png"
            metadata_uri_full = f"{uri_metadata_ipfs}/{file_stem}.json"
            license_uri_full = uri_license_ipfs
            
            # TODO: remember the following are not here and instead of in the minter:
            # edition_number
            # wallet_id
            
            minting_metadata = {
                "uris": [data_uri_full],
                "hash": data_hash,
                "meta_uris": [metadata_uri_full],
                "meta_hash": metadata_hash,
                "license_uris": [license_uri_full],
                "license_hash": license_hash,
                "edition_total": edition_total,
                "royalty_address": royalty_address,
                "target_address": target_address,
                "royalty_percentage": royalty_percentage
            }
            
            try:
                minting_filedata_path = os.path.join(nft_minting_data_output_path, file_stem + ".json")
                with open(minting_filedata_path, 'w', encoding='utf8') as outfile:
                    json.dump(minting_metadata, outfile, sort_keys=False, indent=4, ensure_ascii=False)
            except Exception as e:
                print(e)
                sys.exit(f"ERROR writing out {minting_filedata_path}")
        except Exception as e:
            print(e)
            sys.exit(f"ERROR reading {path}")
    
    
    print('-----------')
    # print all
    print(json.dumps(hashes_dict, sort_keys=False, indent=4))
    
    # print last one for inspection
    print(json.dumps(minting_metadata, sort_keys=False, indent=4))
    print('-----------')
    
    
    
    


def get_args():
    
    parser = argparse.ArgumentParser(description='Prepate the minting data necessary to mint the NFT on Chia blockchain.')
    
    ## Assumes metadata is validated
    parser.add_argument('-pmd', '--prep-minting-data', metavar=('NFT_DATA_PATH, NFT_METADATA_PATH, NFT_LICENSE_PATH, NFT_MINTING_DATA_OUTPUT_PATH'), nargs=4, required=False, help='Provide the Chia data and metadata dirs to create the minting input data.')
    # parser.add_argument('-wi', '--wallet-index', metavar=('CHIA_WALLET_ID'), nargs=1, required=False, help='Chia wallet ID')
    # parser.add_argument('-wf', '--wallet-fingerprint', metavar=('CHIA_WALLET_FINGERPRINT'), nargs=1, required=False, help='Chia wallet fingerprint')
    parser.add_argument('-udi', '--uri-data-ipfs', metavar=('URI_DATA_IPFS'), nargs=1, required=False, help='IPFS data URI')
    parser.add_argument('-umi', '--uri-metadata-ipfs', metavar=('URI_METADATA_IPFS'), nargs=1, required=False, help='IPFS metadata URI')
    parser.add_argument('-uli', '--uri-license-ipfs', metavar=('URI_LICENSE_IPFS'), nargs=1, required=False, help='IPFS license URI')
    parser.add_argument('-ec', '--edition-total', metavar=('EDITION_TOTAL'), nargs=1, required=False, help='Total number of editions. Specify ONLY if this NFT has multiple editions. (Default: 1)')
    parser.add_argument('-rp', '--royalty-percentage', metavar=('ROYALTY_PERCENTAGE'), nargs=1, required=False, help='Royalty percentage. E.g. 200 = 2%, 3000 = 30% (Default: 0)')
    parser.add_argument('-ra', '--royalty-address', metavar=('ROYALTY_ADDRESS'), nargs=1, required=False, help='Royalty XCH address.')
    parser.add_argument('-ta', '--target-address', metavar=('TARGET_ADDRESS'), nargs=1, required=False, help='Target XCH address.')
    
    if len(sys.argv) < 2:
        # parser.print_usage()
        parser.print_help()
        sys.exit(1)
    
    return parser.parse_args()

async def main():
    
    ARGS = get_args()
    
    if ARGS.prep_minting_data:
        nft_data_path = ARGS.prep_minting_data[0]
        nft_metadata_path = ARGS.prep_minting_data[1]
        nft_license_path = ARGS.prep_minting_data[2]
        nft_minting_data_output_path = ARGS.prep_minting_data[3]
        
        # wallet_index = ARGS.wallet_index[0]
        # wallet_fingerprint = ARGS.wallet_fingerprint[0]
        uri_data_ipfs = ARGS.uri_data_ipfs[0]
        uri_metadata_ipfs = ARGS.uri_metadata_ipfs[0]
        uri_license_ipfs = ARGS.uri_license_ipfs[0]
        edition_total = ARGS.edition_total[0]
        royalty_percentage = ARGS.royalty_percentage[0]
        royalty_address = ARGS.royalty_address[0]
        target_address = ARGS.target_address[0]
        
        # nft_prep_nft(nft_data_path, nft_metadata_path, nft_license_path, nft_minting_data_output_path, wallet_index, wallet_fingerprint, uri_data_ipfs, uri_metadata_ipfs, uri_license_ipfs, edition_total, royalty_percentage, royalty_address, target_address)
        nft_prep_nft(nft_data_path, nft_metadata_path, nft_license_path, nft_minting_data_output_path, uri_data_ipfs, uri_metadata_ipfs, uri_license_ipfs, edition_total, royalty_percentage, royalty_address, target_address)

# Prevent auto executing main when called from another program
if __name__ == "__main__":
    asyncio.run(main())
