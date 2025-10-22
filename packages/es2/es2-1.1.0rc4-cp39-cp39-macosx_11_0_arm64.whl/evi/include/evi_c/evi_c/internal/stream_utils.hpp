////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
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

#include "evi_c/common.h"

#include "utils/Exceptions.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <istream>
#include <ostream>
#include <streambuf>

namespace evi::c_api::detail {

class WriteCallbackStreambuf : public std::streambuf {
public:
    WriteCallbackStreambuf(evi_stream_write_fn fn, void *handle) : fn_(fn), handle_(handle) {
        setp(buffer_, buffer_ + sizeof(buffer_));
    }

    int sync() override {
        const std::ptrdiff_t pending = pptr() - pbase();
        if (pending <= 0) {
            return 0;
        }
        const size_t written = fn_(handle_, reinterpret_cast<const uint8_t *>(pbase()), static_cast<size_t>(pending));
        if (written != static_cast<size_t>(pending)) {
            return -1;
        }
        setp(buffer_, buffer_ + sizeof(buffer_));
        return 0;
    }

protected:
    int_type overflow(int_type ch) override {
        if (sync() != 0) {
            return traits_type::eof();
        }
        if (traits_type::eq_int_type(ch, traits_type::eof())) {
            return traits_type::not_eof(ch);
        }
        *pptr() = static_cast<char>(ch);
        pbump(1);
        return ch;
    }

    std::streamsize xsputn(const char_type *s, std::streamsize count) override {
        std::streamsize total = 0;
        while (count > 0) {
            const auto space = static_cast<std::streamsize>(epptr() - pptr());
            if (space == 0) {
                if (sync() != 0) {
                    break;
                }
                continue;
            }
            const std::streamsize chunk = std::min(space, count);
            std::memcpy(pptr(), s, static_cast<size_t>(chunk));
            pbump(static_cast<int>(chunk));
            s += chunk;
            count -= chunk;
            total += chunk;
        }
        return total;
    }

private:
    evi_stream_write_fn fn_;
    void *handle_;
    char buffer_[4096];
};

class ReadCallbackStreambuf : public std::streambuf {
public:
    ReadCallbackStreambuf(evi_stream_read_fn fn, void *handle) : fn_(fn), handle_(handle) {
        setg(buffer_, buffer_, buffer_);
    }

protected:
    int_type underflow() override {
        if (gptr() < egptr()) {
            return traits_type::to_int_type(*gptr());
        }
        const size_t received = fn_(handle_, reinterpret_cast<uint8_t *>(buffer_), sizeof(buffer_));
        if (received == 0) {
            return traits_type::eof();
        }
        setg(buffer_, buffer_, buffer_ + received);
        return traits_type::to_int_type(*gptr());
    }

private:
    evi_stream_read_fn fn_;
    void *handle_;
    char buffer_[4096];
};

} // namespace evi::c_api::detail
