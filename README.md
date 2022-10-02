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

POST https://api.dexie.space/v1/offers
success	boolean	Indicates success
id	string	Base58 encoded SHA256 Offer Hash
known	boolean	Indicates whether the offer file was already known by dexie
offer	Full offer object	For details see examples

curl -X POST -H 'Content-Type: application/json' -d '{"offer":"offer1qqz83wcsltt6wcmqvpsxygqqwc7hynr6hum6e0mnf72sn7uvvkpt68eyumkhelprk0adeg42nlelk2mpafs8tkhg2qa9qmxpk8znee5xnfq4edmh0ndpyerkh6k2kw3r06amc8mhdfde2ukhre430gyjsvym5x60jsk9afzcujmrpuhcx8lp62k6202ljnklhfm0nu05zdhvht8lkucmew9j2jqqzmy0g0dja7dzmqp570l90q5fe09td3gmns7uvh85advvjalug79jnz8xe8fe2xsaha22acaazhfmt97x0pmglj7mghdy70lfk450ulnpuxalyhvcyc5gdv39wgau5y7d4lqcd4lgcd3lg6d3lg7d3lg7d3llq948usq27uz7d7e7y77xkmf5mcmrwvn2gthfzkxx75q7vu7hqmrw6r8vmfwj8264q42mvn8ruzskxlaklvrfwfyx87ch3j83dt4crhtkcpkrjk6jvreexejdv959tq2ucyx7w4tyvzpn0dzx8f7qch9m0fekynqefu6c8hstrx2uj3haptrg4yhdtxft5xf8qfn5eddwm04pzd59dxjmgk08madexcfrjqsqxx3qake07zcgxhcladasdskneuylkppfp22q7dwrkeketuykp0w8y9a5tkngc4fernrvy68sc5vfqd06e43t03edu5hmh7zlta5vsdqt2dhlzluvkua7lehmegpql9r0vma35478283kultt84zh4u5824ew83f4n8cz23jl7l6pa7tq70c0k34rg00stvazl6q9n0sfkmg3l4frkdlhe7cds4kv6rwv6q6fl0l30ny00mg2z6x4rdlmlc8e4evhhm5cuc0xve772emxk3lhatplzlkag5tl7tucjal70p85ymy52v72tk3ccvcl4xdnvwjm4g77mwf60yt2k50zqmf78l6mlqthzqkakmsw9fvlw29g0mlkat8xvvv7dvml8tkec06a8c6n5tmlfj3d46ujw5kepx6g659ranlsyskdktljmgzxtyp4ze4aar8wjnv7ltl886m2s8v4z6uvnylaeyyu7232t66vu9tutgsdwteg7ctxsxpx9rwgl3e46jamjmv3czld0ame4tflxtr6mwresff0xlxhq7ucz3mwxflc4cthufvn3n6w7pkresuhlh8slv4l0g58m2kd4knkds664ehsn770tjulalw7y30fd6hl3lnnlvlju8m8cxm7274xk43s4lkkc5vh2dav0mgqptjqg7ggwmv9c"}' https://api.dexie.space/v1/offers

Equivalent dexie.space API call:

    curl -X POST -H 'Content-Type: application/json' -d '{"offer":"offer1qqph3wlykhv8jcmqvpsxygqqwc7hynr6hum6e0mnf72sn7uvvkpt68eyumkhelprk0adeg42nlelk2mpafsyjlm5pqpj3d3q08muhhjhllnyu7fgk7gr88k3lxnvefkawfemvtz76ut24munv3m66x4g5n4ynam73ygfv66aflz20m64n4hxslrpwt0m7dha09eem9qws3z2ezlumu4wu50ksgqkerdlsf9yvkqy60j69mafzl3h3efxa7w0pjmfgt4dhzee5ud3nmzkpra8fz45rahvuk9pnnc7rnxklvtk47gkasyam8ghdv0h0nr9cw0ajh0j7tgrsc5yja86xgeverjar6qge05q3j7srdscrf8dqh66hryz7l0mm78qme55adjdw7fdcacl8x0aq8mpzg4kuafml8zedxhelutne56ujq6fz5fcu3q6dha95hm3d82hx9ke4l36uh7agn22zad4umut3awlpljr4xfxwsxzsx6xl72xdv8zmtankg46uwk4h4hvn3t90e9uu845t5ym2z4e7qvpm4apf5pps8whrxlwxwhqqjlkpq00lncr9lusy4mquphm0manvv89kke54tj6jekt9m58s9ljeulygwc8c506laq953jff9qmr9d70e095jt3f9l9zcn64f0yuej7kelxvs26k9l9ycj6v4fx5e4z09rtuj2pg9ayv7np3f5hvnj329zc5u2209gkzu2k24rytzd3w9myul366zvgeey2cnzdfg5vmj3tfmzzlhx9egzechaqdpn6q4u7jsyhv5k836uucwjt840356jmhj8y6pp62whnakf6590vl6h899jfwu4f3tqr4nmgzhd5lur4y60x5nwdfyjyjzpm9zhn7wqzuqnkqtl3lj9pn9knnxwf49uut2fst2h6fgsyv35hz84gcdf9essv7fhvdq4kyv4z7de7zdtkm4t0kca46f8f6xtf5x88h6ark5xz4z9uzm9rtuqv3xgep0z038u8455mqhu45tak03h9trrpwwlccht26a2uhu6kp555k4sjrnp9kzv0l4l9aknma6x3930lhcl8ucr9thf7w4nd0d443vna389ht6uneu7j74hze30vaqvzqjnwrgwsx8qaqvjwp8hl5d3cp3xxzd7uvqppvh0ar4d09tt67c5spegml0lqc3u6w5leze04hfpt0ehru9z5djm7n846rf2fndughh9ckraxjmtuun7lvx6zhs3hvgt7hxlsu5x4h0y77yk4gh8rksz5kyfe8ttrvwkkxczvdk4qw9zmlmk6s29y224z06e4d0trvru7rhcckm8wj75hh6ddeqdtl0nd3hha84g7crmye5frqsmlqyuslmjqkjkr2mzhh7pqmh4s6qkagdw508texu9lp2jjh60md6hfew8x44d7g2w0tnym3vkev8mn789ahz8rnv847sfftzwfs7anfz4avzjkvqe27k0hptqp24ywkf3s67lfjakeke9clel9608swsclkdklq2x77mxhh7hf50rct9xp9cpc64vpr5xxe05przc9rsq9snrxzg2eq8vwkgagzfjrsvwxlkmll0lqvqx5lhyz2af4llqsm5ug2twnx0378utuqvn8j8hlstz2tl6kqkt5tsnjdnne9w07x0h9lvn00ft75l3ehwxujv3nw0fn720f208ue77hq7mk24n0j9t05u8em402wtdup07qa0rrxzgtsxt46tuu2affvmej8hlupflaetlew752490t7xkqkzehf7gxwh9f5wftf7cvtdetwc8dw3x7z2s8wynspa5qlalsk74n3h"}' https://api-testnet.dexie.space/v1/offers



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






