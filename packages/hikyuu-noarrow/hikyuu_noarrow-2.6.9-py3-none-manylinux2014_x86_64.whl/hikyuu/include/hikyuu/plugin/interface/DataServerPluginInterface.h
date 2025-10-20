/*
 *  Copyright (c) 2025 hikyuu.org
 *
 *  Created on: 2025-04-08
 *      Author: fasiondog
 */

#pragma once

#include "hikyuu/utilities/plugin/PluginBase.h"

namespace hku {

class DataServerPluginInterface : public PluginBase {
public:
    DataServerPluginInterface() = default;
    virtual ~DataServerPluginInterface() = default;

    virtual void start(const std::string& addr, size_t work_num, bool save_tick, bool buf_tick,
                       const std::string& parquet_path) noexcept = 0;
    virtual void stop() noexcept = 0;
};

}  // namespace hku
