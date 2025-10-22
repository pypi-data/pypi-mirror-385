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
#include "EVI/Context.hpp"
#include "EVI/Export.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/SecretKey.hpp"
#include <memory>

namespace evi {
namespace detail {
class KeyGenerator;
class MultiKeyGenerator;
} // namespace detail

/**
 * @class KeyGenerator
 * @brief Generates a SecretKey, EncryptionKey, and EvaluationKey for homomorphic encryption.
 *
 * The `KeyGenerator` is responsible for creating a `SecretKey` and the corresponding public keys
 * such as the Encryption Key and Evaluation Key, based on the given encryption context.
 * The generated secret key is stored within a `SecretKey` instance,
 * while the public keys are typically stored in a `KeyPack` instance.
 */
class EVI_API KeyGenerator {
public:
    /// @brief Default constructor is deleted. Use `makeKeyGenerator()` factory functions instead.
    KeyGenerator() = delete;

    /**
     * @brief Constructs a KeyGenerator with a internal implementation.
     * @param impl Shared pointer to the internal `detail::KeyGenerator` object.
     */
    explicit KeyGenerator(std::shared_ptr<detail::KeyGenerator> impl) noexcept;

    /**
     * @brief Generates a new secret key.
     * @return The generated `SecretKey` object.
     */
    SecretKey genSecKey();

    /**
     * @brief Generates public keys (e.g., EncKey, EvalKey) and stores them in the associated KeyPack.
     * @param sec_key Secret key used to derive public keys.
     */
    void genPubKeys(SecretKey &sec_key);

private:
    std::shared_ptr<detail::KeyGenerator> impl_;
};

/**
 * @brief Creates a KeyGenerator with a given context and key storage.
 *
 * @param context Context used for key initialization and device selection.
 * @param pack The key pack used to store generated public keys.
 * @param seed Optional seed for deterministic key generation.
 * @return A configured `KeyGenerator` instance.
 */
EVI_API KeyGenerator makeKeyGenerator(const Context &context, KeyPack &pack,
                                      std::optional<std::vector<uint8_t>> seed = std::nullopt);

/**
 * @brief Creates a KeyGenerator and automatically initializes an internal KeyPack.
 *
 * @param context Context used for key initialization and device selection.
 * @param seed Optional seed for deterministic key generation.
 * @return A configured `KeyGenerator` instance.
 */
EVI_API KeyGenerator makeKeyGenerator(const Context &context, std::optional<std::vector<uint8_t>> seed = std::nullopt);

/**
 * @class MultiKeyGenerator
 * @brief Generates and seals secret keys across multiple contexts and stores them securely.
 *
 * `MultiKeyGenerator` is typically used for generating sealed secret keys across multiple devices or ranks,
 * especially in distributed or multi-GPU setups.
 */
class EVI_API MultiKeyGenerator {
public:
    /// @brief Default constructor is deleted. Use `makeMultiKeyGenerator()` factory functions instead.
    MultiKeyGenerator() = delete;

    /**
     * @brief Constructs a MultiKeyGenerator from multiple contexts.
     * @param contexts List of context.
     * @param dir_path Path to the directory where all key files are stored.
     * @param sInfo Sealing configuration (e.g., AES-KEK).
     * @param seed Optional seed for deterministic key generation.
     */
    MultiKeyGenerator(const std::vector<Context> &contexts, const std::string &dir_path, SealInfo &sInfo,
                      std::optional<std::vector<uint8_t>> seed = std::nullopt);

    /**
     * @brief Constructs a MultiKeyGenerator with an internal implementation.
     * @param impl Shared pointer to the internal `detail::MultiKeyGenerator` object.
     */
    explicit MultiKeyGenerator(std::shared_ptr<detail::MultiKeyGenerator> impl) noexcept;

    /**
     * @brief Checks whether the key files already exist in the target directory.
     * @return `true` if key files are found; otherwise `false`.
     */
    bool checkFileExist() const;

    /**
     * @brief Generates a new SecretKey.
     * @return The generated `SecretKey` object.
     */
    SecretKey generate_keys();

private:
    std::shared_ptr<detail::MultiKeyGenerator> impl_;
};

/**
 * @brief Creates a `MultiKeyGenerator` instance for distributed secret key generation and sealing.
 *
 * @param contexts List of context.
 * @param dir_path Path to the directory where all key files are stored.
 * @param sInfo Sealing configuration used to protect the generated secret key.
 * @param seed Optional seed for deterministic key generation.
 * @return A configured `MultiKeyGenerator` instance.
 */
EVI_API MultiKeyGenerator makeMultiKeyGenerator(std::vector<Context> &contexts, const std::string &dir_path,
                                                SealInfo &sInfo,
                                                std::optional<std::vector<uint8_t>> seed = std::nullopt);

} // namespace evi
