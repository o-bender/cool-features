// Простая замена для ES2015 `Test ${0}`
// '{1}est {0} string'.format('some', 'T') => 'Test some string'
(function(st){
    st.format = function(){
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(m, num, len, f, params){
            return args[num];
        });
    }
})(String.prototype);
