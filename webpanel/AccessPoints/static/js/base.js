/**
 * Created by mysteq on 01.11.14.
 */


var router_details_holder = "#router-details-holder";
var router_details_by_action_holder="#router-details-by-action-holder";
var global_returned;
var global_form_changes;
var group_details_holder = "#group-details-holder";
$(document).ready(function() {
         global_form_changes = "";
         function json_iter(obj) {
           for (var key in obj) {
                        if (typeof(obj[key]) == 'object') {

                            json_iter(obj[key]);
                            $('#modalJSONHolder').append("<br>");

                        } else {
                            $('#modalJSONHolder').append("<li>" + key + " => " + obj[key] + "</li>");
                        }
           }
         }
         function loadDataToModalAndShow(action_id){

                var url = "/apiqueries/action/"
                var request_data = {"action_id":action_id};
              $.get(url, request_data, function( data ){


                console.log(data);
                var obj = data[0]

                  //SECURITY ISSUE?!
               $('#modalJSONHolder').html("<ul>");
                json_iter(obj);
               $('#modalJSONHolder').append("</ul>");
               $('#generalModal').modal('show');

            });

         }


         function doTheMagic(_data) {
             //tutaj dzieje sie magia po nacisnieciu details
            console.log("Doing magic");
            var returned_data = _data;
            global_returned = returned_data;
            str = JSON.stringify(global_returned[0]['fields'])
            console.log("data returned: "+str);

            $(router_details_holder).fadeOut(500,function(){
                console.log("Fading out");
                $(router_details_holder).html(str);
                console.log("Content replaced");
                $(router_details_holder).fadeIn(500);
                console.log("Faded in");
            });
            }

        function showRouterDetailsFromView(_data){

              console.log("Showing router details");
              $(router_details_holder).html(_data);

          }
        function showRouterDetailsFromViewByAction(_data){

            //var router_pk;
            //var command_key;


        }
        function clickShowDetailsByAction(element)
        {

        }
        $("body").on('click','.group-details-btn',function(e){
            var group_pk;
            var url = "/groups/details/";
            group_pk = $(this).data("group");
            $('#processingModal').modal('show');
            $.get(url,{"group_pk":group_pk},function (data){
                $(group_details_holder).html(data);
                $('#processingModal').modal('hide');
            })
        });

        $("body").on('click','.router-detail-action-btn',function(e){
            console.log("router-detail-action-btn CLICK! ->" + this.value);
            var router_pk;
            var command_key;
            var url = "/router/details/action/";
            router_pk = $(this).attr("data-router");
            command_key = $(this).attr("data-command_key");
            command_type = $(this).attr("data-command_type");
            request_data = {"router_pk": router_pk, "command_key":command_key,"command_type":command_type};
            console.log("request data: "+JSON.stringify(request_data));
            //$(router_details_by_action_holder).fadeOut(50);
            $('#processingModal').modal('show');
            $(router_details_by_action_holder).html("LOADING...");
            $.get(url, request_data, function( data ){
               // doTheMagic(data);
               // showRouterDetailsFromView(data);
                //tutaj odbywa się ładowanie zablokowanego fomularza z opcjami edycji
                $(router_details_by_action_holder).html(data);
                $('#processingModal').modal('hide');
            });


        });

        $(".table > tbody > tr").click( function()
        {
            var action_id = $(this).data('action_id');
            if( typeof action_id != "undefined" ){
                console.log("action_id : "+action_id);

                loadDataToModalAndShow(action_id);

            }
        });
        $(".router-detail-btn").click( function() {

            var router_pk;
            router_pk = $(this).attr("data-router");
            //alert( "Router selected: "+router_pk );
            $(router_details_by_action_holder).fadeOut(500);
            $(router_details_by_action_holder).html("Pick router.");
            $(router_details_by_action_holder).fadeIn(500);
            var url = "/router/details/";
            var request_data = {"router_pk": router_pk};
            $.get(url, request_data, function( data ){
               // doTheMagic(data);
                showRouterDetailsFromView(data);

            });
        });




});
        function selectNetworkProfile(element){
            console.log(element);
            var profile_name = $(element).data('profile_name');
            var group_name = $(element).data('group_name');
            var group_pk = $(element).data('group');
            var profile_pk = $(element).data('profile');

            var select = confirm("Apply "+ profile_name+" to group "+ group_name+"?");
            var url = "/groups/apply_profile/";
            if(select == true) {
                $('#loading-indicator').slideDown(500);
                console.log("applying profile to group");
                $('#processingModal').modal('show');
                $.get(url,{"group_pk":group_pk, "profile_pk":profile_pk},function(data){
                    console.log(data);
                    $('#processingModal').modal('hide');
                    $('#loading-indicator').slideUp(500);
                } );
                console.log("applied!");
            }

        }

        function applyClick(element){
            var form = $(element).closest("form");
            var inputs = form.find('input');
            var form_id = form.data("item_id");
            var router = form.data("router");
            var action_id = form.data("action");
            var command_type = form.data("command_type");
            var command_method = $(element).data("command_method");
            console.log(form);
            console.log(global_form_changes);
            var post_url = "/router/details/apply/";
            var serial = form.serialize();
            console.log("serialized form:"+serial );
            $.post( post_url,{"form": serial,"command_type":command_type,
                "command_method":command_method,"router":router} , function(data){
                console.log("post done");
                console.log(data);

            } );

        }
        function changeClick(element){
            var form = $(element).closest("form");
            var form_id = form.data("item_id");
            var router_pk = form.data("router");
            var action_id = form.data("action");
            global_form_changes = [];
            console.log("flush global changes");

            var inputs = form.find('input').each( function(){
                $(this).prop('disabled', false);
                $(this).change(function(data){
                    console.log("form_id: "+form_id+"," +
                        " router: "+router_pk+
                        ", action_id: "+action_id+
                        " ,value: "+this.value);
                var item_name = $(this).data("item");
                var item_value = this.value;
                var item = {};
                item["router"] = router_pk;
                item["action_id"] = action_id;
                item["item_id"] = form_id;
                item["item_name"] = item_name;
                item["item_value"] = item_value;
                global_form_changes.push(item);
                })

            });
            console.log(inputs);

        }
        function revertClick(element){
            var form = $(element).closest("form");
            var inputs = form.find('input');

            console.log(inputs);
            alert("KLIKŁEŚ RIWERT!");
        }
      //  function addToGlobalFormChanges(key,value){
       //     global_form_changes[key] = value;
      //  }