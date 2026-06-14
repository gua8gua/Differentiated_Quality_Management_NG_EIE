from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EntityType:
    name: str
    description: str
    examples: tuple[str, ...]


@dataclass(frozen=True)
class RelationType:
    name: str
    description: str
    direction: str


ENTITY_TYPES = (
    EntityType("装备对象", "整机、分系统、模块等被管控对象", ("雷达整机", "接收通道")),
    EntityType("软件对象", "软件版本、模块、接口和缺陷对象", ("软件版本变更", "接口异常")),
    EntityType("元器件状态", "元器件质量状态与退化表现", ("器件老化", "容量衰减")),
    EntityType("质量现象", "可观测质量问题或异常现象", ("接收通道噪声升高", "ESR升高")),
    EntityType("质量指标", "可量化质量指标", ("SNR下降", "跟踪稳定性下降")),
    EntityType("环境工况", "温度、振动、电磁等工况因素", ("温度漂移",)),
    EntityType("过程状态", "制造、试验或采集过程中的质量状态", ("制造过程波动", "设备状态漂移")),
    EntityType("失效机理", "解释元器件或系统退化的机理性原因", ("电应力老化",)),
    EntityType("处置措施", "问题处置、复核、替换和试验措施", ("校准或更换", "回归测试或版本回退")),
)

RELATION_TYPES = (
    RelationType("影响", "上游状态影响下游指标或对象", "head_to_tail"),
    RelationType("导致", "因果关系", "head_to_tail"),
    RelationType("可能原因", "候选根因关系", "phenomenon_to_cause"),
    RelationType("关联", "弱相关或经验相关", "bidirectional"),
    RelationType("处置措施", "根因或现象对应的处置建议", "cause_to_action"),
)


def ontology_summary() -> dict[str, list[dict[str, object]]]:
    return {
        "entities": [entity.__dict__ for entity in ENTITY_TYPES],
        "relations": [relation.__dict__ for relation in RELATION_TYPES],
    }

