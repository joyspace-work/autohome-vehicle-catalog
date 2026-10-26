"""Conservative display plans for the existing internal catalog; no source requests."""

import json
import re

IMAGE_FIELD = "图片URL清单（json字符串）"
STATUS_FIELDS = ("图库状态", "图库状态说明")
TECHNICAL = re.compile(r"ID$|SHA256|JSON|json字符串|原文|^原始|^原所属|^原车系")
CATEGORY_ORDER = (
    "基本参数", "车身", "发动机", "电动机", "电池/充电", "变速箱", "底盘转向",
    "车轮制动", "被动安全", "主动安全", "驾驶操控", "四驱/越野", "驾驶硬件",
    "驾驶功能", "外观/防盗", "车外灯光", "天窗/玻璃", "外后视镜", "互联/智能化",
    "方向盘/内后视镜", "车内充电", "座椅配置", "音响/车内灯光", "空调/冰箱",
    "特色配置", "外观颜色", "内饰颜色", "选装包",
)


def gallery_status(row):
    """Classify saved URL evidence, never infer present HTTP validity or completeness."""
    try:
        urls = json.loads(row.get(IMAGE_FIELD) or "[]")
        groups = json.loads(row.get("图库分组JSON") or "[]")
    except (ValueError, TypeError):
        return "待核验", "已有图片JSON无法解析；保留原值，需核对。"
    if not isinstance(urls, list) or not isinstance(groups, list):
        return "待核验", "已有图片JSON结构异常；保留原值，需核对。"
    if any(not isinstance(u, str) or not u.startswith("https://") for u in urls):
        return "待核验", "图片URL结构需核对；未作本次HTTP检查。"
    if row.get("图片数") != len(urls):
        return "待核验", "图片数与现有URL清单不一致；未改原值。"
    if not urls:
        evidence = str(row.get("图片说明") or "")
        if re.search(r"401|403|429|验证码|来源暂停", evidence):
            return "来源暂停", "已有说明记录访问限制；本次未重试。"
        if "失败" in evidence:
            return "失败", "已有说明记录采集失败；本次未重试。"
        return "待采", "现有快照没有图片URL；不等同于官网无图。"
    valid_groups = [g for g in groups if isinstance(g, dict)]
    if not valid_groups or len(valid_groups) != len(groups):
        return "待核验", "已有URL，但动力/年款分组证据不完整；未作本次HTTP检查。"
    if any(g.get("图片类别") == "车系封面" or not g.get("图片URL") for g in valid_groups):
        return "部分", "含仅封面兜底或缺图分组；封面不证明具体配置/年款；未作本次HTTP检查。"
    return "已采", "已有快照已保存图库URL及动力/年款分组；每组限量采集，非官网全量；未作本次HTTP检查。"


def visible_plan(role, fields, current):
    """Keep official parameter order from the current view; hide only technical columns."""
    names = [f["name"] for f in fields]
    if role == "车系":
        preferred = ["车系名称", "brochure_cover", "品牌", "动力类型", "配置版本",
                     *STATUS_FIELDS, "图片数", "图片类别", "图片年款", "图片来源页",
                     "来源车系页", "来源采集时间"]
    elif role == "配置索引":
        preferred = ["车型全称", "品牌", "车系名称", "配置名称", "动力类型", "销售状态",
                     "所属车型", *CATEGORY_ORDER, "颜色资料", "选配价格说明", "来源参数页",
                     "来源采集时间"]
    else:
        preferred = [n for n in current if not TECHNICAL.search(n)]
    return list(dict.fromkeys(n for n in preferred if n in names))
