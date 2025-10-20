/*
 *  Copyright (c) 2024 hikyuu.org
 *
 *  Created on: 2024-03-09
 *      Author: fasiondog
 */

#pragma once

#include "../Indicator.h"

namespace hku {

class IIc : public IndicatorImp {
public:
    IIc();
    IIc(const StockList& stks, const KQuery& query, int n, const Stock& ref_stk, bool spearman,
        bool strict);
    virtual ~IIc();

    virtual void _checkParam(const string& name) const override;
    virtual void _calculate(const Indicator& data) override;
    virtual IndicatorImpPtr _clone() override;

private:
    KQuery m_query;
    Stock m_ref_stk;
    StockList m_stks;

//============================================
// 序列化支持
//============================================
#if HKU_SUPPORT_SERIALIZATION
private:
    friend class boost::serialization::access;
    template <class Archive>
    void serialize(Archive& ar, const unsigned int version) {
        ar& BOOST_SERIALIZATION_BASE_OBJECT_NVP(IndicatorImp);
        ar& BOOST_SERIALIZATION_NVP(m_query);
        ar& BOOST_SERIALIZATION_NVP(m_ref_stk);
        ar& BOOST_SERIALIZATION_NVP(m_stks);
    }
#endif
};

}  // namespace hku