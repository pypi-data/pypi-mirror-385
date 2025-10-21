#pragma once

#include <optional>

#include "akida/hardware_device.h"
#include "akida/ip_version.h"
#include "akida/np.h"
#include "akida/sram_size.h"

namespace akida {
/**
 * The default SRAM size for v1.
 *
 * Input SRAM: each NP has 2 input SRAM block of 5.25 x 1024 x 32-bit words.
 * Weight SRAM: each NP has a weight SRAM of 7 x 1024 x 50-bit words.
 */
inline constexpr SramSize SramSize_v1 = {43008, 44800};

/**
 * The default SRAM size for v2.
 *
 * Input SRAM: each NP has 2 input SRAM blocks of 8 x 1024 x 32-bit words.
 * Weight SRAM: each NP has a weight SRAM of 4 x 1024 x 100-bit words.
 */
inline constexpr SramSize SramSize_v2 = {65536, 51200};

/**
 * The layout of a mesh of Neural Processors.
 */
struct AKIDASHAREDLIB_EXPORT Mesh final {
  /**
   * Discover the topology of a Device Mesh.
   */
  static std::unique_ptr<Mesh> discover(HardwareDevice* device);

  explicit Mesh(IpVersion version, const hw::Ident& dma_event,
                const hw::Ident& dma_conf, std::optional<np::Info> hrc,
                std::vector<np::Info> nps,
                std::vector<np::Info> skip_dmas = {});

  bool operator==(const Mesh&) const = default;

  bool has_lut_on_all_nps() const;

  IpVersion version;               /**< The IP version of the mesh (v1 or v2) */
  hw::Ident dma_event;             /**< The DMA event endpoint */
  hw::Ident dma_conf;              /**< The DMA configuration endpoint */
  std::optional<np::Info> hrc;     /**< HRC if installed */
  std::vector<np::Info> nps;       /**< The available Neural Processors */
  std::vector<np::Info> skip_dmas; /**< The available skip dmas */
  /**
   * Size of shared SRAM in bytes available inside the mesh
   * for each two NPs.
   */
  SramSize np_sram_size{};
};

}  // namespace akida
