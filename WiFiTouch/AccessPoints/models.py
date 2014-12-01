#-*- coding: utf-8 -*-
from django.db import models

STATUSES = [("OK", "OK"), ("NOT_FINISHED","NOT_FINISHED"), ("ERROR", "ERROR"), ]

# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class AccessPoint(models.Model):
    #Przynależnosc do poszczególnej grupy
    group = models.ForeignKey(Group)

    #identyfikacja AP
    mac_address = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=False )

    #dane do logowania na AP
    login = models.CharField(max_length=100)
    password_ap = models.CharField(max_length=100)

    #informacje dotyczace sieci
    bssid = models.CharField(max_length=100)
    ssid = models.CharField(max_length=100)
    ip_addres = models.CharField(max_length=100)
    encryption = models.CharField(max_length=100)
    password_wlan = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RouterGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    def __str__(self):
        return self.name

class Configuration(models.Model):

    config_body = models.TextField()

    def __str__(self):
        return "CONFIG %s" % self.id


class Router(models.Model):

    management_ip = models.GenericIPAddressField(blank=False, null=False)
    name = models.CharField(max_length=32, blank=False)
    login = models.CharField(max_length=32, blank=False)
    password = models.CharField(max_length=32, blank=True)
    config = models.ForeignKey(Configuration, null=True, blank=True)
    router_group = models.ForeignKey(RouterGroup, null=True, blank=True)
    default_wlan_name = models.CharField(max_length=255, blank=False, default="wlan1")

    def __str__(self):
        return self.name


class ApiQuery(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    request_id = models.CharField(unique=True, max_length=32)
    status = models.CharField(max_length=32, choices=STATUSES, blank=False)
    response_body = models.TextField()
    action_id = models.CharField(max_length=32)
    #command = models.ForeignKey(CommandItem)

    def __str__(self):
        return self.action_id


class CommandItem(models.Model):
    """
        Zastanowić się jutro nad senstem tej klasy
        oraz nad sposobem lookup'u zapytanie <-> komenda
        aby to logika nie zawierała mapowań tylko mapowania zawierały się w bazie
        dzięki temu będzie można z bazy wyciągać komendy podając tylko action_id

        action_id pochodzi z guzika (konkretne linkowanie - akcja/odpowiedz

        czyli nacisniecie guzika interfaces da nam action_id na konkretny guzik lub router
        oraz drugim wymaganym parametrem będzie command_id


        """
    command = models.CharField(max_length=255)
    arguments = models.TextField(blank=True)
    description = models.TextField(blank=True)
    command_key = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.command


class NetworkProfile(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ssid = models.CharField(max_length=32)
    key = models.CharField(max_length=63)
    security_type = models.CharField(max_length=255, blank=True)
    channel = models.IntegerField(max_length=10)

    def __str__(self):
        return self.name

