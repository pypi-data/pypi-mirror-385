/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

/**
 * @file
 * Tokenizer interface declaration.
 */

#pragma once

#include <pytorch/tokenizers/error.h>
#include <pytorch/tokenizers/result.h>
#include <string>
#include <vector>

namespace tokenizers {

struct TokenIndex {
  const char* str;
  int32_t id;
};

class Tokenizer {
 public:
  explicit Tokenizer() {}
  virtual ~Tokenizer() {}

  virtual Error load(const std::string& tokenizer_path) = 0;

  /**
   * Encode the input string into a vector of token IDs.
   *
   * @param input The input string to tokenize
   * @param bos The number of beginning-of-sequence (BOS) tokens to prepend to
   * the result
   * @param eos The number of end-of-sequence (EOS) tokens to append to the
   * result
   * @return Result containing a vector of token IDs, or an error if encoding
   * fails
   */
  virtual Result<std::vector<uint64_t>>
  encode(const std::string& input, int8_t bos = 0, int8_t eos = 0) const = 0;

  virtual Result<std::string> decode(uint64_t prev_token, uint64_t token)
      const = 0;

  // getters
  int32_t vocab_size() const {
    return vocab_size_;
  }

  uint64_t bos_tok() const {
    return bos_tok_;
  }

  uint64_t eos_tok() const {
    return eos_tok_;
  }

  virtual bool is_loaded() const {
    return initialized_;
  }

 protected:
  bool initialized_ = false;
  int32_t vocab_size_ = 0;
  uint64_t bos_tok_ = 0, eos_tok_ = 0;
};

} // namespace tokenizers
