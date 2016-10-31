
var app = angular.module('app', []);

app.controller('mainController', function ($scope, $http) {

    $scope.attrs = {};
    $scope.methods = {};

    // Attributes
        $scope.attrs.searchType;

    // Methods
        $scope.methods.constructor = function () {
            $scope.methods.searchByUser();
            $scope.methods.reset();
        }
        $scope.methods.reset = function () {
            $scope.attrs.query = '';
            $scope.attrs.userData = null;
            $scope.attrs.contributions = null;
            $scope.attrs.relatedRepos = null;
            $scope.attrs.results = false;
            $scope.attrs.loading = false;
        }
        $scope.methods.searchByUser = function () {
            $scope.methods.reset();
            $scope.attrs.searchType = 'user';
        }
        $scope.methods.searchByRepo = function () {
            $scope.methods.reset();
            $scope.attrs.searchType = 'repo';
        }
        $scope.methods.search = function () {
            switch ($scope.attrs.searchType) {
                case 'user':
                    $scope.methods.loadUserData();
                    $scope.methods.relatedRepos();
                break;
                case 'repo':
                    $scope.methods.relatedRepos();
                break;
            }
        }
        $scope.methods.loadUserData = function () {
            $http.get('https://api.github.com/users/'+$scope.attrs.query).then(function (resp) {
                $scope.attrs.userData = resp.data;
                $scope.methods.loadContributions(resp.data.repos_url);
            });
        }
        $scope.methods.loadContributions = function (url) {
            $http.get(url).then(function (resp) {
                $scope.attrs.contributions = resp.data;
            });
        }
        $scope.methods.relatedRepos = function () {
            $scope.attrs.loading = true;
            $scope.attrs.results = false;
            $http.get('/api/'+$scope.attrs.query).then(function (resp) {
                switch ($scope.attrs.searchType) {
                    case 'user':
                        $scope.attrs.relatedRepos = resp.data.recommended;
                    break;
                    case 'repo':
                        $scope.attrs.relatedRepos = resp.data.similar;
                    break;
                }
                $scope.attrs.results = true;
                $scope.attrs.loading = false;
            });
        }

    // Construct
        $scope.methods.constructor();


})
