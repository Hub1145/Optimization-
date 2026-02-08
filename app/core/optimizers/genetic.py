import random
import numpy as np
from deap import base, creator, tools, algorithms
from typing import Dict, List, Any, Tuple
import pandas as pd
from app.core.backtesting.engine import BacktestingEngine

class GeneticOptimizer:
    """Genetic algorithm for strategy optimization"""

    def __init__(self, data: pd.DataFrame, strategy_definition: Dict[str, str],
                 capital: float = 10000, commission: float = 0.001, slippage: float = 0.0005):
        self.data = data
        self.strategy_definition = strategy_definition
        self.capital = capital
        self.commission = commission
        self.slippage = slippage

        # DEAP setup
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

    def optimize(self, parameter_bounds: Dict[str, Dict[str, float]],
                 population_size: int = 50,
                 generations: int = 20,
                 mutation_rate: float = 0.15,
                 crossover_rate: float = 0.7,
                 objective: str = 'sharpe_ratio') -> Dict[str, Any]:
        """
        Run genetic algorithm optimization

        Args:
            parameter_bounds: Dict of {param_name: {'min': x, 'max': y}}
            population_size: Number of individuals
            generations: Number of generations
            mutation_rate: Mutation probability
            crossover_rate: Crossover probability
            objective: Metric to maximize

        Returns:
            Best parameters and performance
        """
        param_names = list(parameter_bounds.keys())
        bounds = [(parameter_bounds[p]['min'], parameter_bounds[p]['max']) for p in param_names]

        # Register genetic operators
        self.toolbox.register("individual", self._create_individual, bounds)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate, param_names=param_names, objective=objective)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # Create initial population
        population = self.toolbox.population(n=population_size)

        # Evaluate initial population
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Evolution
        for gen in range(generations):
            # Select next generation
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < crossover_rate:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in offspring:
                if random.random() < mutation_rate:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate offspring
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Replace population
            population[:] = offspring

        # Best individual
        best_ind = tools.selBest(population, 1)[0]
        best_params = dict(zip(param_names, best_ind))

        # Re-evaluate best to get full stats
        engine = BacktestingEngine(self.data, self.capital, self.commission, self.slippage)
        strategy_class = engine.create_strategy_class(
            self.strategy_definition.get('type', 'custom'),
            self.strategy_definition.get('entry_rule'),
            self.strategy_definition.get('exit_rule'),
            best_params
        )
        result = engine.run_backtest(strategy_class)

        return {
            'best_parameters': best_params,
            'best_performance': {
                'total_return': result['total_return'],
                'sharpe_ratio': result['sharpe_ratio'],
                'max_drawdown': result['max_drawdown'],
                'win_rate': result['win_rate'],
                'profit_factor': result['profit_factor'],
                'total_trades': result['total_trades'],
                'avg_trade_duration_days': result['avg_trade_duration']
            }
        }

    def _create_individual(self, bounds: List[Tuple[float, float]]):
        """Create random individual within bounds"""
        return creator.Individual([random.uniform(low, high) for low, high in bounds])

    def _evaluate(self, individual: List[float], param_names: List[str], objective: str) -> Tuple[float,]:
        """Evaluate fitness of an individual"""
        try:
            params = dict(zip(param_names, individual))

            engine = BacktestingEngine(self.data, self.capital, self.commission, self.slippage)
            strategy_class = engine.create_strategy_class(
                self.strategy_definition.get('type', 'custom'),
                self.strategy_definition.get('entry_rule'),
                self.strategy_definition.get('exit_rule'),
                params
            )
            result = engine.run_backtest(strategy_class)

            val = result.get(objective, 0.0)
            if objective in ['max_drawdown']:
                val = -val # Minimize drawdown

            return (val,)
        except:
            return (0.0,)  # Return 0 fitness on error
