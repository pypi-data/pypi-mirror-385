/*
 *  Copyright (c) 2025 hikyuu.org
 *
 *  Created on: 2025-04-10
 *      Author: fasiondog
 */

#pragma once

#include "hikyuu/config.h"

#include "BackTestPluginInterface.h"
#include "DevicePluginInterface.h"
#include "DataServerPluginInterface.h"
#include "ImportKDataToHdf5PluginInterface.h"
#include "ExtendIndicatorsPluginInterface.h"
#include "TMReportPluginInterface.h"
#include "DataDriverPluginInterface.h"
#include "HkuExtraPluginInterface.h"

#if HKU_ENABLE_ARROW
#include "HkuViewsPluginInterface.h"
#endif

namespace hku {

#define HKU_PLUGIN_BACKTEST "backtest"
#define HKU_PLUGIN_DEVICE "device"
#define HKU_PLUGIN_DATASERVER "dataserver"
#define HKU_PLUGIN_IMPORTKDATATOHDF5 "import2hdf5"
#define HKU_PLUGIN_EXTEND_INDICATOR "extind"
#define HKU_PLUGIN_TMREPORT "tmreport"
#define HKU_PLUGIN_CLICKHOUSE_DRIVER "clickhousedriver"
#define HKU_PLUGIN_HKU_EXTRA "hkuextra"
#define HKU_PLUGIN_HKU_VIEWS "hkuviews"

}  // namespace hku