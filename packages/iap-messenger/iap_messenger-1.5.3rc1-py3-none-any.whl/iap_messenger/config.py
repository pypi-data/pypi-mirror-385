"""Config reader class"""
import logging
import os
import json
from json.decoder import JSONDecodeError
from dataclasses import dataclass
import yaml
from yamlcore import CoreLoader
from yamlcore import CoreDumper

from iap_messenger.data_encoder import DataEncoder


LOGGER = logging.getLogger("Config")


@dataclass
class PipeInputOutput:
    """Config reader class"""
    data: dict
    name: str
    type: str
    link: str
    parameters: dict[str, str]
    output: str | None = None
    
    def __init__(self, item: dict):
        """Load config from file"""
        self.data = item
        self.name = item["name"]
        self.type = item["type"]
        self.link = item["link"]
        self.parameters = {}
        if "parameters" in item:
            for p in item["parameters"]:
                self.parameters[p["name"]] = p["type"]
        if "output" in item:
            self.output = item["output"]
    
class Config:
    """Config reader class"""
    def __init__(self, filename: str):
        """Load config from file"""
        self.data: dict = {}
        self.Inputs: dict[str, PipeInputOutput] = {}
        self.Outputs: dict[str, PipeInputOutput] = {}
        self.input_list: list[str] = []
        self.output_list: list[str] = []
        self.encoders: dict[str, DataEncoder] = {}
        self.default_output: str = ""
        
        self.load(filename)
        if "inputs" in self.data:
            input_list = self.data["inputs"].split(",")
            for item in input_list:
                self.input_list.append(item.replace("/", "-"))
        if "outputs" in self.data:
            output_list = self.data["outputs"].split(",")
            for item in output_list:
                self.output_list.append(item.replace("/", "-"))

        if "pipeline" in self.data and len(self.data["pipeline"]) > 0:
            # Case config comes from IA Parc
            entity = self.data["pipeline"][0]
            for item in entity["input_def"]:
                if "link" in item and item["link"] in input_list and item["type"] != "query":
                    link_name = item["link"].replace("/", "-")
                    self.Inputs[link_name] = PipeInputOutput(item)

            # Get outputs from last entity
            entity = self.data["pipeline"][-1]
            for item in entity.output_def:
                if "link" not in item:
                    item["link"] = item["name"]
                if item["link"] in self.output_list:
                    self.Outputs[item["link"]] = PipeInputOutput(item)
                    self.encoders[item["link"]] = DataEncoder(item)
            self.default_output = self.output_list[0]
        
        elif "spec" in self.data and "inputs" in self.data["spec"]:
            # Case config comes from service config file
            for item in self.data["spec"]["inputs"]:
                item["link"] = item["name"]
                item_name = item["name"].replace("/", "-")
                self.Inputs[item_name] = PipeInputOutput(item)
                self.input_list.append(item_name)
            for item in self.data["spec"]["outputs"]:
                item["link"] = item["name"]
                item_name = item["name"].replace("/", "-")
                self.Outputs[item_name] = PipeInputOutput(item)
                self.encoders[item_name] = DataEncoder(item)
                self.output_list.append(item_name)
            self.default_output = self.output_list[0]


    def load(self, filename: str):
        """Load config from file"""
        with open(filename, "r", encoding="utf-8") as _:
            self.data = DictConfig(filename)
            


class DictConfig(dict):
    """
    Config reader class
    """
    def __init__(self, data=None):
        super(DictConfig, self).__init__()
        if data:
            if isinstance(data, dict):
                self.__update(data, {})
            elif isinstance(data, str):
                filename = os.path.basename(data)
                ext = os.path.splitext(filename)[1]
                self.__path = data
                self.__ext = ext
                if ext == "json":
                    self.__update(self.load_json(data), {})
                elif ext == "yaml" or ext == "yml":
                    self.__update(self.load_yaml(data), {})
                else:
                    try:
                        self.__update(self.load_json(data), {})
                    except (JSONDecodeError,TypeError):
                        self.__update(self.load_yaml(data), {})
            else:
                raise ValueError("Unknown data format")

    @staticmethod
    def dump_yaml(data, file_name):
        '''Dump data to yaml file'''
        to_dump = data.copy()
        del to_dump['_Config__path']
        del to_dump['_Config__ext']
        with open(f"{file_name}", "w", encoding="utf-8") as f:
            yaml.dump(to_dump, f, Dumper=CoreDumper)

    @staticmethod
    def dump_json(data, file_name):
        '''Dump data to json file'''
        to_dump = data.copy()
        del to_dump['_Config__path']
        del to_dump['_Config__ext']
        with open(f"{file_name}", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(to_dump, indent=4))

    def save(self):
        '''Save config to file'''
        try:
            if self.__ext.lower() == ".json":
                self.save_to_json(self.__path)
            elif self.__ext.lower() == ".yaml" or self.__ext.lower() == ".yml":
                self.save_to_yaml(self.__path)
            else:
                LOGGER.error("Cannot save file, unknown extenstion %s", self.__ext)
        except Exception:
            LOGGER.error("Cannot save config", exc_info=True)

    def save_to_json(self, filename):
        '''Save config to json file'''
        self.dump_json(self, filename)

    def save_to_yaml(self, filename):
        '''Save config to yaml file'''
        self.dump_yaml(self, filename)

    @staticmethod
    def load_json(config):
        '''Load json file'''
        with open(config, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @staticmethod
    def load_yaml(config):
        '''Load yaml file'''
        with open(config, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=CoreLoader)
        return data

    def new(self, data):
        '''Create new config from data'''
        self.__update(data, {})

    def load(self, data, did):
        """load methode"""
        self.__update(data, did)

    def __update(self, data, did):
        dataid = id(data)
        did[dataid] = self
        for k in data:
            dkid = id(data[k])
            if dkid in did.keys():
                self[k] = did[dkid]
            elif isinstance(data[k], DictConfig):
                self[k] = data[k]
            elif isinstance(data[k], dict):
                obj = DictConfig()
                obj.load(data[k], did)
                self[k] = obj
                obj = None
            elif isinstance(data[k], list) or isinstance(data[k], tuple):
                self[k] = self._add_list(data[k], did)
            else:
                self[k] = data[k]

    def _add_list(self, data, did):
        lst = []
        for item in data:
            if isinstance(item, dict):
                obj = DictConfig()
                obj.load(item, did)
                lst.append(obj)
                obj = None
            elif isinstance(item, list) or isinstance(item, tuple):
                lst.append(self._add_list(item, did))
            else:
                lst.append(item)
        if isinstance(data, tuple):
            lst = tuple(lst)
        return lst

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            self[key] = DictConfig(value)
        else:
            self[key] = value

    def has_key(self, k):
        """ returns True if key is present in the config"""
        if k in self.keys():
            return True
        else:
            return False

    def update(self, *args):
        for obj in args:
            for k in obj:
                if isinstance(obj[k], dict):
                    self[k] = DictConfig(obj[k])
                else:
                    self[k] = obj[k]
        return self

    def merge(self, *args):
        """ merges the config with one or more configs"""
        for obj in args:
            for k in obj:
                if k in self.keys():
                    if isinstance(self[k], list) and isinstance(obj[k], list):
                        self[k] += obj[k]
                    elif isinstance(self[k], list):
                        self[k].append(obj[k])
                    elif isinstance(obj[k], list):
                        self[k] = [self[k]] + obj[k]
                    elif isinstance(self[k], DictConfig) and isinstance(obj[k], DictConfig):
                        self[k].merge(obj[k])
                    elif isinstance(self[k], DictConfig) and isinstance(obj[k], dict):
                        self[k].merge(obj[k])
                    else:
                        self[k] = [self[k], obj[k]]
                else:
                    if isinstance(obj[k], dict):
                        self[k] = DictConfig(obj[k])
                    else:
                        self[k] = obj[k]
        return self

    def replace_variables(self, variables):
        """ replaces all variables in the config with the given variables"""
        for k, obj in self.items():
            if isinstance(obj, DictConfig):
                obj.replace_variables(variables)
            elif isinstance(obj, str):
                self[k] = obj.format(**variables)
            elif isinstance(obj, list) or isinstance(obj, tuple):
                self[k] = self.replace_in_list(obj, variables)

    def replace_in_list(self, obj, variables):
        """ replaces all variables in the list with the given variables"""
        for i, entry in enumerate(obj):
            if isinstance(entry, DictConfig):
                entry.replace_variables(variables)
            elif isinstance(entry, str):
                if isinstance(obj, tuple):
                    obj = list(obj)
                    obj[i] = entry.format(**variables)
                    obj = tuple(obj)
                else:
                    obj[i] = entry.format(**variables)
            elif isinstance(obj, list) or isinstance(obj, tuple):
                self.replace_in_list(obj, variables)
        return obj

