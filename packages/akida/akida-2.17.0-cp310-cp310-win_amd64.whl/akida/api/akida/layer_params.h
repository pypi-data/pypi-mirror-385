#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "infra/exports.h"

/** file akida/layer_params.h
 * Contains layer related enums and layers parameters structures.
 */

namespace akida {

// Layer enum definitions. When dropping the supports of layers, the enum values
// of remaining layers must remain unchanged to ensure backward
// compatibility.
/**
 * @enum LayerType
 * @brief The layer type
 */
enum class LayerType {
  Unknown,
  InputData,
  InputConvolutional,
  FullyConnected,
  Convolutional,
  SeparableConvolutional,
  Add,
  Concatenate = 12,
  Conv2D = 14,
  InputConv2D,
  DepthwiseConv2D,
  Conv2DTranspose,
  ExtractToken,
  Dequantizer,
  DepthwiseConv2DTranspose,
  BufferTempConv,
  DepthwiseBufferTempConv,
  Dense1D = 25,
  StatefulRecurrent
};

/**
 * @enum Padding
 * @brief The padding type
 */
enum class Padding {
  Valid /**<No padding*/,
  Same /**<Padded so that output size is input size divided by the stride*/,
};

/**
 * @enum PoolType
 * @brief The pooling type
 */
enum class PoolType {
  NoPooling /**<No pooling applied*/,
  Max /**<Maximum pixel value is selected*/,
  Average /**<Average pixel value is selected*/
};

/**
 * @enum ActivationType
 * @brief The activation type
 */
enum class ActivationType {
  NoActivation /**<No activation applied*/,
  ReLU /**<ReLU activation is selected*/,
  LUT /**<LUT activation is selected*/
};

/**
 * @class LayerParams
 * @brief Generic parameters that can be used for several layers
 */
class AKIDASHAREDLIB_EXPORT LayerParams {
 public:
  // Value is a basic type large enough to hold the data for every type in a
  // lossless way.
  using Value = int32_t;
  using KeyType = const std::string;
  using Dict = std::map<KeyType, Value>;

  virtual ~LayerParams() = default;

  /**
   * @brief Simplified static cast to Value
   * @param value: Value to be casted
   * @return casted value, ready to be inserted
   */
  template<typename T>
  static constexpr Value as_value(T value) {
    return static_cast<Value>(value);
  }

  /**
   * @brief Return the name of a value
   * @param value: the input value
   * @return the value name
   */
  static std::string as_name(ActivationType value) {
    switch (value) {
      case ActivationType::NoActivation:
        return "NoActivation";
      case ActivationType::ReLU:
        return "ReLU";
      case ActivationType::LUT:
        return "LUT";
      default:
        return "Unknown";
    }
  }

  /**
   * @brief Create a LayerParams object
   * @param layer_type: layer type for these parameters
   * @param entries: a map of key-entries
   * @return a LayerParams object
   */
  static std::unique_ptr<LayerParams> create(LayerType type,
                                             const Dict& entries);

  /**
   * @brief Copy a LayerParams object
   * @param src: source object
   * @return A copy of the source object
   */
  static std::unique_ptr<LayerParams> clone(const LayerParams* src);

  /**
   * @brief Reads a value from LayerParams.
   * @param key: identifier for the value
   * @return Value associated with the key
   */
  virtual Value get(KeyType const& key) const = 0;

  /**
   * @brief Check if the paramater exists in LayerParams.
   * @param name: parameter name
   * @return Boolean asserting the existence or not of the parameter
   */
  virtual bool has(const std::string& name) const = 0;

  /**
   * @brief Get all the keys in the LayerParams instance.
   * @return Vector of keys
   */
  virtual std::vector<std::string> keys() const = 0;

  /**
   * @brief compare two LayerParams objects.
   * @param other: object to compare with
   * @return true if values and layer type are the same
   */
  virtual bool operator==(const LayerParams& other) const = 0;

  /**
   * @brief Get the layer type
   * @return the layer type
   */
  virtual LayerType layer_type() const = 0;
};
}  // namespace akida
