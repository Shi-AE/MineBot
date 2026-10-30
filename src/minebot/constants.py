"""跨模块共享的语义常量与领域参数。

约定：
- 语义字符串（类别、状态、Provider 名）必须从这里引用，禁止在调用处重写字面量；
- QML 无法导入 Python 常量，UI 内的同类字符串暂以字面量维护，修改时需同步本文件；
- 仅在单一函数内使用的算法调参值不在此集中，保留在各自模块并配合注释。
"""
from enum import IntEnum

# ── 识别类别（与模型 class_names / 资源文件名一致，禁止重命名） ──

UNKNOWN = "UNKNOWN"
COVERED = "COVERED"
REVEALED = "REVEALED"
CORRECT_FLAG = "CORRECT_FLAG"
WRONG_FLAG = "WRONG_FLAG"

FLAG_POSITIVE_REAL = "FLAG_POSITIVE_REAL"
FLAG_NEGATIVE_REAL = "FLAG_NEGATIVE_REAL"
FLAG_POSITIVE_IMAGINARY = "FLAG_POSITIVE_IMAGINARY"
FLAG_NEGATIVE_IMAGINARY = "FLAG_NEGATIVE_IMAGINARY"

FLAG_KINDS = frozenset(
    {
        FLAG_POSITIVE_REAL,
        FLAG_NEGATIVE_REAL,
        FLAG_POSITIVE_IMAGINARY,
        FLAG_NEGATIVE_IMAGINARY,
    }
)
FLAG_PREFIX = "FLAG_"


class NormSquare(IntEnum):
    """数字格类别 → 范数平方 D（与素材表 D= 标注一致）。

    游戏格面显示的是 √D，因此：
    - 整数格 OPEN_INTEGER_n 对应 D = n²；
    - 根号格 OPEN_RADICAL_系数_被开方数 对应 D = 系数² × 被开方数。
    成员名与识别类别字符串完全一致，可用 NormSquare[kind].value 取值。
    """

    OPEN_INTEGER_0 = 0
    OPEN_INTEGER_1 = 1
    OPEN_RADICAL_1_2 = 2
    OPEN_INTEGER_2 = 4
    OPEN_RADICAL_1_5 = 5
    OPEN_RADICAL_2_2 = 8
    OPEN_INTEGER_3 = 9
    OPEN_RADICAL_1_10 = 10
    OPEN_RADICAL_1_13 = 13
    OPEN_INTEGER_4 = 16
    OPEN_RADICAL_1_17 = 17
    OPEN_RADICAL_3_2 = 18
    OPEN_RADICAL_2_5 = 20
    OPEN_INTEGER_5 = 25
    OPEN_RADICAL_1_26 = 26
    OPEN_RADICAL_1_29 = 29
    OPEN_RADICAL_4_2 = 32
    OPEN_RADICAL_1_34 = 34
    OPEN_INTEGER_6 = 36
    OPEN_RADICAL_1_37 = 37
    OPEN_RADICAL_2_10 = 40
    OPEN_INTEGER_7 = 49
    OPEN_RADICAL_5_2 = 50
    OPEN_INTEGER_8 = 64


# 求解提示可用的操作类型（OPEN 表示建议翻开）。
OPEN = "OPEN"
HINT_KINDS = FLAG_KINDS | {OPEN}

# 余雷区 LED 槽位类别；数字槽位为 "0"–"9"。
SLOT_MINUS = "MINUS"
SLOT_IMAGINARY = "IMAGINARY"
SLOT_BLANK = "BLANK"
SLOT_DIGITS = tuple(str(digit) for digit in range(10))
SLOT_COUNT = 4

# YOLO 检测类别名（与 minebot-yolo26n-detector 元数据一致）。
DETECTOR_MINEFIELD = "minefield"
DETECTOR_REMAINING_COUNTER = "remaining_counter"

# 每帧必须检出的区域数量。
REQUIRED_MINEFIELD_COUNT = 1
REQUIRED_COUNTER_COUNT = 4

# 雷区裁图向外扩张比例，保证边缘格子完整。
MINEFIELD_EXPAND_FRACTION = 0.01

# ── 分类决策阈值（仅在识别模块内部使用，不下发 QML/求解器） ──
# 阈值 0 表示始终接受 top-1；UNKNOWN 仅由切分失败等异常路径产生。

CELL_CONFIDENCE_THRESHOLD = 0.0
CELL_MARGIN_THRESHOLD = 0.0
FLAG_CONFIDENCE_THRESHOLD = 0.0
FLAG_MARGIN_THRESHOLD = 0.0
SLOT_CONFIDENCE_THRESHOLD = 0.0
SLOT_MARGIN_THRESHOLD = 0.0

# ── 求解结果状态 ──

STATUS_SOLVED = "solved"
STATUS_PARTIAL = "partial"
STATUS_CONFLICT = "conflict"
STATUS_UNKNOWN = "unknown"
RESULT_STATUSES = frozenset(
    {STATUS_SOLVED, STATUS_PARTIAL, STATUS_CONFLICT, STATUS_UNKNOWN}
)

# ── 处理器选项（设置页、Session 创建共用） ──

PROCESSOR_AUTO = "auto"
PROCESSOR_CPU = "cpu"
PROCESSOR_CUDA_PREFIX = "cuda:"

# ── 开发者模式截图命名（外部脚本按此约定读取） ──

DEBUG_MINEFIELD_FILENAME = "minefield.png"
DEBUG_COUNTER_PREFIX = "counter_"
DEBUG_CELL_DIRNAME = "cells"
DEBUG_CELL_NAME_TEMPLATE = "row_{row:03d}_col_{column:03d}.png"
DEBUG_CELL_GLOB = "row_*_col_*.png"
