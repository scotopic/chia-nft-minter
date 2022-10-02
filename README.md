# Chia NFT minter and NFT toolset

Python project for minting Chia NFTs.

## Tools

Assumes you provide an nft project as such:
    
    _your_nft_project/
                      images/
                      meta/
                      license/license.txt

1. `nft_mint_prep.py` takes your NFT project metadata and creates the data for Chia `nft_mint_nft` RPC calls to use as input.
 * Assumption: valid Chia's CHIP-0007 (or whatever is latest) metadata.
 * I created/use https://github.com/scotopic/nft-generate-metadata to generate Chia NFT metadata.
1. `nft_mint_nft.py` uses data from `nft_mint_prep.py` and calls `chia rpc `chia rpc wallet nft_mint_nft` to mint.


## Setup

`nft_offers.py` requires Chia dependencies:

    python3 -m venv venvnft
    . ./venvnft/bin/activate
    pip3 install -r requirements.txt

### Troubleshooting

On Ubuntu 20.04.4 LTS if you get:

    ERROR: Command errored out with exit status 1
    ...
    error: invalid command 'bdist_wheel'
    ----------------------------------------
    ERROR: Failed building wheel for zstd

Fix:

    sudo apt install python3.8-venv python3.8-dev


## Usage

### NFT prep minter data

Testnet

    python3 nft_mint_prep.py \
    -pmd "_nft_project/images" "_nft_project/meta" "_nft_project/license/license.txt" "_minter_data_testnet" \
    -udi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/images" \
    -umi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/meta" \
    -uli "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/license/license.txt" \
    -ec 16 \
    -rp 500 \
    -ra txch1qu9ef2fczxfnthw6lmnsy7r3j2ysff26kaw3ghnmjr77va07ftrs0lapgu \
    -ta txch1qu9ef2fczxfnthw6lmnsy7r3j2ysff26kaw3ghnmjr77va07ftrs0lapgu

Mainnet

    python3 nft_mint_prep.py \
    -pmd "_nft_project/images" "_nft_project/meta" "_nft_project/license/license.txt" "_minter_data_mainnet" \
    -udi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/images" \
    -umi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/meta" \
    -uli "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/license/license.txt" \
    -ec 16 \
    -rp 500 \
    -ra xch1yyfjncad4msh79a4rxvr592vhe2f74h4wutgcjzuqlhsxdepc6ts004h6v \
    -ta xch1yyfjncad4msh79a4rxvr592vhe2f74h4wutgcjzuqlhsxdepc6ts004h6v

## NFT mint using minter data

Testnet

    python3 nft_mint_nft.py \
    -md "_minter_data_testnet" \
    -wi 3 \
    -fm 100 \
    -oa txch10z3zg92wn24wuqqylp8cz44wgttc5texrmqdt05u8hwlhygklscq4pne3z \
    -dry

Mainnet
  
    python3 nft_mint_nft.py \
    -md "_minter_data_mainnet" \
    -wi 3 \
    -fm 100
    -dry

Background execution

    ## Run in background (Ubuntu)
    nohup python3 nft_mint_nft.py -md "_minter_data_mainnet" -wi 3 -fm 100 > _minting_mainnet_log.txt &
    
    ## Checking on minting
    tail -f _minting_mainnet_log.txt
    

## NFT offer tools

### List all NFTs ( and convert/encode hex to hash )

Simple list of NFT IDs

    python3 nft_offers.py -l \
                          -wf 3936560748 \
                          -wi 3
    

Simple list of NFT IDs formatted as JSON

    python3 nft_offers.py -l \
                          -wf 3936560748 \
                          -wi 3 \
                          -j
    

Raw output with encoded NFT/XCH/DID values (chia rpc wallet nft_get_nfts)

    python3 nft_offers.py -l \
                          -wf 3936560748 \
                          -wi 3 \
                          -r

Output the NFTs for a specific edition

    python3 nft_offers.py -l \
                          -wf 3936560748 \
                          -wi 3 \
                          -en 1

Equivalent Chia RPC/CLI commands:

    chia rpc wallet nft_get_nfts '{"wallet_id": 3}'
    chia wallet nft list -i 3 -f 3936560748

### Create NFT offer files

Create offer for a single NFT for XCH (price is per NFT)

    python3 nft_offers.py -co \
                          -wf 3936560748 \
                          -o nft1uc56qc53qyf4fcrffmf2th4zeujrtq5hadjwl9djytgcf6aktaws0z9c49 \
                          -xch 0.1 \
                          -pn fup \
                          -fo _offers_single
  
Create offer for a edition # NFTs for XCH (price is per NFT)

    python3 nft_offers.py -co \
                          -wf 3936560748 \
                          -wi 3 \
                          -en 2 \
                          -xch 0.1 \
                          -pn fup \
                          -fo _offers_edition

Create offer for all NFTs for XCH (price is per NFT)

    python3 nft_offers.py -co \
                          -wf 3936560748 \
                          -wi 3 \
                          -en 0 \
                          -xch 0.1 \
                          -pn fup \
                          -fo _offers_editions

Equivalent Chia RPC/CLI commands:

    chia wallet make_offer -f 3936560748 -o nft1uc56qc53qyf4fcrffmf2th4zeujrtq5hadjwl9djytgcf6aktaws0z9c49:1 -r 1:0.3 -p 1fup_x_0.3xch.offer


### Upload NFT offer files

Upload the offer files to https://dexie.space/api

    python3 nft_offers.py -up -fo _offers_editions

Equivalent dexie.space API call:

    curl -X POST -H 'Content-Type: application/json' -d '{"offer":"offer1..."}' https://api-testnet.dexie.space/v1/offers



## Requirements

Python 3.8+ (hashing function)

## TODO

1. add ability for metadata project to be easily retrieved
1. add ability to generate from a dir of metadata
 * python3 nft_upload_data_ipfs.py -gmm "_nft_meta" "_minter_data" 
                                   -wi 6
                                   -wf 234234
 * python3 nft_upload_data_arweave.py -gmm "_nft_meta" "_minter_data" 
                                   -wi 6
                                   -wf 234234

1. Minting: Add sample project for anyone to use to mint on testnet
1. Minting: Add ability to pre-split coins? perhaps as separate tool?
   * Does this work? Does Chia wallet pick largest coin first?
   * What happens when they change this algo?

         python3 chia_coin_split.py -scm 100 (split coin mojos)
                                    -sci 384 (split coin iterations)
                                    -wi 1
                                    -wf 234234
1. NFT offers
 * python3 nft_offers.py -go "collection_id"
                         -wi 6
                         -wf 234234


 * python3 nft_offers.py -go "collection_id"
                         -wi 6
                         -wf 234234
 * python3 nft_offers.py -co "collection_id"
                         -ni "nft_id"
                         -xp 0.1
 * python3 nft_offers.py -co "collection_id"
                          -ni "nft_id"
                         -ens "edition_number" single
                         -xp 0.1
 * python3 nft_offers.py -co "collection_id"
                         -enb "edition_number" bundle
                         -xp 2.4
    
        get a list of all nfts
          chia rpc wallet nft_get_nfts '{"wallet_id": 3}'
          chia wallet nft list -i 3 -f 3936560748
          chia wallet show -f 3936560748
          
        which are part of THIS collection ?
        
        generate offers for 1 nft for X.X XCH
        
        generate offers for a list of NFTs for X.X XCH
        
        -> https://chialisp.com/docs/tutorials/offers_cli_tutorial/
        chia wallet make_offer -f 3936560748 -o nft1u72s8payxfxljcdupr5nfqe0rjsfzqpux8z6vafjyy3ahd3vkj4sdw00ma:1 -r nft1y7aj90hvt4ypj0279jjj2m4hxr8pjjqsrcjfrj6a670t36wq7xxsnnje9f:1 -p offerfile.offer
        
        -> https://chialisp.com/docs/tutorials/offers_cli_tutorial/#create-a-multiple-token-offer
        chia wallet make_offer -f 3936560748 -o nft1uc56qc53qyf4fcrffmf2th4zeujrtq5hadjwl9djytgcf6aktaws0z9c49:1 -o nft1zzf5ddlc44aac53f75y5vkjgzmuhn4xrp6scza389f3qhkl3pzkqe8f74v:1 -o nft17j3s84mlz5jk6slkdfk5svqt4ly84cq5qprc8tlqqnr8yawzrhfqjy6q92:1 -r 1:0.3 -p ~/offers/1fup_1fup_1fup_for_0.3xch.offer
        
        generate offers for a editions of NFTs for X.X XCH
    
1. add ability to mint based on above output on testnet
 * individual
 * series
1. add ability to create offer files
 * individual
 * series






