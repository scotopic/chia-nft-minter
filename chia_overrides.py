import pathlib
from decimal import Decimal
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

import aiohttp

from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16
from chia.cmds.cmds_util import get_any_service_client

# Other useful links
#   https://github.com/Chia-Network/chia-blockchain/blob/1.6.2/chia/cmds/wallet.py
#   https://github.com/Chia-Network/chia-blockchain/blob/1.6.2/chia/cmds/wallet_funcs.py
#   https://github.com/Chia-Network/chia-blockchain/blob/1.6.2/chia/rpc/wallet_rpc_client.py

# https://github.com/Chia-Network/chia-blockchain/blob/1.6.2/chia/cmds/cmds_util.py
async def execute_with_wallet(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
    extra_params: Dict[str, Any],
    function: Callable[[Dict[str, Any], WalletRpcClient, int], Awaitable[None]],
):
    wallet_client: Optional[WalletRpcClient]
    async with get_any_service_client("wallet", wallet_rpc_port, fingerprint=fingerprint) as (wallet_client, _, new_fp):
        if wallet_client is not None:
            assert new_fp is not None  # wallet only sanity check
            result = await function(extra_params, wallet_client, new_fp)
            
            return result
        else:
            return "ERROR: oh boy, you better look at the source code now x_x"
            


# https://github.com/Chia-Network/chia-blockchain/blob/1.5.1/chia/cmds/wallet_funcs.py
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.server.start_wallet import SERVICE_NAME
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
async def list_nfts(args: Dict, wallet_client: WalletRpcClient, fingerprint: int):
    wallet_id = args["wallet_id"]
    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
        response = await wallet_client.list_nfts(wallet_id)
        nft_list = response["nft_list"]
        # if len(nft_list) > 0:
        #     for n in nft_list:
        #         nft = NFTInfo.from_json_dict(n)
        #         # print_nft_info(nft, config=config)
        #         print("-----")
        #         # print(nft)
        #         n["launcher_id"] = encode_puzzle_hash(nft.launcher_id, AddressType.NFT.hrp(config))
        #         print(json.dumps(n, sort_keys=False, indent=4))
        # else:
        #     print(f"No NFTs found for wallet with id {wallet_id} on key {fingerprint}")
        return nft_list
    except Exception as e:
        print(f"Failed to list NFTs for wallet with id {wallet_id} on key {fingerprint}: {e}")
        return None


# https://github.com/Chia-Network/chia-blockchain/blob/1.5.1/chia/cmds/wallet_funcs.py

from chia.cmds.units import units
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import bech32_decode, decode_puzzle_hash, encode_puzzle_hash
from chia.util.ints import uint32, uint64
from chia.wallet.nft_wallet.nft_info import NFTInfo
from chia.wallet.trading.offer import Offer
async def make_offer(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    offers: List[str] = args["offers"]
    requests: List[str] = args["requests"]
    filepath: str = args["filepath"]
    fee: int = int(Decimal(args["fee"]) * units["chia"])
    skip_prompts: bool = args["skip_prompts"]
    
    if [] in [offers, requests]:
        print("Not creating offer: Must be offering and requesting at least one asset")
    else:
        offer_dict: Dict[Union[uint32, str], int] = {}
        driver_dict: Dict[str, Any] = {}
        printable_dict: Dict[str, Tuple[str, int, int]] = {}  # Dict[asset_name, Tuple[amount, unit, multiplier]]
        nft_warning: bool = False
        for item in [*offers, *requests]:
            name, amount = tuple(item.split(":")[0:2])
            try:
                id: Union[uint32, str] = bytes32.from_hexstr(name).hex()
                unit = 1
            except ValueError:
                try:
                    hrp, _ = bech32_decode(name)
                    if hrp == "nft":
                        coin_id = decode_puzzle_hash(name)
                        unit = 1
                        info = NFTInfo.from_json_dict((await wallet_client.get_nft_info(coin_id.hex()))["nft_info"])
                        nft_warning = True
                        id = info.launcher_id.hex()
                        assert isinstance(id, str)
                        if item in requests:
                            driver_dict[id] = {
                                "type": "singleton",
                                "launcher_id": "0x" + id,
                                "launcher_ph": "0x" + info.launcher_puzhash.hex(),
                                "also": {
                                    "type": "metadata",
                                    "metadata": info.chain_info,
                                    "updater_hash": "0x" + info.updater_puzhash.hex(),
                                },
                            }
                            if info.supports_did:
                                assert info.royalty_puzzle_hash is not None
                                driver_dict[id]["also"]["also"] = {
                                    "type": "ownership",
                                    "owner": "()",
                                    "transfer_program": {
                                        "type": "royalty transfer program",
                                        "launcher_id": "0x" + info.launcher_id.hex(),
                                        "royalty_address": "0x" + info.royalty_puzzle_hash.hex(),
                                        "royalty_percentage": str(info.royalty_percentage),
                                    },
                                }
                    else:
                        id = decode_puzzle_hash(name).hex()
                        assert hrp is not None
                        unit = units[hrp]
                except ValueError:
                    id = uint32(int(name))
                    if id == 1:
                        name = "XCH"
                        unit = units["chia"]
                    else:
                        name = await wallet_client.get_cat_name(str(id))
                        unit = units["cat"]
            multiplier: int = -1 if item in offers else 1
            printable_dict[name] = (amount, unit, multiplier)
            if id in offer_dict:
                print("Not creating offer: Cannot offer and request the same asset in a trade")
                break
            else:
                offer_dict[id] = int(Decimal(amount) * unit) * multiplier
        else:
            print("Creating Offer")
            print("--------------")
            print()
            print("OFFERING:")
            for name, data in printable_dict.items():
                amount, unit, multiplier = data
                if multiplier < 0:
                    print(f"  - {amount} {name} ({int(Decimal(amount) * unit)} mojos)")
            print("REQUESTING:")
            for name, data in printable_dict.items():
                amount, unit, multiplier = data
                if multiplier > 0:
                    print(f"  - {amount} {name} ({int(Decimal(amount) * unit)} mojos)")
            
            if skip_prompts == False:
                if nft_warning:
                    nft_confirmation = input(
                        "Offers for NFTs will have royalties automatically added.  "
                        + "Are you sure you would like to continue? (y/n): "
                    )
                    if nft_confirmation not in ["y", "yes"]:
                        print("Not creating offer...")
                        return
            
            if skip_prompts == False:
                confirmation = input("Confirm (y/n): ")
                if confirmation not in ["y", "yes"]:
                    print("Not creating offer...")
                    return
            
            offer, trade_record = await wallet_client.create_offer_for_ids(
                offer_dict, driver_dict=driver_dict, fee=fee
            )
            if offer is not None:
                with open(pathlib.Path(filepath), "w") as file:
                    file.write(offer.to_bech32())
                print(f"Created offer with ID {trade_record.trade_id}")
                print(f"To view status:\nchia wallet get_offers --id {trade_record.trade_id} -f {fingerprint}")
            else:
                print("Error creating offer")
