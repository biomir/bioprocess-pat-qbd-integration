from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class CPP:
    name: str
    unit: str
    lower: float
    upper: float
    linked_cqas: tuple[str, ...]

@dataclass(frozen=True)
class CQA:
    name: str
    rationale: str
    severity: int

@dataclass(frozen=True)
class QbDModel:
    cpps: Mapping[str, CPP]
    cqas: Mapping[str, CQA]

    def cpp_out_of_range(self, name: str, value: float) -> bool:
        cpp = self.cpps[name]
        return not (cpp.lower <= float(value) <= cpp.upper)

def default_qbd_model() -> QbDModel:
    cqas = {
        'productivity_proxy': CQA('productivity_proxy', 'Synthetic endpoint used for soft-sensor demonstration.', 3),
        'quality_proxy': CQA('quality_proxy', 'Synthetic quality endpoint influenced by process environment.', 4),
    }
    cpps = {
        'temperature_c': CPP('temperature_c', 'degC', 36.5, 37.5, ('quality_proxy',)),
        'ph': CPP('ph', 'pH', 6.85, 7.20, ('quality_proxy','productivity_proxy')),
        'do_percent': CPP('do_percent', '%', 25.0, 70.0, ('productivity_proxy',)),
        'feed_rate': CPP('feed_rate', 'relative', 0.0, 1.6, ('productivity_proxy','quality_proxy')),
    }
    return QbDModel(cpps=cpps, cqas=cqas)
