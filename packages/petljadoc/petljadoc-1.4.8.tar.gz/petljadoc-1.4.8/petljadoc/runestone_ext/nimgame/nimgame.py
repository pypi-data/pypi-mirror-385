__author__ = 'petlja'

import os
import shutil
import json

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from runestone.common.runestonedirective import add_i18n_js


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('nimgame', NimGameDirective)

    app.add_css_file('nimgame.css')

    app.add_js_file('nimgame.js')
    add_i18n_js(app, {"en","sr-Cyrl","sr","sr-Latn"},"nimgame-i18n")

    app.add_node(NimGamesNode, html=(visit_nim_game_node, depart_nim_game_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
<div class="course-box course-box-problem">
    <div id="%(divid)s" class="nim-game" data-nimgame='%(data)s'>
        <p class="nim-game-game-msg"> На табли je %(count)s жетона - побеђује ко узме последњи </p>
        <div class="canvas-wrapper">
            <canvas>

            </canvas>
        </div>
        <div class="canvas-control">          
            <div class="game-input">
                <div class="nim-controls" data-player="controls-1">
                    <div class="row player-labels">
                        <p class="p1-label"> Ти </p>
                        <p class="turn"> На потезу </p>
                    </div>
                    <div class="player-one row">
                        <button class="btn btn-success nim-take" data-take=1 data-id="player-1">Узми 1</button>
                        <button class="btn btn-success nim-take" data-take=2 data-id="player-1">Узми 2</button> 
                        <button class="btn btn-success nim-take" data-take=3 data-id="player-1">Узми 3</button> 
                    </div>
                </div>
                <div class="nim-controls" data-player="controls-2">
                    <div class="row player-labels">
                        <p class="p2-label"> Рачунар </p>
                        <p class="turn d-none"> На потезу </p>
                    </div>
                    <div class="player-two row">
                        <button class="btn btn-success nim-take"  data-take=1 data-id="player-2">Узми 1</button>
                        <button class="btn btn-success nim-take"  data-take=2 data-id="player-2">Узми 2</button> 
                        <button class="btn btn-success nim-take"  data-take=3 data-id="player-2">Узми 3</button> 
                    </div>
                </div>
            </div>
            <div class="reset-controls"> 
                <button class="btn btn-danger" data-restart="sp">Нова игра против рачунара</button>
                <button class="btn btn-danger" data-restart="mp">Нова игра у двоје</button>
            </div>
"""

TEMPLATE_END = """
        </div>
    </div>
</div>
"""


class NimGamesNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(NimGamesNode, self).__init__()
        self.components = content


def visit_nim_game_node(self, node):
    node.delimiter = "_start__{}_".format(node.components['divid'])
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.components
    self.body.append(res)


def depart_nim_game_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class NimGameDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {}
    option_spec.update({
        'takeaway': directives.unchanged,
        'count': directives.unchanged,
    })
    def run(self):
        env = self.state.document.settings.env 
        self.options['divid'] = self.arguments[0]
        data = {}
        if 'takeaway' not in self.options: 
            data['takeaway']  = 2
        else:
            data['takeaway'] = int(self.options['takeaway'])
        if 'count' not in self.options: 
            data['count'] = 15
        else:
            data['count'] = int(self.options['count']) 

        self.options['data'] = json.dumps(data)
        nimgamenode = NimGamesNode(self.options)
        return [nimgamenode]

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)
