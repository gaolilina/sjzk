var domain = window.location.host;
if(domain.indexOf("pre") == 0) domain = domain.replace(/pre/,'pre.api');
else if(domain=='' || domain.indexOf('localhost')!=-1) domain = 'pre.api.web.chuangyh.com';
else  domain = 'api.' + domain;
domain = domain.replace('admin','web');
const base_url = "http://"+domain+"/";
const base_admin_url = "http://pre.api.admin.chuangyh.com/";
const base_page_url = "http://pre.web.chuangyh.com/";
const base_static_url = "http://static.chuangyh.com/";

function getRequest() { 
  var url = location.search; //获取url中"?"符后的字串 
  var theRequest = new Object(); 
  if (url.indexOf("?") != -1) { 
      var str = url.substr(1);
      strs = str.split("&");
      for(let i = 0; i < strs.length; i ++) {
          if(strs[i].indexOf('token')==-1)
            theRequest[strs[i].split("=")[0]]=decodeURI(strs[i].split("=")[1]);
          else
            theRequest[strs[i].split("=")[0]]=decodeURI(strs[i].replace("token=",""));
      } 
  }
  return theRequest; 
}
//token
function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");

    if (arr = document.cookie.match(reg))

        return unescape(arr[2]);
    else
        return null;
}

/*jqueryUI
*/
function showAlert(info){
  $.alert({
        title: null,
        content: info,
        confirmButton: 'Okay',
        columnClass:'width-300',
        confirmButtonClass: 'btn-primary',
        icon: 'fa fa-info',
        animation: 'zoom',                                    
        confirm: function(){}
    });
}
function showAlertReload(info){
  $.alert({
        title: null,
        content: info,
        confirmButton: 'Okay',
        columnClass:'width-300',
        confirmButtonClass: 'btn-primary',
        icon: 'fa fa-info',
        animation: 'zoom',                                    
        confirm: function(){
            window.location.reload();
        }
    });
}
