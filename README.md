# Realme OTA 获取工具

这是一个基于 Python 的命令行工具，用于查询和获取 Realme 设备的 OTA（Over-The-Air）更新链接。支持多种 RealmeUI 版本和地区。

## **🚀 使用方法**

### **1. 环境准备**
确保已安装 Python 3.x 以及 `requests` 库：
```bash
pip install requests
```

### **2. 运行参数**
```bash
python main.py <product_model> <ota_version> <rui_version> [nv_identifier] [选项]
```

- `product_model`: 产品型号 (如 `RMX3360`)。
- `ota_version`: 当前 OTA 版本 (如 `RMX3360_11.A.01_0010_202101010000`)。
- `rui_version`: RealmeUI 版本 (支持 `1, 2, 3, 4, 5, 6`)。
- `nv_identifier`: 运营商标识符 (可选，默认为 0)。

### **3. 常用选项**
- `-r, --region`: 指定请求区域 (`0=GL, 1=CN, 2=IN, 3=EU`)。
- `-b, --beta`: 尝试获取测试版（Beta）更新。
- `-i, --imei`: 提供 IMEI 以获取特定更新。
- `-d, --dump`: 将响应保存到 JSON 文件。
- `-v, --verbosity`: 设置日志详细程度 (0-5)。
- `-s, --silent`: 静默模式。

### **4. 示例**
查询 RMX3360 的中国区更新：
```bash
python main.py RMX3360 RMX3360_11.A.01_0010_202101010000 3 0 -r 1
```

---

## **⚠️ 常见报错及解决**

- **`ImportError: No module named 'requests'`**
  - **原因**：缺少依赖库。
  - **解决**：运行 `pip install requests`。

- **`RuntimeError: Response status mismatch, expected '200' got 'xxx'`**
  - **原因**：服务器返回错误，可能是参数不正确或服务器维护。
  - **解决**：检查 `product_model` 和 `ota_version` 是否匹配，或更换 `-r` 区域参数。

- **`RuntimeError: Response contents mismatch, expected 'body' got 'xxx'`**
  - **原因**：未找到更新，或请求的参数（如 IMEI）不正确。
  - **解决**：确认设备是否有可用的更新，或尝试使用 `-b` (Beta) 选项。

- **`json.decoder.JSONDecodeError`**
  - **原因**：响应内容不是有效的 JSON（通常是网络代理或连接错误）。
  - **解决**：检查网络连接，关闭 VPN 或更换网络环境。

---

## **🔗 类似仓库推荐**

如果你需要更多功能或不同平台的工具，可以参考以下仓库：
- [OPlus-Tracker](https://github.com/JerryTse-OSS/OPlus-Tracker) - 现代 OPlus ROM 追踪器。
- [oplus_ota_finder](https://github.com/SushiSanCat/oplus_ota_finder) - 适用于 Realme, Oppo, OnePlus 的 OTA 发现工具。
- [OTA-Multi-Tools](https://github.com/Devone127/OTA-Multi-Tools) - 自动搜索和下载官方固件的多功能工具。
- [realme-ota (Original)](https://github.com/R0rt1z2/realme-ota) - 本项目基于的原始仓库。

---

## **✍️ 署名与致谢**

- **原始作者**: [Roger Ortiz (R0rt1z2)](https://github.com/R0rt1z2/realme-ota)
- **工具支持**: 由 Trae (Gemini-3-Flash-Preview) 辅助整理。

---

## **⚖️ 许可证**
本项目遵循 [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) 开源协议。
