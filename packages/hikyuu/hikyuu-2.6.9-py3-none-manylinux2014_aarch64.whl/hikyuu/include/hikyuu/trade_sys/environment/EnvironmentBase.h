/*
 * Environment.h
 *
 *  Created on: 2013-2-28
 *      Author: fasiondog
 */

#pragma once
#ifndef ENVIRONMENT_H_
#define ENVIRONMENT_H_

#include <set>
#include <shared_mutex>
#include "../../KQuery.h"
#include "../../utilities/Parameter.h"
#include "hikyuu/indicator/Indicator.h"

namespace hku {

/**
 * 环境判定策略基类
 * @note 外部环境应该和具体的交易对象没有关系
 * @ingroup Environment
 */
class HKU_API EnvironmentBase : public enable_shared_from_this<EnvironmentBase> {
    PARAMETER_SUPPORT_WITH_CHECK

public:
    EnvironmentBase();
    explicit EnvironmentBase(const string& name);
    virtual ~EnvironmentBase();

    // 用于 python clone, 但由于 mutex, 是非线程安全的
    EnvironmentBase(const EnvironmentBase&);

    /** 获取名称 */
    const string& name() const {
        return m_name;
    }

    /** 设置名称 */
    void name(const string& name) {
        m_name = name;
    }

    /** 复位 */
    void reset();

    /** 设置查询条件 */
    void setQuery(const KQuery& query);

    /** 获取查询条件 */
    const KQuery& getQuery() const {
        return m_query;
    }

    typedef shared_ptr<EnvironmentBase> EnvironmentPtr;
    /**
     * 克隆操作
     * @note Environment不同于其他的系统策略组件，它是不和特定的交易对象绑定的，可以共享，本质是
     *       上是不需要clone操作的，这里仅仅是为了整齐以及可能存在的特殊场景使用。
     */
    EnvironmentPtr clone();

    /**
     * 加入有效时间，在_calculate中调用
     * @param datetime 系统有效日期
     * @param value 默认为1.0，大于0表示有效，小于等于0表示无效
     */
    void _addValid(const Datetime& datetime, price_t value = 1.0);

    /**
     * 判断指定日期的外部环境是否有效
     * @param datetime 指定日期
     * @return true 有效 | false 无效
     */
    bool isValid(const Datetime& datetime) const;

    price_t getValue(const Datetime& datetime) const;

    /**
     * 以指标的形式获取实际值，与交易对象等长，<=0表示无效，>0表示系统有效
     * @note 带日期的时间序列指标
     */
    Indicator getValues() const;

    /** 子类计算接口 */
    virtual void _calculate() = 0;

    /** 子类复位接口 */
    virtual void _reset() {}

    /** 子类克隆接口 */
    virtual EnvironmentPtr _clone() = 0;

protected:
    virtual bool isPythonObject() const {
        return false;
    }

protected:
    string m_name;
    KQuery m_query;
    map<Datetime, size_t> m_date_index;
    vector<price_t> m_values;
    mutable std::shared_mutex m_mutex;

//============================================
// 序列化支持
//============================================
#if HKU_SUPPORT_SERIALIZATION
private:
    friend class boost::serialization::access;
    template <class Archive>
    void save(Archive& ar, const unsigned int version) const {
        ar& BOOST_SERIALIZATION_NVP(m_name);
        ar& BOOST_SERIALIZATION_NVP(m_params);
        // ev可能多个系统共享，保留m_query可能用于查错
        ar& BOOST_SERIALIZATION_NVP(m_query);
        ar& BOOST_SERIALIZATION_NVP(m_date_index);
        ar& BOOST_SERIALIZATION_NVP(m_values);
    }

    template <class Archive>
    void load(Archive& ar, const unsigned int version) {
        ar& BOOST_SERIALIZATION_NVP(m_name);
        ar& BOOST_SERIALIZATION_NVP(m_params);
        ar& BOOST_SERIALIZATION_NVP(m_query);
        ar& BOOST_SERIALIZATION_NVP(m_date_index);
        ar& BOOST_SERIALIZATION_NVP(m_values);
    }

    BOOST_SERIALIZATION_SPLIT_MEMBER()
#endif /* HKU_SUPPORT_SERIALIZATION */
};

#if HKU_SUPPORT_SERIALIZATION
BOOST_SERIALIZATION_ASSUME_ABSTRACT(EnvironmentBase)
#endif

#if HKU_SUPPORT_SERIALIZATION
/**
 * 对于没有私有变量的继承子类，可直接使用该宏定义序列化
 * @code
 * class Drived: public EnvironmentBase {
 *     ENVIRONMENT_NO_PRIVATE_MEMBER_SERIALIZATION
 *
 * public:
 *     Drived();
 *     ...
 * };
 * @endcode
 * @ingroup Environment
 */
#define ENVIRONMENT_NO_PRIVATE_MEMBER_SERIALIZATION               \
private:                                                          \
    friend class boost::serialization::access;                    \
    template <class Archive>                                      \
    void serialize(Archive& ar, const unsigned int version) {     \
        ar& BOOST_SERIALIZATION_BASE_OBJECT_NVP(EnvironmentBase); \
    }
#else
#define ENVIRONMENT_NO_PRIVATE_MEMBER_SERIALIZATION
#endif

/**
 * 客户程序都应使用该指针类型
 * @ingroup Environment
 */
typedef shared_ptr<EnvironmentBase> EnvironmentPtr;
typedef shared_ptr<EnvironmentBase> EVPtr;

#define ENVIRONMENT_IMP(classname)             \
public:                                        \
    virtual EnvironmentPtr _clone() override { \
        return std::make_shared<classname>();  \
    }                                          \
    virtual void _calculate() override;

/**
 * 输出Environment信息，如：Environment(name, params[...])
 * @ingroup Environment
 */
HKU_API std::ostream& operator<<(std::ostream& os, const EnvironmentPtr&);
HKU_API std::ostream& operator<<(std::ostream& os, const EnvironmentBase&);

} /* namespace hku */

#if FMT_VERSION >= 90000
template <>
struct fmt::formatter<hku::EnvironmentBase> : ostream_formatter {};

template <>
struct fmt::formatter<hku::EnvironmentPtr> : ostream_formatter {};
#endif

#endif /* ENVIRONMENT_H_ */
