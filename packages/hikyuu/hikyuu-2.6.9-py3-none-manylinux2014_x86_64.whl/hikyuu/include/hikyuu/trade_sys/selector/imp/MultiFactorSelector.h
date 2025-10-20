/*
 *  Copyright (c) 2024 hikyuu.org
 *
 *  Created on: 2024-03-30
 *      Author: fasiondog
 */

#pragma once

#include "../SelectorBase.h"

namespace hku {

class MultiFactorSelector : public SelectorBase {
public:
    MultiFactorSelector();
    MultiFactorSelector(const MFPtr& mf, int topn);
    virtual ~MultiFactorSelector();

    virtual void _checkParam(const string& name) const override;
    virtual void _reset() override;
    virtual SelectorPtr _clone() override;
    virtual SystemWeightList _getSelected(Datetime date) override;
    virtual bool isMatchAF(const AFPtr& af) override;
    virtual void _calculate() override;

    void setIndicators(const IndicatorList& inds) {
        HKU_ASSERT(!inds.empty());
        m_inds = inds;
    }

private:
    ScoreRecordList filterOnlyShouldBuy(Datetime date, const ScoreRecordList& scores, size_t topn);
    ScoreRecordList filterTopN(Datetime date, const ScoreRecordList& raw_scores, size_t topn,
                               bool only_should_buy);
    ScoreRecordList filterTopNReverse(Datetime date, const ScoreRecordList& raw_scores, size_t topn,
                                      bool only_should_buy, bool ignore_null);

private:
    IndicatorList m_inds;
    unordered_map<Stock, SYSPtr> m_stk_sys_dict;

    //============================================
    // 序列化支持
    //============================================
#if HKU_SUPPORT_SERIALIZATION
    friend class boost::serialization::access;
    template <class Archive>
    void serialize(Archive& ar, const unsigned int version) {
        ar& BOOST_SERIALIZATION_BASE_OBJECT_NVP(SelectorBase);
        ar& BOOST_SERIALIZATION_NVP(m_inds);
    }
#endif
};

}  // namespace hku