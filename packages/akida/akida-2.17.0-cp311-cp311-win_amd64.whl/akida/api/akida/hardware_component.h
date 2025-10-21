#pragma once

#include <algorithm>
#include <optional>
#include <vector>

#include "akida/hardware_ident.h"
#include "akida/hardware_type.h"
#include "akida/shape.h"

namespace akida {

struct NpSpace {
  bool operator==(const NpSpace& other) const = default;

  Index x;
  Index y;
  Shape shape;
};

struct MemoryInfo {
  bool operator==(const MemoryInfo& other) const = default;

  // Input memory size. (Bytes)
  uint32_t input_size{};
  // Weights memory size. (Bytes)
  uint32_t weight_size{};
  // External memory size. (Bytes)
  uint32_t external_size{};
};

namespace hw {

struct NpMapping {
  NpMapping(const NpSpace& in_int, const NpSpace& in_aug, Index start_n,
            Index neurons, bool single_buf)
      : start_neuron(start_n),
        num_neurons(neurons),
        input_int(in_int),
        input_aug(in_aug),
        single_buffer(single_buf) {}

  bool operator==(const NpMapping& other) const {
    return start_neuron == other.start_neuron &&
           num_neurons == other.num_neurons && input_int == other.input_int &&
           input_aug == other.input_aug;
  }

  Index start_neuron;
  Index num_neurons;
  // Internal input box
  NpSpace input_int;
  // Augmented input box
  NpSpace input_aug;
  // Use single buffer or dual dual buffer
  bool single_buffer;
};

struct Component {
  static Component create_np(hw::Type np_type, const NpSpace& in_int,
                             const NpSpace& in_aug, Index start_n,
                             Index neurons, bool single_buf, hw::Ident np_id,
                             const MemoryInfo& mem_info) {
    Component component(np_type, np_id, mem_info);
    component.np = NpMapping(in_int, in_aug, start_n, neurons, single_buf);
    return component;
  }

  static Component create_hrc(const MemoryInfo& mem_info) {
    return Component(hw::Type::HRC, HRC_IDENT, mem_info);
  }

  static Component create_skip_dma(const hw::Type type, const hw::Ident& id,
                                   const MemoryInfo& mem_info) {
    auto component = Component(type, id, mem_info);

    return component;
  }

  static Component create_dma(hw::Ident id, const MemoryInfo& mem_info) {
    return Component(hw::Type::DMA, id, mem_info);
  }

  bool operator==(const Component& other) const = default;

  hw::Type type;
  hw::Ident id;
  std::optional<NpMapping> np = std::nullopt;
  MemoryInfo mem_info;

 private:
  explicit Component(hw::Type comp_type, hw::Ident comp_id,
                     const MemoryInfo& comp_mem_info)
      : type(comp_type), id(comp_id), mem_info(comp_mem_info) {}
};

}  // namespace hw

// utility function to find the leftmost or rightmost NPs
inline uint8_t find_border_column(const std::vector<hw::Component>& nps,
                                  bool find_left) {
  if (nps.size() == 1 && nps[0].type == hw::Type::HRC) {
    return 1;
  }
  auto border_np = *std::ranges::min_element(
      nps, [find_left](const auto& left, const auto& right) {
        return find_left ? left.id.col < right.id.col
                         : left.id.col > right.id.col;
      });
  return border_np.id.col;
}

}  // namespace akida
