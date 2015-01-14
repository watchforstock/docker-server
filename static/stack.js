angular.module('stackApp', ['restangular', 'angular-growl'])
  .controller('StackController', ['$scope', 'Restangular', 'growl', function($scope, Restangular, growl) {
      
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
        
        var data = {
            'username': $scope.username,
            'stackid': $scope.newstack
        }
        growl.info("Creating stack, please wait");
        Restangular.all('stacks').post(data).then(function() {
            // Success
            console.log("Success");
            growl.success("Created stack");
            $scope.refresh();
        }, function() {
            // Failed
            console.log("Failed");
            growl.error("Failed to create stack");
        });
    };
     
$scope.deleteStack = function(identifier, stackid) {
	console.log(identifier);
	console.log(stackid);
growl.info("Deleting stack, please wait");
	  Restangular.all('stacks').customDELETE(identifier + '/' + stackid + '/').then(function() {
                growl.success("Deleted stack");
		$scope.refresh();
	}, function() {
	growl.success("Failed to delete stack");
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
