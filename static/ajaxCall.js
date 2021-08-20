/**
 * Created by Reliability Group on 7/27/2017.
 */
ajaxPost = function (url,data,sucessCallBack) {
    $.ajax({url:url,data:JSON.stringify(data),contentType:'application/' +
    '; charset=utf-8',
        type:"POST",dataType:'json',success:sucessCallBack,error:sucessCallBack})
};
 ajaxGet = function (url,data,sucessCallBack) {
    $.ajax({url:url,data:JSON.stringify(data),contentType:'application/json; charset=utf-8',
        type:"GET",dataType:'json',success:sucessCallBack,error:sucessCallBack})
};

