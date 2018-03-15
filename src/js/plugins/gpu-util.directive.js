angular.module('linuxDash').directive('gpuUtil', ['server', function(server) {
  return {
    restrict: 'E',
    scope: {},
    template: '\
      <multi-line-chart-plugin \
          heading="GPU Utilisation" \
          module-name="gpu_util" \
          units="units"> \
      </multi-line-chart-plugin> \
    ',
    link: function(scope) {
      scope.units = '%'
    }
  }
}])