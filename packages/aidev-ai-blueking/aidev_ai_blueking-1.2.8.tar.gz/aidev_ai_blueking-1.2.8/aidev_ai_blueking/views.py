# -*- coding: utf-8 -*-

from aidev_agent.api.bk_aidev import BKAidevApi
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView


class IndexView(APIView):
    def get(self, request):
        client = BKAidevApi.get_client()
        result = client.api.retrieve_agent_config(path_params={"agent_code": settings.APP_CODE})
        agent_name = result["data"]["agent_name"]
        return render(
            request,
            "home.html",
            context=dict(
                SITE_URL="",
                BK_STATIC_URL="",
                BK_API_PREFIX="/bk_plugin/plugin_api",
                BK_USER_NAME=getattr(request.user, "username", ""),
                BK_AGENT_NAME=agent_name,
            ),
        )
