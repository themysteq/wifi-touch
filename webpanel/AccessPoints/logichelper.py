#-*- coding: utf-8 -*-
__author__ = 'mysteq'
import apihelper
import logging
import socket
from models import ApiQuery
from models import Router
from models import CommandItem, NetworkProfile, RouterGroup
import time
import django.core.exceptions
import json
from django.http import QueryDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sendApiQueryWithSync(api_query):
    """ Do funkcji wpada juz aktywowane apiquery - wystarczy wyslac i pollowac o wyniki"""
    ticks_for_timeout = 50
    assert isinstance(api_query, apihelper.APIQuery)
    query_id = api_query.query_id
    result = sendApiQueryFromView(api_query)
    api_query_from_db = None
    ticks_counter = 0
    while api_query_from_db is None:
        ticks_counter += 1
        time.sleep(0.1)
        try:
            api_query_from_db = ApiQuery.objects.get(request_id=query_id)
        except django.core.exceptions.ObjectDoesNotExist:
            logger.warning("[sendApiQueryWithSync] request_id %s not found",query_id)
            api_query_from_db = None
        if ticks_counter > ticks_for_timeout:
            logger.warning("[sendApiQueryWithSync] Send with sync timeout reached!")
            break

    logger.info("[sendApiQueryWithSync] completed.")
    return api_query_from_db




def sendApiQueryFromView(api_query):
    assert isinstance(api_query, apihelper.APIQuery)
    query_to_backend_for_more = api_query
    if len(api_query.query_id) < 10:
        logger.error("[sendApiQueryFromView] query_id too short!")

    try:
        #logger.debug("Creating socket")
        sock = socket.socket()
        sock.connect(("localhost", apihelper.API_SERVER_PORT))
        #logger.debug("Socket connected")
        #logger.debug("Trying to serialize...")
        data_to_send = apihelper.serialize(query_to_backend_for_more)
        #logger.debug("Sending data... %s", data_to_send)
        sock.sendall(data_to_send)
        #logger.debug("Data sent!")
        raw_response = sock.recv(4096).strip()
        #logger.debug("Response received")
        #logger.debug("Raw response: %s", raw_response )
        backend_api_response = apihelper.deserialize(raw_response)
        #logger.debug("[sendApiQueryFromView]: %s", backend_api_response)

    except IOError, e:
        logger.error("Exception: " + e.strerror)
        raise

    finally:
        sock.close()
    return backend_api_response


def special_filter(key, value):
    if key in ["wpa-pre-shared-key", "wpa2-pre-shared-key", ]:
        value = '"' + value + '"'
        return key, value
    else:
        return key, value


def globalQueryFilter(key, command):
    logger  = logging.getLogger(__name__)
    logger.debug("\n| query filter | %s : %s", command, key)
    #/ip/address/set actual-interface
    if command == '/ip/address/set':
        if key in ["dynamic", "actual-interface", "invalid"]:
            return False
        else:
            return True

    if command == "/interface/wireless/set":
        if key in ["running", "interface-type"]:
            return False
        else:
            return True

    if command == "/interface/wireless/security-profiles/set":
        if key in ["default"]:
            return False
        else:
            return True

    else:
        logger.debug("filter accept")
        return True


def prepareArgumentsForApiQuery(args, command):
    logger = logging.getLogger(__name__)
    if args is not None:
        assert isinstance(args, dict)
        flat_list = list()


        for key, value in args.items():
            if globalQueryFilter(key, command):

                logger.debug("key : %s, value : %s", key, value[0] )
                #key, value[0] = special_filter(key, value[0])
                item = "="+key+"="+str(value[0])
                flat_list.append(item)
        logger.debug("sorting flat_list")
        flat_list.sort()
        logger.debug("flat_list: %s", flat_list)
        return flat_list
    else:
        return ""

def prepareApiQueryToSend(command_key, router_pk, args, ):
    router = Router.objects.get(pk=router_pk)
    command = CommandItem.objects.get(command_key=command_key)
    api_query = apihelper.APIQuery(query_type=apihelper.API_COMMAND_PUT_QUERY,
                                   query_action=command_key+str(router_pk))
    api_query.query_body = dict()
    api_query.query_body["command"] = command.command
    api_query.query_body["args"] = prepareArgumentsForApiQuery(args, command.command)
    api_query.opt1 = dict()
    api_query.opt1["credentials"] = (router.login, router.password)
    api_query.opt1["host"] = router.management_ip
    api_query.activate()
    return api_query

def extrudeContentFromResponseBody(query_from_db):
    return extrudeResponseBodyToDict(query_from_db)['content']

def extrudeResponseBodyToDict(query_from_db):
    assert isinstance(query_from_db, ApiQuery)
    return json.loads(query_from_db.response_body)[0]

def setNetworkProfileForGroup(network_profile, group):
    assert isinstance(network_profile, NetworkProfile)
    assert isinstance(group, RouterGroup)
    profile_name_prefix = "__wi__"
    """
    Najpierw  zobacz czy taki security profile istnieje na tym AP
    Jesli nie to go utwórz, jesli tak to go edytuj i zastosuj

    Sprawdź czy taki WLAN istnieje, jeśli tak to zmień mu ssid i security profile.
    jesli nie istnieje to taki stworz i ustaw mu security profile

    """

    # get routers where router.group == group
    # foreach router in routers
    # get security profiles
    #   foreach security profile in profiles
    #       filterProfile(security_profile)

    #


    """ Potential performance hit! """
    routers_in_group = Router.objects.all().filter(router_group=group)
    custom_wlan_name = "vap"
    default_master_wlan = "wlan1"
    master_wlan = "wlan1"
    security_profile_name = profile_name_prefix+network_profile.name
    profile_found_flag = False

    for router in routers_in_group:
        master_wlan = router.default_wlan_name
        if master_wlan is None:
            master_wlan = default_master_wlan

        security_profiles_unparsed = b_getSecurityProfiles(router)
        security_profiles = extrudeResponseBodyToDict(security_profiles_unparsed)['content']
        wlans = b_getWLANs(router)['content']
        status = extrudeResponseBodyToDict(security_profiles_unparsed)['status']
        profile_found_flag = False
        for single_security_profile in security_profiles:
            print "security profile name: %s" % single_security_profile['name']
            if security_profile_name == single_security_profile['name']:
                #profile utworzone przez nasz system, tylko one nas interesuja
                #na razie obslugujemy jeden profil
                #nadpisz ten security profile
                security_profile_id = single_security_profile['.id']
                setSecurityProfileForRouter(router, security_profile_id, network_profile.key)
                profile_found_flag = True
                break
        if profile_found_flag is False:
            #nie znalezlismy szukanego profilu, trzeba go utworzyc
            #zmienic na wartosc z profilu NetworkProfile
            createSecurityProfile(router, security_profile_name, network_profile.key)

        """ set wlans """

        wlan_found = None
        for wlan in wlans:
            if wlan['name'] == default_master_wlan:
                wlan_found = wlan
                break
        """
        if wlan_found is None:
            # utworz taki wlan
            createWLAN(router, custom_wlan_name, master_wlan)
            new_wlans = b_getWLANs(router)['content']
            for wlan in wlans:
                if wlan['name'] == custom_wlan_name:
                    wlan_found = wlan
                    break
        """
        if wlan_found is not None:
            setSecurityProfileForWLAN(router, wlan_found['.id'], security_profile_name)
            setSSIDForWLAN(router, wlan_found['.id'], network_profile.ssid)
            setChannelForWLAN(router, wlan_found['.id'], network_profile.channel)




def b_getRouterElement(router, command_key):
    logger.info("[b_getRouterElement] router: %s", router)
    get_command_key = command_key
    if "print" != get_command_key[-5:]:
        logger.warning("[b_getRouterElement] not print command issued. Returning None.")
        return None
    assert isinstance(router, Router)
    apiquery = prepareApiQueryToSend(get_command_key, router.pk, None)
    result = sendApiQueryWithSync(apiquery)
    if result is None:
        logger.warning("[b_getRouterElement] sendApiQueryWithSync returned None!")
        return None
    return result


def b_getSecurityProfiles(router):
    logger.info("[b_getSecurityProfiles] router: %s", router)
    get_security_profile_command_key = "sec_prof_print"
    assert isinstance(router, Router)
    #this_router = Router.objects.get(pk=router.pk)
    #command = CommandItem.objects.get(command_key=get_security_profile_command_key)
    apiquery = prepareApiQueryToSend(get_security_profile_command_key, router.pk, None)
    #wait for finish
    result = sendApiQueryWithSync(apiquery)
    if result is None:
        logger.warning("[b_getSecurityProfiles] sendApiQueryWithSync returned None!")
    else:
        assert isinstance(result, ApiQuery)
        #content = extrudeContent(result)
        logger.debug("[b_getSecurityProfiles] content: %s", str(result))
    return result
def getFrequencyFromChannel24GHZ(channel):
    base_channel_freq = 2412
    channel = int(channel)
    if channel >=1 and channel <=13:
        freq = base_channel_freq + 5*(channel-1)
        return freq
    else:
        return None

def getChannelFromFreq24GHZ(freq):
    freq = int(freq)
    base_channel_freq = 2412
    diff = freq - base_channel_freq
    diff /= 5
    diff += 1
    return diff

def setChannelForWLAN(router, wlan_id, channel):
    logger.info("setting channel : %d for wlan_id : %s", channel, wlan_id)
    args = dict()
    args[".id"] = [wlan_id]
    args["frequency"] = [getFrequencyFromChannel24GHZ(channel)]
    apiquery = prepareApiQueryToSend('if_wireless_set', router.pk, args)
    sendApiQueryFromView(apiquery)
    pass

def b_getWLANs(router):
    elements = b_getRouterElement(router, 'if_wireless_print')
    return extrudeResponseBodyToDict(elements)


def setSSIDForWLAN(router, wlan_id, ssid):
    logger.info("setting ssid : %s for wlan_id : %s", ssid, wlan_id)
    args = dict()
    args[".id"] = [wlan_id]
    args["ssid"] = [ssid]
    apiquery = prepareApiQueryToSend('if_wireless_set', router.pk, args)
    sendApiQueryFromView(apiquery)
    pass


def createWLAN(router, wlan_name, master_wlan):
    logger.info("creating WLAN %s - master : %s",wlan_name,master_wlan)
    args = dict()
    args["master-interface"] = [master_wlan]
    args["name"] = [wlan_name]
    apiquery = prepareApiQueryToSend('if_wireless_add', router.pk, args)
    sendApiQueryFromView(apiquery)


def setDefaultWLAN(router, wlan_name):
    elements = b_getRouterElement(router, 'if_wireless_print')
    content = extrudeResponseBodyToDict(elements)

    wlans = content['content']
    wlan_found = None
    try:
        for wlan in wlans:
            if wlan['name'] == wlan_name:
                wlan_found = wlan
                break

    except KeyError:
        logger.error('Failed to get default wlans for %s router', router.name)
    if wlan_found is not None:
        #znalazłeś taki WLAN to go teraz ustaw
        router.default_wlan_name = wlan_found['name']
        router.save()
        return router.default_wlan_name
    else:
        #nie ma takiego WLANU:<
        return None


def getDefaultWLAN(router):
    elements = b_getRouterElement(router, 'if_wireless_print')
    content = extrudeResponseBodyToDict(elements)

    wlans = content['content']
    wlan_found = None

    try:
        for wlan in wlans:
            if wlan['name'] == router.default_wlan_name:
                wlan_found = wlan
                break

    except KeyError:
        logger.error('Failed to get default wlans for %s router', router.name)
    if wlan_found is not None:
        return wlan_found
    else:
        #nie ma takiego WLANU:<
        return None


def setSecurityProfileForWLAN(router, wlan_id, security_profile_name):
    args = dict()
    args[".id"] = [wlan_id]
    args["security-profile"] = [security_profile_name]
    apiquery = prepareApiQueryToSend('if_wireless_set', router.pk, args)
    sendApiQueryFromView(apiquery)



def setSecurityProfileForRouter(router, profile_id, key):
    args = dict()
    args[".id"] = [profile_id]
    args["wpa2-pre-shared-key"] = [key]
    args["wpa-pre-shared-key"] = [key]
    apiquery = prepareApiQueryToSend('sec_prof_set', router.pk, args)
    sendApiQueryFromView(apiquery)


def createSecurityProfile(router, profile_name, key):
    args = dict()
    args["name"] = [profile_name]
    args["wpa2-pre-shared-key"] = [key]
    args["wpa-pre-shared-key"] = [key]
    logger.debug("[createSecurityProfile] args: %s", args)
    apiquery = prepareApiQueryToSend('sec_prof_add', router.pk, args)
    sendApiQueryFromView(apiquery)


def wants_json(request):
    json = False
    if request.method == "GET":
        qd = request.GET
        assert isinstance(qd, QueryDict)
        json = qd.get('json', None)
        if json is not None:
            return True
        else:
            return False
    return json