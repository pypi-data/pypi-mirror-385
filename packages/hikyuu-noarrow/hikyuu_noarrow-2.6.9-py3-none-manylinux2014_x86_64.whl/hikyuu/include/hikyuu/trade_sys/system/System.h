/*
 * SystemBase.h
 *
 *  Created on: 2013-3-3
 *      Author: fasiondog
 */

#pragma once
#ifndef SYSTEMBASE_H_
#define SYSTEMBASE_H_

#include <nlohmann/json.hpp>
// #include "../../KData.h"
// #include "../../utilities/Parameter.h"
// #include "../../trade_manage/TradeManager.h"
#include "../environment/EnvironmentBase.h"
#include "../condition/ConditionBase.h"
#include "../moneymanager/MoneyManagerBase.h"
#include "../signal/SignalBase.h"
#include "../stoploss/StoplossBase.h"
#include "../profitgoal/ProfitGoalBase.h"
#include "../slippage/SlippageBase.h"
#include "TradeRequest.h"
#include "SystemPart.h"
#include "../../serialization/KData_serialization.h"

namespace hku {

using json = nlohmann::json;

class HKU_API Portfolio;
class HKU_API AllocateFundsBase;
class HKU_API WalkForwardSystem;

/**
 * 交易系统基类
 * @ingroup System
 */
class HKU_API System {
    PARAMETER_SUPPORT_WITH_CHECK
    friend class HKU_API Portfolio;
    friend class HKU_API AllocateFundsBase;
    friend class HKU_API WalkForwardSystem;

public:
    /** 默认构造函数 */
    System();

    /** 指定系统名称的构造函数 */
    explicit System(const string& name);

    /**
     * @brief 构造函数
     *
     * @param tm 指定账户
     * @param mm 指定资金管理策略
     * @param ev 指定市场环境判断策略
     * @param cn 指定系统条件判断策略
     * @param sg 指定信号指示器
     * @param st 指定止损策略
     * @param tp 指定止盈策略
     * @param pg 指定目标盈利策略
     * @param sp 指定移滑价差算法
     * @param name 系统名称
     */
    System(const TradeManagerPtr& tm, const MoneyManagerPtr& mm, const EnvironmentPtr& ev,
           const ConditionPtr& cn, const SignalPtr& sg, const StoplossPtr& st,
           const StoplossPtr& tp, const ProfitGoalPtr& pg, const SlippagePtr& sp,
           const string& name);

    System(const System&) = default;

    /** 析构函数 */
    virtual ~System();

    typedef SystemPart Part;

    /** 获取名称 */
    const string& name() const;

    /** 设置名称 */
    void name(const string& name);

    /** 获取交易对象 */
    KData getTO() const;

    /** 获取管理账户 */
    TradeManagerPtr getTM() const;

    /** 获取资金管理策略 */
    MoneyManagerPtr getMM() const;

    /** 获取市场环境判定策略 */
    EnvironmentPtr getEV() const;

    /** 获取系统条件判定策略 */
    ConditionPtr getCN() const;

    /** 获取信号指示器 */
    SignalPtr getSG() const;

    /** 获取止损策略 */
    StoplossPtr getST() const;

    /** 获取止盈策略 */
    StoplossPtr getTP() const;

    /** 获取盈利目标策略 */
    ProfitGoalPtr getPG() const;

    /** 获取移滑价差策略 */
    SlippagePtr getSP() const;

    /** 设定管理账户 */
    void setTM(const TradeManagerPtr& tm);

    /** 设定资金管理策略 */
    void setMM(const MoneyManagerPtr& mm);

    /** 设定市场环境判定策略 */
    void setEV(const EnvironmentPtr& ev);

    /** 设定系统条件判定策略 */
    void setCN(const ConditionPtr& cn);

    /** 设定信号指示器 */
    void setSG(const SignalPtr& sg);

    /** 设定止损策略 */
    void setST(const StoplossPtr& st);

    /** 设定止盈策略 */
    void setTP(const StoplossPtr& tp);

    /** 设定盈利目标策略 */
    void setPG(const ProfitGoalPtr& pg);

    /** 设定移滑价差算法 */
    void setSP(const SlippagePtr& sp);

    /** 获取交易的证券 */
    Stock getStock() const;

    /** 设定交易的证券 */
    void setStock(const Stock& stk);

    const KQuery& getQuery() const;

    /** 获取实际执行的交易记录，和 TM 的区别是不包含权息调整带来的交易记录 */
    const TradeRecordList& getTradeRecordList() const;

    /** 获取买入请求，“delay”模式下查看下一时刻是否存在买入操作 */
    const TradeRequest& getBuyTradeRequest() const;

    /** 获取卖出请求，“delay”模式下查看下一时刻是否存在卖出操作 */
    const TradeRequest& getSellTradeRequest() const;

    const TradeRequest& getSellShortTradeRequest() const;
    const TradeRequest& getBuyShortTradeRequest() const;

    /** 将所有组件全部置为非共享 */
    void setNotSharedAll();

    /**
     * 复位，但不包括已有的交易对象，以及共享的部件
     * @note 实际复位操作依赖于系统中各个部件的共享参数
     */
    void reset();

    /** 强制复位所有组件以及清空已有的交易对象，忽略组件的共享属性 */
    void forceResetAll();

    typedef shared_ptr<System> SystemPtr;

    /**
     * 克隆操作，会依次调用所有部件的clone操作
     */
    SystemPtr clone();

    /**
     * 设置交易对象
     * @note 其中tm, ev没有setTO接口
     */
    void setTO(const KData& kdata);

    /**
     * 回测完成后，返回最后一天交易记录，以及需要延迟的买入和卖出延迟请求
     */
    json lastSuggestion() const;

    /**
     * @brief 不指定stock的方式下run，需要事先通过setStock设定stock
     * @param query 查询条件
     * @param reset 执行前是否依据系统部件共享属性复位
     * @param resetAll 强制复位所有部件
     */
    void run(const KQuery& query, bool reset = true, bool resetAll = false);

    /**
     * @brief 运行系统策略
     * @param stock 指定的证券
     * @param query 指定查询条件
     * @param reset 执行前是否依据系统部件共享属性复位
     * @param resetAll 强制复位所有部件
     */
    void run(const Stock& stock, const KQuery& query, bool reset = true, bool resetAll = false);

    /**
     * @brief 运行系统
     * @param kdata 指定的交易对象
     * @param reset 执行前是否依据系统部件共享属性复位
     * @param resetAll 强制复位所有部件
     */
    virtual void run(const KData& kdata, bool reset = true, bool resetAll = false);

    /**
     * @brief 在指定的日期执行一步，仅由 PF 调用
     * @param datetime 指定的日期
     * @return TradeRecord
     */
    virtual TradeRecord runMoment(const Datetime& datetime);

    virtual TradeRecord runMomentOnOpen(const Datetime& datetime);
    virtual TradeRecord runMomentOnClose(const Datetime& datetime);

    // 运行前准备工作, 失败将抛出异常
    virtual void readyForRun();

    // 由各个相关组件调用，用于组件参数变化时通知 sys，以便重算
    void partChangedNotify() {
        m_calculated = false;
    }

    virtual void _reset() {}
    virtual void _forceResetAll() {}

    /** 子类克隆接口 */
    virtual SystemPtr _clone() {
        return make_shared<System>();
    }

    virtual string str() const;

public:
    //-------------------------
    // 仅供 PF/AF 内部调用
    //-------------------------

    // 强制以开盘价卖出，仅供 PF/AF 内部调用
    virtual TradeRecord sellForceOnOpen(const Datetime& date, double num, Part from) {
        HKU_ASSERT(from == PART_ALLOCATEFUNDS || from == PART_PORTFOLIO);
        return _sellForce(date, num, from, true);
    }

    // 强制以收盘价卖出，仅供 PF/AF 内部调用
    virtual TradeRecord sellForceOnClose(const Datetime& date, double num, Part from) {
        HKU_ASSERT(from == PART_ALLOCATEFUNDS || from == PART_PORTFOLIO);
        return _sellForce(date, num, from, false);
    }

    // 清除已有的交易请求，供Portfolio使用
    virtual void clearDelayBuyRequest();

    // 当前是否存在延迟的操作请求，供Portfolio
    bool haveDelaySellRequest() const {
        return m_sellRequest.valid;
    }

    bool haveDelayBuyRequest() const {
        return m_buyRequest.valid;
    }

    // 处理延迟买入请求，仅供 PF 调用
    virtual TradeRecord pfProcessDelaySellRequest(const Datetime& date);

    // 处理延迟买入请求，仅供 PF 调用
    virtual TradeRecord pfProcessDelayBuyRequest(const Datetime& date);

protected:
    virtual bool isPythonObject() const {
        return false;
    }

private:
    bool _environmentIsValid(const Datetime& datetime);
    bool _conditionIsValid(const Datetime& datetime);

    // 通知所有需要接收实际买入交易记录的部件
    void _buyNotifyAll(const TradeRecord&);

    // 通知所有需要接收实际卖出交易记录的部件
    void _sellNotifyAll(const TradeRecord&);

    double _getBuyNumber(const Datetime&, price_t price, price_t risk, Part from);
    double _getSellNumber(const Datetime&, price_t price, price_t risk, Part from);
    double _getSellShortNumber(const Datetime&, price_t price, price_t risk, Part from);
    double _getBuyShortNumber(const Datetime&, price_t price, price_t risk, Part from);

    price_t _getStoplossPrice(const KRecord& today, const KRecord& src_today, price_t price);
    price_t _getShortStoplossPrice(const KRecord& today, const KRecord& src_today, price_t price);

    price_t _getTakeProfitPrice(const Datetime& datetime, price_t currentPrice);

    price_t _getGoalPrice(const Datetime& datetime, price_t price);
    price_t _getShortGoalPrice(const Datetime&, price_t price);

    price_t _getRealBuyPrice(const Datetime& datetime, price_t planPrice);
    price_t _getRealSellPrice(const Datetime& datetime, price_t planPrice);

    TradeRecord _buy(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _buyNow(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _buyDelay(const KRecord& today, const KRecord& src_today);
    void _submitBuyRequest(const KRecord& today, const KRecord& src_today, Part from);

    TradeRecord _sell(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _sellNow(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _sellDelay(const KRecord& today, const KRecord& src_today);
    void _submitSellRequest(const KRecord& today, const KRecord& src_today, Part from);

    TradeRecord _sellShort(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _sellShortNow(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _sellShortDelay(const KRecord& today, const KRecord& src_today);
    void _submitSellShortRequest(const KRecord& today, const KRecord& src_today, Part from);

    TradeRecord _buyShort(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _buyShortNow(const KRecord& today, const KRecord& src_today, Part from);
    TradeRecord _buyShortDelay(const KRecord& today, const KRecord& src_today);
    void _submitBuyShortRequest(const KRecord& today, const KRecord& src_today, Part from);

    TradeRecord _processRequest(const KRecord& today, const KRecord& src_today);

    TradeRecord _runMoment(const KRecord& today, const KRecord& src_today);
    TradeRecord _runMomentOnOpen(const KRecord& today, const KRecord& src_today);
    TradeRecord _runMomentOnClose(const KRecord& today, const KRecord& src_today);

    // Portfolio | AllocateFunds 指示立即进行强制卖出，以便对 buy_delay 的系统进行资金调整
    TradeRecord _sellForce(const Datetime& date, double num, Part from, bool on_open);

protected:
    TradeManagerPtr m_tm;
    MoneyManagerPtr m_mm;
    EnvironmentPtr m_ev;
    ConditionPtr m_cn;
    SignalPtr m_sg;
    StoplossPtr m_st;
    StoplossPtr m_tp;
    ProfitGoalPtr m_pg;
    SlippagePtr m_sp;

    string m_name;
    Stock m_stock;
    KData m_kdata;
    KData m_src_kdata;  // 未复权的原始 K 线数据

    bool m_calculated;  // 控制是否需要重新计算
    bool m_pre_ev_valid;
    bool m_pre_cn_valid;

    int m_buy_days;                 // 每一次买入清零，计算一次加1，即买入后的天数
    int m_sell_short_days;          // 每一次卖空清零
    TradeRecordList m_trade_list;   // 保存实际执行的交易记录
    price_t m_lastTakeProfit;       // 上一次多头止损价，用于保证止赢价单调递增
    price_t m_lastShortTakeProfit;  // 上一次空头止赢价

    TradeRequest m_buyRequest;
    TradeRequest m_sellRequest;
    TradeRequest m_sellShortRequest;
    TradeRequest m_buyShortRequest;

private:
    void initParam();  // 初始化参数及其默认值

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

        ar& BOOST_SERIALIZATION_NVP(m_tm);
        ar& BOOST_SERIALIZATION_NVP(m_ev);
        ar& BOOST_SERIALIZATION_NVP(m_cn);
        ar& BOOST_SERIALIZATION_NVP(m_mm);
        ar& BOOST_SERIALIZATION_NVP(m_sg);
        ar& BOOST_SERIALIZATION_NVP(m_st);
        ar& BOOST_SERIALIZATION_NVP(m_tp);
        ar& BOOST_SERIALIZATION_NVP(m_pg);
        ar& BOOST_SERIALIZATION_NVP(m_sp);

        ar& BOOST_SERIALIZATION_NVP(m_kdata);
        ar& BOOST_SERIALIZATION_NVP(m_stock);

        ar& BOOST_SERIALIZATION_NVP(m_calculated);
        ar& BOOST_SERIALIZATION_NVP(m_pre_ev_valid);
        ar& BOOST_SERIALIZATION_NVP(m_pre_cn_valid);

        ar& BOOST_SERIALIZATION_NVP(m_buy_days);
        ar& BOOST_SERIALIZATION_NVP(m_sell_short_days);
        ar& BOOST_SERIALIZATION_NVP(m_trade_list);
        ar& BOOST_SERIALIZATION_NVP(m_lastTakeProfit);
        ar& BOOST_SERIALIZATION_NVP(m_lastShortTakeProfit);

        ar& BOOST_SERIALIZATION_NVP(m_buyRequest);
        ar& BOOST_SERIALIZATION_NVP(m_sellRequest);
        ar& BOOST_SERIALIZATION_NVP(m_sellShortRequest);
        ar& BOOST_SERIALIZATION_NVP(m_buyShortRequest);
    }

    template <class Archive>
    void load(Archive& ar, const unsigned int version) {
        ar& BOOST_SERIALIZATION_NVP(m_name);
        ar& BOOST_SERIALIZATION_NVP(m_params);

        ar& BOOST_SERIALIZATION_NVP(m_tm);
        ar& BOOST_SERIALIZATION_NVP(m_ev);
        ar& BOOST_SERIALIZATION_NVP(m_cn);
        ar& BOOST_SERIALIZATION_NVP(m_mm);
        ar& BOOST_SERIALIZATION_NVP(m_sg);
        ar& BOOST_SERIALIZATION_NVP(m_st);
        ar& BOOST_SERIALIZATION_NVP(m_tp);
        ar& BOOST_SERIALIZATION_NVP(m_pg);
        ar& BOOST_SERIALIZATION_NVP(m_sp);

        ar& BOOST_SERIALIZATION_NVP(m_kdata);
        ar& BOOST_SERIALIZATION_NVP(m_stock);

        ar& BOOST_SERIALIZATION_NVP(m_calculated);
        ar& BOOST_SERIALIZATION_NVP(m_pre_ev_valid);
        ar& BOOST_SERIALIZATION_NVP(m_pre_cn_valid);

        ar& BOOST_SERIALIZATION_NVP(m_buy_days);
        ar& BOOST_SERIALIZATION_NVP(m_sell_short_days);
        ar& BOOST_SERIALIZATION_NVP(m_trade_list);
        ar& BOOST_SERIALIZATION_NVP(m_lastTakeProfit);
        ar& BOOST_SERIALIZATION_NVP(m_lastShortTakeProfit);

        ar& BOOST_SERIALIZATION_NVP(m_buyRequest);
        ar& BOOST_SERIALIZATION_NVP(m_sellRequest);
        ar& BOOST_SERIALIZATION_NVP(m_sellShortRequest);
        ar& BOOST_SERIALIZATION_NVP(m_buyShortRequest);
    }

    BOOST_SERIALIZATION_SPLIT_MEMBER()
#endif /* HKU_SUPPORT_SERIALIZATION */
};

/**
 * 客户程序应使用该指针进行操作
 * @ingroup System
 */
typedef shared_ptr<System> SystemPtr;
typedef shared_ptr<System> SYSPtr;
typedef vector<SystemPtr> SystemList;

HKU_API std::ostream& operator<<(std::ostream& os, const System& sys);
HKU_API std::ostream& operator<<(std::ostream& os, const SystemPtr& sys);

inline const string& System::name() const {
    return m_name;
}

inline void System::name(const string& name) {
    m_name = name;
}

inline KData System::getTO() const {
    return m_kdata;
}

inline TradeManagerPtr System::getTM() const {
    return m_tm;
}

inline MoneyManagerPtr System::getMM() const {
    return m_mm;
}

inline EnvironmentPtr System::getEV() const {
    return m_ev;
}

inline ConditionPtr System::getCN() const {
    return m_cn;
}

inline SignalPtr System::getSG() const {
    return m_sg;
}

inline StoplossPtr System::getST() const {
    return m_st;
}

inline StoplossPtr System::getTP() const {
    return m_tp;
}

inline ProfitGoalPtr System::getPG() const {
    return m_pg;
}

inline SlippagePtr System::getSP() const {
    return m_sp;
}

inline void System::setTM(const TradeManagerPtr& tm) {
    if (m_tm != tm) {
        m_tm = tm;
        m_calculated = false;
    }
}

inline void System::setMM(const MoneyManagerPtr& mm) {
    if (m_mm != mm) {
        m_mm = mm;
        m_calculated = false;
    }
}

inline void System::setEV(const EnvironmentPtr& ev) {
    if (m_ev != ev) {
        m_ev = ev;
        m_calculated = false;
    }
}

inline void System::setCN(const ConditionPtr& cn) {
    if (m_cn != cn) {
        m_cn = cn;
        m_calculated = false;
    }
}

inline void System::setSG(const SignalPtr& sg) {
    if (m_sg != sg) {
        m_sg = sg;
        m_calculated = false;
    }
}

inline void System::setST(const StoplossPtr& st) {
    if (m_st != st) {
        m_st = st;
        m_calculated = false;
    }
}

inline void System::setTP(const StoplossPtr& tp) {
    if (m_tp != tp) {
        m_tp = tp;
        m_calculated = false;
    }
}

inline void System::setPG(const ProfitGoalPtr& pg) {
    if (m_pg != pg) {
        m_pg = pg;
        m_calculated = false;
    }
}

inline void System::setSP(const SlippagePtr& sp) {
    if (m_sp != sp) {
        m_sp = sp;
        m_calculated = false;
    }
}

inline Stock System::getStock() const {
    return m_stock;
}

inline void System::setStock(const Stock& stk) {
    if (m_stock != stk) {
        m_stock = stk;
        m_calculated = false;
    }
}

inline const KQuery& System::getQuery() const {
    return m_kdata.getQuery();
}

inline const TradeRecordList& System::getTradeRecordList() const {
    return m_trade_list;
}

inline const TradeRequest& System::getBuyTradeRequest() const {
    return m_buyRequest;
}

inline const TradeRequest& System::getSellTradeRequest() const {
    return m_sellRequest;
}

inline const TradeRequest& System::getSellShortTradeRequest() const {
    return m_sellShortRequest;
}

inline const TradeRequest& System::getBuyShortTradeRequest() const {
    return m_buyShortRequest;
}

inline bool System::_environmentIsValid(const Datetime& datetime) {
    return m_ev ? m_ev->isValid(datetime) : true;
}

inline bool System::_conditionIsValid(const Datetime& datetime) {
    return m_cn ? m_cn->isValid(datetime) : true;
}

inline double System ::_getBuyNumber(const Datetime& datetime, price_t price, price_t risk,
                                     Part from) {
    return m_mm ? m_mm->getBuyNumber(datetime, m_stock, price, risk, from) : 0;
}

inline double System ::_getSellNumber(const Datetime& datetime, price_t price, price_t risk,
                                      Part from) {
    return m_mm ? m_mm->getSellNumber(datetime, m_stock, price, risk, from) : 0;
}

inline double System ::_getSellShortNumber(const Datetime& datetime, price_t price, price_t risk,
                                           Part from) {
    return m_mm ? m_mm->getSellShortNumber(datetime, m_stock, price, risk, from) : 0;
}

inline double System ::_getBuyShortNumber(const Datetime& datetime, price_t price, price_t risk,
                                          Part from) {
    return m_mm ? m_mm->getBuyShortNumber(datetime, m_stock, price, risk, from) : 0;
}

inline price_t System ::_getRealBuyPrice(const Datetime& datetime, price_t planPrice) {
    return m_sp ? m_sp->getRealBuyPrice(datetime, planPrice) : planPrice;
}

inline price_t System ::_getRealSellPrice(const Datetime& datetime, price_t planPrice) {
    return m_sp ? m_sp->getRealSellPrice(datetime, planPrice) : planPrice;
}

inline price_t System ::_getTakeProfitPrice(const Datetime& datetime, price_t currentPrice) {
    return m_tp ? m_tp->getPrice(datetime, currentPrice) : 0.0;
}

inline price_t System ::_getGoalPrice(const Datetime& datetime, price_t price) {
    return m_pg ? m_pg->getGoal(datetime, price) : Null<price_t>();
}

inline price_t System ::_getShortGoalPrice(const Datetime& datetime, price_t price) {
    return m_pg ? m_pg->getShortGoal(datetime, price) : 0.0;
}

} /* namespace hku */

#if FMT_VERSION >= 90000
template <>
struct fmt::formatter<hku::System> : ostream_formatter {};

template <>
struct fmt::formatter<hku::SystemPtr> : ostream_formatter {};
#endif

#endif /* SYSTEMBASE_H_ */
