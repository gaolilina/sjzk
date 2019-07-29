/*
领域
 */
function get_field(select_id,field=null,init=true){
  $.get(base_url+'web/field/')
  .then(function(data){
    let inner_html = '';
    let fields = data.fields;
    for(let field_index in fields){
      let field = fields[field_index];
      inner_html += '<option value="'+field.name+'">'+field.name+'</option>';
    }
    $('#'+select_id).html(inner_html);
    if(init){
      const $button = '<input type="button" name="" value="添加" class="btn-field" onclick="add_field(\''+select_id+'\')" style="margin-top:-5px;">\
      <input type="button" name="" value="删除" class="btn-field" onclick="delete_field(\''+select_id+'\')" style="margin-top:-5px;">';
      $('#'+select_id).parent().append($button);
    }
    if(field!=null && field!=''){
      $('#'+select_id).val(field);
    }
  }).fail(function(){
    
  });
}
function add_field(select_id){
  $.confirm({
    title: null,
    content: '<h2>输入领域名称</h2><br/><input type="text" />',
    type: 'blue',
    icon: 'glyphicon glyphicon-question-sign',
    backgroundDismiss:true,
    columnClass:'width-300',
    buttons: {
      ok: {
        text: '确认',
        btnClass: 'btn-primary',
        action: function() {
            var name = $('.jconfirm-box').find('input').val();
            $.post(base_url+'web/field/',{'name':name})
            .then(function(data){
              if(data.code==-1) showAlert(data.msg);
              else {
                showAlert('添加成功');
                get_field(select_id,null,false);
              }
            }).fail(function(){
              showAlert(data.msg);
            });
        }
      },
      cancel: {
        text: '取消',
        btnClass: 'btn-default',
        action: function() {
            // 
        }
      }
    }
  });
}
function delete_field(select_id){
  $.confirm({
    title: null,
    content: '确认删除？',
    type: 'blue',
    icon: 'glyphicon glyphicon-question-sign',
    backgroundDismiss:true,
    columnClass:'width-300',
    buttons: {
      ok: {
          text: '确认',
          btnClass: 'btn-primary',
          action: function() {
              let field_id = $('#'+select_id).val();
                $.ajax({
                  type:'DELETE',
                  url: base_url+'web/field/'+field_id+'/',
                  dataType:'json',
                  error:function(){showAlert('删除失败');},
                  success: function(data){
                    showAlert('删除成功');
                    get_field(select_id,null,false);
                  }
                });
          }
      },
      cancel: {
          text: '取消',
          btnClass: 'btn-default',
          action: function() {}
      }
    }
  });
}