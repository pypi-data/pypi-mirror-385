import json
import os
from collections import defaultdict
from os import path
from pkg_resources import resource_filename
from copy import deepcopy

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.fileutil import copy_asset
from sphinx.util.matching import DOTFILES

SHPINX_TO_ISO_LANGUAGE_CODES = {'sr_RS' : 'sr-Cyrl', 'sr' : 'sr-Cyrl', 'sr@latn' : 'sr-Latn'}

class PetljaBuilder(StandaloneHTMLBuilder):
    name = 'petlja_builder'
    bc_outdir = 'bc_html'

    def __init__(self, app):
        super().__init__(app)
        self.outdir = path.join(self.outdir, self.bc_outdir)
        self.app.outdir = self.outdir
        self.search = False
        self.copysource = False
        self.config.language = SHPINX_TO_ISO_LANGUAGE_CODES.get(self.config.language, self.config.language)
        petlja_player_driver = resource_filename('petljadoc', 'themes/bc_theme/platform')
        copy_asset(petlja_player_driver, path.join(self.outdir, 'platform'), excluded=DOTFILES)
        
    def get_theme_config(self):
        return self.config.html_bc_theme , self.config.html_theme_options

    def write_buildinfo(self):
        pass

    def dump_inventory(self):
        pass

    def write_genindex(self):
        pass

def override_env_dict(app, env):
    if(os.path.isfile('override.json')):
        with open('override.json') as file:
            data = json.load(file)
        app.env.metadata = defaultdict(dict, dict_of_dicts_merge(dict(env.metadata), data))

def dict_of_dicts_merge(x, y):
    merged_dict = {}
    if isinstance(x,dict) and isinstance(y,dict):
        overlapping_keys = x.keys() & y.keys()
        for key in overlapping_keys:
            merged_dict[key] = dict_of_dicts_merge(x[key], y[key])
        for key in x.keys() - overlapping_keys:
            merged_dict[key] = deepcopy(x[key])
        for key in y.keys() - overlapping_keys:
            merged_dict[key] = deepcopy(y[key])
        return merged_dict
    else:
        return y

def setup(app: Sphinx):
    app.add_config_value('html_bc_theme', 'petljadoc_bc_theme', 'html')
    app.connect('env-updated',override_env_dict)
    app.add_builder(PetljaBuilder)




