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

            $scope.deleteStack = function (identifier, stackid) {
                growl.info("Deleting stack, please wait");
                Restangular.all('stacks').customDELETE(identifier + '/' + stackid + '/').then(function () {
                    growl.success("Deleted stack");
                    $scope.refresh();
                }, function () {
                    growl.success("Failed to delete stack");
                });
            };

  }]);