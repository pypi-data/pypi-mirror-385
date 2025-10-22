# ========================================================================================
#  Copyright (C) 2025 CryptoLab Inc. All rights reserved.
#
#  This software is proprietary and confidential.
#  Unauthorized use, modification, reproduction, or redistribution is strictly prohibited.
#
#  Commercial use is permitted only under a separate, signed agreement with CryptoLab Inc.
#
#  For licensing inquiries or permission requests, please contact: pypi@cryptolab.co.kr
# ========================================================================================

import secrets
from typing import Any, List, Optional, Tuple, Union

import evi
import numpy as np
from proto import type_pb2 as es2_type_pb
from proto.es2e import es2e_api_pb2_grpc as es2_grpc
from proto.es2e import es2e_message_pb2 as es2_msg_pb2

from es2.api.connection import Connection
from es2.crypto import CipherBlock
from es2.utils import version as version_utils
from es2.utils.logging_config import logger

###################################
# Indexer Class
###################################


class Indexer:
    """
    High-level client for managing encrypted index and performing vector search operations on the ES2 server.

    This API provides:

    - Connection to the ES2 server (local or remote)
    - Key and context setup for homomorphic encryption at server side
    - Index creation, deletion, and management (encrypted/plain(TBD))
    - Batch or incremental vector insertion (encrypted/plain)
    - Encrypted similarity search
    - Both synchronous and asynchronous search operations

    Notes
    -----
    Instances should be created via the static `connect()` methods.

    Example
    --------

    >>> indexer = Indexer.connect("localhost:50050", access_token="your_access_token")
    >>> if indexer.is_connected():
    >>>     print("Connected to ES2 service.")
    >>> else:
    >>>     print("Failed to connect to ES2 service.")

    """

    def __init__(self, connection: Connection, access_token: str = None):
        self.connection = connection
        self.stub = es2_grpc.ES2EServiceStub(connection.get_channel())
        self.access_token = access_token
        self.grpc_metadata = []
        if self.access_token:
            self.grpc_metadata.append(("authorization", f"Bearer {self.access_token}"))

    ###################################
    # Connection Management
    ###################################

    @classmethod
    def connect(cls, address: str, access_token: str = None) -> "Indexer":
        """
        Establishes a connection to the ES2 service.

        Parameters
        ----------
        address : str
            The address of the ES2 service endpoint (e.g., "localhost:50050").
        access_token : str, optional
            Access token for authentication (default: None).

        Parameters
        ----------
        None

        Returns
        -------
        Indexer
            An instance of the Indexer class connected to the specified address.
        """
        secure = True if access_token else False
        conn = Connection(address, secure=secure)
        if not conn.is_connected():
            raise RuntimeError(f"Failed to connect to {address}")
        return cls(conn, access_token)

    def is_connected(self):
        """
        Checks if the ES2 connection is active.

        Returns
        -------
        bool
            True if the connection is active, False otherwise.
        """
        return self.connection.is_connected()

    def disconnect(self):
        """
        Closes the ES2 connection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.connection.close()

    ###################################
    # Server Info
    ###################################

    def get_server_version(self) -> Optional[str]:
        """
        Retrieve server version via gRPC metadata.

        This method performs a lightweight RPC (get_key_list) and reads
        the server version from response metadata injected by the server.

        Returns
        -------
        Optional[str]
            Version string if available, otherwise None.
        """
        try:
            request = es2_msg_pb2.GetKeyListRequest()
            request.header.type = es2_type_pb.MessageType.GetKeyList
            # use with_call to access metadata
            response, call = self.stub.get_key_list.with_call(
                request,
                metadata=self.grpc_metadata,
            )
            # prefer trailing metadata
            md = dict(call.trailing_metadata()) if hasattr(call, "trailing_metadata") else {}
            server_version = md.get("x-es2e-server-version")
            if not server_version and hasattr(call, "initial_metadata"):
                imd = dict(call.initial_metadata())
                server_version = imd.get("x-es2e-server-version")
            return server_version
        except Exception as e:
            logger.warning(f"Failed to retrieve server version from metadata: {e}")
            return None

    def check_version_compat(self) -> None:
        """
        Compare SDK version with server version and enforce compatibility policy.

        Policy:
        - If ES2_VERSION_CHECK is 0/false/no, skip.
        - If server version does not start with 'v', skip (non-versioned server).
        - Otherwise compare using semantic parsing incl. pre-release tags.
          If mismatch and ES2_VERSION_CHECK_STRICT is on (default), raise; else warn.
        """
        import os

        do_check = os.getenv("ES2_VERSION_CHECK", "1").lower() not in ("0", "false", "no")
        if not do_check:
            return

        try:
            import es2 as _es2_pkg  # lazy to avoid circular import on package init

            sdk_version: Optional[str] = getattr(_es2_pkg, "__version__", None)
        except Exception:
            sdk_version = None

        server_version = None
        try:
            server_version = self.get_server_version()
        except Exception as e:
            logger.debug(f"Version check: unable to fetch server version: {e}")

        if sdk_version and server_version:
            if not version_utils.should_check(server_version):
                logger.debug("Server version '%s' has no 'v' prefix; skipping version check.", server_version)
                return
            strict = os.getenv("ES2_VERSION_CHECK_STRICT", "1").lower() not in ("0", "false", "no")
            if not version_utils.is_equal(sdk_version, server_version):
                server_pep440 = version_utils.to_pep440(server_version)
                msg = (
                    f"SDK/Server version mismatch: sdk={sdk_version}, server={server_version}"
                    f" (server_pep440={server_pep440}). "
                    f"Set ES2_VERSION_CHECK=0 to skip, or ES2_VERSION_CHECK_STRICT=0 to warn only."
                )
                if strict:
                    raise RuntimeError(msg)
                else:
                    logger.warning(msg)
        else:
            logger.debug(
                "Version check skipped: missing sdk or server version (sdk=%s, server=%s)",
                str(sdk_version),
                str(server_version),
            )

    ###################################
    # Key Management
    ###################################

    def register_key(
        self, key_id: str, key_path: str, key_type: str = "EvalKey", preset: str = "IP", eval_mode: str = "RMP"
    ):
        """
        Registers a public key from the specified file path to ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key.
        key_path : str
            The file path to the key to be registered.
        preset : str
            The preset to use for the key. Default is "IP".
        eval_mode : str
            The evaluation mode to use for the key. Default is "RMP".

        Returns
        -------
        None
        """

        def register_key_request_generator():
            try:
                with open(key_path, "rb") as key_file:
                    while True:
                        chunk = key_file.read(1 * 1024 * 1024)  # 1MB씩 읽기
                        if not chunk:
                            break
                        request = es2_msg_pb2.RegisterKeyRequest()
                        request.header.type = es2_type_pb.MessageType.RegisterKey

                        request.key_info.key_id = key_id
                        request.key_info.type = key_type
                        request.key_info.preset = preset
                        request.key_info.eval_mode = eval_mode
                        # TODO: request.key_info.sha256sum = ""

                        request.key.value = chunk
                        request.key.size = len(chunk)
                        yield request

            except Exception as e:
                logger.error(f"Error reading key file '{key_path}': {e}")
                return

        response = self.stub.register_key(
            register_key_request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to register key with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key '{key_id}' registered successfully.")

    def get_key_list(self):
        """
        Get a list of all registered key IDs.

        Returns
        -------
        Optional[List[str]]
            A list of registered key IDs, or None if the request failed.
        """
        request = es2_msg_pb2.GetKeyListRequest()

        request.header.type = es2_type_pb.MessageType.GetKeyList

        response = self.stub.get_key_list(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to list keys with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info("Get key list successfully.")
            key_list = list(response.key_id)
            if len(key_list) == 0:
                logger.info("No keys registered in the ES2 server.")
            return key_list

    def get_key_info(self, key_id: str):
        """
        Retrieves key information about a specific key from ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key.

        Returns
        -------
        Optional[dict]
            A dictionary containing key information (key_id, key_type, dim, url), or None if the request failed.
        """
        request = es2_msg_pb2.GetKeyInfoRequest()

        request.header.type = es2_type_pb.MessageType.GetKeyInfo
        request.key_id = key_id

        response = self.stub.get_key_info(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get key info with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key info for '{key_id}' received successfully.")

            return {
                "key_id": key_id,
                "key_type": response.key_info.type,
                "preset": response.key_info.preset,
                "eval_mode": response.key_info.eval_mode,
                "sha256sum": response.key_info.sha256sum,
            }

    def delete_key(self, key_id: str):
        """
        Deletes a registered key by its ID from ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key to be deleted.
        """
        request = es2_msg_pb2.DeleteKeyRequest()
        request.header.type = es2_type_pb.MessageType.DeleteKey
        request.key_id = key_id

        response = self.stub.delete_key(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to delete key with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key '{key_id}' deleted successfully.")

    def load_key(self, key_id: str):
        """
        Loads a registered key by its ID from ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key to be loaded.
        """
        request = es2_msg_pb2.LoadKeyRequest()
        request.header.type = es2_type_pb.MessageType.LoadKey
        request.key_id = key_id

        response = self.stub.load_key(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to load key with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key '{key_id}' loaded successfully.")

    def unload_key(self, key_id: str):
        """
        Unloads a registered key by its ID from ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key to be loaded.
        """
        request = es2_msg_pb2.UnloadKeyRequest()
        request.header.type = es2_type_pb.MessageType.UnloadKey
        request.key_id = key_id

        response = self.stub.unload_key(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to unload key with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key '{key_id}' unloaded successfully.")

    ###################################
    # Index Management
    ###################################

    def create_index(
        self,
        index_name: str,
        key_id: str,
        dim: int,
        search_type: str = "ip",
        index_encryption: str = "cipher",
        query_encryption: str = "plain",
        index_params: dict = {"index_type": "flat"},
    ):
        """
        Creates a new index into ES2 server.

        Index includes the following information:
        - Encrypted Vectors to store
        - Metadata for each vector

        Parameters
        ----------
        index_name : str
            The name of the index to be created.
        key_id : str
            The unique identifier for the key associated with the index.
        dim : int
            Vector dimension to be stored in the index.
        search_type : Union[str, es2_type_pb.SearchType], optional
            The type of search to be performed on the index (default: "ip").
        index_encryption : str, optional
            The type of index to be created (default: "cipher"). Options are "plain" or "cipher".
        query_encryption : str, optional
            The type of query to be performed on the index (default: "plain"). Options are "plain" or "cipher".
        index_type : str, optional
            The type of index to be created (default: "flat"). Options are "flat" or "ivf_flat".

        Returns
        -------
        Dict
            A dictionary containing index information.
        """
        request = es2_msg_pb2.CreateIndexRequest()
        request.header.type = es2_type_pb.MessageType.CreateIndex
        logger.debug(
            f"Creating index with name: {index_name}, dim: {dim}, search_type: {search_type}, "
            f"key_id: {key_id}, index_encryption: {index_encryption}, "
            f"query_encryption: {query_encryption}, index_params: {index_params}"
        )
        if isinstance(search_type, str):
            if search_type.lower() == "iponly" or search_type.lower() == "ip":
                search_type = es2_type_pb.SearchType.IPOnly
            elif search_type.lower() == "ipandqf" or search_type.lower() == "qf":
                search_type = es2_type_pb.SearchType.IPAndQF
            else:
                logger.debug(f"Invalid search type: {search_type}. Defaulting to IPOnly.")
                search_type = es2_type_pb.SearchType.IPOnly

        elif isinstance(search_type, int):
            if search_type not in [es2_type_pb.SearchType.IPOnly, es2_type_pb.SearchType.IPAndQF]:
                logger.debug(f"Invalid search type: {search_type}. Defaulting to IPOnly.")
                search_type = es2_type_pb.SearchType.IPOnly
            else:
                search_type = search_type
        else:
            raise ValueError(f"Invalid type for search_type: {type(search_type)}.")

        if isinstance(index_encryption, str) and index_encryption.lower() in ["plain", "cipher", "hybrid"]:
            index_encryption = index_encryption.lower()
        else:
            raise ValueError(f"Invalid index_encryption: {index_encryption}. Expected 'plain' or 'cipher'.")

        if isinstance(index_params["index_type"], str):
            logger.debug(f"Index params: {index_params}")
            if index_params["index_type"].upper() == "FLAT":
                index_type = es2_type_pb.IndexType.FLAT
            elif index_params["index_type"].upper() == "IVF_FLAT":
                index_type = es2_type_pb.IndexType.IVF_FLAT
                if index_params.get("nlist") is None:
                    raise ValueError("nlist must be provided for IVF_FLAT index type.")
                if index_params.get("default_nprobe") is None:
                    raise ValueError("default_nprobe must be provided for IVF_FLAT index type.")
                centroids = index_params.get("centroids")
                if centroids is None:
                    logger.info("Centroids not provided for IVF_FLAT index type. Generating random centroids locally.")
                    centroids = np.random.rand(index_params["nlist"], dim).astype(np.float32)
                    centroids /= np.sum(centroids, axis=1, keepdims=True)
                if len(centroids) != index_params["nlist"]:
                    raise ValueError(
                        f"Centroids size ({len(centroids)}) does not match nlist ({index_params['nlist']})"
                    )
                for centroid in centroids:
                    dt = es2_type_pb.DataType()
                    dt.plain_vector.data.extend(centroid)
                    request.index_info.index_detail.ivf_detail.centroids.append(dt)

                request.index_info.index_detail.ivf_detail.nlist = index_params["nlist"]
                request.index_info.index_detail.ivf_detail.default_nprobe = index_params["default_nprobe"]

        request.index_info.index_name = index_name
        request.index_info.dim = dim
        request.index_info.search_type = search_type
        request.index_info.key_id = key_id
        request.index_info.index_encryption = index_encryption
        request.index_info.query_encryption = query_encryption
        request.index_info.index_type = index_type

        def request_generator():
            yield request

        response = self.stub.create_index(
            request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(f"Failed to create index with error code {response.header.return_code}: {response.header}")
        else:
            logger.info(f"Index '{index_name}' created successfully.")
            return {
                "index_name": index_name,
                "dim": dim,
                "search_type": search_type,
                "key_id": key_id,
                "index_encryption": index_encryption,
                "query_encryption": query_encryption,
                "index_type": index_type,
            }

    def get_index_list(self, loaded_only: bool = False):
        """
        Get a list of all index names in ES2 server.

        Parameters
        ----------
        loaded_only : bool, optional
            If True, only return names of loaded indexes.

        Returns
        -------
        List[str]
            A list of index names, or None if the request failed.
        """
        request = es2_msg_pb2.GetIndexListRequest()
        request.header.type = es2_type_pb.MessageType.GetIndexList
        request.loaded_only = loaded_only

        response = self.stub.get_index_list(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get index list with error code {response.header.return_code}: "
                f"{response.header.error_message}"
            )
        else:
            logger.info("Get Index list received successfully.")
            return list(response.index_names)

    def get_index_info(self, index_name: str):
        """
        Retrieves information about a specific index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index to retrieve information for.

        Returns
        -------
        Dict
            A dictionary containing index information (index_name, dim, row_count, search_type, key_id, created_time),
                or None if the request failed.
        """
        request = es2_msg_pb2.GetIndexInfoRequest()
        request.header.type = es2_type_pb.MessageType.GetIndexInfo
        request.index_name = index_name

        for response in self.stub.get_index_info(
            request,
            metadata=self.grpc_metadata,
        ):
            if response.header.return_code != es2_type_pb.ReturnCode.Success:
                raise ValueError(
                    f"Failed to get index info with error code "
                    f"{response.header.return_code}: {response.header.error_message}"
                )

            else:
                logger.info(f"Index info for '{index_name}' received successfully.")
                res = {
                    "index_name": index_name,
                    "dim": response.index_info.dim,
                    "row_count": response.index_info.row_count,
                    "search_type": es2_type_pb.SearchType.Name(response.index_info.search_type),
                    "key_id": response.index_info.key_id,
                    "index_encryption": response.index_info.index_encryption,
                    "query_encryption": response.index_info.query_encryption,
                    "created_time": response.index_info.created_time,
                    "is_loaded": response.index_info.is_loaded,
                    "index_type": es2_type_pb.IndexType.Name(response.index_info.index_type),
                }
                if res["index_type"].upper() == "IVF_FLAT":
                    res["ivf_detail"] = response.index_info.index_detail.ivf_detail
                return res

    def load_index(self, index_name: str):
        """
        Loads a specified index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index to be loaded.

        Returns
        -------
        None
        """
        request = es2_msg_pb2.LoadIndexRequest()
        request.header.type = es2_type_pb.MessageType.LoadIndex
        request.index_name = index_name

        response = self.stub.load_index(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to load index with error code {response.header.return_code}: "
                f"{response.header.error_message}"
            )
        else:
            logger.info(f"Index '{index_name}' loaded successfully.")

    def unload_index(self, index_name: str):
        """
        Unloads a specified index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index to be unloaded.

        Returns
        -------
        None
        """
        request = es2_msg_pb2.UnloadIndexRequest()
        request.header.type = es2_type_pb.MessageType.UnloadIndex
        request.index_name = index_name

        response = self.stub.unload_index(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to unload index with error code {response.header.return_code}: "
                f"{response.header.error_message}"
            )
        else:
            logger.info(f"Index '{index_name}' unloaded successfully.")

    def delete_index(self, index_name: str):
        """
        Deletes a specified index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index to be deleted.

        Returns
        -------
        None
        """
        request = es2_msg_pb2.DeleteIndexRequest()
        request.header.type = es2_type_pb.MessageType.DeleteIndex
        request.index_name = index_name

        response = self.stub.delete_index(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to delete index with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Index '{index_name}' deleted successfully.")

    ###################################
    # Data Management
    ###################################

    def insert_data(self, index_name: str, enc_vec: List[evi.Query], metadata: List[str] = []) -> List[Any]:
        """
        Inserts encrypted data and their metadata into an index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index where data will be inserted.
        enc_vec : List[evi.Query]
            A list of encrypted vectors to be inserted.
        metadata : List[str], optional
            A list of metadata strings associated with the data. The default is an empty list.

        Returns
        -------
        List[Any]
            Inserted item identifiers in the order they were provided.
        """

        def insert_data_request_generator():
            for vec_idx, vec in enumerate(enc_vec):
                data = evi.Query.serializeTo(vec)
                chunk_size = 1024 * 1024 * 129  # 1MB
                for offset in range(0, len(data), chunk_size):
                    request = es2_msg_pb2.InsertDataRequest()
                    request.header.type = es2_type_pb.MessageType.InsertData
                    request.index_name = index_name
                    chunk = data[offset : offset + chunk_size]
                    packed_vector = request.packed_vectors.add()
                    packed_vector.vector.cipher_vector.id = str(vec_idx)
                    packed_vector.vector.cipher_vector.data = chunk
                    packed_vector.num_vector = 1
                    if metadata and offset == 0:
                        packed_vector.metadata.append(metadata[vec_idx] if vec_idx < len(metadata) else "")
                    yield request

        response = self.stub.insert_data(
            insert_data_request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to insert data with error code {response.header.return_code}: {response.header.error_message}"
            )

        logger.info(f"Data inserted successfully into index '{index_name}'.")
        return list(response.item_ids)

    def insert_data_bulk(
        self,
        index_name: str,
        enc_vec: List[evi.Query],
        numitems: List[int],
        metadata: List[List[str]] = [],
        centroid_idx: int = -1,
    ) -> List[Any]:
        """
        Inserts encrypted data and their metadata into an index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index where data will be inserted.
        enc_vec : List[evi.Query]
            A list of encrypted vectors to be inserted.
        metadata : List[str], optional
            A list of metadata strings associated with the data. The default is an empty list.

        Returns
        -------
        List[Any]
            Inserted item identifiers in the order they were provided.
        """
        # Use a unique header ID as an BatchInsert API identifier
        header_id = f"{secrets.token_hex(10)}"

        def insert_data_request_generator():
            for vec_idx, vec in enumerate(enc_vec):
                data = evi.Query.serializeTo(vec)
                chunk_size = 1024 * 1024 * 129  # 1MB
                for offset in range(0, len(data), chunk_size):
                    request = es2_msg_pb2.BatchInsertDataRequest()
                    request.header.type = es2_type_pb.MessageType.BatchInsertData
                    request.header.id = header_id
                    request.index_name = index_name
                    if centroid_idx >= 0:
                        request.cluster_id = centroid_idx
                    chunk = data[offset : offset + chunk_size]

                    packed_vector = request.packed_vectors.add()
                    packed_vector.vector.cipher_vector.id = str(vec_idx)
                    packed_vector.vector.cipher_vector.data = chunk
                    packed_vector.num_vector = numitems[vec_idx] if vec_idx < len(numitems) else 1

                    if metadata and offset == 0:
                        for idx in range(packed_vector.num_vector):
                            packed_vector.metadata.append(
                                metadata[vec_idx][idx]
                                if vec_idx < len(metadata) and idx < len(metadata[vec_idx])
                                else ""
                            )

                    yield request

        # print("time to batch insert")
        response = self.stub.batch_insert_data(
            insert_data_request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to insert data with error code {response.header.return_code}: {response.header.error_message}"
            )

        logger.info(f"Data inserted successfully into index '{index_name}'.")
        return list(response.item_ids)

    ###################################
    # Search APIs
    ###################################

    def search(self, index_name: str, query: List[List[float]], topk: List[List[int]] = []):
        """
        Performs encrypted similarity search on the specified index from ES2 server.
        ES2 server performs secure homomorphic encryption operations with the registered evaluation key.

        Parameters
        ----------
        index_name : str
            The name of the index to search.
        query : List[List[float]]
            A list of query vectors to search for.

        Returns
        -------
        List[evi.CiphertextLv0]
            A list of search results, or None if the request failed.
        """
        # PC Search gRPC call
        request = es2_msg_pb2.InnerProductRequest()
        request.header.type = es2_type_pb.MessageType.InnerProduct
        request.index_name = index_name

        for i, q in enumerate(query):
            dt = es2_type_pb.DataType()
            dt.plain_vector.id = f"id-{secrets.token_hex(5)}"
            dt.plain_vector.data.extend(q)
            dt.plain_vector.dim = len(q)
            request.query_vector.append(dt)
            if len(topk) > 0:
                # print(topk)
                request.cluster_infos.append(es2_type_pb.CentroidsList())
                for idx in topk[i]:
                    request.cluster_infos[-1].centroids.append(idx)
                # print(f"{request.cluster_infos=}")

        query_ids = [dt.plain_vector.id for dt in request.query_vector]

        response_stream = self.stub.inner_product(
            request,
            metadata=self.grpc_metadata,
        )

        shard_idx = {k: [] for k in query_ids}
        results = {k: [] for k in query_ids}
        for response in response_stream:
            if response.header.return_code != es2_type_pb.ReturnCode.Success:
                raise ValueError(
                    f"Failed to search with error code {response.header.return_code}: {response.header.error_message}"
                )
            output = list(response.ctxt_score)[0]
            results[output.id].append(list(output.ctxt_score)[0])
            shard_idx[output.id].extend(list(output.shard_idx))

        outputs = [
            es2_type_pb.CiphertextScore(
                id=query_id,
                ctxt_score=results[query_id],
                shard_idx=shard_idx[query_id],
            )
            for query_id in query_ids
        ]

        return outputs

    def encrypted_search(self, index_name: str, enc_query: List[CipherBlock], topk: List[List[int]] = []):
        """
        Performs encrypted similarity search on the specified index from ES2 server.
        ES2 server performs secure homomorphic encryption operations with the registered evaluation key.

        Parameters
        ----------
        index_name : str
            The name of the index to search.
        query : List[CipherBlock]
            A list of encrypted query vectors to search for.

        Returns
        -------
        List[evi.CiphertextLv0]
            A list of search results, or None if the request failed.
        """
        # CC Search gRPC call
        request = es2_msg_pb2.InnerProductRequest()
        request.header.type = es2_type_pb.MessageType.InnerProduct
        request.index_name = index_name

        for i, vec in enumerate(enc_query):
            dt = es2_type_pb.DataType()
            dt.cipher_vector.id = f"id-{secrets.token_hex(5)}"
            dt.cipher_vector.data = vec.serialize()
            request.query_vector.append(dt)
            if len(topk) > 0:
                request.cluster_infos.append(es2_type_pb.CentroidsList())
                for idx in topk[i]:
                    request.cluster_infos[-1].centroids.append(idx)

        query_ids = [dt.cipher_vector.id for dt in request.query_vector]

        response_stream = self.stub.inner_product(
            request,
            metadata=self.grpc_metadata,
        )

        shard_idx = {k: [] for k in query_ids}
        results = {k: [] for k in query_ids}
        for response in response_stream:
            if response.header.return_code != es2_type_pb.ReturnCode.Success:
                raise ValueError(
                    f"Failed to search with error code {response.header.return_code}: {response.header.error_message}"
                )
            output = list(response.ctxt_score)[0]
            results[output.id].append(list(output.ctxt_score)[0])
            shard_idx[output.id].extend(list(output.shard_idx))

        outputs = [
            es2_type_pb.CiphertextScore(
                id=query_id,
                ctxt_score=results[query_id],
                shard_idx=shard_idx[query_id],
            )
            for query_id in query_ids
        ]

        return outputs

    ###################################
    # Query APIs
    ###################################

    def get_metadata(self, index_name: str, idx: Union[List, Tuple], fields: list[str] = []):
        """
        Retrieves metadata for specified indices and output fields in an index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index from which to retrieve metadata.
        idx : Union[List, Tuple]
            A list of Position objects specifying the shard and row indices for metadata retrieval.
        fields : List[str]
            A list of field names to retrieve from the metadata.
            The default is an empty list, which does not retrieve metadata.

        Returns
        -------
        Optional[List]
            A list of metadata entries for the specified positions and fields, or None if the request failed.
        """
        request = es2_msg_pb2.GetMetadataRequest()
        request.header.type = es2_type_pb.MessageType.GetMetadata
        request.index_name = index_name

        if isinstance(idx, list) or isinstance(idx, tuple):
            if isinstance(idx[0], dict):
                for position in idx:
                    pos = request.idx.add()
                    pos.shard_idx = position["shard_idx"]
                    pos.row_idx = position["row_idx"]

            elif isinstance(idx[0], list) or isinstance(idx[0], tuple):
                for position in idx:
                    pos = request.idx.add()
                    pos.shard_idx = position[0]
                    pos.row_idx = position[1]

        else:
            raise ValueError(f"Ambiguous format for idx: {type(idx)}.\nExpected 'List[Position]' or 'List[List[int]]'.")

        if fields:
            for field in fields:
                request.output_fields.append(field)

        response = self.stub.get_metadata(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get metadata with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Metadata for index '{index_name}' received successfully.")
            return list(response.metadata)
