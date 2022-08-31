from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

import aiohttp

from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16
from chia.cmds.cmds_util import get_wallet

# https://github.com/Chia-Network/chia-blockchain/blob/1.5.1/chia/cmds/cmds_util.py
async def execute_with_wallet(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
    extra_params: Dict[str, Any],
    function: Callable[[Dict[str, object], WalletRpcClient, int], Awaitable[None]],
):
    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if wallet_rpc_port is None:
            wallet_rpc_port = config["wallet"]["rpc_port"]
        wallet_client = await WalletRpcClient.create(self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config)
        wallet_client_f = await get_wallet(wallet_client, fingerprint=fingerprint)
        if wallet_client_f is None:
            wallet_client.close()
            await wallet_client.await_closed()
            return None
        wallet_client, fingerprint = wallet_client_f
        result = await function(extra_params, wallet_client, fingerprint)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            print(
                f"Connection error. Check if the wallet is running at {wallet_rpc_port}. "
                "You can run the wallet via:\n\tchia start wallet"
            )
        else:
            print(f"Exception from 'wallet' {e}")
    wallet_client.close()
    await wallet_client.await_closed()
    return result



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
    
    # if len(nft_list) > 0:
    #     return nft_list
    # else:
    #     return None

