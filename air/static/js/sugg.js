
 var $table = $('#table'),
        $button = $('#button');
    $(function () {
        $button.click(function () {
            var JSONObj=$table.bootstrapTable('getSelections')
            if(JSONObj.length > 1)
            	{alert('getSelections: ' + 'Please select only one ');}
            else
		//{alert('getSelections: ' + JSON.stringify(JSONObj[0].Player));}
		{window.open("/redirectToDash?player="+JSONObj[0].Player,"_self");
                 }
        });
    });

