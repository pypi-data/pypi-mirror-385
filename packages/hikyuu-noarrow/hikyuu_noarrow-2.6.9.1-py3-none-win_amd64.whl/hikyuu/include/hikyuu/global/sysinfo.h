/*
 *  Copyright (c) 2023 hikyuu.org
 *
 *  Created on: 2023-09-26
 *      Author: fasiondog
 */

#pragma once

#include <string>

#ifndef HKU_API
#define HKU_API
#endif

namespace hku {

/**
 * 获取Hikyuu当前版本号
 * @return 版本号
 */
std::string HKU_API getVersion();

/**
 * 获取详细版本号，包含构建时间
 */
std::string HKU_API getVersionWithBuild();

/* 获取包括Git commit信息的版本号 */
std::string HKU_API getVersionWithGit();

/**
 * 判断是否有更新的版本可以升级
 */
bool HKU_API CanUpgrade();

/**
 * 获取当前最新的版本号，用于判断是否升级
 * @return std::string
 */
std::string HKU_API getLatestVersion();

/** 发送反馈信息 */
void HKU_API sendFeedback();

/** 用于发送 python 版本信息 */
void HKU_API sendPythonVersionFeedBack(int major, int minor, int micro);

/** 当前是否运行在 python 环境中 */
bool HKU_API runningInPython();

/** 当前是否运行在 Jupyter 环境中 */
bool HKU_API pythonInJupyter();

/** python 是否运行在交互模式下 */
bool HKU_API pythonInInteractive();

/** 设置是否运行在 python 下*/
void HKU_API setRunningInPython(bool inpython);

/** 设置 python 是否运行在交互模式下 */
void HKU_API setPythonInInteractive(bool interactive);

/** 当前是否运行在 Jupyter 环境中 */
void HKU_API setPythonInJupyter(bool injupyter);

}  // namespace hku
