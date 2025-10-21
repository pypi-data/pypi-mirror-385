/*******************************************************************************
 * Copyright 2019 Brainchip Holdings Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ********************************************************************************
 */

#pragma once

#include <memory>
#include <stdexcept>

#include "akida/hw_version.h"
#include "akida/ip_version.h"
#include "akida/mesh.h"
#include "infra/exports.h"

namespace akida {

class HardwareDevice;

class Device;

using DevicePtr = std::shared_ptr<Device>;
using DeviceConstPtr = std::shared_ptr<const Device>;

/**
 * class Device
 *
 * Public interface to an Akida Device (real or virtual)
 *
 */
class AKIDASHAREDLIB_EXPORT Device {
 public:
  virtual ~Device() = default;
  /**
   * @brief Get the Device version
   * @return a HwVersion
   */
  virtual HwVersion version() const = 0;

  /**
   * @brief Get the Device IP version
   * @return a IpVersion
   */
  IpVersion get_ip_version() const { return version().get_ip_version(); }

  /**
   * @brief Partial reconfiguration feature
   * @return if the feature is supported.
   */
  bool support_hwpr() const { return version().product_id >= 0xA1; }

  /**
   * @brief Sparse inputs feature
   * @return if the feature is supported.
   */
  bool support_sparse_inputs() const { return version().product_id == 0; }

  /**
   * @brief Dense outputs feature
   * @return if the feature is supported.
   */
  bool support_dense_outputs() const { return version().product_id >= 0xA1; }

  /**
   * @brief Checks if the Device is compatible with a IP version.
   * @param ip_version The IP version.
   * @throws std::invalid_argument if versions are incompatible.
   */
  void check_hw_and_ip_version_compatibility(IpVersion ip_version) const {
    if (version().get_ip_version() != ip_version) {
      throw std::invalid_argument(
          "Incompatible hardware and Ip versions: "
          "HW Version is " +
          version().to_string() + " with product id = " +
          std::to_string(static_cast<int>(version().product_id)) +
          " while IP version is " + to_string(ip_version) + ".");
    }
  }

  /**
   * @brief Get the Device description
   * @return a char*
   */
  virtual const char* desc() const = 0;

  /**
   * @brief Return the Device Neural Processor Mesh layout
   *
   * @return a reference to a Mesh class
   */
  virtual const Mesh& mesh() const = 0;

  /**
   * @brief Return the Hardware Device if exist
   *
   * @return a pointer to a HardwareDevice
   */
  virtual HardwareDevice* hardware() const = 0;

 private:
};

}  // namespace akida
