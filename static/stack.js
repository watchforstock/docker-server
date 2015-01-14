angular.module('stackApp', ['restangular'])
  .controller('StackController', ['$scope', 'Restangular', function($scope, Restangular) {
      
      Restangular.setRequestSuffix('/');
 

    $scope.refresh = function() {      
        Restangular.all('stacks').getList().then(function(data) {
            $scope.stacks = data;
        });
        Restangular.all('running').getList().then(function(data) {
            $scope.running = data;
        });
    }

    $scope.refresh();
    
      
    $scope.createStack = function() {
        console.log("Hello");
      console.log($scope.username);
        console.log($scope.newstack);
        
        var data = {
            'username': $scope.username,
            'stackid': $scope.newstack
        }
        
        Restangular.all('stacks').post(data).then(function() {
            // Success
            console.log("Success");
            $scope.refresh();
        }, function() {
            // Failed
            console.log("Failed");
        });
    };
     
$scope.deleteStack = function(identifier, stackid) {
	console.log(identifier);
	console.log(stackid);
	  Restangular.all('stacks').customDELETE(identifier + '/' + stackid + '/').then(function() {
		$scope.refresh();
	});
}; 
    $scope.addTodo = function() {
      $scope.todos.push({text:$scope.todoText, done:false});
      $scope.todoText = '';
    };
 
    $scope.remaining = function() {
      var count = 0;
      angular.forEach($scope.todos, function(todo) {
        count += todo.done ? 0 : 1;
      });
      return count;
    };
 
    $scope.archive = function() {
      var oldTodos = $scope.todos;
      $scope.todos = [];
      angular.forEach(oldTodos, function(todo) {
        if (!todo.done) $scope.todos.push(todo);
      });
    };
  }]);
