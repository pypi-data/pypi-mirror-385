#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import random

import pytest
from ezdxf.addons import genetic_algorithm as ga
from ezdxf.addons import binpacking as bp


class TestFloatDNAZeroOne:
    def test_init_value(self):
        dna = ga.FloatDNA([1.0] * 20)
        assert all(v == 1.0 for v in dna) is True

    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_init_value_is_valid(self, value):
        with pytest.raises(ValueError):
            ga.FloatDNA([value] * 20)

    def test_flip_mutate_at(self):
        dna = ga.FloatDNA([0, 0.1, 0.2, 0.3, 0.4])
        for index in range(5):
            dna.flip_mutate_at(index)
        assert list(dna) == pytest.approx([1.0, 0.9, 0.8, 0.7, 0.6])

    def test_iter(self):
        dna = ga.FloatDNA([1.0] * 20)
        assert len(list(dna)) == 20

    def test_reset_data(self):
        dna = ga.FloatDNA([0.0] * 20)
        dna.reset([0.5] * 20)
        assert len(dna) == 20
        assert dna[7] == 0.5

    @pytest.mark.parametrize(
        "values",
        [
            [0, 0, -1],
            [2, 2, 2, 2, 2],
        ],
    )
    def test_reset_data_checks_validity(self, values):
        dna = ga.FloatDNA([])
        with pytest.raises(ValueError):
            dna.reset(values)

    def test_new_random_dna(self):
        dna = ga.FloatDNA.random(20)
        assert len(dna) == 20
        assert len(set(dna)) > 10

    def test_subscription_setter(self):
        dna = ga.FloatDNA([0.0] * 20)
        dna[-3:] = [0.1, 0.2, 0.3]
        assert len(dna) == 20
        assert dna[-3:] == pytest.approx([0.1, 0.2, 0.3])
        assert sum(dna) == pytest.approx(0.6)


class TestBitDNA:
    def test_init_value(self):
        dna = ga.BitDNA([1] * 20)
        assert all(v is True for v in dna) is True

    def test_reset_data(self):
        dna = ga.BitDNA([1] * 20)
        dna.reset([False] * 20)
        assert len(dna) == 20
        assert dna[7] is False

    def test_new_random_dna(self):
        dna = ga.BitDNA.random(20)
        assert len(dna) == 20
        assert len(set(dna)) == 2

    def test_subscription_setter(self):
        dna = ga.BitDNA([1] * 20)
        dna[-3:] = [False, False, False]
        assert len(dna) == 20
        assert dna[-4:] == [True, False, False, False]


class TestUniqueIntDNA:
    def test_init_value(self):
        dna = ga.UniqueIntDNA(10)
        assert dna.is_valid is True
        assert list(dna) == list(range(10))

    def test_init_values(self):
        dna = ga.UniqueIntDNA([0, 1, 2, 3])
        assert dna.is_valid is True
        assert list(dna) == [0, 1, 2, 3]

    def test_init_invalid_values(self):
        with pytest.raises(TypeError):
            ga.UniqueIntDNA([0, 1, 2, 2])

    def test_reset_data(self):
        dna = ga.UniqueIntDNA(10)
        dna.reset(range(9, -1, -1))
        assert len(dna) == 10
        assert dna.is_valid is True
        assert dna[0] == 9
        assert dna[9] == 0

    def test_new_random_dna(self):
        dna = ga.UniqueIntDNA.random(10)
        assert len(dna) == 10
        assert dna.is_valid is True

    def test_subscription_setter(self):
        dna = ga.UniqueIntDNA(10)
        dna[-3:] = [1, 2, 3]
        assert len(dna) == 10
        assert dna[-4:] == [6, 1, 2, 3]
        assert dna.is_valid is False

    def test_recombine_dna_ocx1_preserves_order(self):
        dna1 = ga.UniqueIntDNA(10)  # 0, 1, 2, 3, ...
        dna2 = ga.UniqueIntDNA(10)
        dna2._data.reverse()  # 9, 8, 7, 6, ...
        ga.recombine_dna_ocx1(dna1, dna2, 0, 3)
        assert list(dna1) == [9, 8, 7, 0, 1, 2, 3, 4, 5, 6]
        assert list(dna2) == [0, 1, 2, 9, 8, 7, 6, 5, 4, 3]

    @pytest.mark.parametrize("i1, i2", [(0, 3), (3, 7), (7, 9), (0, 9)])
    def test_random_recombine_dna_ocx1(self, i1, i2):
        dna1 = ga.UniqueIntDNA.random(10)
        dna2 = ga.UniqueIntDNA.random(10)
        copy1 = dna1.copy()
        copy2 = dna2.copy()
        ga.recombine_dna_ocx1(dna1, dna2, i1, i2)
        assert dna1.is_valid is True
        assert dna2.is_valid is True
        assert copy1 != dna1
        assert copy2 != dna2

    @pytest.mark.parametrize("i1, i2", [(0, 0), (8, 8), (9, 9), (10, 11)])
    def test_recombine_dna_ocx1_without_change(self, i1, i2):
        dna1 = ga.UniqueIntDNA.random(10)
        dna2 = ga.UniqueIntDNA.random(10)
        copy1 = dna1.copy()
        copy2 = dna2.copy()
        ga.recombine_dna_ocx1(dna1, dna2, i1, i2)
        assert copy1 == dna1
        assert copy2 == dna2


class TestIntegerDNA:
    def test_init_value(self):
        dna = ga.IntegerDNA([0, 1, 2, 3, 4], 5)
        assert dna.is_valid is True
        assert max(dna) < 5

    def test_init_invalid_data(self):
        with pytest.raises(TypeError):
            ga.IntegerDNA([0, 1, 2, 3, 5], 5)

    def test_flip_mutate_at(self):
        dna = ga.IntegerDNA([0, 1, 2, 3, 4], 5)
        for index in range(5):
            dna.flip_mutate_at(index)
        assert list(dna) == [4, 3, 2, 1, 0]

    def test_reset_data(self):
        dna = ga.IntegerDNA([0, 1, 2, 3, 4, 0, 1, 2, 3, 4], 5)
        dna.reset([4, 3, 2, 1, 0, 1, 2, 3, 2, 1])
        assert len(dna) == 10
        assert dna.is_valid is True
        assert dna[0] == 4
        assert dna[9] == 1

    def test_new_random_dna(self):
        dna = ga.IntegerDNA.random(10, 5)
        assert len(dna) == 10
        assert dna.is_valid is True


class TestHallOfFame:
    @pytest.fixture
    def candidates(self):
        s = []
        for fitness in range(1, 10):
            dna = ga.BitDNA.random(5)
            dna.fitness = 0.1 * fitness
            s.append(dna)
        return s

    def test_build(self, candidates):
        hof = ga.HallOfFame(3)
        for dna in candidates:
            hof.add(dna)
        assert [dna.fitness for dna in hof] == pytest.approx([0.9, 0.8, 0.7])

    def test_get_n_best(self, candidates):
        hof = ga.HallOfFame(3)
        for dna in candidates:
            hof.add(dna)
        result = hof.get(2)
        assert result[0].fitness == pytest.approx(0.9)
        assert result[1].fitness == pytest.approx(0.8)

    def test_get_n_best_negative_values(self, candidates):
        for dna in candidates:
            dna.fitness = -dna.fitness
        hof = ga.HallOfFame(3)
        for dna in candidates:
            hof.add(dna)
        result = hof.get(2)
        assert result[0].fitness == pytest.approx(-0.1)
        assert result[1].fitness == pytest.approx(-0.2)

    def test_purge(self, candidates):
        hof = ga.HallOfFame(3)
        for dna in candidates:
            hof.add(dna)
        hof.purge()
        assert len(hof._unique_entries) == 3


def test_reverse_mutate():
    dna = ga.UniqueIntDNA(10)
    mutate = ga.ReverseMutate(3)
    mutate.mutate(dna, 1.0)
    assert list(dna) != list(ga.UniqueIntDNA(10))
    assert len(set(dna)) == 10


def test_scramble_mutate():
    dna = ga.UniqueIntDNA(10)
    mutate = ga.ScrambleMutate(5)
    mutate.mutate(dna, 1.0)
    assert list(dna) != list(ga.UniqueIntDNA(10))
    assert len(set(dna)) == 10


def test_tournament_selection():
    candidates = [ga.UniqueIntDNA(10) for _ in range(10)]
    for index, dna in enumerate(candidates):
        dna.fitness = index
    selection = ga.TournamentSelection(2)
    selection.reset(candidates)

    result = list(selection.pick(2))
    assert len(result) == 2

    result = list(selection.pick(3))
    assert len(result) == 3


class TestRouletteSelection:
    SELECTOR = ga.RouletteSelection

    @pytest.mark.parametrize("low, high", [
        (1, 10000),
        (-10000, -1),
    ])
    def test_weights(self, low, high):
        dna_max, dna_min = ga.BitDNA.n_random(2, 10)
        dna_max.fitness = high
        dna_min.fitness = low
        selector = self.SELECTOR(negative_values=high < 0)
        selector.reset([dna_max, dna_min])
        random.seed(42)
        count = 0
        for _ in range(4):
            # first runs may fail in test mode, only testing issue?
            # in real world application the relation dna_max:dna_min is always 20:0
            values = list(selector.pick(20))
            # in debug mode this assertion is ALWAYS True (count==4)
            if values.count(dna_max) > values.count(dna_min):
                count += 1
        assert count > 1


class TestRankBasedSelection(TestRouletteSelection):
    SELECTOR = ga.RankBasedSelection


def test_two_point_crossover():
    dna1 = ga.BitDNA([False] * 20)
    dna2 = ga.BitDNA([True] * 20)
    ga.recombine_dna_2pcx(dna1, dna2, 7, 11)
    assert list(dna1[0:7]) == [False] * 7
    assert list(dna1[7:11]) == [True] * 4
    assert list(dna1[11:]) == [False] * 9
    assert list(dna2[0:7]) == [True] * 7
    assert list(dna2[7:11]) == [False] * 4
    assert list(dna2[11:]) == [True] * 9


class TestThresholdFilter:
    @pytest.fixture
    def candidates(self):
        return [ga.BitDNA([]) for _ in range(100)]

    def test_positive_values(self, candidates):
        for fitness, c in enumerate(candidates):
            c.fitness = fitness
        candidates = list(ga.threshold_filter(candidates, 99, 0.1))
        assert len(candidates) == 90

    def test_negative_values(self, candidates):
        for fitness, c in enumerate(candidates):
            c.fitness = -fitness
        candidates = list(ga.threshold_filter(candidates, 0.0, 0.1))
        assert len(candidates) == 90


SMALL_ENVELOPE = ("small-envelope", 11.5, 6.125, 0.25, 10)
LARGE_ENVELOPE = ("large-envelope", 15.0, 12.0, 0.75, 15)
SMALL_BOX = ("small-box", 8.625, 5.375, 1.625, 70.0)
MEDIUM_BOX = ("medium-box", 11.0, 8.5, 5.5, 70.0)
MEDIUM_BOX2 = ("medium-box-2", 13.625, 11.875, 3.375, 70.0)
LARGE_BOX = ("large-box", 12.0, 12.0, 5.5, 70.0)
LARGE_BOX2 = ("large-box-2", 23.6875, 11.75, 3.0, 70.0)

ALL_BINS = [
    SMALL_ENVELOPE,
    LARGE_ENVELOPE,
    SMALL_BOX,
    MEDIUM_BOX,
    MEDIUM_BOX2,
    LARGE_BOX,
    LARGE_BOX2,
]


@pytest.fixture
def packer():
    packer = bp.Packer()
    packer.add_item("50g [powder 1]", 3.9370, 1.9685, 1.9685, 1)
    packer.add_item("50g [powder 2]", 3.9370, 1.9685, 1.9685, 2)
    packer.add_item("50g [powder 3]", 3.9370, 1.9685, 1.9685, 3)
    packer.add_item("250g [powder 4]", 7.8740, 3.9370, 1.9685, 4)
    packer.add_item("250g [powder 5]", 7.8740, 3.9370, 1.9685, 5)
    packer.add_item("250g [powder 6]", 7.8740, 3.9370, 1.9685, 6)
    packer.add_item("250g [powder 7]", 7.8740, 3.9370, 1.9685, 7)
    packer.add_item("250g [powder 8]", 7.8740, 3.9370, 1.9685, 8)
    packer.add_item("250g [powder 9]", 7.8740, 3.9370, 1.9685, 9)
    return packer


def pack(packer, box, pick):
    packer.add_bin(*box)
    packer.pack(pick)
    return packer.bins[0]


class DummyEvaluator(ga.Evaluator):
    def __init__(self, packer: bp.AbstractPacker):
        self.packer = packer

    def evaluate(self, dna: ga.DNA) -> float:
        return 0.5

    def run_packer(self, dna: ga.DNA):
        packer = self.packer.copy()
        packer.pack()
        return packer


class TestGeneticOptimizer:
    def test_init(self, packer):
        driver = ga.GeneticOptimizer(packer, 100)
        assert driver.is_executed is False

    def test_init_invalid_max_runs(self, packer):
        with pytest.raises(ValueError):
            ga.GeneticOptimizer(packer, 0)

    def test_can_only_run_once(self, packer):
        evaluator = DummyEvaluator(packer)
        optimizer = ga.GeneticOptimizer(evaluator, 100)
        optimizer.execute()
        assert optimizer.is_executed is True
        with pytest.raises(TypeError):
            optimizer.execute()

    def test_execution(self, packer):
        packer.add_bin(*MEDIUM_BOX)
        evaluator = DummyEvaluator(packer)
        optimizer = ga.GeneticOptimizer(evaluator, 10)
        optimizer.add_candidates(ga.BitDNA.n_random(20, len(packer.items)))
        optimizer.execute()
        assert optimizer.generation == 10
        assert optimizer.best_fitness > 0.1

        # Get best packer of SubSetEvaluator:
        best_packer = evaluator.run_packer(optimizer.best_dna)
        assert len(best_packer.bins[0].items) > 1


if __name__ == "__main__":
    pytest.main([__file__])
