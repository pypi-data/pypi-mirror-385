/*
 * hikyuu.h
 *
 *  Created on: 2011-11-13
 *      Author: fasiondog
 */

#pragma once
#ifndef HIKYUU_H_
#define HIKYUU_H_

#include "KData.h"
#include "Stock.h"
#include "StockManager.h"
#include "utilities/Parameter.h"
#include "trade_manage/build_in.h"
#include "trade_sys/all.h"
#include "strategy/Strategy.h"
#include "indicator/build_in.h"

namespace hku {

/**
 * @ingroup StockManage
 * @{
 */

/**
 * Hikyuu核心初始化，客户端必须在程序入口处调用
 * @param config_file_name 配置信息文件名
 * @param ignore_preload 忽略配置信息中的预加载设置，即不加载数据至内存。
 *                       用于某些场合启动hikyuu，但仅用于获取数据库的基本信息。
 * @param context 指定加载数据上下文，用于独立策略时仅加载指定的股票数据
 */
void HKU_API hikyuu_init(const string& config_file_name, bool ignore_preload = false,
                         const StrategyContext& context = StrategyContext({"all"}));

/**
 * @brief 尝试从 ini 文件获取配置参数
 * @param config_file_name ini 文件名
 * @param baseParam [out]
 * @param blockParam [out]
 * @param kdataParam [out]
 * @param preloadParam [out]
 * @param hkuParam [out]
 */
void HKU_API getConfigFromIni(const string& config_file_name, Parameter& baseParam,
                              Parameter& blockParam, Parameter& kdataParam, Parameter& preloadParam,
                              Parameter& hkuParam);

/** @} */

}  // namespace hku

#endif /* HIKYUU_H_ */
