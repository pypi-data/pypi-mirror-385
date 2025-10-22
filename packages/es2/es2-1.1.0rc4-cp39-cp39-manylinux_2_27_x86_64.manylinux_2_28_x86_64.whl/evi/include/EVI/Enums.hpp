////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2021-2024, CryptoLab Inc. All rights reserved.               //
//                                                                            //
// This software and/or source code may be commercially used and/or           //
// disseminated only with the written permission of CryptoLab Inc,            //
// or in accordance with the terms and conditions stipulated in the           //
// agreement/contract under which the software and/or source code has been    //
// supplied by CryptoLab Inc. Any unauthorized commercial use and/or          //
// dissemination of this file is strictly prohibited and will constitute      //
// an infringement of copyright.                                              //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

#pragma once
#include "EVI/Export.hpp"
#include <cstdint>
namespace evi {

/**
 * @enum ParameterPreset
 * @brief Predefined parameter sets for homomorphic encryption.
 *
 * - RUNTIME:
 * - IP0 : Default parameters for inner product computations.
 */
enum class ParameterPreset {
    RUNTIME,
    /// @cond INTERNAL
    QF0,
    QF1,
    QF2,
    QF3,
    /// @endcond
    IP0,
};

/**
 * @enum EvalMode
 * @brief Evaluation modes for homomorphic operations.
 *
 * - RMP: Evaluation mode optimized for reduced key size and faster computation.
 * - FLAT: Default evaluation mode.
 * - MM: Evaluation mode for batch processing, supports multiple queries at once.
 */
enum class EvalMode : uint8_t {
    RMP,
    /// @cond INTERNAL
    RMS,
    MS,
    /// @endcond
    FLAT,
    MM
};

#define CHECK_SHARED_A(M) ((M) == evi::EvalMode::RMS || (M == evi::EvalMode::MS))
#define CHECK_RMP(M) ((M) == evi::EvalMode::RMS || (M == evi::EvalMode::RMP))
#define CHECK_MM(M) ((M) == evi::EvalMode::MM)

enum class QueryType : uint8_t {
    SINGLE = 0,
    MATRIX = 1,
};

/**
 * @enum DeviceType
 * @brief Target device type for evaluation
 *
 * - CPU: Runs operations on CPU
 * - GPU: Runs operations on GPU
 * - AVX2: CPU with AVX2 optimizations
 */
enum class DeviceType : uint8_t { CPU = 0, GPU = 1, AVX2 = 2 };

/**
 * @enum DataType
 * @brief Data type for index or query representation
 *
 * - CIPHER: Encrypted ciphertext
 * - PLAIN: Plaintext
 */
enum class DataType : uint8_t {
    CIPHER,
    PLAIN,
    /// @cond INTERNAL
    SERIALIZED_CIPHER,
    SERIALIZED_PLAIN,
    /// @endcond
};

/**
 * @enum BatchType
 * @brief Type of batch processing for distributed execution
 *
 * - ISOLATED: Targeted to a single GPU device
 * - BROADCAST: Broadcasted across GPU devices
 */
enum class BatchType : uint8_t {
    ISOLATED,
    BROADCAST
    // SCATTER,
};

/**
 * @enum ErrorCode
 * @brief Standardized error codes for EVI operations
 *
 * - UNDEFINED: Unknown or unspecified error.
 * - FAIL: General failure not classified under a specific category.
 * - OK: Operation completed successfully.
 * - INVALID_ARGUMENT_ERROR: One or more input arguments are invalid.
 * - OUT_OF_INDEX_ERROR: Index is out of the valid range.
 * - NOT_FOUND_ERROR: Requested data was not found.
 */
enum class ErrorCode { UNDEFINED, FAIL, OK, INVALID_ARGUMENT_ERROR, OUT_OF_INDEX_ERROR, NOT_FOUND_ERROR };

/**
 * @enum EncodeType
 * @brief Encoding type for homomorphic encryption input vectors.
 *
 * - ITEM: Represents encrypted data stored in the database.
 * - QUERY: Represents a query vector used to search against the encrypted data.
 */
enum class EncodeType : uint8_t {
    ITEM,
    QUERY,
};

/**
 * @enum SealMode
 * @brief Sealing modes used to protect secret keys during storage.
 *
 * - AES_KEK: Uses a 256-bit AES key to encrypt and protect the secret key.
 * - NONE: No sealing applied; the key is stored as-is.
 */
enum class SealMode {
    /// @cond INTERNAL
    HSM_PORT,
    HSM_SERIAL,
    /// @endcond
    AES_KEK,
    NONE,
};

} // namespace evi
