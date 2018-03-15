angular.module('linuxDash').directive('gpuMem', ['server', function(server) {
  return {
    restrict: 'E',
    scope: {},
    template: '\
      <multi-line-chart-plugin \
          heading="GPU RAM" \
          module-name="gpu_mem" \
          units="units"> \
      </multi-line-chart-plugin> \
    ',
    link: function(scope) {
      scope.units = '%'
    }
  }
}])