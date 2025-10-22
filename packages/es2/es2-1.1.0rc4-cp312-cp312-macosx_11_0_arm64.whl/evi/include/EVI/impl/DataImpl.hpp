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
#include "EVI/impl/QueryImpl.hpp"
#include <vector>
namespace evi {

struct IData {
public:
    u64 dim;
    u64 degree;
    u64 n;

    virtual polyvec &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual const polyvec &getPoly(const int pos, const int level,
                                   std::optional<const int> index = std::nullopt) const = 0;
    virtual polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual polydata getPolyData(const int pos, const int level,
                                 std::optional<const int> index = std::nullopt) const = 0;

    virtual void serializeTo(std::vector<u8> &buf) const = 0;
    virtual void deserializeFrom(const std::vector<u8> &buf) = 0;
    virtual void serializeTo(std::ostream &stream) const = 0;
    virtual void deserializeFrom(std::istream &stream) = 0;

    virtual void setSize(const int size, std::optional<int> = std::nullopt) = 0;

    virtual DataType &getDataType() = 0;
    virtual int &getLevel() = 0;
};

template <DataType T>
struct Matrix : public IData {
public:
    Matrix(const int level);
    Matrix(polyvec q);
    Matrix(polyvec a_q, polyvec b_q);
    Matrix(polyvec a_q, polyvec a_p, polyvec b_q, polyvec b_p);

    polyvec &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    const polyvec &getPoly(const int pos, const int level,
                           std::optional<const int> index = std::nullopt) const override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;

    void serializeTo(std::vector<u8> &buf) const override;
    void deserializeFrom(const std::vector<u8> &buf) override;
    void serializeTo(std::ostream &stream) const override;
    void deserializeFrom(std::istream &stream) override;

    void setSize(const int size, std::optional<int> = std::nullopt) override;
    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

private:
    DataType dtype;
    int level_;
    polyvec a_q_;
    polyvec a_p_;
    polyvec b_q_;
    polyvec b_p_;
};

struct IPSearchResult {
    std::shared_ptr<IData> ip_;
#ifdef BUILD_WITH_HEAAN
    std::vector<HEaaN::Ciphertext> qf_;
#endif
};

// using DataState = std::vector<std::shared_ptr<IData>>;
// using SearchResult = std::shared_ptr<IPSearchResult>;
using DataState = std::shared_ptr<IData>;
using Blob = std::vector<DataState>;

struct VariadicKeyType : std::shared_ptr<Matrix<DataType::CIPHER>> {
    VariadicKeyType() : std::shared_ptr<Matrix<DataType::CIPHER>>(std::make_shared<Matrix<DataType::CIPHER>>(LEVEL1)) {}
    VariadicKeyType(const VariadicKeyType &to_copy) : std::shared_ptr<Matrix<DataType::CIPHER>>(to_copy) {}
};

struct FixedKeyType : std::shared_ptr<SingleBlock<DataType::CIPHER>> {
    FixedKeyType()
        : std::shared_ptr<SingleBlock<DataType::CIPHER>>(std::make_shared<SingleBlock<DataType::CIPHER>>(LEVEL1)) {}
    FixedKeyType(const FixedKeyType &to_copy) : std::shared_ptr<SingleBlock<DataType::CIPHER>>(to_copy) {}
};

template <DataType T>
struct PolyData {
    void setSize(const int size);
    int getSize() const;
    polydata &getPolyData(const int pos, const int level, std::optional<int> idx = std::nullopt);

private:
    std::vector<polydata> a_q;
    std::vector<polydata> a_p;
    std::vector<polydata> b_q;
    std::vector<polydata> b_p;
};

template <DataType T>
using DeviceData = std::shared_ptr<PolyData<T>>;

} // namespace evi
