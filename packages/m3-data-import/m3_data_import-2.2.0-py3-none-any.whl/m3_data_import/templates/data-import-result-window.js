
function forceLoad(){

	var params = {
		'force': true,
		'file': '{{ component.params.file }}'
	}

	Ext.Ajax.request({
        url: '{{ component.params.import_url }}',
        method: 'POST',
        params: params,
        success: function (res, opt) {
            smart_eval(res.responseText);
            win.close(true);
        },
        failure: Ext.emptyFn
    });
}

function closeWin(){
	win.close(true);
}
