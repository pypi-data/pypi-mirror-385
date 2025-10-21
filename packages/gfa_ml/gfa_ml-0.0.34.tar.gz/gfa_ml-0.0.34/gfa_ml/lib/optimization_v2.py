import optuna

from gfa_ml.data_model.data_type import OptimizationObjective, OptunaSampler

from gfa_ml.data_model.common import ControlParameter
import pandas as pd
from gfa_ml.lib.data_processing import create_inference_input_v2
from gfa_ml.lib.serving import ModelServing
import logging
import traceback
import importlib
from gfa_ml.data_model.common import ProcessesOptimizationSpecification

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ControlParameterOptimizerV2:
    def __init__(
        self,
        specification: ProcessesOptimizationSpecification,
    ):
        process_dict = {}
        self.control_parameters_spec = {}
        self.output_constraints = {}

        for (
            process_name,
            process_info,
        ) in specification.data_specifications.items():
            process_dict[process_name] = {}
            model_path = process_info.model_path
            data_config = process_info.data_config
            num_rows = data_config.num_rows
            ml_model = ModelServing(model_path=model_path, data_config=data_config)
            input_spec = process_info.input_specification
            output_constraint = process_info.output_constraint
            if output_constraint != None:
                self.output_constraints[process_name] = output_constraint
            for parameter in input_spec.specification.values():
                if (
                    isinstance(parameter, ControlParameter)
                    and parameter.parameter_name not in self.control_parameters_spec
                ):
                    self.control_parameters_spec[parameter.parameter_name] = parameter
            process_dict[process_name]["model"] = ml_model
            process_dict[process_name]["num_rows"] = num_rows
            process_dict[process_name]["input_spec"] = input_spec

        self.process_dict = process_dict
        self.optimization_objective = specification.optimization_objectives

        if self.optimization_objective != None:
            self.output_constraints[self.optimization_objective.parameter_name] = (
                self.optimization_objective
            )

    def get_directions(self) -> list[str]:
        try:
            """Return a list of 'maximize'/'minimize' for objectives."""
            directions = []
            if self.output_constraints == {}:
                logging.warning("No output constraints defined.")
                return directions
            for quality in self.output_constraints.values():
                if quality.objective != OptimizationObjective.NONE:
                    directions.append(quality.objective.value)
            return directions
        except Exception as e:
            logging.error(f"Error getting directions: {e}")
            logging.info(traceback.format_exc())
            return []

    def pick_objectives(self, result: dict):
        try:
            """Return actual objective values for a trial."""
            objectives = []
            if self.output_constraints == {}:
                logging.warning("No output constraints defined.")
                return objectives
            for name, quality in self.output_constraints.items():
                if quality.objective != OptimizationObjective.NONE:
                    objectives.append(result[name])
            return objectives
        except Exception as e:
            logging.error(f"Error picking objectives: {e}")
            logging.info(traceback.format_exc())
            return []

    def compute_constraints(self, result: dict) -> list[float]:
        try:
            """Convert black-box outputs into Optuna constraint values."""
            values = []
            if self.output_constraints == {}:
                logging.warning("No output constraints defined.")
                return values
            for name, quality in self.output_constraints.items():
                val = result[name]

                # check upper bound
                if quality.upper_limit is not None:
                    values.append(val - quality.upper_limit)

                # check lower bound
                if quality.lower_limit is not None:
                    values.append(quality.lower_limit - val)
            return values
        except Exception as e:
            logging.error(f"Error computing constraints: {e}")
            logging.info(traceback.format_exc())
            return []

    def __call__(self, trial: optuna.Trial) -> float:
        try:
            # Define the search space
            for parameter in self.control_parameters_spec.values():
                parameter.set_current_value(self.input_df)
                low, high = parameter.get_suggestion_range()
                parameter.trial_value = trial.suggest_float(
                    parameter.parameter_name, low, high, step=parameter.step_size
                )
            result = {}
            for process_name, process_info in self.process_dict.items():
                try:
                    input_data = create_inference_input_v2(
                        df=self.input_df,
                        num_rows=process_info["num_rows"],
                        input_spec=process_info["input_spec"],
                        trial_run=True,
                    )
                    ml_model = process_info["model"]
                    input_data = input_data.astype("float32")
                    result[process_name] = ml_model.single_inference_np(input_data)

                except Exception as e:
                    logging.error(f"Error creating inference input: {e}")
                    logging.info(traceback.format_exc())

            if self.optimization_objective != None:
                cost_saving = 0
                for parameter in self.control_parameters_spec.values():
                    if parameter.cost_function != None:
                        cost_function_module = importlib.import_module(
                            "gfa_ml.custom.cost_function"
                        )
                        cost_function = getattr(
                            cost_function_module, parameter.cost_function
                        )
                        cost_saving += cost_function(
                            parameter.current_value, parameter.trial_value
                        )
                result[self.optimization_objective.parameter_name] = cost_saving

            # define objective
            constraints = self.compute_constraints(result)
            trial.set_user_attr("constraints", constraints)
            logging.debug(f"Result: {result}, Constraints: {constraints}")
            objectives = self.pick_objectives(result)
            return tuple(objectives)
        except Exception as e:
            logging.error(f"Error during trial evaluation: {e}")
            logging.info(traceback.format_exc())
            return ()

    def optimize(
        self,
        input_df: pd.DataFrame,
        n_trials: int = 50,
        sampler_type: OptunaSampler = OptunaSampler.QMCSampler,
        log_info: bool = False,
    ) -> optuna.Study:
        try:
            self.input_df = input_df

            if log_info:
                optuna.logging.set_verbosity(optuna.logging.INFO)
            else:
                optuna.logging.set_verbosity(optuna.logging.ERROR)
            directions = self.get_directions()
            if sampler_type == OptunaSampler.TPE:
                sampler = optuna.samplers.TPESampler()
            elif sampler_type == OptunaSampler.CMAES:
                sampler = optuna.samplers.CmaEsSampler()
            elif sampler_type == OptunaSampler.QMCSampler:
                sampler = optuna.samplers.QMCSampler()
            elif sampler_type == OptunaSampler.GRID:
                sampler = optuna.samplers.GridSampler()
            elif sampler_type == OptunaSampler.RANDOM:
                sampler = optuna.samplers.RandomSampler()
            elif sampler_type == OptunaSampler.NSGAII:
                sampler = optuna.samplers.NSGAIISampler()
            elif sampler_type == OptunaSampler.BRUTE_FORCE:
                sampler = optuna.samplers.BruteForceSampler()
            elif sampler_type == OptunaSampler.BOTORCH:
                sampler = optuna.samplers.BoTorchSampler()
            elif sampler_type == OptunaSampler.GP:
                sampler = optuna.samplers.GPSampler()
            else:
                sampler = optuna.samplers.TPESampler()

            study = optuna.create_study(directions=directions, sampler=sampler)
            # --- Run optimization ---
            study.optimize(self, n_trials=n_trials)

            feasible_trials = []
            for t in study.trials:
                cons = t.user_attrs["constraints"]
                if all(c <= 0 for c in cons):
                    feasible_trials.append(t)
            logging.info(f"Number of feasible trials: {len(feasible_trials)}")
            # Get the best trial
            if feasible_trials:
                if self.optimization_objective is not None:
                    if (
                        self.optimization_objective.objective
                        == OptimizationObjective.MAXIMIZE
                    ):
                        best_trial = max(
                            feasible_trials, key=lambda t: t.values[0]
                        )  # maximize first objective
                    elif (
                        self.optimization_objective.objective
                        == OptimizationObjective.MINIMIZE
                    ):
                        best_trial = min(feasible_trials, key=lambda t: t.values[0])
                    else:
                        logging.error("Invalid optimization objective.")
                        return None
                else:
                    logging.error("No optimization objective defined.")
                    return None

                logging.info(
                    f"Best trial: {best_trial.number}, Objectives: {best_trial.values}, Parameters: {best_trial.params}"
                )
                return best_trial
            else:
                logging.info("No feasible trial found, selecting best overall trial.")
                return None

        except Exception as e:
            logging.error(f"Error during optimization: {e}")
            logging.info(traceback.format_exc())
            return None
