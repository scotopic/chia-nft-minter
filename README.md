# Chia NFT minter

Python project for minting Chia NFTs.

## Requirements

Python 3.8+ (hashing function)

## TODO

1. add ability for metadata project to be easily retrieved
1. DONE - create a new minting project
1. add ability to generate from a dir of metadata
 * python3 nft_upload_data_ipfs.py -gmm "_nft_meta" "_minter_data" 
                                   -wi 6
                                   -wf 234234
 * python3 nft_upload_data_arweave.py -gmm "_nft_meta" "_minter_data" 
                                   -wi 6
                                   -wf 234234
  python3 nft_mint_prep.py \
  -pmd "_nft_project/images" "_nft_project/meta" "_nft_project/license/license.txt" "_minter_data_testnet" \
  -udi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/images" \
  -umi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/meta" \
  -uli "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/license/license.txt" \
  -ec 16 \
  -rp 500 \
  -ra txch1qu9ef2fczxfnthw6lmnsy7r3j2ysff26kaw3ghnmjr77va07ftrs0lapgu \
  -ta txch1qu9ef2fczxfnthw6lmnsy7r3j2ysff26kaw3ghnmjr77va07ftrs0lapgu

  python3 nft_mint_prep.py \
  -pmd "_nft_project/images" "_nft_project/meta" "_nft_project/license/license.txt" "_minter_data_mainnet" \
  -udi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/images" \
  -umi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/meta" \
  -uli "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/license/license.txt" \
  -ec 16 \
  -rp 500 \
  -ra xch1yyfjncad4msh79a4rxvr592vhe2f74h4wutgcjzuqlhsxdepc6ts004h6v \
  -ta xch1yyfjncad4msh79a4rxvr592vhe2f74h4wutgcjzuqlhsxdepc6ts004h6v


 * python3 nft_mint_nft.py -md "_minter_data_mainnet" 
                           -wi 6
                           -fm 100
  python3 nft_mint_nft.py \
  -md "_minter_data_testnet" \
  -wi 3 \
  -fm 100
  
  python3 nft_mint_nft.py \
  -md "_minter_data_mainnet" \
  -wi 3 \
  -fm 100
  
    add ability to pre-split coins? perhaps as separate tool?
    add a "if coinbalance > 0 && < necessary amount for fee then mint, otherwise wait 10 seconds ?"
    
 * python3 nft_create_offers.py -m "_minter_data" 
                                -wi 6
                                -wf 234234
  
    {
        "wallet_id": 6,
        "uris": ["https://mnjrjtdzc5ng6sq5ur3vt7dqcwop3hobgfc4qa4ouum5445c5poq.arweave.net/Y1MUzHkXWm9KHaR3WfxwFZz9ncExRcgDjqUZ3nOi690","ar://Y1MUzHkXWm9KHaR3WfxwFZz9ncExRcgDjqUZ3nOi690"],
        "hash": "18534cd1d3e7b2d2b5a6064beb4081dc0555d9f157d00da65df8b0a01e706c76",
        "meta_uris": ["https://zofqxdagit2nlgu6yo2zig24zwq7dsjrurvpoa47diootuocajxq.arweave.net/y4sLjAZE9NWansO1lBtczaHxyTGkavcDnxoc6dHCAm8","ar://y4sLjAZE9NWansO1lBtczaHxyTGkavcDnxoc6dHCAm8"],
        "meta_hash": "d2397ec3c236950d4c4793b45d1c228788af7d84de57af865d5d9b335229a2ff",
        "license_uris": ["https://vgowprh5i3k5nkq4cxcctpzoflomoabq5k5kzqcyldr4brs6.arweave.net/qZ1nxP1G1daqHBXEKb-8uKtzHADDquqzAWFjjwM_Zew"],
        "license_hash": "270ac935b3f45d71b50fbe395f81ce099d76efd8e3a7c0e622712e2aa2e338af",
        "edition_number": 1,
        "edition_count": 1,
        "royalty_address": "xch1rtgkqnqfr8na9hg7atuwmmuvtcf2qp0ugs7faqvxw7pk0c6llqsqryz4my",
        "target_address": "xch1rtgkqnqfr8na9hg7atuwmmuvtcf2qp0ugs7faqvxw7pk0c6llqsqryz4my",
        "royalty_percentage": 100
    }
    
    python3 nft_mint_prep.py \
    -pmd "_nft_project/images" "_nft_project/meta" "_nft_project/license/license.txt" "_minter_data" \
    -wi 6 \
    -udi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/data" \
    -umi "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/meta" \
    -uli "https://nftstorage.link/ipfs/bafybeia7ho4ppghgqd5klrrxd3dwrqsjzhxt33klogttphcxaaerhmrfkq/license/license.txt" \
    -ec 16 \
    -rp 400 \
    -ra xch1rtgkqnqfr8na9hg7atuwmmuvtcf2qp0ugs7faqvxw7pk0c6llqsqryz4my \
    -ta xch1rtgkqnqfr8na9hg7atuwmmuvtcf2qp0ugs7faqvxw7pk0c6llqsqryz4my
    
1. add ability to mint based on above output on testnet
 * individual
 * series
1. add ability to create offer files
 * individual
 * series


1. testnet: send mint data files to server
1. testnet: run a mint on testnet
1. mainnet: send mint data files to server
1. mainnet: send DID to FUP wallet, send XCH to FUP wallet
1. mainnet: run mint