Blockly.Blocks['move'] = {
  /**
   * Block for moving karel forward.
   * @this {Blockly.Block}
   */
  init: function () { 
    this.jsonInit({
      "message0": $.i18n('move_forward'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": $.i18n('move_forward_tooltip')
    });
  }
};

Blockly.JavaScript['move'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'move_forward()\n';
};

Blockly.Blocks['move_back'] = {
  /**
   * Block for moving karel forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('move_back'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": $.i18n('move_back_tooltip')
    });
  }
};

Blockly.JavaScript['move_back'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'move_backward()\n';
};

Blockly.Blocks['turn_left'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('turn_left'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": $.i18n('turn_left_tooltip')
    });
  }
};

Blockly.JavaScript['turn_left'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'turn_left()\n';
};

Blockly.Blocks['turn_right'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('turn_right'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": $.i18n('turn_right_tooltip')
    });
  }
};

Blockly.JavaScript['turn_right'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'turn_right()\n';
};

Blockly.Blocks['turn_around'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('turn_around'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 255,
      "tooltip": $.i18n('turn_around_tooltip')
    });
  }
};

Blockly.JavaScript['turn_around'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'turn_around()\n';
};

Blockly.Blocks['pick_up'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('pick_up'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": $.i18n('pick_up_tooltip')
    });
  }
};

Blockly.JavaScript['pick_up'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'pick_up()\n';
};

Blockly.Blocks['drop_off'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('drop_off'),
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": $.i18n('drop_off_tooltip')
    });
  }
};

Blockly.JavaScript['drop_off'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'drop_off()\n';
};

Blockly.Blocks['can_move'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('can_move'),
      "output": "Boolean",
      "colour": 250,
      "tooltip": $.i18n('can_move_tooltip')
    });
  }
};

Blockly.JavaScript['can_move'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['can_move()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['balls_present'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('balls_present'),
      "output": "Boolean",
      "colour": 250,
      "tooltip": $.i18n('balls_present_tooltip')
    });
  }
};

Blockly.JavaScript['balls_present'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['balls_present()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['has_balls'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('has_balls'),
      "output": "Boolean",
      "colour": 250,
      "tooltip": $.i18n('has_balls_tooltip')
    });
  }
};

Blockly.JavaScript['has_balls'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['has_ball()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['count_balls'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('count_balls'),
      "output": "Number",
      "colour": 250,
      "tooltip": $.i18n('count_balls_tooltip')
    });
  }
};

Blockly.JavaScript['count_balls'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['count_balls()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['count_balls_on_hand'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": $.i18n('count_balls_on_hand'),
      "output": "Number",
      "colour": 250,
      "tooltip": $.i18n('count_balls_on_hand_tooltip')
    });
  }
};

Blockly.JavaScript['count_balls_on_hand'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['count_balls_on_hand()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['karel_controls_whileUntil'] = {
  init: function () {
    this.jsonInit({
      'type': 'controls_whileUntil',
      'message0': $.i18n('karel_controls_whileUntil'),
      'args0': [
        {
          'type': 'field_dropdown',
          'name': 'KAREL_BOOL',
          'options': [
            [$.i18n('robot_has_ball'), 'has_ball()'],
            [$.i18n('balls_present_on_field'), 'balls_present()'],
            [$.i18n('robot_can_move_forward'), 'can_move()'],
          ],
        },
      ],
      'message1': '%{BKY_CONTROLS_REPEAT_INPUT_DO} %1',
      'args1': [{
        'type': 'input_statement',
        'name': 'DO',
      }],
      'previousStatement': null,
      'nextStatement': null,
      'style': 'loop_blocks',
      'helpUrl': '%{BKY_CONTROLS_WHILEUNTIL_HELPURL}',
      'extensions': ['controls_whileUntil_tooltip'],
    },)
  }
}

Blockly.JavaScript['karel_controls_whileUntil'] = function (block) {
  // Do while/until loop.
  let argument0 = block.getFieldValue('KAREL_BOOL')
  let branch = Blockly.JavaScript.statementToCode(block, 'DO');
  branch = Blockly.JavaScript.addLoopTrap(branch, block);
  return 'while (' + argument0 + ') {\n' + branch + '}\n';
};




Blockly.Blocks['controls_whileUntil'] = {
  init: function () {
    this.jsonInit({
      'type': 'controls_whileUntil',
      'message0': '%{BKY_CONTROLS_WHILEUNTIL_OPERATOR_WHILE} %1',
      'args0': [
        {
          'type': 'input_value',
          'name': 'BOOL',
          'check': 'Boolean',
        },
      ],
      'message1': '%{BKY_CONTROLS_REPEAT_INPUT_DO} %1',
      'args1': [{
        'type': 'input_statement',
        'name': 'DO',
      }],
      'previousStatement': null,
      'nextStatement': null,
      'style': 'loop_blocks',
      'helpUrl': '%{BKY_CONTROLS_WHILEUNTIL_HELPURL}',
      'extensions': ['controls_whileUntil_tooltip'],
    },)
  }
}


Blockly.Blocks['controls_ifelse_simple'] = {
  init: function () {
    this.jsonInit({
      'type': 'controls_ifelse',
      'message0': '%{BKY_CONTROLS_IF_MSG_IF} %1',
      'args0': [
        {
          'type': 'field_dropdown',
          'name': 'KAREL_BOOL',
          'options': [
            [$.i18n('robot_has_ball'), 'has_ball()'],
            [$.i18n('balls_present_on_field'), 'balls_present()'],
            [$.i18n('robot_can_move_forward'), 'can_move()'],
          ],
        },
      ],
      'message1': '%{BKY_CONTROLS_IF_MSG_THEN} %1',
      'args1': [
        {
          'type': 'input_statement',
          'name': 'DO0',
        },
      ],
      'message2': '%{BKY_CONTROLS_IF_MSG_ELSE} %1',
      'args2': [
        {
          'type': 'input_statement',
          'name': 'ELSE',
        },
      ],
      'previousStatement': null,
      'nextStatement': null,
      'style': 'logic_blocks',
      'tooltip': '%{BKYCONTROLS_IF_TOOLTIP_2}',
      'helpUrl': '%{BKY_CONTROLS_IF_HELPURL}',
      'suppressPrefixSuffix': true,
      'extensions': ['controls_if_tooltip'],
    },)
  }
}

Blockly.Blocks['controls_if_simple'] = {
  init: function () {
    this.jsonInit({
      'type': 'controls_ifelse',
      'message0': '%{BKY_CONTROLS_IF_MSG_IF} %1',
      'args0': [
        {
          'type': 'field_dropdown',
          'name': 'KAREL_BOOL',
          'options': [
            [$.i18n('robot_has_ball'), 'has_ball()'],
            [$.i18n('balls_present_on_field'), 'balls_present()'],
            [$.i18n('robot_can_move_forward'), 'can_move()'],
          ],
        },
      ],
      'message1': '%{BKY_CONTROLS_IF_MSG_THEN} %1',
      'args1': [
        {
          'type': 'input_statement',
          'name': 'DO0',
        },
      ],
      'previousStatement': null,
      'nextStatement': null,
      'style': 'logic_blocks',
      'tooltip': '%{BKYCONTROLS_IF_TOOLTIP_2}',
      'helpUrl': '%{BKY_CONTROLS_IF_HELPURL}',
      'suppressPrefixSuffix': true,
      'extensions': ['controls_if_tooltip'],
    },)
  }
}
Blockly.Blocks['variables_get'] = {
  init: function () {
    this.jsonInit(
      {
        'type': 'variables_get',
        'message0': '%1',
        'args0': [
          {
            'type': 'field_variable',
            'name': 'VAR',
            'variable': 'x',
          },
        ],
        'output': null,
        'style': 'variable_blocks',
        'helpUrl': '%{BKY_VARIABLES_GET_HELPURL}',
        'tooltip': '%{BKY_VARIABLES_GET_TOOLTIP}',
        'extensions': ['contextMenu_variableSetterGetter'],
      },
    )
  }
}
Blockly.Blocks['variables_set'] = {
  init: function () {
    this.jsonInit(
      {
        'type': 'variables_set',
        'message0': $.i18n('variables_set'),
        'args0': [
          {
            'type': 'field_variable',
            'name': 'VAR',
            'variable': 'x',
          },
          {
            'type': 'input_value',
            'name': 'VALUE',
          },
        ],
        'previousStatement': null,
        'nextStatement': null,
        'style': 'variable_blocks',
        'tooltip': '%{BKY_VARIABLES_SET_TOOLTIP}',
        'helpUrl': '%{BKY_VARIABLES_SET_HELPURL}',
        'extensions': ['contextMenu_variableSetterGetter'],
      },
    )
  }
}
Blockly.Blocks['number_prompt'] = {
  init: function() {
    this.appendDummyInput()
        .appendField($.i18n('number_prompt'))
        .appendField(new Blockly.FieldTextInput(""), "PROMPT");
    this.setOutput(true, "Number");
    this.setColour(230);
    this.setTooltip("");
    this.setHelpUrl("");
  }
};

Blockly.JavaScript['number_prompt'] = function(block) {
  var promptText = block.getFieldValue('PROMPT');
  var code = 'parseFloat(window.prompt(' + JSON.stringify(promptText) + '))';
  return [code, Blockly.JavaScript.ORDER_ATOMIC];
};