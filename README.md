# Chia NFT minter

Python project for minting Chia NFTs.

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
    -oa txch10z3zg92wn24wuqqylp8cz44wgttc5texrmqdt05u8hwlhygklscq4pne3z

Mainnet
  
    python3 nft_mint_nft.py \
    -md "_minter_data_mainnet" \
    -wi 3 \
    -fm 100


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


 * python3 nft_mint_nft.py -md "_minter_data_mainnet" 
                           -wi 6
                           -fm 100
  
    add ability to pre-split coins? perhaps as separate tool?
    
 * python3 nft_create_offers.py -m "_minter_data" 
                                -wi 6
                                -wf 234234
  
  get a list of all nfts
    
      chia rpc wallet nft_get_nfts '{"wallet_id": 3}'
      chia wallet nft list -i 3 -f 3936560748
    
    
  which are part of THIS collection ?
  generate offers for 1 nft for X.X XCH
  generate offers for a list of NFTs for X.X XCH
  generate offers for a editions of NFTs for X.X XCH
    
1. add ability to mint based on above output on testnet
 * individual
 * series
1. add ability to create offer files
 * individual
 * series






