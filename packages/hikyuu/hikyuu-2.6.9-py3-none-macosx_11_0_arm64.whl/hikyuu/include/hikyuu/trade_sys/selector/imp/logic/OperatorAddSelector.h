/*
 *  Copyright (c) 2024 hikyuu.org
 *
 *  Created on: 2024-05-27
 *      Author: fasiondog
 */

#pragma once

#include "OperatorSelector.h"

namespace hku {

class HKU_API OperatorAddSelector : public OperatorSelector {
    OPERATOR_SELECTOR_IMP(OperatorAddSelector, "SE_Add")
    OPERATOR_SELECTOR_SERIALIZATION
};

}  // namespace hku