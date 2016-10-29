
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
            /*$http.get('http://localhost:3000/repo2.json').then(function (resp) {
                $scope.attrs.relatedRepos = resp.data.similar;
                $scope.attrs.results = true;
            });*/
            var data = { "contributed": [ { "contributor": "keksobot", "what": [ "PUSHED" ] }, { "contributor": "CunoVery", "what": [ "PULL_REQUEST" ] } ], "creator": null, "forks": [], "similar": [ { "count": 1, "repo": "htmlacademy-htmlcss/267983-sedona" }, { "count": 1, "repo": "htmlacademy-htmlcss/251249-sedona" }, { "count": 1, "repo": "htmlacademy-htmlcss/279207-nerds" }, { "count": 1, "repo": "htmlacademy-htmlcss/144865-sedona" }, { "count": 1, "repo": "CunoVery/239472-technomart" }, { "count": 1, "repo": "htmlacademy-htmlcss/235021-sedona" }, { "count": 1, "repo": "htmlacademy-htmlcss/176447-sedona" }, { "count": 1, "repo": "htmlacademy-htmlcss/250559-barbershop" } ], "stars": 0 };
            $scope.attrs.relatedRepos = data.similar;
            $scope.attrs.results = true;
        }

    // Construct
        $scope.methods.constructor();


})