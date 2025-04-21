from json import loads as json_loads
from yaml import safe_load
from pickle import load as pickle_load
import importlib.util
import inspect
import os
import sys

# Introduce path to realsim
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../")
))

# Introduce path to api.loader
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
))

# Get logger
from common.utils import define_logger
logger = define_logger()

# Get scheduler hierarchy
from common.hierarchy import import_schedulers_hierarchy
scheduler_hierarchy = import_schedulers_hierarchy(os.path.abspath(os.path.join(os.path.dirname(__file__), "../realsim/scheduler")))

# LoadManager
from api.loader import LoadManager

# Database
from realsim.database import Database

# Generators
from realsim.generators.AGenerator import AbstractGenerator
from realsim.generators.random import RandomGenerator
from realsim.generators.randomfromlist import RandomFromListGenerator
from realsim.generators.keysdict import KeysDictGenerator
from realsim.generators.keyslist import KeysListGenerator
from realsim.generators.shufflekeyslist import ShuffleKeysListGenerator
from realsim.generators.swf import SWFGenerator

# Distributions
from realsim.generators.distribution.idistribution import IDistribution
from realsim.generators.distribution.constantdistr import ConstantDistribution
from realsim.generators.distribution.randomdistr import RandomDistribution
from realsim.generators.distribution.poissondistr import PoissonDistribution

# Cluster
from realsim.cluster.cluster import Cluster

# Schedulers
# from realsim.scheduler.scheduler import Scheduler
# from realsim.scheduler.schedulers.fifo import FIFOScheduler
# from realsim.scheduler.schedulers.easy import EASYScheduler
# from realsim.scheduler.schedulers.conservative import ConservativeScheduler
# from realsim.scheduler.coschedulers.ranks.random import RandomRanksCoscheduler

# Logger
from realsim.logger.logger import Logger

# ComputeEngine
from realsim.compengine import ComputeEngine

def import_module(path):
    mod_name = os.path.basename(path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    gen_mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = gen_mod
    spec.loader.exec_module(gen_mod)
    return spec.name

def translate_action(action: str, translate: bool = False):
    translated_actions = {
        "get-workloads": "get_workload",
        "get-gantt-diagrams": "get_gantt_representation",
        "get-waiting-queue-diagrams": "get_waiting_queue_graph",
        "get-jobs-throughput-diagrams": "get_jobs_throughput",
        "get-unused-cores-diagrams": "get_unused_cores_graph",
        "get-animated-clusters": "get_animated_cluster"
    }
    if translate:
        return translated_actions[action]
    else:
        return action


class BatchCreator:

    def __init__(self, project_file_path: str, webui: bool = False):

        # Ready to use generators implementing the AbstractGenerator interface
        self.__impl_generators = {
            RandomGenerator.name: RandomGenerator,
            RandomFromListGenerator.name: RandomFromListGenerator,
            KeysDictGenerator.name: KeysDictGenerator,
            KeysListGenerator.name: KeysListGenerator,
            ShuffleKeysListGenerator.name: ShuffleKeysListGenerator,
            SWFGenerator.name: SWFGenerator
        }

        # Ready to use schedulers implementing the Distribution interface
        self.__impl_distributions = {
            "Constant": ConstantDistribution,
            "Random": RandomDistribution,
            "Poisson": PoissonDistribution
        }

        # Ready to use schedulers implementing the Scheduler interface
        self.__impl_schedulers = {}
        for sched_key, sched_val in scheduler_hierarchy.items():
            scheduler_name = sched_val["name"]
            if not scheduler_name:
                scheduler_name = sched_key
            self.__impl_schedulers[scheduler_name] = sched_val["obj"]
        # self.__impl_schedulers = {
        #     FIFOScheduler.name: FIFOScheduler,
        #     EASYScheduler.name: EASYScheduler,
        #     ConservativeScheduler.name: ConservativeScheduler,
        #     RandomRanksCoscheduler.name: RandomRanksCoscheduler
        # }
        
        # If it is called from WebUI the actions will be translated
        self.__webui = webui
        
        logger.debug(f"Opening project file: {project_file_path}")
        # Load the configuration file
        with open(project_file_path, "r") as fd:

            self.config = safe_load(fd)
            
            sanity_entries = ["name", "inputs", "schedulers", "actions"]

            if list(filter(lambda x: x not in self.config, sanity_entries)):
                raise RuntimeError("The configuration file is not properly designed")

            self.__project_name = self.config["name"]
            self.__project_inputs = self.config["inputs"]
            self.__project_schedulers = self.config["schedulers"]
            self.__project_actions = self.config["actions"] if "actions" in self.config else dict()

        # If using MPI store modules that should be exported to other MPI procs
        self.mods_export = list()

    def get_sim_configs_num(self) -> int:
        logger.debug("Calculating the total number of simulation configurations")
        inputs_num = 0
        for input in self.__project_inputs:
            inputs_num += 1 if "repeat" not in input else int(input["repeat"])

        return inputs_num * (1 + len(self.__project_schedulers["others"]))

    def process_inputs(self) -> None:

        logger.debug("Begin processing the inputs")

        # Process the inputs
        self.__inputs = list()

        for input in self.__project_inputs:
        
            # Create a LoadManager based on the options given
            lm = LoadManager(machine=input["loads-machine"],
                             suite=input["loads-suite"])
            # A LoadManager instance can be created using
            if "path" in input:
                # A path to a directory with the real logs
                path = input["path"]
                lm.init_loads(runs_dir=path)
            elif "load-manager" in input:
                # A pickled LoadManager instance (or json WIP)
                with open(input["load-manager"], "rb") as fd:
                    lm = pickle_load(fd)
            elif "db" in input:
                # A mongo database url
                lm.import_from_db(host=input["db"], dbname="storehouse")
            elif "json" in input:
                lm.import_from_json(input["json"])
            else:
                raise RuntimeError("Couldn't provide a way to create a LoadManager")

            # Create a heatmap from the LoadManager instance or use a user-defined
            # if a path is provided
            if "heatmap" in input:
                with open(input["heatmap"], "r") as fd:
                    heatmap = json_loads(fd.read())
            else:
                heatmap = lm.export_heatmap()

            logger.debug(f"Finished calculating the heatmap: {heatmap}")

            # Create the input using the generator provided
            if "generator" in input:
                generator = input["generator"]
                gen_type = generator["type"]
                gen_arg = generator["arg"]

                # If a python file is provided for the generator
                if os.path.exists(gen_type) and ".py" in gen_type:
                    # Import generator module
                    spec_name = import_module(gen_type)
                    gen_mod = sys.modules[spec_name]
                    # Get the generator class from the module
                    classes = inspect.getmembers(gen_mod, inspect.isclass)
                    # It must be a concrete class implementing the AbstractGenerator interface
                    classes = list(filter(lambda it: not inspect.isabstract(it[1]) and issubclass(it[1], AbstractGenerator), classes))

                    # If there are multiple then inform the user that the first will be used
                    if len(classes) > 1:
                        print(f"Multiple generator definitions were found. Using the first definition: {classes[0][0]}")

                    _, gen_cls = classes[0]

                    # Export module for MPI procs
                    self.mods_export.append(gen_type)
                else:
                    try:
                        gen_cls = self.__impl_generators[gen_type]
                    except:
                        raise RuntimeError(f"The name {gen_type} of the generator provided does not exist")

                # Create instance of generator
                gen_inst = gen_cls(load_manager=lm)
                # gen_inst = gen_cls()
            
                logger.debug(f"Got the generator: {gen_inst.name}")

                if "repeat" in input:
                    repeat = int(input["repeat"])
                else:
                    repeat = 1

                for _ in range(repeat):

                    # Generate the input
                    if gen_type in ["List Generator","Shuffle List Generator"]:
                        with open(gen_arg, 'r') as _f:
                            gen_data = _f.read()
                        gen_input = gen_inst.generate_jobs_set(gen_data)

                    elif gen_type in ["Random From List Generator"]:
                        with open(gen_arg[1], 'r') as _f:
                            gen_data = _f.read()
                        gen_input = gen_inst.generate_jobs_set([gen_arg[0], gen_data])

                    else:
                        gen_input = gen_inst.generate_jobs_set(gen_arg)


                    logger.debug(f"Finished generating the input")

                    # Check if a transformer distribution is provided by the user
                    if "distribution" in generator:
                    
                        distribution = generator["distribution"]
                        distr_type = distribution["type"]
                        distr_arg = distribution["arg"]

                        # If a path is provided for the distribution transformer
                        if os.path.exists(distr_type) and ".py" in distr_type:
                            spec_name = import_module(distr_type)
                            distr_mod = sys.modules[spec_name]
                            classes = inspect.getmembers(distr_mod, inspect.isclass)
                            classes = list(filter(lambda it: not inspect.isabstract(it[1]) and issubclass(it[1], IDistribution), classes))
                            # If there are multiple then inform the user that the first will be used
                            if len(classes) > 1:
                                print(f"Multiple distribution definitions were found. Using the first definition: {classes[0][0]}")

                            _, distr_cls = classes[0]
                            # Export module for MPI procs
                            self.mods_export.append(distr_type)
                        else:
                            try:
                                distr_cls = self.__impl_distributions[distr_type]
                            except:
                                raise RuntimeError(f"Distribution of type {distr_type} does not exist")

                        distr_inst = distr_cls()
                        distr_inst.apply_distribution(gen_input, time_step=distr_arg)

                        logger.debug(f"A distribution was applied to the input: {distr_inst.name}")


                    nodes = int(input["cluster"]["nodes"])
                    socket_conf = tuple(input["cluster"]["socket-conf"])
                    self.__inputs.append((gen_input, heatmap, nodes, socket_conf))

            else:
                raise RuntimeError("A generator was not provided")

        logger.debug("Finished processing the inputs")

    def process_schedulers(self) -> None:

        logger.debug("Begin processing the schedulers")

        # Process the schedulers
        # The first one in the list will always be the default
        self.__schedulers = list()
        
        # Because there might multiple schedulers with the same name but different arguments
        # give each one of them an index
        sched_index = 0

        for scheduler in [self.__project_schedulers["default"]] + self.__project_schedulers["others"]:

            if os.path.exists(scheduler) and ".py" in scheduler:
                spec_name = import_module(scheduler)
                sched_mod = sys.modules[spec_name]
                classes = inspect.getmembers(sched_mod, inspect.isclass)
                classes = list(filter(lambda it: not inspect.isabstract(it[1]) and issubclass(it[1], Scheduler), classes))
                # If there are multiple then inform the user that the first will be used
                if len(classes) > 1:
                    print(f"Multiple scheduler definitions were found. Using the first definition: {classes[0][0]}")

                _, sched_cls = classes[0]

                # To export modules for MPI procs
                print(scheduler)
                self.mods_export.append(scheduler)
            else:
                try:
                    sched_cls = self.__impl_schedulers[scheduler]
                except:
                    raise RuntimeError(f"Scheduler of type {scheduler} does not exist")

            self.__schedulers.append((sched_index, sched_cls))
            sched_index += 1

        logger.debug(f"Finished processing the schedulers: {self.__schedulers}")

    def process_actions(self) -> None:
        """
        The structure of self.__actions
        actions = {
            input0 = {
                scheduler0 = [],
                scheduler1 = [],
                ..
                schedulerM = []
            },
            ..
            inputN = {
                scheduler0 = []
                scheduler1 = []
                ..
                schedulerM = []
            }
        }
        The structure of self.__extra_features is a list of (arg: str, val: T) tuples
        self.__extra_features = [(arg0, val0), (arg1, val1), ...]
        """

        logger.debug("Begin processing the postprocessing actions")

        # Define __actions
        self.__actions = dict()
        for input_index in range(len(self.__inputs)):
            input_dict = dict()
            for sched_index, sched_cls in self.__schedulers:
                input_dict.update({sched_index: []})
            self.__actions.update({input_index: input_dict})

        # Define __extra_features
        self.__extra_features: list[tuple] = list()

        for action in self.__project_actions:
            action_inputs = self.__project_actions[action]["inputs"]
            action_schedulers = self.__project_actions[action]["schedulers"]

            action_extra_features = [(arg, val) 
                                     for arg, val in self.__project_actions[action].items() 
                                     if arg not in ["inputs", "schedulers"]]

            # Simple implementation is to overwrite an argument with the latest
            # value provided in the project file
            self.__extra_features.extend(action_extra_features)

            if action_inputs == "all":
                for input_dict in self.__actions.values():
                    if action_schedulers == "all":
                        for sched_dict in input_dict.values():
                            sched_dict.append(translate_action(action, self.__webui))
                    else:
                        for sched_index in action_schedulers:
                            input_dict[sched_index].append(translate_action(action, self.__webui))
            else:
                for input_index in action_inputs:
                    if action_schedulers == "all":
                        for sched_dict in self.__actions[input_index].values():
                            sched_dict.append(translate_action(action, self.__webui))
                    else:
                        for sched_index in action_schedulers:
                            self.__actions[input_index][sched_index].append(translate_action(action, self.__webui))

        logger.debug(f"Finished processing the postprocessing actions: {self.__extra_features}")

    def create_ranks(self) -> None:
        self.process_inputs()
        self.process_schedulers()
        self.process_actions()

        # Id for the simulation run
        sim_idx = 0

        # Create the ranks
        self.ranks = list()
        for input_index, [input, heatmap, nodes, socket_conf] in enumerate(self.__inputs):
            for sched_index, sched_cls in self.__schedulers:

                # Create a database instance
                database = Database(input, heatmap)
                database.setup()

                # Create a cluster instance
                cluster = Cluster(nodes, socket_conf)

                # Create a scheduler instance
                scheduler = sched_cls()
                # Apply all the general options if any exists
                if "general-options" in self.__project_schedulers:
                    for opt, val in self.__project_schedulers["general-options"].items():
                        scheduler.__dict__[opt] = val

                # Create a logger instance
                logger = Logger(debug=False)

                # Create a compute engine instance
                compengine = ComputeEngine(database, cluster, scheduler, logger)
                compengine.setup_preloaded_jobs()

                # Set actions for this simulation
                actions = self.__actions[input_index][sched_index]

                self.ranks.append((sim_idx, input_index, sched_index, database, cluster, scheduler, logger, compengine, actions, self.__extra_features))

                sim_idx += 1
