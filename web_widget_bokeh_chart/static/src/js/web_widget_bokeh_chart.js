openerp.web_widget_bokeh_chart = function (instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.form.BokehChartWidget = instance.web.form.AbstractField.extend({
        render_value: function() {
            var val = this.get('value');
            this.$el.html(val);
        },
     
    });
    instance.web.form.widgets = instance.web.form.widgets.extend({
        'bokeh_chart': 'instance.web.form.BokehChartWidget',
    });

};

