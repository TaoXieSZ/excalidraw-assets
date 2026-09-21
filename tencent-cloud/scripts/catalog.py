#!/usr/bin/env python3
"""Build a Tencent Cloud product icon source catalog from the official SVG zip."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


CATEGORY_RULES = [
    (
        "计算与容器",
        "compute-container",
        [
            "云服务器",
            "cvm",
            "gpu",
            "fpga",
            "批量计算",
            "batchcompute",
            "容器",
            "kubernetes",
            "tke",
            "serverless",
            "函数",
            "专用宿主机",
            "裸金属",
            "bare metal",
            "auto scaling",
            "弹性伸缩",
            "tencentos",
            "专属可用区",
            "dedicated",
            "cloud virtual machine",
            "cloud virtual desktop",
            "云桌面",
            "cloud hosting cluster",
            "云托付物理服务器",
            "cloudbase run",
            "云托管",
            "web 应用托管",
            "lighthouse",
            "轻量应用服务器",
            "high performance computing",
            "hpc",
            "高性能计算",
            "高性能应用",
        ],
    ),
    (
        "存储",
        "storage",
        [
            "对象存储",
            "object storage",
            "cos",
            "cloud object storage",
            "cloud infinite",
            "数据万象",
            "文件存储",
            "file storage",
            "cfs",
            "云硬盘",
            "block storage",
            "归档存储",
            "archive storage",
            "hdfs",
            "storage gateway",
            "数据保险箱",
            "data coffer",
            "goose filesystem",
            "tstor",
            "备份一体机",
            "存储一体机",
            "并行文件",
            "parallel file",
        ],
    ),
    (
        "网络与CDN",
        "network-cdn",
        [
            "cdn",
            "content delivery",
            "网络",
            "公网",
            "anycast",
            "加速",
            "负载均衡",
            "load balancer",
            "clb",
            "nat",
            "vpn",
            "vpc",
            "私有网络",
            "云联网",
            "connect network",
            "专线",
            "direct connect",
            "sd-wan",
            "域名",
            "dns",
            "边缘",
            "edge",
            "带宽包",
            "bandwidth",
            "p2p",
            "x-p2p",
            "5g",
            "traffic package",
            "共享流量包",
            "peering",
            "对等连接",
            "private link",
            "私有连接",
            "network interface",
            "弹性网卡",
        ],
    ),
    (
        "数据库",
        "database",
        [
            "数据库",
            "database",
            "tdsql",
            "mysql",
            "postgresql",
            "postgres",
            "redis",
            "mongodb",
            "sql server",
            "mariadb",
            "memcached",
            "keewidb",
            "elasticsearch",
            "dts",
            "data transmission service",
            "数据传输",
            "数据迁移",
            "data migration",
            "htap",
            "libra",
        ],
    ),
    (
        "安全",
        "security",
        [
            "安全",
            "security",
            "ddos",
            "防火墙",
            "firewall",
            "waf",
            "漏洞",
            "vulnerability",
            "主机安全",
            "workload protection",
            "ssl",
            "证书",
            "certificate",
            "堡垒机",
            "bastion",
            "风控",
            "risk",
            "合规",
            "compliance",
            "审计",
            "audit",
            "加密",
            "encryption",
            "密钥",
            "kms",
            "身份",
            "identity",
            "访问管理",
            "access management",
            "cam",
            "零信任",
            "captcha",
            "人脸核身",
            "账号安全",
            "攻防",
            "attack",
            "数据脱敏",
            "data mask",
            "software composition",
            "二进制软件成分",
            "secrets manager",
            "凭据管理",
            "threat",
            "威胁",
            "micro-segmentation",
            "微隔离",
            "anti-fraud",
            "反欺诈",
            "advanced threat",
            "高级威胁",
            "credential",
            "云证通",
            "number verification",
            "号码认证",
            "exposure",
            "暴露面",
        ],
    ),
    (
        "AI与智能",
        "ai-intelligence",
        [
            "ai",
            "人工智能",
            "智能",
            "机器学习",
            "machine learning",
            "深度学习",
            "deep learning",
            "语音",
            "speech",
            "nlp",
            "自然语言",
            "人脸",
            "人体",
            "ocr",
            "视觉",
            "vision",
            "图像",
            "image",
            "机器人",
            "bot",
            "算法",
            "analytics",
            "预测",
            "assistant",
            "临床",
            "就医",
            "精准预约",
            "avatar",
            "content recognition",
            "内容识别",
            "optical character recognition",
            "文字识别",
            "translation",
            "机器翻译",
            "oral evaluation",
            "口语评测",
            "homework correction",
            "作文批改",
            "作业批改",
            "federated learning",
            "联邦学习",
            "hunyuan",
            "混元",
            "ti 平台",
            "ti platform",
            "同传",
            "simultaneous interpretation",
            "小微",
        ],
    ),
    (
        "大数据",
        "big-data",
        [
            "大数据",
            "big data",
            "数据湖",
            "data lake",
            "datalake",
            "data lake compute",
            "data lake accelerator",
            "数据仓库",
            "warehouse",
            "数据开发",
            "data development",
            "数据集成",
            "datainlong",
            "数据治理",
            "governance",
            "商业智能",
            "business intelligence",
            "可视化",
            "visualization",
            "数据分析",
            "data analysis",
            "emr",
            "mapreduce",
            "oceanus",
            "stream computing",
            "流计算",
        ],
    ),
    (
        "音视频",
        "media",
        [
            "音视频",
            "audio",
            "video",
            "直播",
            "live",
            "点播",
            "vod",
            "trtc",
            "webrtc",
            "媒体",
            "media",
            "云导播",
            "导播",
            "streaming",
            "白板",
            "whiteboard",
            "实时音视频",
            "云游戏",
            "vr",
            "渲染",
            "rendering",
            "player sdk",
            "播放器",
            "effect sdk",
            "特效",
        ],
    ),
    (
        "中间件",
        "middleware",
        [
            "消息",
            "message",
            "队列",
            "queue",
            "mq",
            "kafka",
            "rabbitmq",
            "rocketmq",
            "事件总线",
            "eventbridge",
            "api 网关",
            "api gateway",
            "微服务",
            "microservice",
            "mesh",
            "注册中心",
            "配置中心",
            "中间件",
            "middleware",
            "cloud native gateway",
            "云 api",
            "application programming interface",
            "instant messaging",
            "即时通信",
        ],
    ),
    (
        "开发与运维",
        "devops",
        [
            "coding",
            "devops",
            "代码",
            "code",
            "持续集成",
            "continuous integration",
            "持续部署",
            "continuous deployment",
            "测试",
            "test",
            "cloud studio",
            "ide",
            "监控",
            "monitor",
            "prometheus",
            "grafana",
            "日志",
            "log",
            "cloudaudit",
            "cloud audit",
            "云顾问",
            "advisor",
            "terraform",
            "自动化",
            "automation",
            "配置",
            "config",
            "故障",
            "chaos",
            "拨测",
            "tccli",
            "命令行",
            "cloudbase",
            "cloud base",
            "webify",
            "云开发",
            "移动开发平台",
            "mini program platform",
            "迁移服务平台",
            "migration service",
            "remote debugging",
            "远程调试",
            "health dashboard",
            "健康看板",
            "chaotic fault",
            "混沌演练",
            "检测工具",
            "tencent kona",
        ],
    ),
    (
        "企业应用",
        "enterprise-apps",
        [
            "企业",
            "enterprise",
            "办公",
            "协同",
            "collaborative",
            "crm",
            "客户",
            "customer",
            "联络中心",
            "contact center",
            "工单",
            "ticket",
            "支付",
            "payment",
            "营销",
            "marketing",
            "会议",
            "腾讯会议",
            "tapd",
            "项目管理",
            "business connect",
            "bpaas",
            "qq",
            "财务",
            "document service",
            "文档服务",
            "e-sign",
            "电子签",
            "survey",
            "问卷",
            "hr",
            "organization",
            "集团账号",
            "企点",
            "qidian",
            "乐享",
            "lexiang",
            "用户运营",
            "user operation",
            "商标",
            "工商注册",
            "business registration",
            "网站建设",
            "建站",
        ],
    ),
    (
        "行业与物联网",
        "industry-iot",
        [
            "物联网",
            "iot",
            "制造",
            "manufacturing",
            "工业",
            "industry",
            "医疗",
            "medical",
            "clinical",
            "金融",
            "finance",
            "供应链",
            "supply chain",
            "教育",
            "政务",
            "物流",
            "logistics",
            "车",
            "automotive",
            "iot explorer",
            "云端智造",
            "print",
            "印刷",
            "telecom",
            "电信",
            "会展",
            "exhibition",
            "党建",
            "party building",
            "carbon",
            "碳",
            "能源",
            "energy",
            "healthcare",
            "health",
            "omics",
            "组学",
            "materials",
            "材料",
            "andon",
            "安灯",
        ],
    ),
]

FALLBACK_CATEGORY = ("其他", "other")
CATEGORY_PRIORITY = {
    "security": 0,
    "database": 1,
    "storage": 2,
    "compute-container": 3,
    "network-cdn": 4,
    "middleware": 5,
    "devops": 6,
    "ai-intelligence": 7,
    "big-data": 8,
    "media": 9,
    "enterprise-apps": 10,
    "industry-iot": 11,
    "other": 99,
}
ABBREVIATION_ALIASES = [
    ("COS", ["cloud object storage", "对象存储"]),
    ("CVM", ["cloud virtual machine", "云服务器"]),
    ("CBS", ["cloud block storage", "云硬盘"]),
    ("CFS", ["cloud file storage", "文件存储"]),
    ("VPC", ["virtual private cloud", "私有网络"]),
    ("CLB", ["cloud load balancer", "负载均衡"]),
    ("TKE", ["tencent kubernetes engine"]),
    ("TCR", ["tencent container registry", "容器镜像服务"]),
    ("SCF", ["serverless cloud function", "云函数"]),
    ("CLS", ["cloud log service", "日志服务"]),
    ("CAM", ["cloud access management", "访问管理"]),
]


def _strip_namespace(tag: str) -> str:
    return tag.split("}", 1)[-1].lower() if "}" in tag else tag.lower()


def _collapse_space(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _normalize_attr(value: str | None) -> str:
    value = _collapse_space(value)
    return re.sub(r"url\(#[^)]+\)", "url(#id)", value)


def _normalize_svg(svg_bytes: bytes) -> str:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=False))
    root = ET.fromstring(svg_bytes, parser=parser)

    def walk(element: ET.Element):
        tag = _strip_namespace(element.tag)
        if tag in {"title", "desc", "metadata"}:
            return None

        attrs = []
        for raw_key, raw_value in element.attrib.items():
            key = _strip_namespace(raw_key)
            if key == "id" or key.startswith("aria-"):
                continue
            attrs.append((key, _normalize_attr(raw_value)))
        attrs.sort()

        children = []
        for child in list(element):
            normalized = walk(child)
            if normalized is not None:
                children.append(normalized)

        text = "" if tag == "svg" else _collapse_space(element.text)
        return (tag, tuple(attrs), tuple(children), text)

    return repr(walk(root))


def _is_zh_source(path: str) -> bool:
    return "/tencent_cloud_product_icons_zh/" in f"/{path}"


def _is_en_source(path: str) -> bool:
    return "/tencent_cloud_product_icons_en/" in f"/{path}"


def _display_name(path: str) -> str:
    name = os.path.basename(path)
    return os.path.splitext(name)[0].replace("\u00a0", " ").strip()


def _base_alias(name: str) -> str:
    return re.sub(r"-\d+$", "", name).strip()


def _variant_suffix(name: str) -> str:
    match = re.search(r"-(\d+)$", name)
    return match.group(1) if match else ""


def _append_unique(items: list[str], candidate: str, seen: set[str]) -> None:
    if candidate and candidate not in seen:
        items.append(candidate)
        seen.add(candidate)


def _slugify(name: str, key: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    ascii_name = ascii_name.lower().replace("&", " and ")
    ascii_name = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    if not ascii_name:
        ascii_name = "icon"
    suffix = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
    return f"{ascii_name}-{suffix}"


CATEGORY_OVERRIDES = {
    'middleware': ['北极星网格', '移动推送', '邮件推送'],
    'network-cdn': ['智能全局流量管理', '移动解析 HTTPDNS'],
    'security': ['网络入侵防护系统', '渗透测试服务', '应急响应服务', '可信计算服务', '机密计算平台'],
    'compute-container': ['计算加速套件 TACO Kit', '腾讯云遨驰终端'],
    'devops': ['腾讯云可观测平台', '腾讯云助手', '多云管理', '控制中心'],
    'media': ['极速高清'],
}

def _category_for(names: list[str]) -> dict[str, str]:
    base_names={re.sub(r'-[0-9]+$', '', n).strip() for n in names}
    for slug, exact_names in CATEGORY_OVERRIDES.items():
        if base_names.intersection(exact_names):
            title=next(title for title, category_slug, _ in CATEGORY_RULES if category_slug==slug)
            return {"name":title,"slug":slug}
    haystack = " ".join(names).replace("\u00a0", " ").lower()
    matches = []
    for category_name, category_slug, keywords in CATEGORY_RULES:
        if any(_has_keyword(haystack, keyword) for keyword in keywords):
            matches.append((CATEGORY_PRIORITY.get(category_slug, 50), category_name, category_slug))
    if matches:
        _, category_name, category_slug = min(matches)
        return {"name": category_name, "slug": category_slug}
    return {"name": FALLBACK_CATEGORY[0], "slug": FALLBACK_CATEGORY[1]}


def _has_keyword(haystack: str, keyword: str) -> bool:
    keyword = keyword.replace("\u00a0", " ").lower()
    if not keyword:
        return False
    if re.search(r"[^a-z0-9 \-:/&+]", keyword):
        return keyword in haystack
    pattern = r"(?<![a-z0-9])" + re.escape(keyword).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
    return re.search(pattern, haystack) is not None


def _abbr_aliases(names: list[str]) -> list[str]:
    haystack = " ".join(names).replace("\u00a0", " ").lower()
    aliases = []
    seen = set()
    for alias, keywords in ABBREVIATION_ALIASES:
        if any(_has_keyword(haystack, keyword) for keyword in keywords):
            _append_unique(aliases, alias, seen)
    return aliases


def _paths_to_aliases(paths: list[str], name: str) -> list[str]:
    aliases = []
    seen_aliases = {name}
    for path in sorted(paths):
        alias = _display_name(path)
        for candidate in (alias, _base_alias(alias)):
            _append_unique(aliases, candidate, seen_aliases)
    for alias in _abbr_aliases([name] + aliases):
        _append_unique(aliases, alias, seen_aliases)
    return aliases


def _entry_from_paths(svg_hash: str, preferred_path: str, paths: list[str]) -> dict:
    paths = sorted(paths)
    name = _display_name(preferred_path)
    aliases = _paths_to_aliases(paths, name)

    all_names = [_display_name(path) for path in paths] + aliases
    key = "\n".join(paths) + "\n" + svg_hash
    category = _category_for(all_names)
    source_languages = []
    if any(_is_zh_source(path) for path in paths):
        source_languages.append("zh")
    if any(_is_en_source(path) for path in paths):
        source_languages.append("en")

    return {
        "name": name,
        "slug": _slugify(name, key),
        "category": category["name"],
        "category_slug": category["slug"],
        "source_path": preferred_path,
        "source_paths": paths,
        "aliases": aliases,
        "source_languages": source_languages,
        "variant": any(re.search(r"-\d+\.svg$", path) for path in paths),
        "source_hash": svg_hash[:16],
    }


def _score_english_match(en_path: str, zh_path: str, zh_index: int) -> tuple[int, int, str]:
    en_name = _display_name(en_path)
    zh_name = _display_name(zh_path)
    en_suffix = _variant_suffix(en_name)
    zh_suffix = _variant_suffix(zh_name)
    score = 0
    if en_suffix == zh_suffix:
        score -= 20
    elif en_suffix and zh_suffix:
        score += 20
    elif en_suffix or zh_suffix:
        score += 4

    if _base_alias(en_name).lower() == _base_alias(zh_name).lower():
        score -= 5
    if not zh_suffix:
        score -= 1
    return (score, zh_index, zh_path)


def build_catalog(zip_path: str | os.PathLike[str]) -> list[dict]:
    """Return catalog entries for all Chinese icons plus English-only geometries."""
    groups: dict[str, list[str]] = defaultdict(list)
    with zipfile.ZipFile(zip_path) as archive:
        for path in sorted(archive.namelist()):
            if not path.lower().endswith(".svg"):
                continue
            svg_hash = hashlib.sha256(_normalize_svg(archive.read(path)).encode("utf-8")).hexdigest()
            groups[svg_hash].append(path)

    entries = []
    for svg_hash, paths in groups.items():
        zh_paths = sorted(path for path in paths if _is_zh_source(path))
        en_paths = sorted(path for path in paths if _is_en_source(path))

        if zh_paths:
            assigned_en_paths: dict[str, list[str]] = {path: [] for path in zh_paths}
            for en_path in en_paths:
                best_zh_path = min(
                    zh_paths,
                    key=lambda zh_path: _score_english_match(en_path, zh_path, zh_paths.index(zh_path)),
                )
                assigned_en_paths[best_zh_path].append(en_path)

            for zh_path in zh_paths:
                entry_paths = [zh_path] + assigned_en_paths[zh_path]
                entries.append(_entry_from_paths(svg_hash, zh_path, entry_paths))
        else:
            preferred_path = sorted(en_paths or paths, key=lambda path: (_display_name(path), path))[0]
            entries.append(_entry_from_paths(svg_hash, preferred_path, en_paths or paths))

    return sorted(entries, key=lambda item: (item["category_slug"], item["name"], item["slug"]))


def _write_catalog(zip_path: str, output_path: str) -> list[dict]:
    catalog = build_catalog(zip_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", nargs="?", default="/tmp/tencent-cloud-icons.zip")
    parser.add_argument(
        "-o",
        "--output",
        default=str(Path(__file__).resolve().parents[1] / "data" / "source-catalog.json"),
    )
    args = parser.parse_args()
    catalog = _write_catalog(args.zip_path, args.output)
    source_count = sum(len(entry["source_paths"]) for entry in catalog)
    categories = sorted({entry["category_slug"] for entry in catalog})
    print(f"wrote {len(catalog)} entries from {source_count} SVG sources to {args.output}")
    print(f"categories: {', '.join(categories)}")


if __name__ == "__main__":
    main()
