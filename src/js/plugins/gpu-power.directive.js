angular.module('linuxDash').directive('gpuPower', ['server', function(server) {
  return {
    restrict: 'E',
    scope: {},
    template: '\
      <multi-line-chart-plugin \
          heading="GPU Power" \
          module-name="gpu_power" \
          units="units"> \
      </multi-line-chart-plugin> \
    ',
    link: function(scope) {
      scope.units = 'W'
	  scope.min = 0
      scope.max = 300

    }
  }
}])