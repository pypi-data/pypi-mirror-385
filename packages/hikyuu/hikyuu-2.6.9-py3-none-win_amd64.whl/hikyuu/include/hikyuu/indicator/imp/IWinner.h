/*
 *  Copyright (c) 2025 hikyuu.org
 *
 *  Created on: 2025-01-25
 *      Author: fasiondog
 */

#pragma once
#ifndef INDICATOR_IMP_IWINNER_H_
#define INDICATOR_IMP_IWINNER_H_

#include "../Indicator.h"

namespace hku {

class IWinner : public IndicatorImp {
    INDICATOR_IMP(IWinner)
    INDICATOR_IMP_NO_PRIVATE_MEMBER_SERIALIZATION

public:
    IWinner();
    virtual ~IWinner();
};

} /* namespace hku */
#endif /* INDICATOR_IMP_IWINNER_H_ */
