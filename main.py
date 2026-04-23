#!/usr/bin/python3
#
# 本文件是 realme-ota 的一部分 (https://github.com/R0rt1z2/realme-ota)。
# 版权所有 (c) 2022 Roger Ortiz。
#
# 本程序是自由软件：你可以根据自由软件基金会发布的 GNU 通用公共许可证第 3 版重新分发和/或修改它。
#
# 本程序是基于希望它有用的目的而发布，但没有任何形式的保证；甚至没有适销性或特定用途适用性的暗示保证。
# 请参阅 GNU 通用公共许可证以获取更多详细信息。
#
# 你应该已经收到了一份 GNU 通用公共许可证副本。如果没有，请访问 <http://www.gnu.org/licenses/>。
#

import os
import sys
import json
import requests
import io

from argparse import ArgumentParser

try:
    from utils import crypto
    from utils import data
    from utils.logger import Logger
    from utils.request import Request
except ImportError:
    from realme_ota.utils import crypto
    from realme_ota.utils import data
    from realme_ota.utils.request import Request
    from realme_ota.utils.logger import Logger

def main():
    # 设置标准输出编码为 utf-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    parser = ArgumentParser()
    # 详细程度
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbosity", type=int, choices=range(0, 6), default=4, help="设置详细程度级别。范围：0（无日志记录）到 5（调试）。默认值：4（信息）。")
    verbosity.add_argument("-s", "--silent", action='store_true', help="启用静默输出（清除日志记录）。'-v0' 的快捷方式。")
    # 位置参数
    parser.add_argument("product_model", type=str, help="产品型号 (ro.product.name)。")
    parser.add_argument("ota_version", help="OTA 版本 (ro.build.version.ota)。")
    parser.add_argument("rui_version", type=int, choices=[1, 2, 3, 4, 5, 6], help="RealmeUI 版本 (ro.build.version.realmeui)。")
    parser.add_argument("nv_identifier", type=str, nargs='?', help="NV（运营商）标识符 (ro.build.oplus_nv_id)（如果没有，请提供 0 或省略）。")
    # 请求属性
    req_opts = parser.add_argument_group("请求选项")
    req_opts.add_argument("-r", "--region", type=int, choices=[0, 1, 2, 3], default=0, help="为请求使用自定义区域 (GL = 0, CN = 1, IN = 2, EU = 3)。")
    req_opts.add_argument("-g", "--guid", type=str, default="0", help="文件 /data/system/openid_config.xml 中第三行的 guid（仅在中国提取 'CBT' 时需要）。")
    req_opts.add_argument("-i", "--imei", type=str, nargs='+', help="为请求指定一个或两个 IMEI。")
    req_opts.add_argument("-b", "--beta", action='store_true', help="尝试获取测试版本（可能需要 IMEI）。")
    req_opts.add_argument("-l", "--language", type=str, default=None, help="指定响应的语言（默认 en-EN，在中国为 zh-CN）。")
    req_opts.add_argument("--old-method", action='store_true', help="使用旧的请求方法（仅在 rui_version >= 2 时适用）。")
    # 输出设置
    out_opts = parser.add_argument_group("输出选项")
    out_opts.add_argument("-d", "--dump", type=str, help="将请求响应保存到文件中。")
    out_opts.add_argument("-o", "--only", type=str, help="仅显示响应中所需的值。")

    args = parser.parse_args()

    logger = Logger(
        level = 0 if args.silent else args.verbosity
    )

    request = Request(
        req_version = 1 if (args.old_method or args.rui_version == 1) else 2,
        model = args.product_model,
        ota_version = args.ota_version,
        rui_version = args.rui_version,
        nv_identifier = args.nv_identifier,
        region = args.region,
        deviceId = args.guid,
        imei0 = args.imei[0] if args.imei and len(args.imei) > 0 else None,
        imei1 = args.imei[1] if args.imei and len(args.imei) > 1 else None,
        beta = args.beta,
        language=args.language
    )

    logger.log(f"加载 {args.product_model} 的请求负载 (RealmeUI V{args.rui_version})")
    try:
        request.set_vars()
        req_body, req_hdrs, plain_body = request.set_body_headers()
    except Exception as e:
        logger.die(f"设置请求变量时出错 :( ({e})!", 2)

    logger.log(f"请求头:\n{json.dumps(req_hdrs, indent=4, sort_keys=True, ensure_ascii=False)}", 5)
    logger.log(f"请求体:\n{json.dumps(plain_body, indent=4, sort_keys=True, ensure_ascii=False)}", 5)
    logger.log(f"加密后的请求体:\n{json.dumps(req_body, indent=4, sort_keys=True, ensure_ascii=False)}", 5)

    logger.log("等待端点响应")
    try:
        response = requests.post(request.url, data = request.body, headers = request.headers, timeout = 30)
    except Exception as e:
        logger.die(f"向端点发送请求时出错 :( {e}!", 1)

    try:
        request.validate_response(response)
    except Exception as e:
        if args.ota_version[-17:] != '0000_000000000000':
            sys.argv[sys.argv.index(args.ota_version)] = args.ota_version[:-17] + '0000_000000000000'
            os.execl(sys.executable, sys.executable, *sys.argv)
        logger.die(f'{e}', 1)
    else:
        logger.log("一切正常")

    logger.log("开始处理")
    try:
        json_response = json.loads(response.content)
        logger.log(f"响应:\n{json.dumps(json_response, indent=4, sort_keys=True, ensure_ascii=False)}", 5)
        content = json.loads(request.decrypt(json_response[request.resp_key]))
    except Exception as e:
        logger.die(f"解析响应时出错 :( {e}!", 2)

    try:
        request.validate_content(content)
    except Exception as e:
        logger.die(f'{e}', 1)
    else:
        logger.log("处理完成")

    if args.only:
        try:
            content = content[args.only]
        except Exception as e:
            logger.die(f"无效的响应键: {args.only}!", 2)

    if args.dump:
        try:
            with open(args.dump, "w") as fp:
                json.dump(content, fp, sort_keys=True, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.die(f"将响应写入 {args.dump} 时出错 {e}!", 1)
        else:
            logger.log(f"成功将请求保存为 {args.dump}!")
    else:
        print(f"{json.dumps(content, indent=4, sort_keys=True, ensure_ascii=False)}")

if __name__ == '__main__':
    main()