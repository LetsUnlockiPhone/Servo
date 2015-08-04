/**
 * rules.js
 */

// start data model
// a condition consist of a key, an operator (=) and a value
var Condition = function(init){
  var self = this;

  self.init = init;

  self.id = null;
  self.key = ko.observable('QUEUE');
  self.value = ko.observable('');
  self.operator = ko.observable('=');

  self.keyChoices = [
    {key: 'QUEUE', title: 'Queue'},
    {key: 'STATUS', title: 'Status'},
    {key: 'CUSTOMER', title: 'Customer'},
    {key: 'DEVICE', title: 'Device'},
  ]

  self.valueChoices = ko.computed(function(){
    return self.init[self.key()];
  });

  self.selectable = new Array('QUEUE', 'STATUS');

  self.canSelect = function(){
    return self.selectable.indexOf(self.key()) != -1;
  }
  
}

var Action = function(init){
  var self = this;

  self.init = init;

  self.id = null;
  self.title = ko.observable('Send Email');
  self.key = ko.observable('SEND_EMAIL');
  self.value = ko.observable('');

  self.selectable = new Array(
    'SET_QUEUE', 'SET_STATUS', 'SET_USER', 'ADD_TAG'
  );

  self.keyChoices = [
    {title: 'Send Email', key: 'SEND_EMAIL'},
    {title: 'Send SMS', key: 'SEND_SMS'},
    {title: 'Add Tag', key: 'ADD_TAG'},
    {title: 'Set Queue', key: 'SET_QUEUE'},
    {title: 'Assign to', key: 'SET_USER'}
  ];

  self.canSelect = function() {
    return self.selectable.indexOf(self.key()) != -1;
  }

  self.valueChoices = ko.computed(function(){
    return self.init[self.key()];
  });
}

var Rule = function(condInit, actionInit){
  var self = this;

  self.id = null;
  self.match = ko.observable('ANY');
  self.description = ko.observable('New Rule');

  self.matchChoices = [
    {title: 'Any', value: 'ANY'},
    {title: 'All', value: 'ALL'}
  ];

  // rules consist of conditions and actions
  self.conditions = ko.observableArray([new Condition(condInit)]);
  self.actions = ko.observableArray([new Action(actionInit)]);

}
// end data model

var ViewModel = function(cData, aData){
  var self = this;
  self.rule = new Rule(cData, aData);

  self.addCondition = function(){
    self.rule.conditions.push(new Condition(cData));
  };

  self.removeCondition = function(){
    if (self.rule.conditions().length < 2) return;
    self.rule.conditions.remove(this);
  };

  self.addAction = function(){
    self.rule.actions.push(new Action(aData));
  };

  self.removeAction = function(){
    if (self.rule.actions().length < 2) return;
    self.rule.actions.remove(this);
  };

  self.validateAndSave = function(form){
    $.post($(form).attr('action'), $(form).serialize(), function(r){
      console.log(r);
    });
  };

  self.init = function(data){
    console.log(data);
    self.rule = new Rule(cData, aData);
  }
}
