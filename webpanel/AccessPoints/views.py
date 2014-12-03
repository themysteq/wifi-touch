#-*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import  HttpResponse
from models import AccessPoint, ApiQuery,Router,RouterGroup, CommandItem, NetworkProfile
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect,HttpResponseBadRequest,HttpResponseNotFound
from django.db.models import Count
from django.http import QueryDict
import socket
import logging
import json
import django.core.exceptions
from django.core import serializers
import urlparse
import logichelper
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

#from webhook import webhook
logging.basicConfig(level=logging.INFO)
# Create your views here.

#Strona główna
import apihelper
import logichelper
from django.core import exceptions
import time




@login_required
def apiqueries_json(request):
    data = serializers.serialize('json', ApiQuery.objects.all().order_by('-modified'))
    return HttpResponse(data, 'application/json')


@login_required
def apiqueries(request):
    all_queries = ApiQuery.objects.all().order_by('-modified')
    return render(request, 'apiqueries.html', {'all_queries': all_queries})


@login_required
def routers(request):
    all_routers = Router.objects.all()
    return render(request, 'routers.html', {'routers': all_routers })


@login_required
def groups(request):
    groups = RouterGroup.objects.annotate(routers_count=Count('router'))
    return render(request, 'groups.html', {"groups": groups})


def login_view(request):
    logger = logging.getLogger(__name__)
    if request.method == 'POST':
        data = dict()
        messages = list()
        data["username"] = request.POST['username']
        data["password"] = request.POST['password']
        user = authenticate(username=data["username"], password=data["password"])
        if user is not None:
            if user.is_active:
                login(request, user)
                #redirect to success
                msg = {"type": "alert-success", "msg": "Logged in successfully "}
                messages.append(msg)
                return redirect('/')
            else:
                #disabled account:
                return HttpResponseNotFound("User disabled!")
        else:
            return render(request, 'login.html', {"bad_login_or_password": True})
            #invalid login

        json_data = json.dumps(data)
        logger.debug(json_data)

    return render(request, 'login.html' )


def logout_view(request):
    logout(request)
    return redirect('login_view')


@login_required
def main(request):

    messages = list()
    #msg = {"type":"alert-info","msg":"Heads up! This alert needs your attention, but it's not super important. "}
    #messages.append(msg)
    #msg = {"type":"alert-danger","msg":"Oh snap! Change a few things up and try submitting again. "}
    #messages.append(msg)

    return render(request, 'index.html', {"messages": messages, })

@login_required
def router_details_json(request):
    response = {}
    router_pk = None
    if request.method == "GET":
        router_pk = request.GET.get('router_pk', None)
    if router_pk:
        print "router_pk = %s" % router_pk
        json_response = serializers.serialize('json', Router.objects.filter(pk=router_pk),
                                              fields=('name', 'management_ip', 'router_group'))
    else:
        response["status"] = "ERROR"
        json_response = json.dumps(response)

    return HttpResponse(json_response, 'application/json')

@login_required
def get_action(request):
    #tu cała reszta
    return HttpResponse("GET ACTION OK!")

@login_required
def set_action(request):
    #tu cala reszta
    return HttpResponse("SET ACTION OK!")

@login_required
def show_router_details(request):

    """ Metoda odpowiada za wyświetlenie widoku możliwych ustawien
        Interfaces, ip addresses, security profiles etc. Widok zwraca wlasnie te 3 przyciski przyciski
     """

    router = ""
    if request.method == "GET":
        router_pk = request.GET.get('router_pk', None)
        router = Router.objects.get(pk=router_pk)

    return render(request, 'router_details.html', {"router": router, })



@login_required
def show_router_details_by_action(request):

    """
    command_key == action_id
    Wyciągamy command_key z zapytania, bierzemy nim z bazy stringa dla ApiQuery
    Wyciągamy router_pk z zapytania, bierzemy nim z bazy router (IP, admin/pass)
    Budujemy ApiQuery i wysyłamy asynchronicznie

    Ten widok zwraca formularz ze szczególami interfejsow, adres itd.

    """
    messages = []
    action_id = None
    command_key = None
    command_type = None
    router_pk = None

    if request.method == "GET":
        #action_id = request.GET.get('action_id', None)
        command_key = request.GET.get('command_key', None)
        router_pk = request.GET.get('router_pk', None)
        command_type = request.GET.get('command_type', None)

   # if request.is_ajax():
   #     single_api_query = ApiQuery.objects.get(action_id=action_id)
        single_router = Router.objects.get(pk=router_pk)
        if single_router:
            """ Tutaj nie moze to byc na twardo! Powinien to być command_method == 'print'
            Wtedy dopiero będzie najbardziej poprawnie
            """

            single_command = CommandItem.objects.get(command_key=command_type+"print")
            single_api_query = None
            apihelper_api_query = apihelper.APIQuery(query_type=apihelper.API_COMMAND_PUT_QUERY)
            apihelper_api_query.opt1["credentials"] = (single_router.login, single_router.password)
            apihelper_api_query.opt1["host"] = single_router.management_ip
            apihelper_api_query.query_body["command"] = single_command.command
            apihelper_api_query.query_body["args"] = ""
            apihelper_api_query.query_action = command_type+"print"+router_pk
            apihelper_api_query.activate()
            logichelper.sendApiQueryFromView(apihelper_api_query)
            while single_api_query is None:
                try:
                    single_api_query = ApiQuery.objects.get(action_id=command_type+"print"+router_pk)
                except exceptions.ObjectDoesNotExist:
                    time.sleep(1)


            json_response_body = single_api_query.response_body
            response_body = json.loads(json_response_body)


    #if request.is_ajax():
   #     return HttpResponse(json_response_body, 'application/json')
    if single_api_query.status == "OK":
         return render(request, 'router_details_by_action.html',
                       {"content": response_body[0]['content'],
                       "router_pk": router_pk,
                       "status": single_api_query.status,
                       "action": action_id,
                       "command_type": command_type,
                       })

    elif single_api_query.status == "ERROR":
        msg = {"type":"alert-danger","msg":"Cóż za tragiczny błąd! "}
        messages.append(msg)
        return render(request, 'router_details_by_action.html', {"error": response_body, "status": single_api_query.status, "messages":messages})

@login_required
def action_details(request):
    response = {}
    action_id = None
    api_query = None
    if request.method == "GET":
        action_id = request.GET.get('action_id', None)
    json_response = "[]"
    if request.is_ajax():
        if action_id:
            single_api_query = ApiQuery.objects.get(action_id=action_id)
            json_response = single_api_query.response_body
        else:
            json_response = json.dumps([])

        return HttpResponse(json_response, 'application/json')
    else:
        logger = logging.getLogger(__name__)
        single_api_query = ApiQuery.objects.get(action_id=action_id)
        logger.debug("single_api_query: %s", single_api_query)
        return render(request, 'action_details.html', {"single_api_query": single_api_query})


@login_required
def router_details_apply(request):
    logger = logging.getLogger(__name__)
    json_response = '["GET METHOD CALLED!"]'
    if request.method == "POST":
        qd = request.POST
        elements = qd.dict()
        form_query_string = elements['form']
        #command_key = elements['command_key']
        command_type = elements['command_type']
        command_method = elements['command_method']
        router_pk = elements['router']
        form_dict = urlparse.parse_qs(form_query_string)
        logger.debug(form_dict)
        command = command_type + command_method
        """ Ten element wymagał będzie parsowania! Tak po prostu nie można tego przekazać! """
        logger.debug("[router_details_apply] form_dict: %s", form_dict)
        apiquery = logichelper.prepareApiQueryToSend(command, router_pk, form_dict)
        logichelper.sendApiQueryFromView(apiquery)



        json_response = json.dumps(form_dict)
    #return HttpResponse(json_response,'application/json')
    return HttpResponse(json_response)


@login_required
def group_details(request):
    if request.method == "GET":
        query_dict = request.GET
        group_pk = query_dict.get("group_pk", None)
        group = RouterGroup.objects.get(pk=group_pk)
        routers = Router.objects.all().filter(router_group=group)
        router_set_list = list()
        for router in routers:
            security_profiles_unparsed = logichelper.b_getSecurityProfiles(router)
            wlans = logichelper.b_getWLANs(router)['content']
            for wlan in wlans:
                try:
                    pass
                    wlan["channel"] = logichelper.getChannelFromFreq24GHZ(wlan['frequency'])
                except KeyError:
                    pass
            security_profiles = logichelper.extrudeResponseBodyToDict(security_profiles_unparsed)['content']
            router_set = {"router": router,
                          "security_profiles": security_profiles,
                          "wlans": wlans}

            router_set_list.append(router_set)

        network_profiles = NetworkProfile.objects.all()
        return render(request, 'group_details.html', {"routers": routers,
                                                      "router_set_list": router_set_list,
                                                      "group": group,
                                                      "network_profiles": network_profiles})

    pass


@login_required
def network_profiles(request):
    profiles = NetworkProfile.objects.all()
    return render(request, 'network_profiles.html', {"profiles": profiles})


@login_required
def group_apply_profile(request):
    if request.method == "GET":
        qd = request.GET
        qd_dict = qd.dict()
        try:
            network_profile = NetworkProfile.objects.get(pk=qd_dict['profile_pk'])
            group = RouterGroup.objects.get(pk=qd_dict['group_pk'])
        except django.core.exceptions.ObjectDoesNotExist:
            logger = logging.getLogger(__name__)
            logger.error("Group or NetworkProfile does not exist!")
        logichelper.setNetworkProfileForGroup(network_profile, group)

    return HttpResponse("DONE")



""" Debug section"""


@login_required
def showSecurityProfiles_debug(request, router_pk):

    logger = logging.getLogger(__name__)
    try:
        router = Router.objects.get(pk=router_pk)
    except django.core.exceptions.ObjectDoesNotExist:
        logger.warning("Object not exists %s", router_pk)
        return  HttpResponseNotFound("<h1>HTTP 404 </h1> Router pk = %s not found" % router_pk)
    logger.debug("[showSecurityProfiles_debug] router: %s", router)
    security_profiles = logichelper.b_getSecurityProfiles(router)
    #content = None
    if security_profiles is not None:
        content = logichelper.extrudeResponseBodyToDict(security_profiles)
        status = "OK"
    else:
        status = "ERROR"

    response = {"BODY": content['content'], "STATUS": content['status'], "LENGTH": content['length'] }
    json_response = json.dumps(response)
    if logichelper.wants_json(request):
        return HttpResponse(json_response, "application/json")
    else:
        return render(request, 'security_profiles_list.html', response)


@login_required
def showWLANs_debug(request, router_pk):
    router = Router.objects.get(pk=router_pk)
    content = logichelper.b_getWLANs(router)
    response = {"BODY": content['content'], "STATUS": content['status'], "LENGTH": content['length'] }
    json_response = json.dumps(response)
    if logichelper.wants_json(request):
        return HttpResponse(json_response, 'application/json')
    else:
        return HttpResponseBadRequest('<h1>Bad request</h1><h2>View not implemented for this query</h2>')

""" End debug section """