from abc import ABC, abstractmethod
from typing import Union, Dict, Tuple, Optional

from . import formulas

Number = Union[int, float]

class SkillMixin(ABC):
    _max_energy: int = 0

    def energy(self: "SkillMixin", score_a: Number, score_b: Number) -> int:
        energy_a = self._energy(score_a, self.scenario_a.value.thresholds)
        energy_b = self._energy(score_b, self.scenario_b.value.thresholds)
        return int(min(self._max_energy, max(energy_a, energy_b)))

    @abstractmethod
    def _energy(self: "SkillMixin", score: Number, thresholds: Tuple[int, int, int, int]) -> int:
        pass

    @property
    @abstractmethod
    def _ranks(self: "SkillMixin") -> Dict[str, int]:
        pass

class NoviceMixin(SkillMixin):
    _previous_energy: int = 0
    _max_energy: int = 500

    def _energy(self: "NoviceMixin", score: Number, thresholds: Tuple[int, int, int, int]) -> int:
        """
        = ELEGIR(COINCIDIR(E3, {0, L3:O3}), 0, L$2, M$2, N$2, O$2) # BASE

        + (E3 - ELEGIR(COINCIDIR(E3, {0, L3:O3}), 0, L3, M3, N3, O3)) # ADJUSTMENT

        / ELEGIR(COINCIDIR(E3, {0, L3:O3}), L3, M3-L3, N3-M3, O3-N3, O3-N3) # DENOMINATOR

        * ELEGIR(COINCIDIR(E3, {0, L3:O3}), L$2, M$2-L$2, N$2-M$2, O$2-N$2, O$2-N$2) # FACTOR
        """
        t1, t2, t3, t4 = thresholds # Row 3 on the spreadsheet
        e1, e2, e3, e4 = self._ranks.values() # Row 2 on the spreadsheet

        match_array = [0, t1, t2, t3, t4]
        match_idx = formulas.match(score, match_array)
        if match_idx == 0:
            return 0

        base = formulas.choose(match_idx, self._previous_energy, e1, e2, e3, e4)
        adjustment = score - formulas.choose(match_idx, 0, t1, t2, t3, t4)
        denominator = formulas.choose(match_idx, t1, t2 - t1, t3 - t2, t4 - t3, t4 - t3)
        factor = formulas.choose(match_idx, e1, e2 - e1, e3 - e2, e4 - e3, e4 - e3)

        if denominator == 0:
            return 0
        
        result = base + (adjustment / denominator) * factor
        return result

    @property
    def _ranks(self: "NoviceMixin") -> Dict[str, int]:
        return {"Iron" : 100, "Bronze" : 200, "Silver" : 300, "Gold" : 400}

class IntermediateMixin(SkillMixin):
    _previous_energy: int = 400
    _max_energy: int = 900

    def _energy(self: "IntermediateMixin", score: Number, thresholds: Tuple[int, int, int, int]) -> int:
        """
        = ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), 0, Novice!O$2, L$2, M$2, N$2, O$2)

        + (E3 - ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), 0, L3-(M3-L3), L3, M3, N3, O3))

        / ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), L3-(M3-L3), M3-L3, M3-L3, N3-M3, O3-N3, O3-N3)

        * ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), Novice!O$2, L$2-Novice!O$2, M$2-L$2, N$2-M$2, O$2-N$2, O$2-N$2)
        """
        t1, t2, t3, t4 = thresholds
        e1, e2, e3, e4 = self._ranks.values()

        match_array = [0, t1 - (t2 - t1), t1, t2, t3, t4]
        match_idx = formulas.match(score, match_array)
        if match_idx == 0:
            return 0

        base = formulas.choose(match_idx, 0, self._previous_energy, e1, e2, e3, e4)
        adjustment = score - formulas.choose(match_idx, 0, t1 - (t2 - t1), t1, t2, t3, t4)
        denominator = formulas.choose(match_idx, t1 - (t2 - t1), t2 - t1, t2 - t1, t3 - t2, t4 - t3, t4 - t3)
        factor = formulas.choose(match_idx, self._previous_energy, e1 - self._previous_energy, e2 - e1, e3 - e2, e4 - e3, e4 - e3)

        if denominator == 0:
            return 0
        
        result = base + (adjustment / denominator) * factor
        return result

    @property
    def _ranks(self: "IntermediateMixin") -> Dict[str, int]:
        return {"Platinum" : 500, "Diamond" : 600, "Jade" : 700, "Master" : 800}

class AdvancedMixin(SkillMixin):
    _previous_energy: int = 800
    _max_energy: int = 1200

    def _energy(self: "AdvancedMixin", score: Number, thresholds: Tuple[int, int, int, int]) -> int:
        """
        = ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), 0, Intermediate!O$2, L$2, M$2, N$2, O$2)

        + (E3 - ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), 0, L3-(M3-L3), L3, M3, N3, O3))

        / ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), L3-(M3-L3), M3-L3, M3-L3, N3-M3, O3-N3, O3-N3)

        * ELEGIR(COINCIDIR(E3, {0, L3-(M3-L3), L3:O3}), Intermediate!O$2, L$2-Intermediate!O$2, M$2-L$2, N$2-M$2, O$2-N$2, O$2-N$2)
        """
        t1, t2, t3, t4 = thresholds
        e1, e2, e3, e4 = self._ranks.values()

        match_array = [0, t1 - (t2 - t1), t1, t2, t3, t4]
        match_idx = formulas.match(score, match_array)
        if match_idx == 0:
            return 0

        base = formulas.choose(match_idx, 0, self._previous_energy, e1, e2, e3, e4)
        adjustment = score - formulas.choose(match_idx, 0, t1 - (t2 - t1), t1, t2, t3, t4)
        denominator = formulas.choose(match_idx, t1 - (t2 - t1), t2 - t1, t2 - t1, t3 - t2, t4 - t3, t4 - t3)
        factor = formulas.choose(match_idx, self._previous_energy, e1 - self._previous_energy, e2 - e1, e3 - e2, e4 - e3, e4 - e3)

        if denominator == 0:
            return 0
        
        result = base + (adjustment / denominator) * factor
        return result

    @property
    def _ranks(self: "AdvancedMixin") -> Dict[str, int]:
        return {"Grandmaster" : 900, "Nova" : 1000, "Astra" : 1100, "Celestial" : 1200}


class Scenario:

    def __init__(self, name: str, thresholds: Tuple[int, int, int, int]) -> None:
        self.name = name
        self.thresholds = thresholds


class Benchmark(ABC):
    def __init__(self: "Benchmark", scenario_a: Optional[Scenario] = None, scenario_b: Optional[Scenario] = None, sub_benchmarks: Optional[Tuple["Benchmark", ...]] = None) -> None:

        if sub_benchmarks is None and not any([scenario_a is None, scenario_b is None]):
            self.scenario_a = scenario_a
            self.scenario_b = scenario_b
        elif scenario_a is None and scenario_b is None:
            self.sub_benchmark = sub_benchmarks
        else:
            raise Exception("No data provided in the constructor")

class NoviceBenchmark(Benchmark, NoviceMixin):
    pass

class IntermediateBenchmark(Benchmark, IntermediateMixin):
    pass

class AdvancedBenchmark(Benchmark, AdvancedMixin):
    pass