angular.module('linuxDash').directive('gpuTemp', ['server', function(server) {
  return {
    restrict: 'E',
    scope: {},
    template: '\
      <multi-line-chart-plugin \
          heading="GPU Temprature" \
          module-name="gpu_temp" \
          units="units"> \
      </multi-line-chart-plugin> \
    ',
    link: function(scope) {
      scope.units = '°C'
    }
  }
}])