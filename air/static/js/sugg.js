
 var $table = $('#table'),$table2 = $('#table2'),$table3 = $('#table3'),
        $button = $('#button'),$button2 = $('#button2'),$button3 = $('#button3');
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

      $button2.click(function () {
            var JSONObj=$table2.bootstrapTable('getSelections')
            if(JSONObj.length > 1)
            	{alert('getSelections: ' + 'Please select only one ');}
            else
		//{alert('getSelections: ' + JSON.stringify(JSONObj[0].Player));}
		{window.open("/redirectToDash?player="+JSONObj[0].Player,"_self");
                 }
        });
    });


