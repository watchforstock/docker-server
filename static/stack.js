angular.module('stackApp', ['restangular', 'angular-growl'])
    .controller('StackController', ['$scope', 'Restangular', 'growl',
        function ($scope, Restangular, growl) {

            Restangular.setRequestSuffix('/');


            $scope.refresh = function () {
                Restangular.all('stacks').getList().then(function (data) {
                    $scope.stacks = data;
                });
                Restangular.all('running').getList().then(function (data) {
                    $scope.running = data;
                });
                Restangular.all('scopes').getList().then(function (data) {
                    $scope.scopes = data;
                });
            }

            $scope.refresh();

	    $scope.getStacks = function() {
console.log("spotted change");
		var ret = [];
console.log($scope.stacks);
console.log($scope.scope);
                if ($scope.stacks && $scope.scope) {
  		for (var i=0; i<$scope.stacks.length; ++i) {
			if ($scope.stacks[i].scope == $scope.scope) {
				ret.push($scope.stacks[i]);
                        }		
		}
		}
console.log(ret);
		$scope.availableStacks = ret;
	    };

$scope.$watch('scope', $scope.getStacks);

$scope.logdata = [];

$scope.stackLog = function(scope, name, id, stack_id) {
	Restangular.all('stacks').customGET(scope + '/' + name + '/' + id + '/' + stack_id + '/logs/').then(function(data) {
console.log(data);
$scope.logdata = data[0];
$('#logmodal').modal();
});
}

            $scope.createStack = function () {

                var data = {
                    'identifier': $scope.identifier,
                    'stackid': $scope.newstack,
                    'scope': $scope.scope
                }
                growl.info("Creating stack, please wait");
                Restangular.all('stacks').post(data).then(function () {
                    // Success
                    growl.success("Created stack");
                    $scope.refresh();
                }, function () {
                    // Failed
                    growl.error("Failed to create stack");
                });
            };

            $scope.deleteStack = function (scope, identifier, stackid) {
                growl.info("Deleting stack, please wait");
                Restangular.all('stacks').customDELETE(scope + '/' + identifier + '/' + stackid + '/').then(function () {
                    growl.success("Deleted stack");
                    $scope.refresh();
                }, function () {
                    growl.error("Failed to delete stack");
                });
            };

  }]);
