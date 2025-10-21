// Copyright 2006 The RE2 Authors.  All Rights Reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

#ifndef RE2_SPARSE_SET_H_
#define RE2_SPARSE_SET_H_

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpragmas"
#pragma GCC diagnostic ignored "-Wunused-parameter"

// DESCRIPTION
//
// SparseSet(m) is a set of integers in [0, m).
// It requires sizeof(int)*m memory, but it provides
// fast iteration through the elements in the set and fast clearing
// of the set.
//
// Insertion and deletion are constant time operations.
//
// Allocating the set is a constant time operation
// when memory allocation is a constant time operation.
//
// Clearing the set is a constant time operation (unusual!).
//
// Iterating through the set is an O(n) operation, where n
// is the number of items in the set (not O(m)).
//
// The set iterator visits entries in the order they were first
// inserted into the set.  It is safe to add items to the set while
// using an iterator: the iterator will visit indices added to the set
// during the iteration, but will not re-visit indices whose values
// change after visiting.  Thus SparseSet can be a convenient
// implementation of a work queue.
//
// The SparseSet implementation is NOT thread-safe.  It is up to the
// caller to make sure only one thread is accessing the set.  (Typically
// these sets are temporary values and used in situations where speed is
// important.)
//
// The SparseSet interface does not present all the usual STL bells and
// whistles.
//
// Implemented with reference to Briggs & Torczon, An Efficient
// Representation for Sparse Sets, ACM Letters on Programming Languages
// and Systems, Volume 2, Issue 1-4 (March-Dec.  1993), pp.  59-69.
//
// This is a specialization of sparse array; see sparse_array.h.

// IMPLEMENTATION
//
// See sparse_array.h for implementation details.

// Doing this simplifies the logic below.
#ifndef __has_feature
#define __has_feature(x) 0
#endif

#include <assert.h>
#include <stdint.h>
#if __has_feature(memory_sanitizer)
#include <sanitizer/msan_interface.h>
#endif
#include <algorithm>
#include <memory>
#include <utility>

#include "re2/pod_array.h"

namespace re2 {

template<typename Value>
class SparseSetT {
 public:
  SparseSetT();
  explicit SparseSetT(int max_size);
  ~SparseSetT();

  typedef int* iterator;
  typedef const int* const_iterator;

  // Return the number of entries in the set.
  int size() const {
    return size_;
  }

  // Indicate whether the set is empty.
  int empty() const {
    return size_ == 0;
  }

  // Iterate over the set.
  iterator begin() {
    return dense_.data();
  }
  iterator end() {
    return dense_.data() + size_;
  }

  const_iterator begin() const {
    return dense_.data();
  }
  const_iterator end() const {
    return dense_.data() + size_;
  }

  // Return the maximum size of the set.
  // Indices can be in the range [0, max_size).
  int max_size() const {
    if (dense_.data() != NULL)
      return dense_.size();
    else
      return 0;
  }

  // Clear the set.
  void clear() {
    size_ = 0;
  }

  // Check whether index i is in the set.
  bool contains(int i) const;

 public:
  // Insert index i into the set.
  iterator insert(int i) {
    return InsertInternal(true, i);
  }

  // Insert index i into the set.
  // Fast but unsafe: only use if contains(i) is false.
  iterator insert_new(int i) {
    return InsertInternal(false, i);
  }

 private:
  iterator InsertInternal(bool allow_existing, int i) {
    DebugCheckInvariants();
    if (static_cast<uint32_t>(i) >= static_cast<uint32_t>(max_size())) {
      assert(false && "illegal index");
      // Semantically, end() would be better here, but we already know
      // the user did something stupid, so begin() insulates them from
      // dereferencing an invalid pointer.
      return begin();
    }
    if (!allow_existing) {
      assert(!contains(i));
      create_index(i);
    } else {
      if (!contains(i))
        create_index(i);
    }
    DebugCheckInvariants();
    return dense_.data() + sparse_[i];
  }

  // Add the index i to the set.
  // Only use if contains(i) is known to be false.
  // This function is private, only intended as a helper
  // for other methods.
  void create_index(int i);

  // In debug mode, verify that some invariant properties of the class
  // are being maintained. This is called at the end of the constructor
  // and at the beginning and end of all public non-const member functions.
  void DebugCheckInvariants() const;

  // Initializes memory for elements [min, max).
  void MaybeInitializeMemory(int min, int max) {
#if __has_feature(memory_sanitizer)
    __msan_unpoison(sparse_.data() + min, (max - min) * sizeof sparse_[0]);
#elif defined(RE2_ON_VALGRIND)
    for (int i = min; i < max; i++) {
      sparse_[i] = 0xababababU;
    }
#endif
  }

  int size_ = 0;
  PODArray<int> sparse_;
  PODArray<int> dense_;
};

template<typename Value>
SparseSetT<Value>::SparseSetT() = default;

// Check whether index i is in the set.
template<typename Value>
bool SparseSetT<Value>::contains(int i) const {
  assert(i >= 0);
  assert(i < max_size());
  if (static_cast<uint32_t>(i) >= static_cast<uint32_t>(max_size())) {
    return false;
  }
  // Unsigned comparison avoids checking sparse_[i] < 0.
  return static_cast<uint32_t>(sparse_[i]) < static_cast<uint32_t>(size_) &&
         dense_[sparse_[i]] == i;
}

template<typename Value>
void SparseSetT<Value>::create_index(int i) {
  assert(!contains(i));
  assert(size_ < max_size());
  sparse_[i] = size_;
  dense_[size_] = i;
  size_++;
}

template<typename Value> SparseSetT<Value>::SparseSetT(int max_size) :
    sparse_(max_size), dense_(max_size) {
  MaybeInitializeMemory(size_, max_size);
  DebugCheckInvariants();
}

template<typename Value> SparseSetT<Value>::~SparseSetT() {
  DebugCheckInvariants();
}

template<typename Value> void SparseSetT<Value>::DebugCheckInvariants() const {
  assert(0 <= size_);
  assert(size_ <= max_size());
}

typedef SparseSetT<void> SparseSet;

}  // namespace re2

#pragma GCC diagnostic pop
#endif  // RE2_SPARSE_SET_H_
