#pragma once

#include <cstdint>

#include "infra/exports.h"

namespace akida {
/**
 * Size of shared SRAM
 */
struct AKIDASHAREDLIB_EXPORT SramSize final {
  bool operator==(const SramSize&) const = default;

  /**
   * Size of shared input packet SRAM in bytes available inside the mesh
   * for each two NPs.
   */
  uint32_t input_bytes{};
  /**
   * Size of shared filter SRAM in bytes available inside the mesh for each two
   * NPs.
   */
  uint32_t weight_bytes{};
};
}  // namespace akida
