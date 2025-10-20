"""High-level TAU clustering API."""
from __future__ import annotations

from multiprocessing import Pool, set_start_method
from typing import Iterable, Optional, Sequence, Tuple
import time
import weakref

import igraph as ig
import networkx as nx
import numpy as np
from sklearn.metrics.cluster import pair_confusion_matrix

from .config import TauConfig
from .graph import networkx_to_igraph
from .partition import (
    Partition,
    configure_shared_state,
    create_partition,
    get_graph,
    init_worker,
    mutate_partition,
    optimize_partition,
)

try:  # ensure spawn context for cross-platform safety
    set_start_method("spawn")
except RuntimeError:
    pass


class _SequentialPool:
    """Lightweight stand-in when multiprocessing pools cannot be created."""

    def map(self, func, iterable, chunksize: int = 1):  # noqa: D401 - simple sequential map
        return [func(item) for item in iterable]

    def close(self) -> None:
        pass

    def join(self) -> None:
        pass


def _overlap_memberships(memberships: Iterable[np.ndarray]) -> tuple[np.ndarray, int]:
    """Build a consensus labelling for the provided membership arrays."""

    iterator = iter(memberships)
    consensus = np.array(next(iterator), copy=True)
    dtype = consensus.dtype
    for membership in iterator:
        member_arr = np.asarray(membership, dtype=dtype)
        if consensus.size == 0:
            consensus = member_arr.copy()
            continue
        base_codes = np.unique(consensus, return_inverse=True)[1]
        other_codes = np.unique(member_arr, return_inverse=True)[1]
        pair_codes = (base_codes.astype(np.int64) << 32) | other_codes.astype(np.int64)
        consensus = np.unique(pair_codes, return_inverse=True)[1].astype(dtype, copy=False)
    label_count = int(consensus.max()) + 1 if consensus.size else 0
    return consensus, label_count


def _crossover_pair(args: tuple[np.ndarray, np.ndarray, float]) -> Partition:
    membership_a, membership_b, sample_fraction = args
    membership, n_comms = _overlap_memberships((membership_a, membership_b))
    return Partition.from_membership(
        membership,
        sample_fraction=sample_fraction,
        n_comms=n_comms,
        fitness=None,
        copy_membership=False,
    )

class TauClustering:
    """Evolutionary community detection for large graphs."""

    def __init__(self, graph_source: ig.Graph | nx.Graph, population_size, max_generations, config: Optional[TauConfig] = None):
        self._pool: Optional[Pool] = None
        self._pool_processes: Optional[int] = None
        self.config = config or TauConfig()
        self.graph = self._prepare_graph_source(
            graph_source,
            weight_attribute=self.config.weight_attribute,
            default_weight=self.config.default_edge_weight,
        )
        
        self.config.population_size = population_size
        self.config.max_generations = max_generations

        configure_shared_state(
            self.graph,
            self.config.leiden_iterations,
            self.config.leiden_resolution,
            self.config.weight_attribute,
            self.config.default_edge_weight,
            self.config.random_seed,
        )
        self.rng = np.random.default_rng(self.config.random_seed)
        self.sim_indices: Optional[np.ndarray] = self._init_similarity_indices()
        self.selection_probs = self._selection_probabilities(self.config.population_size)

        self._pool_finalizer = weakref.finalize(self, TauClustering._finalize_pool, weakref.proxy(self))
        print(f"Main parameter values: pop_size={self.config.population_size}, workers={self.config.resolve_worker_count(self.config.population_size)}, max_generations={self.config.max_generations}")
    
    def _prepare_graph_source(
        self,
        graph_source: ig.Graph | nx.Graph,
        weight_attribute: Optional[str],
        default_weight: float,
    ) -> ig.Graph:
        if isinstance(graph_source, ig.Graph):
            return graph_source
        if isinstance(graph_source, nx.Graph):
            return networkx_to_igraph(
                graph_source,
                weight_attribute=weight_attribute,
                default_weight=default_weight,
            )
        raise TypeError(
            "TauClustering expects an igraph.Graph or networkx.Graph instance; file paths are not supported."
        )

    def run(self, track_stats: bool = False):
        worker_count = self.config.resolve_worker_count(self.config.population_size)
        chunk_size = self._resolve_chunk_size(worker_count)
        pool = self._ensure_pool(worker_count)
        elite_count = min(self.config.resolve_elite_count(), self.config.population_size)
        immigrant_count = min(
            self.config.resolve_immigrant_count(),
            max(0, self.config.population_size - elite_count - 1),
        )
        offspring_count = max(0, self.config.population_size - elite_count - immigrant_count)

        mod_history: list[float] = []
        generation_stats: list[dict[str, float]] | None = [] if track_stats else None
        last_best_membership: Optional[np.ndarray] = None
        convergence_streak = 0
        best_partition: Optional[Partition] = None

        population = self._create_population(pool, self.config.population_size, chunk_size)
        for generation in range(1, self.config.max_generations + 1):
            start_time = time.perf_counter()
            optimized = pool.map(optimize_partition, population, chunksize=chunk_size)
            population[:] = optimized

            fitnesses = np.array([p.fitness if p.fitness is not None else float("-inf") for p in population])
            avg_fitness = float(np.mean(fitnesses)) if fitnesses.size else float("-inf")
            best_idx = int(np.argmax(fitnesses))
            best_partition = population[best_idx]
            best_modularity = float(best_partition.fitness or -np.inf)
            mod_history.append(best_modularity)

            if last_best_membership is not None:
                jacc = self._similarity_arrays(best_partition.membership, last_best_membership)
                if jacc >= self.config.stopping_jaccard:
                    convergence_streak += 1
                else:
                    convergence_streak = 0
            last_best_membership = best_partition.membership.copy()

            if convergence_streak >= self.config.stopping_generations:
                break
            if generation >= self.config.max_generations:
                break

            population.sort(key=lambda part: part.fitness or float("-inf"), reverse=True)
            elt_st = time.perf_counter()
            elite_indices = self._elitist_selection(population, self.config.elite_similarity_threshold, elite_count)
            elt_rt = time.perf_counter() - elt_st
            elites = [population[i] for i in elite_indices]

            crim_st = time.perf_counter()
            offspring = self._produce_offspring(pool, chunk_size, population, offspring_count)
            immigrants = (
                self._create_population(pool, immigrant_count, chunk_size)
                if immigrant_count
                else []
            )
            crim_rt = time.perf_counter() - crim_st

            if offspring:
                mutated_offspring = pool.map(mutate_partition, offspring, chunksize=chunk_size)
                offspring = mutated_offspring

            population[:] = elites
            population.extend(offspring)
            population.extend(immigrants)

            gen_elapsed = time.perf_counter() - start_time
            print(
                f'Generation {generation} Top fitness: {best_modularity:.5f}; Average fitness: '
                f'{avg_fitness:.5f}; Time per generation: {gen_elapsed:.3f}; '
                f'convergence: {convergence_streak} ; elt-runtime={elt_rt:.3f} ; crim-runtime={crim_rt:.3f}'
            )
            if track_stats and generation_stats is not None:
                generation_stats.append(
                    {
                        "generation": generation,
                        "top_fitness": best_modularity,
                        "average_fitness": avg_fitness,
                        "time_per_generation": gen_elapsed,
                        "convergence": convergence_streak,
                        "elite_runtime": elt_rt,
                        "crossover_runtime": crim_rt,
                    }
                )

        if best_partition is None:
            raise RuntimeError("TAU clustering failed to produce any solution.")

        if not self.config.reuse_worker_pool:
            self._shutdown_pool()

        membership_result = best_partition.membership.astype(np.int64, copy=True)
        if track_stats and generation_stats is not None:
            return membership_result, mod_history, generation_stats
        return membership_result, mod_history



    def _create_population(self, pool: Pool, size: int, chunk_size: int) -> list[Partition]:
        if size <= 0:
            return []
        low, high = self.config.sample_fraction_range
        fractions = self.rng.uniform(low, high, size)
        return pool.map(create_partition, fractions.tolist(), chunksize=chunk_size)

    def _produce_offspring(
        self,
        pool: Pool,
        chunk_size: int,
        population: Sequence[Partition],
        count: int,
    ) -> list[Partition]:
        if count <= 0:
            return []
        offspring: list[Partition] = []
        crossover_jobs: list[tuple[np.ndarray, np.ndarray, float]] = []
        pop_size = len(population)
        for _ in range(count):
            parents = self.rng.choice(pop_size, size=2, replace=False, p=self.selection_probs)
            parent_a, parent_b = population[int(parents[0])], population[int(parents[1])]
            if self.rng.random() > 0.5:
                sample_fraction = (parent_a._sample_fraction + parent_b._sample_fraction) / 2.0
                crossover_jobs.append(
                    (parent_a.membership, parent_b.membership, sample_fraction)
                )
            else:
                offspring.append(parent_a.clone(copy_membership=False, reset_fitness=True))
        if crossover_jobs:
            offspring.extend(pool.map(_crossover_pair, crossover_jobs, chunksize=chunk_size))
        return offspring

    def close(self) -> None:
        self._shutdown_pool()

    def __enter__(self) -> "TauClustering":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _ensure_pool(self, worker_count: int) -> Pool:
        if self._pool is not None and self._pool_processes == worker_count:
            return self._pool
        self._shutdown_pool()
        initargs = (
            self.graph,
            self.config.leiden_iterations,
            self.config.leiden_resolution,
            self.config.weight_attribute,
            self.config.default_edge_weight,
            self.config.random_seed,
        )
        try:
            self._pool = Pool(
                worker_count,
                initializer=init_worker,
                initargs=initargs,
            )
            self._pool_processes = worker_count
        except PermissionError:
            print("PermissionError creating multiprocessing pool; falling back to sequential execution.")
            self._pool = _SequentialPool()
            self._pool_processes = 1
        return self._pool

    def _shutdown_pool(self) -> None:
        if self._pool is None:
            return
        self._pool.close()
        self._pool.join()
        self._pool = None
        self._pool_processes = None

    def _resolve_chunk_size(self, worker_count: int) -> int:
        explicit = self.config.worker_chunk_size
        if explicit is not None and explicit > 0:
            return int(explicit)
        if worker_count <= 0:
            return 1
        approx = max(1, (self.config.population_size + worker_count - 1) // worker_count)
        return approx

    @staticmethod
    def _finalize_pool(instance_proxy: "TauClustering") -> None:
        try:
            instance_proxy._shutdown_pool()
        except ReferenceError:
            pass

    def _elitist_selection(
        self,
        population: Sequence[Partition],
        threshold: float,
        elite_count: int,
    ) -> list[int]:
        if elite_count >= len(population):
            return list(range(len(population)))

        elites: list[int] = []
        for idx, candidate in enumerate(population):
            if len(elites) >= elite_count:
                break
            if all(self._similarity(population[e], candidate) <= threshold for e in elites):
                elites.append(idx)

        if len(elites) < elite_count:
            remaining = [idx for idx in range(len(population)) if idx not in elites]
            if remaining:
                fill = self.rng.choice(
                    remaining,
                    size=min(len(remaining), elite_count - len(elites)),
                    replace=False,
                )
                elites.extend(int(i) for i in np.atleast_1d(fill))
        return elites

    def _similarity(self, a: Partition, b: Partition) -> float:
        return self._similarity_arrays(a.membership, b.membership)

    def _similarity_arrays(self, a: np.ndarray, b: np.ndarray) -> float:
        if self.sim_indices is not None:
            a = a[self.sim_indices]
            b = b[self.sim_indices]
        tn, fn, fp, tp = pair_confusion_matrix(a, b).flatten()
        denominator = tp + fp + fn
        return float(tp / denominator) if denominator else 1.0

    def _selection_probabilities(self, population_size: int) -> np.ndarray:
        if population_size <= 0:
            return np.array([], dtype=float)
        indices = np.arange(population_size)
        max_val = int(indices[-1]) if population_size else 0
        scaled = max_val + 1 - indices
        weights = np.power(scaled.astype(np.int64), self.config.selection_power)
        weights_sum = weights.sum()
        if weights_sum == 0:
            return np.full(population_size, 1.0 / population_size)
        return weights / weights_sum

    def _overlap(self, memberships: Iterable[np.ndarray]) -> Tuple[np.ndarray, int]:
        return _overlap_memberships(memberships)

    def _init_similarity_indices(self) -> Optional[np.ndarray]:
        sample_size = self.config.sim_sample_size
        graph = get_graph()
        if sample_size is None or graph.vcount() <= sample_size:
            return None
        return self.rng.choice(graph.vcount(), size=sample_size, replace=False)
