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
#include "EVI/Enums.hpp"
#include "EVI/Export.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/Query.hpp"

#include <memory>
#include <optional>
#include <string>
#include <vector>

#ifdef BUILD_WITH_HEM
#include "HEaaN/KeyPack.hpp"
#include "hem/ModulusMatrix.hpp"
#endif

namespace evi {

namespace detail {
class Encryptor;
} // namespace detail

/**
 * @class Encryptor
 * @brief Encodes or encrypts vectors into `Query` objects.
 *
 * An `Encryptor` produces `Query` instances representing either:
 * - `EncodeType::ITEM`  — encrypted database items
 * - `EncodeType::QUERY` — encoded/encrypted search queries
 */
class EVI_API Encryptor {
public:
    /// @brief Empty handle; initialize with makeEncryptor() before use.
    Encryptor() : impl_(nullptr) {}

    /**
     * @brief Constructs an Encryptor with an internal implementation.
     * @param impl Shared pointer to the internal `detail::Encryptor` object.
     */
    explicit Encryptor(std::shared_ptr<detail::Encryptor> impl) noexcept;

    /**
     * @brief Encodes a plaintext vector into a `Query`.
     * @param data Input vector to encode.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @param scale Optional scaling factor for precision control.
     * @return Encoded `Query` object.
     */
    Query encode(const std::vector<float> &data, evi::EncodeType type, int level = 0,
                 std::optional<float> scale = std::nullopt) const;

    /**
     * @brief Encodes a batch of plaintext vectors into individual `Query` objects.
     * @param data List of input vectors to encode.
     * @param type Encoding type only `ITEM` is supported.
     * @param level Optional remaining multiplicative depth (default: 0).
     * @param scale Optional scaling factor for precision control.
     * @return List of encoded `Query` objects.
     */
    std::vector<Query> encode(const std::vector<std::vector<float>> &data, evi::EncodeType type, int level = 0) const;

    /**
     * @brief Encodes a batch of plaintext vectors into a batched `Query`.
     * @param msg List of input vectors to encode.
     * @param type Encode type (`ITEM` or `QUERY`).
     * @param level Optional multiplicative depth to retain.
     * @param scale Optional scaling factor for precision control.
     * @return Encoded `Query`. For multi-vector inputs, the resulting query can carry multiple blocks.
     */
    Query encode(const std::vector<std::vector<float>> &msg, const EncodeType type, const int level,
                 std::optional<float> scale);

    /**
     * @brief Encrypts a plaintext vector using an encryption key file path.
     * @param data Input vector to encrypt.
     * @param enckey_path Path to the encryption key material.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @param scale Optional custom scale factor.
     * @return Encrypted `Query` object.
     */
    Query encrypt(const std::vector<float> &data, const std::string &enckey_path, evi::EncodeType type, int level = 0,
                  std::optional<float> scale = std::nullopt) const;

    /**
     * @brief Encrypts a plaintext vector using an in-memory key pack.
     * @param data Input vector to encrypt.
     * @param keypack Key pack providing the encryption key.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @param scale Optional custom scale factor.
     * @return Encrypted `Query` object.
     */
    Query encrypt(const std::vector<float> &data, const KeyPack &keypack, evi::EncodeType type, int level = 0,
                  std::optional<float> scale = std::nullopt) const;

    /**
     * @brief Encrypts a batch of vectors into `Query` objects.
     * @param data List of input vectors to encrypt.
     * @param enckey_path Path to the encryption key material.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @return List of encrypted `Query` objects.
     */
    std::vector<Query> encrypt(const std::vector<std::vector<float>> &data, const std::string enckey_path,
                               evi::EncodeType type, int level, std::optional<float> scale = std::nullopt) const;

    /**
     * @brief Encrypts a batch of vectors using an in-memory key pack.
     * @param data List of input vectors to encrypt.
     * @param keypack Key pack providing the encryption key.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @param scale Optional custom scale factor.
     * @return List of encrypted `Query` objects.
     */
    std::vector<Query> encrypt(const std::vector<std::vector<float>> &data, const KeyPack &keypack,
                               evi::EncodeType type, int level, std::optional<float> scale = std::nullopt) const;

    [[deprecated(
        "encrypt(data, type, level) will be removed soon; migrate to encrypt(data, keypack, type, level, scale)")]]
    Query encrypt(const std::vector<float> &data, evi::EncodeType type, int level = 0) const;

    [[deprecated(
        "encrypt(data, type, level) will be removed soon; migrate to encrypt(data, keypack, type, level, scale)")]]
    std::vector<Query> encrypt(const std::vector<std::vector<float>> &data, evi::EncodeType type, int level = 0) const;

    [[deprecated("encryptBulk will be removed soon; migrate to encrypt(data, keypack, type, level, scale)")]]
    std::vector<Query> encryptBulk(const std::vector<std::vector<float>> &data, evi::EncodeType type, int level = 0);

private:
    std::shared_ptr<detail::Encryptor> impl_;
};

/**
 * @brief Creates an `Encryptor` using an `Context`.
 *
 * @param context Context used for key initialization and device selection.
 * @return Configured `Encryptor` instance.
 */
EVI_API Encryptor makeEncryptor(const Context &context);

[[deprecated("makeEncryptor(context, key_pack) will be removed soon; update to the newer factory helpers")]]
EVI_API Encryptor makeEncryptor(const Context &context, const KeyPack &key_pack);

[[deprecated("makeEncryptor(context, key_path) will be removed soon; update to the newer factory helpers")]]
EVI_API Encryptor makeEncryptor(const Context &context, const std::string &file_path);

} // namespace evi
