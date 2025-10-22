"use strict";
function WrappingBlicky(){
var ScrollDebounce = {};
var ScrollDebounceLog = {};
var resetInterpreter = {};
$(document).ready(function () {
  var errorText = {};

  errorText.ErrorTitle = $.i18n("msg_activecode_error_title");
  errorText.DescriptionTitle = $.i18n("msg_activecode_description_title");
  errorText.ToFixTitle = $.i18n("msg_activecode_to_fix_title");
  errorText.ParseError = $.i18n("msg_activecode_parse_error");
  errorText.ParseErrorFix = $.i18n("msg_activecode_parse_error_fix");
  errorText.TypeError = $.i18n("msg_activecode_type_error");
  errorText.TypeErrorFix = $.i18n("msg_activecode_type_error_fix");
  errorText.NameError = $.i18n("msg_activecode_name_error");
  errorText.NameErrorFix = $.i18n("msg_activecode_name_error_fix");
  errorText.ValueError = $.i18n("msg_activecode_value_error");
  errorText.ValueErrorFix = $.i18n("msg_activecode_value_error_fix");
  errorText.AttributeError = $.i18n("msg_activecode_attribute_error");
  errorText.AttributeErrorFix = $.i18n("msg_activecode_attribute_error_fix");
  errorText.TokenError = $.i18n("msg_activecode_token_error");
  errorText.TokenErrorFix = $.i18n("msg_activecode_token_error_fix");
  errorText.TimeLimitError = $.i18n("msg_activecode_time_limit_error");
  errorText.TimeLimitErrorFix = $.i18n("msg_activecode_time_limit_error_fix");
  errorText.Error = $.i18n("msg_activecode_general_error");
  errorText.ErrorFix = $.i18n("msg_activecode_general_error_fix");
  errorText.SyntaxError = $.i18n("msg_activecode_syntax_error");
  errorText.SyntaxErrorFix = $.i18n("msg_activecode_syntax_error_fix");
  errorText.IndexError = $.i18n("msg_activecode_index_error");
  errorText.IndexErrorFix = $.i18n("msg_activecode_index_error_fix");
  errorText.URIError = $.i18n("msg_activecode_uri_error");
  errorText.URIErrorFix = $.i18n("msg_activecode_uri_error_fix");
  errorText.ImportError = $.i18n("msg_activecode_import_error");
  errorText.ImportErrorFix = $.i18n("msg_activecode_import_error_fix");
  errorText.ReferenceError = $.i18n("msg_activecode_reference_error");
  errorText.ReferenceErrorFix = $.i18n("msg_activecode_reference_error_fix");
  errorText.ZeroDivisionError = $.i18n("msg_activecode_zero_division_error");
  errorText.ZeroDivisionErrorFix = $.i18n("msg_activecode_zero_division_error_fix");
  errorText.RangeError = $.i18n("msg_activecode_range_error");
  errorText.RangeErrorFix = $.i18n("msg_activecode_range_error_fix");
  errorText.InternalError = $.i18n("msg_activecode_internal_error");
  errorText.InternalErrorFix = $.i18n("msg_activecode_internal_error_fix");
  errorText.IndentationError = $.i18n("msg_activecode_indentation_error");
  errorText.IndentationErrorFix = $.i18n("msg_activecode_indentation_error_fix");
  errorText.NotImplementedError = $.i18n("msg_activecode_not_implemented_error");
  errorText.NotImplementedErrorFix = $.i18n("msg_activecode_not_implemented_error_fix");

  var categories = {
    'KarelCommands': {
        "kind": "category",
        "name": $.i18n('KarelCommands'),
        "colour": 295,
        "contents": [
            {
                "kind": "block",
                "type": "move",
            },
            {
                "kind": "block",
                "type": "turn_left"
            },
            {
                "kind": "block",
                "type": "turn_right"
            },
            {
                "kind": "block",
                "type": "turn_around"
            },
            {
                "kind": "block",
                "type": "pick_up"
            },
            {
                "kind": "block",
                "type": "drop_off"
            },
        ]
    },
    'BeginnerKarelCommands': {
        "kind": "category",
        "name": $.i18n('BeginnerKarelCommands'),
        "colour": 295,
        "contents": [
            {
                "kind": "block",
                "type": "move",
            },
            {
                "kind": "block",
                "type": "turn_left"
            },
            {
                "kind": "block",
                "type": "turn_right"
            },
            {
                "kind": "block",
                "type": "pick_up"
            },
        ]
    },
    'KarelStraightLineCommands': {
        "kind": "category",
        "name": $.i18n('KarelStraightLineCommands'),
        "colour": 295,
        "contents": [
            {
                "kind": "block",
                "type": "move",
            },
            {
                "kind": "block",
                "type": "move_back",
            },
            {
                "kind": "block",
                "type": "pick_up"
            },
        ]
    },
    'KarelBrain': {
        "kind": "category",
        "name": $.i18n('KarelBrain'),
        "colour": 275,
        "contents": [
            {
                "kind": "block",
                "type": "balls_present",
            },
            {
                "kind": "block",
                "type": "can_move",
            },
            {
                "kind": "block",
                "type": "has_balls",
            },
            {
                "kind": "block",
                "type": "count_balls_on_hand",
            },
            {
                "kind": "block",
                "type": "count_balls",
            },
        ]
    },
    'Values': {
        "kind": "category",
        "name": $.i18n('K_Values'),
        "colour": 250,
        "contents": [    
            {
                "kind": "block",
                "type": "math_number",
            },    
        ]
    },
    'Branching': {
        "kind": "category",
        "name": $.i18n('K_Branching'),
        "colour": 130,
        "contents": [
            {
                "kind": "block",
                "type": "controls_if",
            },
            {
                "kind": "block",
                "type": "controls_ifelse",
            },
        ]
    },
    'KarelBranching': {
        "kind": "category",
        "name": $.i18n('KarelBranching'),
        "colour": 150,
        "contents": [
            {
                "kind": "block",
                "type": "controls_if_simple",
            },
            {
                "kind": "block",
                "type": "controls_ifelse_simple",
            },
        ]
    },
    'Vars': {
        "kind": "category",
        "colour": 310,
        "name": $.i18n('K_Vars'),
        "custom": "VARIABLE",
    },
    'Loops': {
        "kind": "category",
        "name": $.i18n('K_Loops'),
        "colour": 190,
        "contents": [
            {
                "kind": "block",
                "type": "controls_repeat"
            },
            {
                "kind": "block",
                "type": "controls_repeat_ext",
            },
            {
                "kind": "block",
                "type": "controls_whileUntil"
            },
        ]
    },
    'KarelLoops': {
        "kind": "category",
        "name": $.i18n('KarelLoops'),
        "colour": 210,
        "contents": [
            {
                "kind": "block",
                "type": "karel_controls_whileUntil"
            },
        ]
    },
    'Logic': {
        "kind": "category",
        "name": $.i18n('K_Logic'),
        "colour": 220,
        "contents": [
            {
                "kind": "block",
                "type": "logic_compare",
            },
            {
                "kind": "block",
                "type": "logic_operation",
            },
            {
                "kind": "block",
                "type": "logic_negate",
            },
        ]
    },
    'Arithmetic': {
        "kind": "category",
        "name": $.i18n('Arithmetic'),
        "colour": 215,
        "contents": [
            {
                "kind": "block",
                "type": "math_number",
            },
            {
                "kind": "block",
                "type": "math_arithmetic",
            },
        ]
    },
    'KarelSays': {
        "kind": "category",
        "name": $.i18n('KarelSays'),
        "colour": 245,
        "contents": [
            {
                "kind": "block",
                "type": "text_print",
            },
        ]
    },
    'AskUser': {
        "kind": "category",
        "name": $.i18n('K_AskUser'),
        "colour": 290,
        "contents": [
            {
                "kind": "block",
                "type": "number_prompt",
            }
        ]
    }
};

  const startBlocks = {
    "variables": [
      {
        "name": "x",
        "id": "x"
      }
    ]
  };

  $('[data-component=blocklyKarel]').each(function (index) {
    var toolboxType = "";
    if (this.hasAttribute("data-flyoutToolbox"))
      toolboxType = "flyoutToolbox"
    else
      toolboxType = "categoryToolbox"
    var toolbox = {
      "kind": toolboxType,
      "contents": []
    }

    var outerDiv = $(this)[0];
    var canvas = $(this).find(".world")[0];
    var problemId = this.id;
    var configarea = $(this).find(".configArea")[0];
    var config = (new Function('return ' + configarea.value.replace('<!--x', '').replace('x-->', '')))();
    var elementDiv = outerDiv.parentElement.parentElement.parentElement.parentElement
    var karelCongrolosDiv = outerDiv.parentElement.parentElement.parentElement.children[0];
    var karelConfigDiv = elementDiv.querySelector("#blocklyKarelDiv");
    var categoriesFilter = JSON.parse(karelConfigDiv.getAttribute("data-categories"));
    if(toolboxType === "flyoutToolbox")
      for(var i= 0;i<categoriesFilter.length;i++){
        toolbox.contents.push({
          "kind": "label",
          "text": categories[categoriesFilter[i]].name,
          "web-class": "petlja-blockly.label"
        },);
        for(var j= 0;j<categories[categoriesFilter[i]].contents.length;j++)
          toolbox.contents.push(categories[categoriesFilter[i]].contents[j]);
      }
    else{
      for(var i= 0;i<categoriesFilter.length;i++)
      toolbox.contents.push(categories[categoriesFilter[i]]);
    }
    var workspace = Blockly.inject(karelConfigDiv, { toolbox:  toolbox, trashcan: true});
    Blockly.serialization.workspaces.load(startBlocks, workspace);

    var setup = config.setup();
    if(setup.hasOwnProperty('domXml')){
      var domXml = setup.domXml;
      Blockly.Xml.domToWorkspace(workspace,Blockly.Xml.textToDom(domXml))
    }
    ScrollDebounce[workspace.id] = true;
    resetInterpreter[workspace.id] = false;

    var robot = setup.robot;
    var world = setup.world;
    var node = this.querySelector(".chat-window");
    var chat = new Chat(node);
    robot.setChat(chat);
    robot.setWorld(world);
    var drawer = new RobotDrawer(canvas, 0);
    drawer.drawFrame(robot);


    function initApi(interpreter, globalObject) {
      var wrapper = function (text) {
        robot.showMessage(text);
      };
      interpreter.setProperty(globalObject, 'alert', interpreter.createNativeFunction(wrapper));
      wrapper = function(text) {
        return prompt(text);
      };
      interpreter.setProperty(globalObject, 'prompt', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.move();
        drawer.drawFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'move_forward', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.moveBack();
        drawer.drawFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'move_backward', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.turnLeft();
        drawer.drawFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'turn_left', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.turnRight();
        drawer.drawFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'turn_right', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.turnRight();
        robot.turnRight();
        drawer.drawFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'turn_around', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.pickBall();
        drawer.drawFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'pick_up', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        robot.putBall();
        drawer.addFrame(robot.clone());
      };
      interpreter.setProperty(globalObject, 'drop_off', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        return robot.frontIsClear()
      };
      interpreter.setProperty(globalObject, 'can_move', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        return robot.ballsPresent()
      };
      interpreter.setProperty(globalObject, 'balls_present', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        return robot.getBalls() != 0;
      };
      interpreter.setProperty(globalObject, 'has_ball', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        return robot.countBalls();
      };
      interpreter.setProperty(globalObject, 'count_balls', interpreter.createNativeFunction(wrapper));
      wrapper = function () {
        return robot.getBalls();
      };
      interpreter.setProperty(globalObject, 'count_balls_on_hand', interpreter.createNativeFunction(wrapper));
      wrapper = function (id) {
        workspace.highlightBlock(id);
      };
      interpreter.setProperty(globalObject, 'highlightBlock', interpreter.createNativeFunction(wrapper));
      wrapper = function (value) {
      return JSON.stringify([...Array(value).keys()]);    
      };
      interpreter.setProperty(globalObject, 'range', interpreter.createNativeFunction(wrapper));
    }

    karelCongrolosDiv.querySelector(".run-button").addEventListener("click",function () {
      var runButton = this;
      runButton.setAttribute('disabled', 'disabled');
      clearError();
      setup = config.setup();
      robot = setup.robot;
      world = setup.world;
      robot.chat = chat;
      robot.setWorld(world);
      robot.clearMessages();
      drawer = new RobotDrawer(canvas, 0);
      drawer.drawFrame(robot);
      var code = Blockly.JavaScript.workspaceToCode(workspace);
      var myInterpreter = new Interpreter(code, initApi);
      drawer.start()
      resetInterpreter[workspace.id] = false;
      function nextStep() {
        try {
          if (myInterpreter.step() && !resetInterpreter[workspace.id]) {
            setTimeout(nextStep, 65);
          }
          else {
            runButton.removeAttribute('disabled');
            var result = config.isSuccess(robot, world);
            if (result) {
              showEndMessageSuccess();
            } else {
              if(!resetInterpreter[workspace.id])
                showEndMessageError($.i18n("msg_karel_incorrect"));
            }
            if(resetInterpreter[workspace.id])
              resetInterpreter[workspace.id] = false
          }
        }
        catch (err) {
          runButton.removeAttribute('disabled');
          drawer.stop(function () {
            var message = "";
            var otherError = false;
            if ((err == "crashed") || (err == "no_ball") || (err == "out_of_bounds") || (err == "no_balls_with_robot"))
              message = $.i18n("msg_karel_" + err);
            else {
              showError(err);
              otherError = true;
            }
            if (!otherError)
              showEndMessageError(message);

          });
        }
      }
      nextStep();
    });

    karelCongrolosDiv.querySelector(".reset-button").addEventListener("click",function () {
      workspace.getAllBlocks().forEach( a => a.setHighlighted(!1));
      resetInterpreter[workspace.id] = true;
      clearError();
      reset();
    });
    document.getElementsByClassName("lectureContentMaterial")[0].addEventListener('scroll',function () {
    if (ScrollDebounce[workspace.id]) {
      ScrollDebounce[workspace.id] = false;
      workspace.updateScreenCalculations_();
      setTimeout(function () { 
        ScrollDebounce[workspace.id] = true; 
        if(ScrollDebounceLog[workspace.id]){
          ScrollDebounceLog[workspace.id] = false; 
          workspace.updateScreenCalculations_();
        }
        }, 1000);
    }
    else{
      ScrollDebounceLog[workspace.id] = true;
    }
    });

    if(karelCongrolosDiv.querySelector(".export-button"))
      karelCongrolosDiv.querySelector(".export-button").addEventListener("click",function () {
        navigator.clipboard.writeText("'" + Blockly.Xml.domToPrettyText(Blockly.Xml.workspaceToDom(workspace)).replaceAll('\n','\\n') + "';" )
      });


    function reset() {
      var setup = config.setup();
      var robot = setup.robot;
      var world = setup.world; 
      robot.chat = chat;
      robot.setWorld(world);
      robot.clearMessages();
      var drawer = new RobotDrawer(canvas, 0);
      drawer.drawFrame(robot);
    }

    function showEndMessageSuccess() {
      var eContainer = outerDiv.appendChild(document.createElement('div'));
      eContainer.className = 'col-md-12 alert alert-success mt-2';
      eContainer.id = problemId + "-success";
      var msgHead = $('<p>').html($.i18n("msg_karel_correct"));
      eContainer.appendChild(msgHead[0]);
    }

    function showEndMessageError(message) {
      var eContainer = outerDiv.appendChild(document.createElement('div'));
      eContainer.className = 'col-md-12 alert alert-danger mt-2';
      eContainer.id = problemId + "-error";
      var msgHead = $('<p>').html(message);
      eContainer.appendChild(msgHead[0]);
    }

    function showError(err) {
      //logRunEvent({'div_id': this.divid, 'code': this.prog, 'errinfo': err.toString()}); // Log the run event
      var errHead = $('<h3>').html(errorText.ErrorTitle);
      var eContainer = outerDiv.appendChild(document.createElement('div'));
      eContainer.className = 'col-md-12 error alert alert-danger mt-2';
      eContainer.appendChild(errHead[0]);
      var errText = eContainer.appendChild(document.createElement('pre'));
      var errString = err.toString();
      var to = errString.indexOf(":");
      var errName = errString.substring(0, to);
      errText.innerHTML = errString;
      var desc = errorText[errName];
      var fix = errorText[errName + 'Fix'];
      if (desc) {
        $(eContainer).append('<h3>' + errorText.DescriptionTitle + '</h3>');
        var errDesc = eContainer.appendChild(document.createElement('p'));
        errDesc.innerHTML = desc;
      }
      if (fix) {
        $(eContainer).append('<h3>' + errorText.ToFixTitle + '</h3>');
        var errFix = eContainer.appendChild(document.createElement('p'));
        errFix.innerHTML = fix;
      }
      //var moreInfo = '../ErrorHelp/' + errName.toLowerCase() + '.html';
      console.log("Runtime Error: " + err.toString());
    };

    function clearError() {
      $(outerDiv).find(".alert-success").remove();
      $(outerDiv).find(".alert-danger").remove();
    }

    reset();
  });

  
  Blockly.JavaScript.STATEMENT_PREFIX = 'highlightBlock(%1);\n';
  Blockly.JavaScript.addReservedWords('highlightBlock');
  
  
});
};
WrappingBlicky();